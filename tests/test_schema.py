import asyncio
from typing import Any

from age_mcp_server.schema import (
    decode_agtype,
    flatten_strings,
    infer_property_type,
    inspect_schema,
)


class SchemaDatabase:
    def __init__(self):
        self.queries: list[tuple[str, int]] = []

    async def read_all(
        self,
        _graph_name: str,
        query: str,
        *,
        max_rows: int,
        parameters=None,
    ) -> list[dict[str, Any]]:
        self.queries.append((query, max_rows))
        if "UNWIND labels" in query:
            return [
                {
                    "label": '"Person"',
                    "entity_count": "3",
                    "property_names": '[["name","age"],["active"]]',
                },
                {
                    "label": '"Company"',
                    "entity_count": "1",
                    "property_names": '[["name"]]',
                },
            ]
        if "MATCH (a)-[r]" in query:
            return [
                {
                    "rel_type": '"WORKS_AT"',
                    "from_labels": '["Person"]',
                    "to_labels": '["Company"]',
                    "entity_count": "2",
                }
            ]
        if "MATCH (n) RETURN labels" in query:
            return [
                {
                    "labels": '["Person"]',
                    "entity": (
                        '{"id":1,"label":"Person","properties":'
                        '{"name":"Ada","age":36,"active":true}}::vertex'
                    ),
                },
                {
                    "labels": '["Person"]',
                    "entity": (
                        '{"id":2,"label":"Person","properties":{"name":"Grace","age":37.5}}::vertex'
                    ),
                },
                {
                    "labels": '["Company"]',
                    "entity": ('{"id":3,"label":"Company","properties":{"name":"ACME"}}::vertex'),
                },
            ]
        return [
            {
                "rel_type": '"WORKS_AT"',
                "entity": (
                    '{"id":4,"label":"WORKS_AT","start_id":1,"end_id":3,'
                    '"properties":{"since":2020,"roles":["engineer"]}}::edge'
                ),
            }
        ]


def test_schema_includes_counts_directions_and_sampled_property_types() -> None:
    database = SchemaDatabase()

    result = asyncio.run(inspect_schema(database, "graph"))

    person = next(node for node in result["nodes"] if node["label"] == "Person")
    assert person["count"] == 3
    assert person["sampled"] == 2
    age = next(prop for prop in person["properties"] if prop["name"] == "age")
    assert age == {
        "name": "age",
        "types": ["integer", "number"],
        "observedInSample": 2,
        "requiredInSample": True,
    }
    active = next(prop for prop in person["properties"] if prop["name"] == "active")
    assert active["requiredInSample"] is False
    assert person["relationships"] == [
        {
            "type": "WORKS_AT",
            "direction": "outgoing",
            "relatedLabels": ["Company"],
            "count": 2,
        }
    ]
    company = next(node for node in result["nodes"] if node["label"] == "Company")
    assert company["relationships"][0]["direction"] == "incoming"
    edge = result["edges"][0]
    assert edge["direction"] == "outgoing"
    assert {prop["name"] for prop in edge["properties"]} == {"roles", "since"}
    assert edge["sampled"] == 1
    assert result["sampling"]["typesAreInferred"] is True
    assert [limit for _, limit in database.queries] == [1000, 1000, 200, 200]


def test_agtype_decoding_flattening_and_type_inference() -> None:
    assert decode_agtype("12.5::numeric") == 12.5
    assert decode_agtype('"hello"') == "hello"
    assert decode_agtype("not-json") == "not-json"
    assert decode_agtype(3) == 3
    assert flatten_strings(["b", ["a", "b"], 1]) == ["a", "b"]
    values = [None, True, 1, 1.5, "x", [], {}, object()]
    assert [infer_property_type(value) for value in values] == [
        "null",
        "boolean",
        "integer",
        "number",
        "string",
        "array",
        "object",
        "unknown",
    ]
