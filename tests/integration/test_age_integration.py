import asyncio
import logging
import os
import uuid

import pytest
from psycopg import AsyncConnection, sql

from age_mcp_server.database import PostgreSQLAGE, QueryPage
from age_mcp_server.schema import inspect_schema

CONNECTION_STRING = os.environ.get("AGE_TEST_CONNECTION_STRING")

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not CONNECTION_STRING,
        reason="AGE_TEST_CONNECTION_STRING is not configured",
    ),
]


async def _prepare_graph(connection_string: str, graph_name: str) -> None:
    connection = await AsyncConnection.connect(connection_string, autocommit=True)
    try:
        await connection.execute("CREATE EXTENSION IF NOT EXISTS age CASCADE")
        await connection.execute("LOAD 'age'")
        await connection.execute("SET search_path = ag_catalog, pg_catalog")
        await connection.execute(
            "SELECT ag_catalog.create_graph(%s::name)",
            (graph_name,),
        )
    finally:
        await connection.close()


async def _drop_graph(connection_string: str, graph_name: str) -> None:
    connection = await AsyncConnection.connect(connection_string, autocommit=True)
    try:
        await connection.execute("LOAD 'age'")
        await connection.execute("SET search_path = ag_catalog, pg_catalog")
        await connection.execute(
            "SELECT ag_catalog.drop_graph(%s::name, true)",
            (graph_name,),
        )
    finally:
        await connection.close()


async def _exercise_real_age(connection_string: str) -> None:
    graph_name = f"mcp_統合_{uuid.uuid4().hex[:8]}"
    await _prepare_graph(connection_string, graph_name)
    database = PostgreSQLAGE(
        connection_string,
        allow_write=True,
        log_level=logging.INFO,
        statement_timeout_ms=2_500,
        pool_min_size=1,
        pool_max_size=3,
        load_age=True,
    )
    await database.open()
    try:
        people = [
            {"name": "Ada", "age": 36, "active": True},
            {"name": "Grace", "age": 37, "active": True},
            {"name": "リン", "age": 38, "active": False},
        ]
        for person in people:
            affected = await database.execute_query(
                graph_name,
                ("CREATE (n:Person {name: $name, age: $age, active: $active}) RETURN n"),
                parameters=person,
                read_only=False,
            )
            assert affected >= 0

        await database.execute_query(
            graph_name,
            (
                "MATCH (a:Person), (b:Person) "
                "WHERE a.name = $from_name AND b.name = $to_name "
                "CREATE (a)-[r:KNOWS {since: $since}]->(b) RETURN r"
            ),
            parameters={"from_name": "Ada", "to_name": "リン", "since": 2026},
            read_only=False,
        )

        first = await database.execute_query(
            graph_name,
            (
                "MATCH (n:Person) WHERE n.age >= $minimum "
                "RETURN n.name AS name, n.age AS age ORDER BY age"
            ),
            parameters={"minimum": 36},
            page_size=2,
        )
        assert isinstance(first, QueryPage)
        assert first.returned == 2
        assert first.next_cursor

        second = await database.execute_query(
            graph_name,
            (
                "MATCH (n:Person) WHERE n.age >= $minimum "
                "RETURN n.name AS name, n.age AS age ORDER BY age"
            ),
            parameters={"minimum": 36},
            page_size=2,
            cursor=first.next_cursor,
        )
        assert isinstance(second, QueryPage)
        assert second.returned == 1
        assert second.next_cursor is None

        schema = await inspect_schema(database, graph_name)
        person = next(node for node in schema["nodes"] if node["label"] == "Person")
        assert person["count"] == 3
        assert {item["name"] for item in person["properties"]} >= {
            "name",
            "age",
            "active",
        }
        assert any(
            relationship["direction"] == "outgoing" and relationship["type"] == "KNOWS"
            for relationship in person["relationships"]
        )
        assert schema["edges"][0]["count"] == 1
        assert schema["edges"][0]["properties"][0]["name"] == "since"

        settings = await database.execute_sql(
            sql.SQL(
                "SELECT current_setting('transaction_read_only') AS read_only, "
                "current_setting('statement_timeout') AS timeout"
            ),
            read_only=True,
        )
        assert settings[0]["read_only"] == "on"
        assert settings[0]["timeout"] in {"2500ms", "2.5s"}
    finally:
        await database.close()
        await _drop_graph(connection_string, graph_name)


def test_real_apache_age_end_to_end() -> None:
    assert CONNECTION_STRING is not None
    asyncio.run(_exercise_real_age(CONNECTION_STRING))
