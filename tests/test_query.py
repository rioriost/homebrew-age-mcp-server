import base64
import json

import pytest

from age_mcp_server.query import (
    MAX_CURSOR_OFFSET,
    MAX_PARAMETERS_BYTES,
    CursorCodec,
    CypherQueryFormatter,
    query_binding_fingerprint,
    serialize_parameters,
    validate_graph_name,
)


@pytest.mark.parametrize(
    "query",
    [
        "CREATE(n) RETURN n",
        "MATCH (n) DELETE n RETURN n",
        "MATCH (n) DETACH DELETE n RETURN n",
        "MATCH (n) SET n.enabled=true RETURN n",
        "MATCH (n) REMOVE n.enabled RETURN n",
        "MERGE (n:Person) RETURN n",
        "MATCH (n) /* comment */ DELETE n RETURN n",
        "MATCH (n) CALL public.procedure(n) RETURN n",
    ],
)
def test_write_clauses_are_never_classified_as_safe(query: str) -> None:
    assert not CypherQueryFormatter.is_safe_cypher_query(query)


def test_keywords_and_dollars_in_string_literals_are_safe() -> None:
    query = "MATCH (n {text: 'CREATE; DELETE; SET', price: '$5'}) RETURN n"

    assert CypherQueryFormatter.is_safe_cypher_query(query)


def test_parameter_placeholders_must_exactly_match_json_parameters() -> None:
    analysis = CypherQueryFormatter.analyze(
        "MATCH (n) WHERE n.name = $name RETURN n",
        {"name": "Ada"},
    )

    assert analysis.parameter_names == ("name",)
    with pytest.raises(ValueError, match="missing=.*name"):
        CypherQueryFormatter.analyze("MATCH (n) WHERE n.name = $name RETURN n")
    with pytest.raises(ValueError, match="extra=.*unused"):
        CypherQueryFormatter.analyze("MATCH (n) RETURN n", {"unused": 1})
    with pytest.raises(ValueError, match="start with a letter"):
        CypherQueryFormatter.analyze("MATCH (n) RETURN n", {"_invalid": 1})


def test_parameter_serialization_is_stable_and_bounded(monkeypatch) -> None:
    assert serialize_parameters({"z": 1, "a": "é"}) == '{"a":"é","z":1}'
    assert serialize_parameters(None) is None
    with pytest.raises(ValueError, match="valid JSON"):
        serialize_parameters({"value": float("nan")})
    with pytest.raises(ValueError, match="valid JSON"):
        serialize_parameters({"value": object()})
    with pytest.raises(ValueError, match=str(MAX_PARAMETERS_BYTES)):
        serialize_parameters({"value": "x" * MAX_PARAMETERS_BYTES})
    with monkeypatch.context() as patch:
        patch.setattr(
            "age_mcp_server.query.json.dumps",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(RecursionError()),
        )
        with pytest.raises(ValueError, match="valid JSON"):
            serialize_parameters({"deeply": "nested"})


def test_query_and_graph_name_are_sql_quoted() -> None:
    formatted = CypherQueryFormatter.format_query(
        graph_name="g'; DROP TABLE secrets; --",
        cypher_query="MATCH (n {name: 'Ada'}) RETURN n.name AS value",
        allow_write=False,
    ).as_string(None)

    assert "'g''; DROP TABLE secrets; --'" in formatted
    assert "$age_mcp$MATCH (n {name: 'Ada'}) RETURN n.name AS value$age_mcp$" in formatted
    assert 'AS ("value" "ag_catalog"."agtype")' in formatted
    assert formatted.endswith("LIMIT 51 OFFSET 0")


def test_parameterized_query_uses_age_parameter_slot_not_literal_values() -> None:
    formatted = CypherQueryFormatter.format_query(
        "graph",
        "MATCH (n) WHERE n.name = $name RETURN n",
        False,
        parameters={"name": "Robert'); DROP TABLE users; --"},
        row_limit=11,
        offset=20,
    ).as_string(None)

    assert "ag_catalog.cypher('graph', " in formatted
    assert ", $1)" in formatted
    assert "Robert" not in formatted
    assert formatted.endswith("LIMIT 11 OFFSET 20")


