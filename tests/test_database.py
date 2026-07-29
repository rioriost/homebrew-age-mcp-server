import asyncio
import logging
from contextlib import AbstractAsyncContextManager
from typing import Any

import pytest
from psycopg import sql

from age_mcp_server.database import (
    DatabaseOperationError,
    PostgreSQLAGE,
    QueryPage,
)
from age_mcp_server.query import MAX_CURSOR_OFFSET, CursorCodec
from age_mcp_server.telemetry import Telemetry


class AsyncContext(AbstractAsyncContextManager[Any]):
    def __init__(self, value: Any):
        self.value = value

    async def __aenter__(self) -> Any:
        return self.value

    async def __aexit__(self, exc_type, exc, traceback) -> bool:
        return False


class FakeCursor:
    def __init__(self, results: list[dict[str, Any]] | None = None):
        self.results = results if results is not None else [{"n": "{}"}]
        self.rowcount = len(self.results)
        self.executions: list[tuple[Any, Any]] = []
        self.failure: Exception | None = None

    async def execute(self, query: Any, params: Any = None) -> None:
        self.executions.append((query, params))
        if self.failure:
            raise self.failure

    async def fetchall(self) -> list[dict[str, Any]]:
        return self.results


class FakeConnection:
    def __init__(self, results: list[dict[str, Any]] | None = None):
        self.cursor_instance = FakeCursor(results)
        self.executions: list[Any] = []
        self.commits = 0
        self.read_only: bool | None = None

    def transaction(self) -> AsyncContext:
        return AsyncContext(self)

    def cursor(self, **_kwargs: Any) -> AsyncContext:
        return AsyncContext(self.cursor_instance)

    async def execute(self, query: Any) -> None:
        self.executions.append(query)

    async def commit(self) -> None:
        self.commits += 1

    async def set_read_only(self, value: bool) -> None:
        self.read_only = value


class FakePool:
    def __init__(self, connection: FakeConnection, *, open_error: Exception | None = None):
        self.connection_instance = connection
        self.open_error = open_error
        self.open_calls: list[tuple[bool, int]] = []
        self.close_calls = 0

    def connection(self) -> AsyncContext:
        return AsyncContext(self.connection_instance)

    async def open(self, *, wait: bool, timeout: int) -> None:
        self.open_calls.append((wait, timeout))
        if self.open_error:
            raise self.open_error

    async def close(self) -> None:
        self.close_calls += 1


def make_database(
    connection: FakeConnection,
    *,
    allow_write: bool = True,
    open_error: Exception | None = None,
) -> tuple[PostgreSQLAGE, FakePool]:
    database = PostgreSQLAGE.__new__(PostgreSQLAGE)
    database.allow_write = allow_write
    database.statement_timeout_ms = 30_000
    database.load_age = False
    database.telemetry = Telemetry()
    database.cursor_codec = CursorCodec(b"x" * 32)
    pool = FakePool(connection, open_error=open_error)
    database.pool = pool
    return database, pool


def run(coroutine: Any) -> Any:
    return asyncio.run(coroutine)


def rendered(query: Any) -> str:
    return query.as_string(None) if isinstance(query, sql.Composable) else str(query)


def test_read_query_runs_in_read_only_transaction_and_paginates() -> None:
    connection = FakeConnection([{"n": 1}, {"n": 2}, {"n": 3}])
    database, _ = make_database(connection)

    first = run(database.execute_query("graph", "MATCH (n) RETURN n", page_size=2))

    assert isinstance(first, QueryPage)
    assert first.rows == [{"n": 1}, {"n": 2}]
    assert first.next_cursor
    executions = connection.cursor_instance.executions
    assert executions[0] == ("SET TRANSACTION READ ONLY", None)
    assert executions[1] == (
        "SELECT set_config('statement_timeout', %s, true)",
        ("30000",),
    )
    assert rendered(executions[2][0]).endswith("LIMIT 3 OFFSET 0")

    connection.cursor_instance.results = [{"n": 3}]
    second = run(
        database.execute_query(
            "graph",
            "MATCH (n) RETURN n",
            page_size=2,
            cursor=first.next_cursor,
        )
    )
    assert isinstance(second, QueryPage)
    assert second.rows == [{"n": 3}]
    assert second.next_cursor is None
    assert rendered(connection.cursor_instance.executions[-1][0]).endswith("LIMIT 3 OFFSET 2")


def test_parameterized_query_uses_safe_prepare_execute_and_deallocate() -> None:
    connection = FakeConnection([{"n": '"Ada"'}])
    database, _ = make_database(connection)
    malicious = "Ada'); DROP TABLE users; --"

    result = run(
        database.execute_query(
            "graph",
            "MATCH (n) WHERE n.name = $name RETURN n",
            parameters={"name": malicious},
        )
    )

    assert isinstance(result, QueryPage)
    sql_text = [rendered(item[0]) for item in connection.cursor_instance.executions]
    prepare = next(text for text in sql_text if text.startswith("PREPARE "))
    execute = next(text for text in sql_text if text.startswith("EXECUTE "))
    assert "$1" in prepare
    assert malicious not in prepare
    assert "DROP TABLE" in execute
    assert "''" in execute
    assert any(text.startswith("DEALLOCATE ") for text in sql_text)
    assert all(params is None for query, params in connection.cursor_instance.executions[2:])


