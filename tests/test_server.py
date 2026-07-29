import asyncio
import json
from typing import Any

import pytest
from mcp.server import Server
from psycopg import sql

from age_mcp_server import server
from age_mcp_server.database import DatabaseOperationError, QueryPage
from age_mcp_server.telemetry import Telemetry


class FakeToolDatabase:
    def __init__(self):
        self.calls: list[tuple[Any, ...]] = []
        self.telemetry = Telemetry()

    async def execute_query(self, graph_name: str, query: str, **kwargs: Any) -> QueryPage | int:
        self.calls.append(("cypher", graph_name, query, kwargs))
        if kwargs["read_only"]:
            return QueryPage([{"value": 1}], "next")
        return 2

    async def execute_sql(
        self,
        query: Any,
        params: tuple[Any, ...] | None = None,
        *,
        read_only: bool,
    ) -> list[dict[str, Any]]:
        self.calls.append(("sql", query, params, read_only))
        if read_only:
            return [{"name": '"alpha"'}, {"name": '"beta"'}]
        return [{"ok": True}]

    async def read_all(
        self,
        _graph_name: str,
        query: str,
        *,
        max_rows: int,
        parameters=None,
    ) -> list[dict[str, Any]]:
        if "UNWIND labels" in query:
            return [
                {
                    "label": '"Person"',
                    "entity_count": "1",
                    "property_names": '[["name"]]',
                }
            ]
        if "MATCH (a)-[r]" in query:
            return []
        if "MATCH (n) RETURN labels" in query:
            return [
                {
                    "labels": '["Person"]',
                    "entity": ('{"id":1,"label":"Person","properties":{"name":"Ada"}}::vertex'),
                }
            ]
        return []


def call(database: Any, allow_write: bool, name: str, arguments: Any):
    return asyncio.run(server.call_tool(database, allow_write, name, arguments))


def structured(result: Any) -> dict[str, Any]:
    assert json.loads(result.content[0].text) == result.structured_content
    return result.structured_content


def test_tools_publish_structured_output_schemas_and_annotations() -> None:
    read_tools = server.build_tools(False)
    write_tools = server.build_tools(True)

    assert {tool.name for tool in read_tools} == {
        "read-age-cypher",
        "list-age-graphs",
        "get-age-schema",
    }
    assert {tool.name for tool in write_tools} >= {
        "write-age-cypher",
        "create-age-graph",
        "drop-age-graph",
    }
    for tool in write_tools:
        assert tool.output_schema["type"] == "object"
        assert tool.input_schema["type"] == "object"
    read = next(tool for tool in read_tools if tool.name == "read-age-cypher")
    assert read.annotations.read_only_hint is True
    assert {"parameters", "page_size", "cursor"} <= set(read.input_schema["properties"])


def test_tool_dispatches_read_write_graph_and_list_operations() -> None:
    database = FakeToolDatabase()

    read = call(
        database,
        False,
        "read-age-cypher",
        {
            "graph_name": "graph",
            "query": "MATCH (n) WHERE n.name = $name RETURN n",
            "parameters": {"name": "Ada"},
            "page_size": 10,
        },
    )
    assert structured(read) == {
        "rows": [{"value": 1}],
        "returned": 1,
        "nextCursor": "next",
    }
    assert read.is_error is False
    assert structured(call(database, False, "list-age-graphs", {})) == {
        "graphs": ["alpha", "beta"],
        "count": 2,
    }
    assert structured(call(database, True, "create-age-graph", {"graph_name": "graph"})) == {
        "graphName": "graph",
        "success": True,
    }
    assert structured(call(database, True, "drop-age-graph", {"graph_name": "graph"})) == {
        "graphName": "graph",
        "success": True,
    }
    assert structured(
        call(
            database,
            True,
            "write-age-cypher",
            {"graph_name": "graph", "query": "CREATE (n) RETURN n"},
        )
    ) == {"affectedRows": 2}
    create_call = next(
        item for item in database.calls if item[0] == "sql" and item[2] == ("graph",)
    )
    assert isinstance(create_call[1], sql.SQL)


def test_schema_tool_returns_structured_rich_schema() -> None:
    result = structured(call(FakeToolDatabase(), False, "get-age-schema", {"graph_name": "graph"}))

    assert result["nodes"][0]["label"] == "Person"
    assert result["nodes"][0]["count"] == 1
    assert result["nodes"][0]["properties"][0]["types"] == ["string"]
    assert result["edges"] == []


@pytest.mark.parametrize(
    ("allow_write", "name", "arguments", "message"),
    [
        (False, "create-age-graph", {"graph_name": "g"}, "disabled"),
        (
            True,
            "write-age-cypher",
            {"graph_name": "g", "query": "MATCH (n) RETURN n"},
            "mutating",
        ),
        (False, "read-age-cypher", None, "arguments"),
        (
            False,
            "read-age-cypher",
            {"graph_name": "g", "query": "MATCH (n) RETURN n", "page_size": True},
            "page_size",
        ),
        (False, "unknown", {}, "Unknown tool"),
    ],
)
def test_tool_validation_errors_are_structured(
    allow_write: bool,
    name: str,
    arguments: Any,
    message: str,
) -> None:
    result = call(FakeToolDatabase(), allow_write, name, arguments)

    assert result.is_error is True
    assert message in structured(result)["error"]


def test_database_and_unexpected_errors_are_sanitized() -> None:
    class FailingDatabase(FakeToolDatabase):
        async def execute_sql(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
            raise DatabaseOperationError("password=secret")

    database_result = call(FailingDatabase(), False, "list-age-graphs", {})
    assert structured(database_result) == {"error": "Database operation failed; see server logs"}

    class UnexpectedDatabase(FakeToolDatabase):
        async def execute_sql(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
            raise RuntimeError("password=secret")

    unexpected_result = call(UnexpectedDatabase(), False, "list-age-graphs", {})
    assert structured(unexpected_result) == {"error": "Internal server error"}


def test_create_server_registers_mcp2_handlers() -> None:
    application = server.create_server(FakeToolDatabase(), False)

    assert isinstance(application, Server)
    assert application.get_request_handler("tools/list") is not None
    assert application.get_request_handler("tools/call") is not None
