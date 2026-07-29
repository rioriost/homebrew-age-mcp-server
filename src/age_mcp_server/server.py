import json
import logging
from importlib.metadata import PackageNotFoundError, version
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from psycopg import sql

from .database import (
    DEFAULT_POOL_MAX_SIZE,
    DEFAULT_POOL_MIN_SIZE,
    DEFAULT_STATEMENT_TIMEOUT_MS,
    DatabaseOperationError,
    PostgreSQLAGE,
    QueryPage,
)
from .query import (
    MAX_GRAPH_NAME_BYTES,
    MAX_PAGE_SIZE,
    MAX_QUERY_LENGTH,
    CursorCodec,
    CypherQueryFormatter,
    validate_graph_name,
)
from .schema import decode_agtype, inspect_schema
from .telemetry import Telemetry

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

READ_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "rows": {"type": "array", "items": {"type": "object"}},
        "returned": {"type": "integer", "minimum": 0, "maximum": MAX_PAGE_SIZE},
        "nextCursor": {"type": ["string", "null"]},
    },
    "required": ["rows", "returned", "nextCursor"],
    "additionalProperties": False,
}
WRITE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {"affectedRows": {"type": "integer", "minimum": 0}},
    "required": ["affectedRows"],
    "additionalProperties": False,
}
GRAPH_OPERATION_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "graphName": {"type": "string"},
        "success": {"type": "boolean"},
    },
    "required": ["graphName", "success"],
    "additionalProperties": False,
}
LIST_GRAPHS_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "graphs": {"type": "array", "items": {"type": "string"}},
        "count": {"type": "integer", "minimum": 0},
    },
    "required": ["graphs", "count"],
    "additionalProperties": False,
}
SCHEMA_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "nodes": {"type": "array", "items": {"type": "object"}},
        "edges": {"type": "array", "items": {"type": "object"}},
        "sampling": {"type": "object"},
    },
    "required": ["nodes", "edges", "sampling"],
    "additionalProperties": False,
}


def _package_version() -> str:
    try:
        return version("age_mcp_server")
    except PackageNotFoundError:
        return "0.3.0"


def _string_argument(arguments: dict[str, Any] | None, name: str) -> str:
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be an object")
    value = arguments.get(name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"'{name}' must be a non-empty string")
    return value


def _optional_parameters(arguments: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be an object")
    value = arguments.get("parameters")
    if value is not None and not isinstance(value, dict):
        raise ValueError("'parameters' must be an object")
    return value


def _page_size(arguments: dict[str, Any] | None) -> int:
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be an object")
    value = arguments.get("page_size", MAX_PAGE_SIZE)
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= MAX_PAGE_SIZE:
        raise ValueError(f"'page_size' must be between 1 and {MAX_PAGE_SIZE}")
    return value


def _optional_cursor(arguments: dict[str, Any] | None) -> str | None:
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be an object")
    value = arguments.get("cursor")
    if value is not None and not isinstance(value, str):
        raise ValueError("'cursor' must be a string")
    return value


def _tool_result(data: Any, *, is_error: bool = False) -> types.CallToolResult:
    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text=json.dumps(
                    data,
                    ensure_ascii=False,
                    default=str,
                    separators=(",", ":"),
                ),
            )
        ],
        structuredContent=data,
        isError=is_error,
    )


def _query_input_schema(*, paginated: bool) -> dict[str, Any]:
    properties: dict[str, Any] = {
        "query": {
            "type": "string",
            "minLength": 1,
            "maxLength": MAX_QUERY_LENGTH,
            "description": "Cypher query to execute",
        },
        "graph_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": MAX_GRAPH_NAME_BYTES,
            "description": "Name of the graph to operate",
        },
        "parameters": {
            "type": "object",
            "description": (
                "JSON values bound to Cypher $placeholders; serialized as an AGE agtype map"
            ),
            "maxProperties": 1_000,
        },
    }
    if paginated:
        properties.update(
            {
                "page_size": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": MAX_PAGE_SIZE,
                    "default": MAX_PAGE_SIZE,
                },
                "cursor": {
                    "type": "string",
                    "description": "Opaque cursor returned by the previous page",
                    "maxLength": 512,
                },
            }
        )
    return {
        "type": "object",
        "properties": properties,
        "required": ["query", "graph_name"],
        "additionalProperties": False,
    }


