import base64
import hashlib
import hmac
import json
import re
import secrets
from dataclasses import dataclass
from typing import Any

from agefreighter.cypherparser import CypherParser
from psycopg import sql

MAX_GRAPH_NAME_BYTES = 63
MAX_QUERY_LENGTH = 100_000
MAX_PARAMETERS_BYTES = 100_000
MAX_PAGE_SIZE = 50
MAX_CURSOR_OFFSET = 100_000

READ_OPERATIONS = frozenset(
    {
        "LIMIT",
        "MANDATORY_MATCH",
        "MATCH",
        "OPTIONAL_MATCH",
        "ORDER",
        "RETURN",
        "RETURN_DISTINCT",
        "SKIP",
        "UNWIND",
        "WITH",
    }
)
WRITE_OPERATIONS = frozenset(
    {"CALL", "CREATE", "DELETE", "DETACH_DELETE", "MERGE", "REMOVE", "SET"}
)
PARAMETER_PATTERN = re.compile(r"\$([A-Za-z][A-Za-z0-9_]*)")


@dataclass(frozen=True)
class QueryAnalysis:
    operations: tuple[str, ...]
    return_values: tuple[str, ...]
    parameter_names: tuple[str, ...]

    @property
    def has_write(self) -> bool:
        return bool(set(self.operations) & WRITE_OPERATIONS)


def validate_graph_name(graph_name: Any) -> str:
    if not isinstance(graph_name, str) or not graph_name:
        raise ValueError("Graph name must be a non-empty string")
    if len(graph_name.encode("utf-8")) > MAX_GRAPH_NAME_BYTES:
        raise ValueError(f"Graph name exceeds {MAX_GRAPH_NAME_BYTES} bytes")
    if any(ord(character) < 32 or ord(character) == 127 for character in graph_name):
        raise ValueError("Graph name contains a control character")
    return graph_name


