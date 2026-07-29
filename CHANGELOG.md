# Changelog

## 0.3.0 - 2026-07-29

### Security

- Safely quote graph names, Cypher text, and result identifiers.
- Parameterize graph creation and deletion.
- Enforce read-only transactions for read tools.
- Treat `CALL` as side-effecting and require write mode.
- Fully qualify Apache AGE objects in `ag_catalog`.
- Remove connection strings, query contents, and raw database errors from logs and
  MCP responses.
- Add query length, result count, and statement timeout limits.
- Authenticate pagination cursors and bind them to the exact query inputs.
- Bind Cypher parameters through an AGE prepared statement instead of interpolating
  values.
- Update dependencies to versions with no known OSV vulnerabilities.

### Added

- MCP safety annotations and conditional publication of write tools.
- MCP structured content and output schemas, with JSON text compatibility content.
- Bounded cursor pagination with configurable page sizes up to 50 rows.
- Rich schema inspection with node and edge counts, relationship direction, and
  sampled property types.
- OpenTelemetry-compatible latency, operation, and failure traces and metrics.
- Explicit Azure CLI token opt-in with `--azure-identity`.
- Configurable `--statement-timeout-ms`.
- Configurable asynchronous PostgreSQL connection-pool limits and `--load-age`.
- A live PostgreSQL/Apache AGE integration suite in CI.
- Unit tests, an 80% coverage gate, Ruff, Bandit, dependency auditing, CI, and
  Dependabot.

### Fixed

- Detect mutating Cypher clauses without relying on whitespace-separated keywords.
- Preserve quoted libpq connection strings.
- Merge all discovered node properties and preserve edge label sets in schema output.
- Report the installed package version during MCP initialization.
- Disable psycopg automatic statement preparation so pooled connection resets cannot
  leave its client-side prepared-statement cache out of sync with PostgreSQL.

### Changed

- Require Python 3.13 or later and MCP Python SDK 2.x.
- Replace the synchronous single connection with `psycopg.AsyncConnectionPool`.
- Require explicit return values; `RETURN *` remains unsupported.
- Acquire Azure access tokens only when `--azure-identity` is supplied.
