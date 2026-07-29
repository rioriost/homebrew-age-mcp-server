import logging
import secrets
from dataclasses import dataclass
from typing import Any

from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from .query import (
    MAX_CURSOR_OFFSET,
    MAX_PAGE_SIZE,
    CursorCodec,
    CypherQueryFormatter,
    query_binding_fingerprint,
    serialize_parameters,
    validate_graph_name,
)
from .telemetry import Telemetry

log = logging.getLogger(__name__)

DEFAULT_STATEMENT_TIMEOUT_MS = 30_000
DEFAULT_POOL_MIN_SIZE = 1
DEFAULT_POOL_MAX_SIZE = 4


class DatabaseOperationError(RuntimeError):
    """An error whose database details must not be returned to an MCP client."""


@dataclass(frozen=True)
class QueryPage:
    rows: list[dict[str, Any]]
    next_cursor: str | None

    @property
    def returned(self) -> int:
        return len(self.rows)


class PostgreSQLAGE:
    """Concurrent Apache AGE access backed by psycopg's async connection pool."""

    def __init__(
        self,
        pg_con_str: str,
        allow_write: bool,
        log_level: int,
        statement_timeout_ms: int = DEFAULT_STATEMENT_TIMEOUT_MS,
        *,
        pool_min_size: int = DEFAULT_POOL_MIN_SIZE,
        pool_max_size: int = DEFAULT_POOL_MAX_SIZE,
        load_age: bool = False,
        telemetry: Telemetry | None = None,
        cursor_codec: CursorCodec | None = None,
    ):
        if not 1 <= statement_timeout_ms <= 3_600_000:
            raise ValueError("Statement timeout must be between 1 and 3600000 milliseconds")
        if pool_min_size < 1 or pool_max_size < pool_min_size or pool_max_size > 64:
            raise ValueError("Pool sizes must satisfy 1 <= min <= max <= 64")
        log.setLevel(log_level)
        self.allow_write = allow_write
        self.statement_timeout_ms = statement_timeout_ms
        self.load_age = load_age
        self.telemetry = telemetry or Telemetry()
        self.cursor_codec = cursor_codec or CursorCodec()
        self.pool = AsyncConnectionPool(
            conninfo=pg_con_str,
            min_size=pool_min_size,
            max_size=pool_max_size,
            open=False,
            configure=self._configure_connection,
            reset=self._reset_connection,
            kwargs={
                "application_name": "age_mcp_server",
                "prepare_threshold": None,
            },
            name="age-mcp-server",
        )

    async def _configure_connection(self, connection: AsyncConnection[Any]) -> None:
        if self.load_age:
            await connection.execute("LOAD 'age'")
        await connection.execute("SET search_path = ag_catalog, pg_catalog")
        await connection.commit()
        if not self.allow_write:
            await connection.set_read_only(True)

    @staticmethod
    async def _reset_connection(connection: AsyncConnection[Any]) -> None:
        await connection.execute("DEALLOCATE ALL")
        await connection.commit()

    async def open(self) -> None:
        try:
            await self.pool.open(wait=True, timeout=30)
        except Exception as exc:
            log.error("Failed to connect to PostgreSQL (%s)", type(exc).__name__)
            await self.pool.close()
            raise ConnectionError("Failed to connect to PostgreSQL") from None

    async def close(self) -> None:
        await self.pool.close()

    async def _configure_transaction(self, cursor: Any, *, read_only: bool) -> None:
        if read_only:
            await cursor.execute("SET TRANSACTION READ ONLY")
        await cursor.execute(
            "SELECT set_config('statement_timeout', %s, true)",
            (str(self.statement_timeout_ms),),
        )

    async def _execute_cypher_sql(
        self,
        statement: sql.Composed,
        *,
        serialized_parameters: str | None,
        read_only: bool,
        has_write: bool,
    ) -> tuple[list[dict[str, Any]], int]:
        async with self.pool.connection() as connection:
            async with connection.transaction():
                async with connection.cursor(row_factory=dict_row) as cursor:
                    await self._configure_transaction(cursor, read_only=read_only)
                    if serialized_parameters is None:
                        await cursor.execute(statement)
                    else:
                        prepared_name = f"age_mcp_{secrets.token_hex(12)}"
                        prepare = sql.SQL("PREPARE {} (ag_catalog.agtype) AS {}").format(
                            sql.Identifier(prepared_name),
                            statement,
                        )
                        execute = sql.SQL("EXECUTE {} ({}::ag_catalog.agtype)").format(
                            sql.Identifier(prepared_name),
                            sql.Literal(serialized_parameters),
                        )
                        await cursor.execute(prepare)
                        await cursor.execute(execute)

                    if has_write:
                        affected_rows = max(cursor.rowcount, 0)
                        rows: list[dict[str, Any]] = []
                    else:
                        rows = await cursor.fetchall()
                        affected_rows = 0

                    if serialized_parameters is not None:
                        await cursor.execute(
                            sql.SQL("DEALLOCATE {}").format(sql.Identifier(prepared_name))
                        )
                    return rows, affected_rows

    async def execute_query(
        self,
        graph_name: str,
        query: str,
        *,
        parameters: dict[str, Any] | None = None,
        read_only: bool = True,
        page_size: int = MAX_PAGE_SIZE,
        cursor: str | None = None,
    ) -> QueryPage | int:
        validate_graph_name(graph_name)
        if not 1 <= page_size <= MAX_PAGE_SIZE:
            raise ValueError(f"Page size must be between 1 and {MAX_PAGE_SIZE}")
        analysis = CypherQueryFormatter.analyze(query, parameters)
        if read_only and analysis.has_write:
            raise ValueError("Write clauses are not allowed in a read operation")
        if analysis.has_write and not self.allow_write:
            raise PermissionError("Write operations are disabled")
        if analysis.has_write and cursor is not None:
            raise ValueError("Pagination cursors are only supported for read queries")

        serialized = serialize_parameters(parameters)
        binding = query_binding_fingerprint(graph_name, query, serialized)
        offset = self.cursor_codec.decode(cursor, binding)
        if offset + page_size > MAX_CURSOR_OFFSET:
            raise ValueError("Pagination cursor exceeds the maximum supported offset")
        row_limit = page_size + 1
        statement = CypherQueryFormatter.format_query(
            graph_name,
            query,
            allow_write=not read_only and self.allow_write,
            parameters=parameters,
            row_limit=row_limit,
            offset=offset,
        )
        fingerprint = binding[:12]
        attributes = {
            "db.system": "postgresql",
            "age.operation": "write" if analysis.has_write else "read",
            "age.parameterized": parameters is not None,
            "age.page.size": page_size,
            "age.query.fingerprint": fingerprint,
        }
        log.debug("Executing Cypher query %s", fingerprint)
        try:
            with self.telemetry.observe("age.cypher", attributes):
                rows, affected_rows = await self._execute_cypher_sql(
                    statement,
                    serialized_parameters=serialized,
                    read_only=read_only,
                    has_write=analysis.has_write,
                )
        except Exception as exc:
            log.error(
                "Database error executing Cypher query %s (%s)",
                fingerprint,
                type(exc).__name__,
            )
            raise DatabaseOperationError("Cypher operation failed") from None

        if analysis.has_write:
            return affected_rows
        has_more = len(rows) > page_size
        page_rows = rows[:page_size]
        next_cursor = self.cursor_codec.encode(binding, offset + page_size) if has_more else None
        return QueryPage(page_rows, next_cursor)

    async def read_all(
        self,
        graph_name: str,
        query: str,
        *,
        parameters: dict[str, Any] | None = None,
        max_rows: int,
    ) -> list[dict[str, Any]]:
        validate_graph_name(graph_name)
        if not 1 <= max_rows <= 1_000:
            raise ValueError("Internal read limit must be between 1 and 1000")
        analysis = CypherQueryFormatter.analyze(query, parameters)
        if analysis.has_write:
            raise ValueError("Internal reads must not contain write clauses")
        serialized = serialize_parameters(parameters)
        statement = CypherQueryFormatter.format_query(
            graph_name,
            query,
            allow_write=False,
            parameters=parameters,
            row_limit=max_rows,
        )
        binding = query_binding_fingerprint(graph_name, query, serialized)
        try:
            with self.telemetry.observe(
                "age.schema_query",
                {
                    "db.system": "postgresql",
                    "age.operation": "schema",
                    "age.parameterized": parameters is not None,
                    "age.query.fingerprint": binding[:12],
                },
            ):
                rows, _ = await self._execute_cypher_sql(
                    statement,
                    serialized_parameters=serialized,
                    read_only=True,
                    has_write=False,
                )
                return rows
        except Exception as exc:
            log.error("Database error executing schema query (%s)", type(exc).__name__)
            raise DatabaseOperationError("Schema query failed") from None

    async def execute_sql(
        self,
        query: sql.Composable,
        params: tuple[Any, ...] | None = None,
        *,
        read_only: bool,
    ) -> list[dict[str, Any]]:
        try:
            with self.telemetry.observe(
                "age.sql",
                {"db.system": "postgresql", "age.operation": "read" if read_only else "write"},
            ):
                async with self.pool.connection() as connection:
                    async with connection.transaction():
                        async with connection.cursor(row_factory=dict_row) as cursor:
                            await self._configure_transaction(cursor, read_only=read_only)
                            await cursor.execute(query, params)
                            return await cursor.fetchall()
        except Exception as exc:
            log.error("Database error executing AGE SQL operation (%s)", type(exc).__name__)
            raise DatabaseOperationError("AGE SQL operation failed") from None