def build_tools(allow_write: bool) -> list[types.Tool]:
    graph_name_schema = {
        "type": "string",
        "description": "Name of the graph to operate",
        "minLength": 1,
        "maxLength": MAX_GRAPH_NAME_BYTES,
    }
    read_annotations = types.ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
    tools = [
        types.Tool(
            name="read-age-cypher",
            description=("Execute paginated read-only Cypher with optional bound parameters"),
            annotations=read_annotations,
            inputSchema=_query_input_schema(paginated=True),
            outputSchema=READ_OUTPUT_SCHEMA,
        ),
        types.Tool(
            name="list-age-graphs",
            description="List all graphs in Apache AGE",
            annotations=read_annotations,
            inputSchema={"type": "object", "additionalProperties": False},
            outputSchema=LIST_GRAPHS_OUTPUT_SCHEMA,
        ),
        types.Tool(
            name="get-age-schema",
            description=("Inspect labels, counts, direction, and sampled property types"),
            annotations=read_annotations,
            inputSchema={
                "type": "object",
                "properties": {"graph_name": graph_name_schema},
                "required": ["graph_name"],
                "additionalProperties": False,
            },
            outputSchema=SCHEMA_OUTPUT_SCHEMA,
        ),
    ]
    if allow_write:
        tools.extend(
            [
                types.Tool(
                    name="write-age-cypher",
                    description=("Execute mutating Cypher with optional bound parameters"),
                    annotations=types.ToolAnnotations(
                        readOnlyHint=False,
                        destructiveHint=True,
                        idempotentHint=False,
                        openWorldHint=True,
                    ),
                    inputSchema=_query_input_schema(paginated=False),
                    outputSchema=WRITE_OUTPUT_SCHEMA,
                ),
                types.Tool(
                    name="create-age-graph",
                    description="Create a new Apache AGE graph",
                    annotations=types.ToolAnnotations(
                        readOnlyHint=False,
                        destructiveHint=False,
                        idempotentHint=False,
                        openWorldHint=True,
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {"graph_name": graph_name_schema},
                        "required": ["graph_name"],
                        "additionalProperties": False,
                    },
                    outputSchema=GRAPH_OPERATION_OUTPUT_SCHEMA,
                ),
                types.Tool(
                    name="drop-age-graph",
                    description="Drop an Apache AGE graph",
                    annotations=types.ToolAnnotations(
                        readOnlyHint=False,
                        destructiveHint=True,
                        idempotentHint=False,
                        openWorldHint=True,
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {"graph_name": graph_name_schema},
                        "required": ["graph_name"],
                        "additionalProperties": False,
                    },
                    outputSchema=GRAPH_OPERATION_OUTPUT_SCHEMA,
                ),
            ]
        )
    return tools