def test_dollar_quote_delimiter_cannot_be_closed_by_query_text() -> None:
    formatted = CypherQueryFormatter.format_query(
        "graph",
        "MATCH (n {text: '$age_mcp$; DROP TABLE users; --'}) RETURN n",
        False,
    ).as_string(None)

    assert "$age_mcp_1$MATCH " in formatted
    assert " RETURN n$age_mcp_1$" in formatted
    assert formatted.count("$age_mcp_1$") == 2


def test_return_identifiers_are_quoted_and_deduplicated() -> None:
    query = 'MATCH (n) RETURN n.name AS `odd"name`, n.name AS `odd"name`'

    assert CypherQueryFormatter.get_return_values(query) == ['odd"name', 'odd"name_2']
    formatted = CypherQueryFormatter.format_query("graph", query, False).as_string(None)
    assert '"odd""name"' in formatted
    assert '"odd""name_2"' in formatted


def test_write_query_is_fully_executed_without_outer_limit() -> None:
    formatted = CypherQueryFormatter.format_query(
        "graph",
        "CREATE (n) RETURN n",
        allow_write=True,
    ).as_string(None)

    assert " LIMIT " not in formatted


@pytest.mark.parametrize(
    ("query", "message"),
    [
        ("MATCH (n) RETURN n; CREATE (x) RETURN x", "Multiple statements"),
        ("MATCH (n) RETURN *", r"RETURN \*"),
        ("MATCH (n {name: 'Ada}) RETURN n", "Unterminated"),
        ("MATCH (n) RETURN n\x00", "null byte"),
        ("MATCH (n)", "exactly one RETURN"),
        ("", "must not be empty"),
    ],
)
def test_invalid_queries_are_rejected(query: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        CypherQueryFormatter.analyze(query)


def test_union_requires_equal_return_arity() -> None:
    with pytest.raises(ValueError, match="same number"):
        CypherQueryFormatter.analyze("MATCH (n) RETURN n UNION MATCH (m) RETURN m, m.name")


@pytest.mark.parametrize("name", ["", "x" * 64, "graph\nname", 12])
def test_invalid_graph_names_are_rejected(name: object) -> None:
    with pytest.raises(ValueError):
        validate_graph_name(name)


def test_cursor_round_trip_is_authenticated_and_query_bound() -> None:
    codec = CursorCodec(b"x" * 32)
    cursor = codec.encode("binding-a", 50)

    assert codec.decode(cursor, "binding-a") == 50
    with pytest.raises(ValueError, match="does not match"):
        codec.decode(cursor, "binding-b")

    raw = bytearray(base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)))
    raw[1] ^= 1
    tampered = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
    with pytest.raises(ValueError, match="Invalid"):
        codec.decode(tampered, "binding-a")


def test_cursor_rejects_invalid_inputs_and_offsets() -> None:
    codec = CursorCodec(b"x" * 32)

    assert codec.decode(None, "binding") == 0
    with pytest.raises(ValueError, match="Invalid"):
        codec.decode("", "binding")
    with pytest.raises(ValueError, match="range"):
        codec.encode("binding", MAX_CURSOR_OFFSET + 1)
    with pytest.raises(ValueError, match="at least 16"):
        CursorCodec(b"short")

    payload = json.dumps({"f": "binding", "o": True, "v": 1}).encode()
    signature = __import__("hmac").digest(b"x" * 32, payload, "sha256")
    cursor = base64.urlsafe_b64encode(payload + signature).rstrip(b"=").decode()
    with pytest.raises(ValueError, match="does not match"):
        codec.decode(cursor, "binding")


def test_query_fingerprint_includes_graph_query_and_parameters() -> None:
    base = query_binding_fingerprint("g", "MATCH (n) RETURN n", None)

    assert base != query_binding_fingerprint("other", "MATCH (n) RETURN n", None)
    assert base != query_binding_fingerprint("g", "MATCH (m) RETURN m", None)
    assert base != query_binding_fingerprint("g", "MATCH (n) RETURN n", "{}")
