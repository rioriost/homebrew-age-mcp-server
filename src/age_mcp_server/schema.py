import json
import re
from collections import defaultdict
from typing import Any

from .database import PostgreSQLAGE

SCHEMA_SAMPLE_SIZE = 200
AGTYPE_ENTITY_SUFFIX = re.compile(r"::(?:vertex|edge|path)$")
AGTYPE_NUMERIC_SUFFIX = re.compile(r"(-?\d+(?:\.\d+)?)::numeric")


def decode_agtype(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    cleaned = AGTYPE_ENTITY_SUFFIX.sub("", value)
    cleaned = AGTYPE_NUMERIC_SUFFIX.sub(r"\1", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return value.strip('"')


def flatten_strings(value: Any) -> list[str]:
    values: set[str] = set()

    def visit(item: Any) -> None:
        if isinstance(item, str):
            values.add(item)
        elif isinstance(item, list):
            for nested_item in item:
                visit(nested_item)

    visit(value)
    return sorted(values)


def infer_property_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "unknown"


def _property_descriptions(
    type_sets: dict[str, set[str]],
    observations: dict[str, int],
    sample_count: int,
) -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "types": sorted(types),
            "observedInSample": observations[name],
            "requiredInSample": bool(sample_count) and observations[name] == sample_count,
        }
        for name, types in sorted(type_sets.items())
    ]


async def inspect_schema(db: PostgreSQLAGE, graph_name: str) -> dict[str, Any]:
    node_summary = await db.read_all(
        graph_name,
        (
            "MATCH (n) "
            "UNWIND labels(n) AS label "
            "RETURN label, count(n) AS entity_count, "
            "collect(DISTINCT keys(n)) AS property_names "
            "ORDER BY label"
        ),
        max_rows=1_000,
    )
    edge_summary = await db.read_all(
        graph_name,
        (
            "MATCH (a)-[r]->(b) "
            "RETURN type(r) AS rel_type, labels(a) AS from_labels, "
            "labels(b) AS to_labels, count(r) AS entity_count "
            "ORDER BY rel_type"
        ),
        max_rows=1_000,
    )
    node_samples = await db.read_all(
        graph_name,
        (
            "MATCH (n) RETURN labels(n) AS labels, n AS entity "
            f"ORDER BY id(n) LIMIT {SCHEMA_SAMPLE_SIZE}"
        ),
        max_rows=SCHEMA_SAMPLE_SIZE,
    )
    edge_samples = await db.read_all(
        graph_name,
        (
            "MATCH ()-[r]->() RETURN type(r) AS rel_type, r AS entity "
            f"ORDER BY id(r) LIMIT {SCHEMA_SAMPLE_SIZE}"
        ),
        max_rows=SCHEMA_SAMPLE_SIZE,
    )

    node_types: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    node_observations: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    node_sample_counts: dict[str, int] = defaultdict(int)
    for row in node_samples:
        labels = flatten_strings(decode_agtype(row["labels"]))
        entity = decode_agtype(row["entity"])
        properties = entity.get("properties", {}) if isinstance(entity, dict) else {}
        for label in labels:
            node_sample_counts[label] += 1
            for name, value in properties.items():
                node_types[label][name].add(infer_property_type(value))
                node_observations[label][name] += 1

    edge_types: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    edge_observations: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    edge_sample_counts: dict[str, int] = defaultdict(int)
    for row in edge_samples:
        rel_type = str(decode_agtype(row["rel_type"]))
        entity = decode_agtype(row["entity"])
        properties = entity.get("properties", {}) if isinstance(entity, dict) else {}
        edge_sample_counts[rel_type] += 1
        for name, value in properties.items():
            edge_types[rel_type][name].add(infer_property_type(value))
            edge_observations[rel_type][name] += 1

    nodes: dict[str, dict[str, Any]] = {}
    for row in node_summary:
        label = str(decode_agtype(row["label"]))
        known_names = flatten_strings(decode_agtype(row["property_names"]))
        for name in known_names:
            node_types[label].setdefault(name, set())
            node_observations[label].setdefault(name, 0)
        nodes[label] = {
            "label": label,
            "count": int(decode_agtype(row["entity_count"])),
            "sampled": node_sample_counts[label],
            "properties": _property_descriptions(
                node_types[label],
                node_observations[label],
                node_sample_counts[label],
            ),
            "relationships": [],
        }

    edges: list[dict[str, Any]] = []
    for row in edge_summary:
        rel_type = str(decode_agtype(row["rel_type"]))
        from_labels = flatten_strings(decode_agtype(row["from_labels"]))
        to_labels = flatten_strings(decode_agtype(row["to_labels"]))
        count = int(decode_agtype(row["entity_count"]))
        edge = {
            "type": rel_type,
            "direction": "outgoing",
            "fromLabels": from_labels,
            "toLabels": to_labels,
            "count": count,
            "sampled": edge_sample_counts[rel_type],
            "properties": _property_descriptions(
                edge_types[rel_type],
                edge_observations[rel_type],
                edge_sample_counts[rel_type],
            ),
        }
        edges.append(edge)
        for label in from_labels:
            if label in nodes:
                nodes[label]["relationships"].append(
                    {
                        "type": rel_type,
                        "direction": "outgoing",
                        "relatedLabels": to_labels,
                        "count": count,
                    }
                )
        for label in to_labels:
            if label in nodes:
                nodes[label]["relationships"].append(
                    {
                        "type": rel_type,
                        "direction": "incoming",
                        "relatedLabels": from_labels,
                        "count": count,
                    }
                )

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "sampling": {
            "nodeLimit": SCHEMA_SAMPLE_SIZE,
            "edgeLimit": SCHEMA_SAMPLE_SIZE,
            "typesAreInferred": True,
        },
    }