async def call_tool(
    db: PostgreSQLAGE,
    allow_write: bool,
    name: str,
    arguments: dict[str, Any] | None,
    telemetry: Telemetry | None = None,
) -> types.CallToolResult:
    telemetry = telemetry or db.telemetry
    try:
        with telemetry.observe("age.tool", {"mcp.tool.name": name}):
            if name == "get-age-schema":
                graph_name = validate_graph_name(_string_argument(arguments, "graph_name"))
                return _tool_result(await inspect_schema(db, graph_name))

            if name == "create-age-graph":
                if not allow_write:
                    raise PermissionError("Write operations are disabled")
                graph_name = validate_graph_name(_string_argument(arguments, "graph_name"))
                await db.execute_sql(
                    sql.SQL("SELECT ag_catalog.create_graph(%s::name)"),
                    (graph_name,),
                    read_only=False,
                )
                return _tool_result({"graphName": graph_name, "success": True})

            if name == "drop-age-graph":
                if not allow_write:
                    raise PermissionError("Write operations are disabled")
                graph_name = validate_graph_name(_string_argument(arguments, "graph_name"))
                await db.execute_sql(
                    sql.SQL("SELECT ag_catalog.drop_graph(%s::name, true)"),
                    (graph_name,),
                    read_only=False,
                )
                return _tool_result({"graphName": graph_name, "success": True})

            if name == "list-age-graphs":
                rows = await db.execute_sql(
                    sql.SQL("SELECT name FROM ag_catalog.ag_graph ORDER BY name"),
                    read_only=True,
                )
                graphs = [str(decode_agtype(row["name"])) for row in rows]
                return _tool_result({"graphs": graphs, "count": len(graphs)})

            if name == "read-age-cypher":
                graph_name = validate_graph_name(_string_argument(arguments, "graph_name"))
                result = await db.execute_query(
                    graph_name,
                    _string_argument(arguments, "query"),
                    parameters=_optional_parameters(arguments),
                    read_only=True,
                    page_size=_page_size(arguments),
                    cursor=_optional_cursor(arguments),
                )
                if not isinstance(result, QueryPage):
                    raise RuntimeError("Read query returned an invalid result")
                return _tool_result(
                    {
                        "rows": result.rows,
                        "returned": result.returned,
                        "nextCursor": result.next_cursor,
                    }
                )

            if name == "write-age-cypher":
                if not allow_write:
                    raise PermissionError("Write operations are disabled")
                graph_name = validate_graph_name(_string_argument(arguments, "graph_name"))
                query = _string_argument(arguments, "query")
                parameters = _optional_parameters(arguments)
                if not CypherQueryFormatter.analyze(query, parameters).has_write:
                    raise ValueError("A write tool call must contain a mutating clause")
                affected_rows = await db.execute_query(
                    graph_name,
                    query,
                    parameters=parameters,
                    read_only=False,
                )
                if not isinstance(affected_rows, int):
                    raise RuntimeError("Write query returned an invalid result")
                return _tool_result({"affectedRows": affected_rows})

            raise ValueError(f"Unknown tool: {name}")
    except (PermissionError, ValueError) as exc:
        return _tool_result({"error": str(exc)}, is_error=True)
    except DatabaseOperationError:
        return _tool_result(
            {"error": "Database operation failed; see server logs"},
            is_error=True,
        )
    except Exception as exc:
        log.error("Unexpected tool error (%s)", type(exc).__name__)
        return _tool_result({"error": "Internal server error"}, is_error=True)


def create_server(
    db: PostgreSQLAGE,
    allow_write: bool,
    telemetry: Telemetry | None = None,
) -> Server[dict[str, Any]]:
    async def list_tools_handler(
        _context: Any,
        _params: types.PaginatedRequestParams | None,
    ) -> types.ListToolsResult:
        return types.ListToolsResult(tools=build_tools(allow_write))

    async def call_tool_handler(
        _context: Any,
        params: types.CallToolRequestParams,
    ) -> types.CallToolResult:
        return await call_tool(
            db,
            allow_write,
            params.name,
            params.arguments,
            telemetry,
        )

    return Server(
        "age-manager",
        version=_package_version(),
        description="Secure Apache AGE graph access",
        on_list_tools=list_tools_handler,
        on_call_tool=call_tool_handler,
    )


async def main(
    pg_con_str: str,
    allow_write: bool,
    log_level: int,
    statement_timeout_ms: int = DEFAULT_STATEMENT_TIMEOUT_MS,
    *,
    pool_min_size: int = DEFAULT_POOL_MIN_SIZE,
    pool_max_size: int = DEFAULT_POOL_MAX_SIZE,
    load_age: bool = False,
    telemetry: Telemetry | None = None,
) -> None:
    log.setLevel(log_level)
    log.info("Connecting to PostgreSQL")
    telemetry = telemetry or Telemetry()
    db = PostgreSQLAGE(
        pg_con_str=pg_con_str,
        allow_write=allow_write,
        log_level=log_level,
        statement_timeout_ms=statement_timeout_ms,
        pool_min_size=pool_min_size,
        pool_max_size=pool_max_size,
        load_age=load_age,
        telemetry=telemetry,
    )
    await db.open()
    server = create_server(db, allow_write, telemetry)
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            log.info("Server running with stdio transport")
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(notification_options=NotificationOptions()),
            )
    finally:
        await db.close()


__all__ = [
    "CursorCodec",
    "CypherQueryFormatter",
    "DatabaseOperationError",
    "PostgreSQLAGE",
    "QueryPage",
    "build_tools",
    "call_tool",
    "create_server",
    "main",
    "validate_graph_name",
]
