#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import re
import sys
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from psycopg import Connection
from psycopg.rows import dict_row
from agefreighter.cypherparser import CypherParser

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class CypherQueryFormatter:
    """Utility class for formatting Cypher queries for Apache AGE."""

    @staticmethod
    def format_query(graph_name: str, cypher_query: str, allow_write: bool) -> str:
        """
        Format the provided Cypher query for Apache AGE.

        Raises:
            ValueError: If the query is unsafe or incorrectly formatted.
        """
        if not allow_write:
            if not CypherQueryFormatter.is_safe_cypher_query(cypher_query):
                raise ValueError("Unsafe query")

        # Append LIMIT 50 if no limit is specified.
        if "limit" not in cypher_query.lower():
            cypher_query += " LIMIT 50"

        # Claude misunderstands the Cypher definition
        if "cast" in cypher_query.lower():
            raise ValueError("'CAST' is not a reserved keyword in Cypher")

        returns = CypherQueryFormatter.get_return_values(cypher_query)
        log.debug(f"Return values: {returns}")

        # Check for parameterized query usage.
        if re.findall(r"\$(\w+)", cypher_query):
            raise ValueError("Parameterized query")

        if returns:
            ag_types = ", ".join([f"{r} agtype" for r in returns])
            return f"SELECT * FROM cypher('{graph_name}', $$ {cypher_query} $$) AS ({ag_types});"
        else:
            raise ValueError("No return values specified")

    @staticmethod
    def is_safe_cypher_query(cypher_query: str) -> bool:
        """
        Ensure the Cypher query does not contain dangerous commands.

        Returns:
            bool: True if safe, False otherwise.
        """
        tokens = cypher_query.split()
        unsafe_keywords = ["add", "create", "delete", "merge", "remove", "set"]
        return all(token.lower() not in unsafe_keywords for token in tokens)

    @staticmethod
    def get_return_values(cypher_query: str) -> list:
        parser = CypherParser()
        try:
            result = parser.parse(cypher_query)
        except Exception as e:
            log.error(f"Failed to parse Cypher query: {e}")
            return []

        for op, opr, *_ in result:
            log.debug(f"Returning values from query: {opr}")
            if op == "RETURN" or op == "RETURN_DISTINCT":
                results = []
                for v in opr:
                    if isinstance(v, str):
                        results.append(v.split(".")[0])
                    elif isinstance(v, tuple):
                        match v[0]:
                            case "alias":
                                results.append(v[-1])
                            case "property":
                                results.append(v[-1])
                            case "func_call":
                                results.append(v[1])
                            case "":
                                pass
                return list(set(results))

        return []