def test_write_permissions_and_read_guards_run_before_database() -> None:
    connection = FakeConnection()
    database, _ = make_database(connection, allow_write=False)

    with pytest.raises(PermissionError, match="disabled"):
        run(database.execute_query("g", "CREATE (n) RETURN n", read_only=False))
    with pytest.raises(ValueError, match="read operation"):
        run(database.execute_query("g", "CREATE (n) RETURN n", read_only=True))
    with pytest.raises(ValueError, match="only supported for read"):
        writable, _ = make_database(connection)
        run(
            writable.execute_query(
                "g",
                "CREATE (n) RETURN n",
                read_only=False,
                cursor="not-used",
            )
        )
    assert connection.cursor_instance.executions == []


def test_write_returns_affected_row_count() -> None:
    connection = FakeConnection([{"n": 1}, {"n": 2}])
    database, _ = make_database(connection)

    result = run(database.execute_query("g", "CREATE (n) RETURN n", read_only=False))

    assert result == 2
    assert all(
        query != "SET TRANSACTION READ ONLY" for query, _ in connection.cursor_instance.executions
    )


def test_page_limits_and_cursor_binding_are_enforced() -> None:
    database, _ = make_database(FakeConnection())

    with pytest.raises(ValueError, match="Graph name"):
        run(database.execute_query("", "MATCH (n) RETURN n"))
    with pytest.raises(ValueError, match="Page size"):
        run(database.execute_query("g", "MATCH (n) RETURN n", page_size=0))
    cursor = database.cursor_codec.encode(
        __import__(
            "age_mcp_server.query", fromlist=["query_binding_fingerprint"]
        ).query_binding_fingerprint("g", "MATCH (n) RETURN n", None),
        MAX_CURSOR_OFFSET,
    )
    with pytest.raises(ValueError, match="maximum supported"):
        run(
            database.execute_query(
                "g",
                "MATCH (n) RETURN n",
                page_size=1,
                cursor=cursor,
            )
        )


def test_fixed_sql_and_internal_reads_use_bounded_read_only_transactions() -> None:
    connection = FakeConnection([{"name": "graph"}])
    database, _ = make_database(connection)

    assert run(
        database.execute_sql(
            sql.SQL("SELECT name FROM ag_catalog.ag_graph"),
            read_only=True,
        )
    ) == [{"name": "graph"}]
    assert run(database.read_all("g", "MATCH (n) RETURN n", max_rows=10)) == [{"name": "graph"}]
    assert (
        sum(
            query == "SET TRANSACTION READ ONLY"
            for query, _ in connection.cursor_instance.executions
        )
        == 2
    )
    with pytest.raises(ValueError, match="Internal read limit"):
        run(database.read_all("g", "MATCH (n) RETURN n", max_rows=0))
    with pytest.raises(ValueError, match="must not contain write"):
        run(database.read_all("g", "CREATE (n) RETURN n", max_rows=10))


def test_database_errors_are_sanitized_and_connection_string_is_not_logged(caplog) -> None:
    connection = FakeConnection()
    connection.cursor_instance.failure = RuntimeError("password=super-secret")
    database, _ = make_database(connection)
    caplog.set_level(logging.ERROR)

    with pytest.raises(DatabaseOperationError, match="Cypher operation failed"):
        run(database.execute_query("g", "MATCH (n) RETURN n"))
    assert "super-secret" not in caplog.text


def test_pool_lifecycle_and_connection_configuration() -> None:
    connection = FakeConnection()
    database, pool = make_database(connection)

    run(database.open())
    run(database.close())
    assert pool.open_calls == [(True, 30)]
    assert pool.close_calls == 1

    database.allow_write = False
    database.load_age = True
    run(database._configure_connection(connection))
    assert connection.executions == [
        "LOAD 'age'",
        "SET search_path = ag_catalog, pg_catalog",
    ]
    assert connection.commits == 1
    assert connection.read_only is True

    run(database._reset_connection(connection))
    assert connection.executions[-1] == "DEALLOCATE ALL"
    assert connection.commits == 2


def test_pool_open_failure_is_sanitized(caplog) -> None:
    database, pool = make_database(
        FakeConnection(),
        open_error=RuntimeError("password=super-secret"),
    )
    caplog.set_level(logging.ERROR)

    with pytest.raises(ConnectionError, match="Failed to connect"):
        run(database.open())
    assert pool.close_calls == 1
    assert "super-secret" not in caplog.text


@pytest.mark.parametrize(
    "kwargs",
    [
        {"statement_timeout_ms": 0},
        {"pool_min_size": 0},
        {"pool_min_size": 3, "pool_max_size": 2},
        {"pool_max_size": 65},
    ],
)
def test_constructor_rejects_invalid_resource_limits(kwargs: dict[str, int]) -> None:
    with pytest.raises(ValueError):
        PostgreSQLAGE("host=unused", False, logging.INFO, **kwargs)