def serialize_parameters(parameters: dict[str, Any] | None) -> str | None:
    if parameters is None:
        return None
    if not isinstance(parameters, dict):
        raise ValueError("Cypher parameters must be an object")
    try:
        serialized = json.dumps(
            parameters,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (RecursionError, TypeError, ValueError) as exc:
        raise ValueError("Cypher parameters must contain valid JSON values") from exc
    if len(serialized.encode("utf-8")) > MAX_PARAMETERS_BYTES:
        raise ValueError(f"Cypher parameters exceed {MAX_PARAMETERS_BYTES} bytes")
    return serialized


def query_binding_fingerprint(
    graph_name: str,
    cypher_query: str,
    serialized_parameters: str | None,
) -> str:
    digest = hashlib.sha256()
    for value in (graph_name, cypher_query, serialized_parameters or ""):
        digest.update(value.encode("utf-8"))
        digest.update(b"\x00")
    return digest.hexdigest()


class CursorCodec:
    """Issue authenticated, query-bound pagination cursors."""

    def __init__(self, secret: bytes | None = None):
        self._secret = secret or secrets.token_bytes(32)
        if len(self._secret) < 16:
            raise ValueError("Cursor secret must be at least 16 bytes")

    def encode(self, fingerprint: str, offset: int) -> str:
        if not 0 <= offset <= MAX_CURSOR_OFFSET:
            raise ValueError("Cursor offset is outside the supported range")
        payload = json.dumps(
            {"f": fingerprint, "o": offset, "v": 1},
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
        signature = hmac.digest(self._secret, payload, "sha256")
        return base64.urlsafe_b64encode(payload + signature).rstrip(b"=").decode()

    def decode(self, cursor: str | None, fingerprint: str) -> int:
        if cursor is None:
            return 0
        if not isinstance(cursor, str) or not cursor or len(cursor) > 512:
            raise ValueError("Invalid pagination cursor")
        try:
            padding = "=" * (-len(cursor) % 4)
            decoded = base64.b64decode(cursor + padding, altchars=b"-_", validate=True)
            if len(decoded) <= 32:
                raise ValueError
            payload, signature = decoded[:-32], decoded[-32:]
            expected = hmac.digest(self._secret, payload, "sha256")
            if not hmac.compare_digest(signature, expected):
                raise ValueError
            data = json.loads(payload)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid pagination cursor") from exc

        offset = data.get("o")
        if (
            data.get("v") != 1
            or data.get("f") != fingerprint
            or not isinstance(offset, int)
            or isinstance(offset, bool)
            or not 0 <= offset <= MAX_CURSOR_OFFSET
        ):
            raise ValueError("Pagination cursor does not match this query")
        return offset


class CypherQueryFormatter:
    """Validate Cypher and safely compose the surrounding Apache AGE SQL."""

    @staticmethod
    def _dollar_quoted_query(query: str) -> sql.Composed:
        suffix = 0
        delimiter = "$age_mcp$"
        while delimiter in query:
            suffix += 1
            delimiter = f"$age_mcp_{suffix}$"
        return sql.Composed(
            [
                sql.SQL(delimiter),
                sql.SQL(query),
                sql.SQL(delimiter),
            ]
        )

    @staticmethod
    def _code_view(query: str) -> str:
        result = list(query)
        state = "code"
        quote = ""
        index = 0
        while index < len(query):
            char = query[index]
            following = query[index + 1] if index + 1 < len(query) else ""
            if state == "code":
                if char in {"'", '"', "`"}:
                    state, quote = "quoted", char
                    result[index] = " "
                elif char == "/" and following == "/":
                    state = "line_comment"
                    result[index] = result[index + 1] = " "
                    index += 1
                elif char == "/" and following == "*":
                    state = "block_comment"
                    result[index] = result[index + 1] = " "
                    index += 1
            elif state == "quoted":
                result[index] = " "
                if char == "\\" and following:
                    result[index + 1] = " "
                    index += 1
                elif char == quote:
                    if following == quote:
                        result[index + 1] = " "
                        index += 1
                    else:
                        state = "code"
            elif state == "line_comment":
                if char in {"\r", "\n"}:
                    state = "code"
                else:
                    result[index] = " "
            else:
                result[index] = " "
                if char == "*" and following == "/":
                    result[index + 1] = " "
                    index += 1
                    state = "code"
            index += 1
        if state in {"quoted", "block_comment"}:
            raise ValueError("Unterminated string, identifier, or block comment")
        return "".join(result)

    @staticmethod
    def _query_parts(parsed: Any) -> list[list[tuple[Any, ...]]]:
        if isinstance(parsed, list):
            return [parsed]
        if isinstance(parsed, tuple) and len(parsed) == 3 and parsed[0] in {"UNION", "UNION_ALL"}:
            return CypherQueryFormatter._query_parts(parsed[1]) + CypherQueryFormatter._query_parts(
                parsed[2]
            )
        raise ValueError("Unsupported Cypher query structure")

    @staticmethod
    def _return_name(value: Any, position: int) -> str:
        if isinstance(value, str):
            return value
        if not isinstance(value, tuple) or not value:
            return f"result_{position}"
        kind = value[0]
        if kind == "alias" and isinstance(value[-1], str):
            return value[-1]
        if kind == "property" and isinstance(value[-1], str):
            return value[-1]
        if kind == "func_call" and isinstance(value[1], str):
            return value[1]
        if kind == "distinct":
            return CypherQueryFormatter._return_name(value[1], position)
        if kind in {"star", "wildcard"}:
            raise ValueError("RETURN * is not supported; list return values explicitly")
        return f"result_{position}"

    @classmethod
    def analyze(
        cls,
        cypher_query: str,
        parameters: dict[str, Any] | None = None,
    ) -> QueryAnalysis:
        if not isinstance(cypher_query, str):
            raise ValueError("Query must be a string")
        if not cypher_query.strip():
            raise ValueError("Query must not be empty")
        if len(cypher_query) > MAX_QUERY_LENGTH:
            raise ValueError(f"Query exceeds the {MAX_QUERY_LENGTH}-character limit")
        if "\x00" in cypher_query:
            raise ValueError("Query contains a null byte")

        code = cls._code_view(cypher_query)
        if ";" in code:
            raise ValueError("Multiple statements are not allowed")
        parameter_names = set(PARAMETER_PATTERN.findall(code))
        serialized = serialize_parameters(parameters)
        supplied_names = set(parameters or {})
        invalid_names = supplied_names - {
            name for name in supplied_names if PARAMETER_PATTERN.fullmatch(f"${name}")
        }
        if invalid_names:
            raise ValueError("Cypher parameter names must start with a letter")
        if parameter_names != supplied_names:
            missing = sorted(parameter_names - supplied_names)
            extra = sorted(supplied_names - parameter_names)
            detail = f"missing={missing}, extra={extra}"
            raise ValueError(f"Cypher parameters do not match placeholders ({detail})")
        if not parameter_names and serialized is not None:
            raise ValueError("Cypher parameters were supplied but the query has no placeholders")

        try:
            parsed = CypherParser().parse(cypher_query)
        except Exception as exc:
            raise ValueError("Invalid Cypher query") from exc

        parts = cls._query_parts(parsed)
        operations: list[str] = []
        return_groups: list[list[Any]] = []
        for part in parts:
            if not part:
                raise ValueError("Query must contain at least one clause")
            part_operations = [
                clause[0]
                for clause in part
                if isinstance(clause, tuple) and clause and isinstance(clause[0], str)
            ]
            if len(part_operations) != len(part):
                raise ValueError("Unsupported Cypher clause")
            unsupported = set(part_operations) - READ_OPERATIONS - WRITE_OPERATIONS
            if unsupported:
                raise ValueError(f"Unsupported Cypher clause: {sorted(unsupported)[0]}")
            return_indexes = [
                index
                for index, operation in enumerate(part_operations)
                if operation in {"RETURN", "RETURN_DISTINCT"}
            ]
            if len(return_indexes) != 1:
                raise ValueError("Each query must contain exactly one RETURN clause")
            return_index = return_indexes[0]
            if set(part_operations[return_index + 1 :]) - {"LIMIT", "ORDER", "SKIP"}:
                raise ValueError("Only ORDER BY, SKIP, and LIMIT may follow RETURN")
            operations.extend(part_operations)
            return_groups.append(part[return_index][1])

        return_count = len(return_groups[0])
        if return_count == 0:
            raise ValueError("No return values specified")
        if any(len(group) != return_count for group in return_groups[1:]):
            raise ValueError("UNION branches must return the same number of values")

        names: list[str] = []
        name_counts: dict[str, int] = {}
        for position, value in enumerate(return_groups[0], start=1):
            base_name = cls._return_name(value, position)
            count = name_counts.get(base_name, 0) + 1
            name_counts[base_name] = count
            names.append(base_name if count == 1 else f"{base_name}_{count}")
        return QueryAnalysis(
            tuple(operations),
            tuple(names),
            tuple(sorted(parameter_names)),
        )

    @classmethod
    def format_query(
        cls,
        graph_name: str,
        cypher_query: str,
        allow_write: bool,
        *,
        parameters: dict[str, Any] | None = None,
        row_limit: int = MAX_PAGE_SIZE + 1,
        offset: int = 0,
    ) -> sql.Composed:
        validate_graph_name(graph_name)
        analysis = cls.analyze(cypher_query, parameters)
        if analysis.has_write and not allow_write:
            raise ValueError("Write clauses are not allowed")
        if row_limit < 1 or offset < 0:
            raise ValueError("Invalid SQL result bounds")

        columns = sql.SQL(", ").join(
            sql.SQL("{} {}").format(
                sql.Identifier(return_value),
                sql.Identifier("ag_catalog", "agtype"),
            )
            for return_value in analysis.return_values
        )
        query_constant = cls._dollar_quoted_query(cypher_query)
        if parameters is None:
            statement = sql.SQL("SELECT * FROM ag_catalog.cypher({}, {}) AS ({})").format(
                sql.Literal(graph_name),
                query_constant,
                columns,
            )
        else:
            statement = sql.SQL("SELECT * FROM ag_catalog.cypher({}, {}, $1) AS ({})").format(
                sql.Literal(graph_name),
                query_constant,
                columns,
            )
        if analysis.has_write:
            return statement
        return sql.SQL("{} LIMIT {} OFFSET {}").format(
            statement,
            sql.Literal(row_limit),
            sql.Literal(offset),
        )

    @classmethod
    def is_safe_cypher_query(
        cls,
        cypher_query: str,
        parameters: dict[str, Any] | None = None,
    ) -> bool:
        try:
            return not cls.analyze(cypher_query, parameters).has_write
        except ValueError:
            return False

    @classmethod
    def get_return_values(
        cls,
        cypher_query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[str]:
        return list(cls.analyze(cypher_query, parameters).return_values)