class PostgreSQLAGE:
    def __init__(self, pg_con_str: str, allow_write: bool, log_level: int):
        """Initialize connection to the PostgreSQL database"""
        log.setLevel(log_level)
        log.debug(f"Initializing database connection to {pg_con_str}")
        self.pg_con_str = pg_con_str
        self.allow_write = allow_write
        self.con: Connection
        try:
            self.con = Connection.connect(
                self.pg_con_str
                + " options='-c search_path=ag_catalog,\"$user\",public'"
            )
        except Exception as e:
            log.error(f"Failed to connect to PostgreSQL database: {e}")
            sys.exit(1)

    def _execute_query(
        self, graph_name: str, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query and return results as a list of dictionaries"""
        log.debug(f"Executing query: {query}")
        try:
            cur = self.con.cursor(row_factory=dict_row)
            cypher_query = CypherQueryFormatter.format_query(
                graph_name=graph_name,
                cypher_query=query,
                allow_write=self.allow_write,
            )
            log.debug(f"Formatted query: {cypher_query}")
            cur.execute(cypher_query, params)
            results = cur.fetchall()
            cur.execute("COMMIT")
            count = len(results)
            if CypherQueryFormatter.is_safe_cypher_query(query):
                log.debug(f"Read query returned {count} rows")
                return results
            else:
                log.debug(f"Write query affected {count}")
                return [count]
        except Exception as e:
            log.error(f"Database error executing query: {e}\n{query}")
            self.con.rollback()  # Roll back to clear the error state
            raise

    def _execute_sql(self, query: str) -> list[dict[str, Any]]:
        """Execute a standard query and return results as a list of dictionaries"""
        log.debug(f"Executing query: {query}")
        try:
            cur = self.con.cursor(row_factory=dict_row)
            cur.execute(query)
            results = cur.fetchall()
            cur.execute("COMMIT")
            return results
        except Exception as e:
            log.error(f"Database error executing query: {e}\n{query}")
            self.con.rollback()  # Roll back to clear the error state
            raise


async def main(pg_con_str: str, allow_write: bool, log_level: int) -> None:
    log.setLevel(log_level)
    log.info(f"Connecting to PostgreSQL with connection string: {pg_con_str}")

    db = PostgreSQLAGE(
        pg_con_str=pg_con_str,
        allow_write=allow_write,
        log_level=log_level,
    )
    server = Server("age-manager")

    # Register handlers
    log.debug("Registering handlers")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="read-age-cypher",
                description="Execute a Cypher query on the AGE",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Cypher read query to execute",
                        },
                        "graph_name": {
                            "type": "string",
                            "description": "Name of the graph to operate",
                        },
                    },
                    "required": ["query", "graph_name"],
                },
            ),
            types.Tool(
                name="write-age-cypher",
                description="Execute a write Cypher query on the AGE",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Cypher write query to execute, including 'RETURN' statement",
                        },
                        "graph_name": {
                            "type": "string",
                            "description": "Name of the graph to operate",
                        },
                    },
                    "required": ["query", "graph_name"],
                },
            ),
            types.Tool(
                name="create-age-graph",
                description="Create a new graph in the AGE",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "graph_name": {
                            "type": "string",
                            "description": "Name of the graph to create",
                        },
                    },
                    "required": ["graph_name"],
                },
            ),
            types.Tool(
                name="drop-age-graph",
                description="Drop a graph in the AGE",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "graph_name": {
                            "type": "string",
                            "description": "Name of the graph to drop",
                        },
                    },
                    "required": ["graph_name"],
                },
            ),
            types.Tool(
                name="list-age-graphs",
                description="List all graphs in the AGE",
                inputSchema={
                    "type": "object",
                },
            ),
            types.Tool(
                name="get-age-schema",
                description="List all node types, their attributes and their relationships TO other node-types in the AGE",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "graph_name": {
                            "type": "string",
                            "description": "Name of the graph to create",
                        },
                    },
                    "required": ["graph_name"],
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if name == "get-age-schema":
                node_results = db._execute_query(
                    graph_name=arguments["graph_name"],
                    query="""
                      MATCH (n)
                      UNWIND labels(n) AS label
                      RETURN DISTINCT label, collect(DISTINCT keys(n)) AS properties
                    """,
                )
                log.debug(f"Node results: {node_results}")
                edge_results = db._execute_query(
                    graph_name=arguments["graph_name"],
                    query="""
                      MATCH (a)-[r]->(b)
                      RETURN DISTINCT type(r) AS rel_type, collect(DISTINCT labels(a)) AS from_labels, collect(DISTINCT labels(b)) AS to_labels
                    """,
                )
                log.debug(f"Edge results: {edge_results}")
                nodes_dict = {}
                for node in node_results:
                    label = node["label"].strip('"')
                    props = json.loads(node["properties"])
                    properties = (
                        props[0]
                        if props and isinstance(props, list) and len(props) > 0
                        else []
                    )
                    nodes_dict[label] = {
                        "label": label,
                        "properties": properties,
                        "relationships": {},
                    }
                edges = []
                for edge in edge_results:
                    rel_type = edge["rel_type"].strip('"')
                    from_labels = json.loads(edge["from_labels"])
                    to_labels = json.loads(edge["to_labels"])
                    from_labels = (
                        from_labels[0]
                        if from_labels and isinstance(from_labels, list)
                        else []
                    )
                    to_labels = (
                        to_labels[0]
                        if to_labels and isinstance(to_labels, list)
                        else []
                    )
                    edges.append(
                        {
                            "rel_type": rel_type,
                            "from_labels": from_labels,
                            "to_labels": to_labels,
                        }
                    )

                    for from_label in from_labels:
                        if from_label in nodes_dict and to_labels:
                            nodes_dict[from_label]["relationships"][rel_type] = (
                                to_labels[0]
                            )
                    for to_label in to_labels:
                        if to_label in nodes_dict and from_labels:
                            nodes_dict[to_label]["relationships"][rel_type] = (
                                from_labels[0]
                            )

                nodes = list(nodes_dict.values())

                return [
                    types.TextContent(
                        type="text", text=str({"nodes": nodes, "edges": edges})
                    )
                ]

            elif name == "create-age-graph":
                if not allow_write:
                    raise PermissionError("Not allowed to create graph")
                query = "SELECT create_graph('{}')".format(arguments["graph_name"])
                log.info(f"Creating graph with name {arguments['graph_name']}")
                results = db._execute_sql(query=query)
                return [types.TextContent(type="text", text=str(results))]

            elif name == "drop-age-graph":
                if not allow_write:
                    raise PermissionError("Not allowed to drop graph")
                query = "SELECT drop_graph('{}', True)".format(arguments["graph_name"])
                log.info(f"Dropping graph with name {arguments['graph_name']}")
                results = db._execute_sql(query=query)
                return [types.TextContent(type="text", text=str(results))]

            elif name == "list-age-graphs":
                query = "SELECT name FROM ag_graph"
                log.info("Listing graphs")
                results = db._execute_sql(query=query)
                return [types.TextContent(type="text", text=str(results))]

            elif name == "read-age-cypher":
                if not CypherQueryFormatter.is_safe_cypher_query(arguments["query"]):
                    raise ValueError("Only MATCH queries are allowed for read-query")
                results = db._execute_query(
                    graph_name=arguments["graph_name"], query=arguments["query"]
                )
                return [types.TextContent(type="text", text=str(results))]

            elif name == "write-age-cypher":
                if CypherQueryFormatter.is_safe_cypher_query(arguments["query"]):
                    raise ValueError("Only write queries are allowed for write-query")
                results = db._execute_query(
                    graph_name=arguments["graph_name"], query=arguments["query"]
                )
                return [types.TextContent(type="text", text=str(results))]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        log.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="age",
                server_version="0.2.1",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
