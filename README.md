# AGE MCP Server

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.13%2B-blue)

An MCP server for querying [Apache AGE](https://age.apache.org/) graphs in PostgreSQL.

Version 0.3.0 makes read-only operation the secure default, adds asynchronous
connection pooling, safe Cypher parameters and bounded cursor pagination, and
returns MCP structured content from every tool.

## Requirements

- Python 3.13 or later
- PostgreSQL with the Apache AGE extension installed and loaded
- A database role restricted to the graphs and operations the MCP client needs

Enable AGE in the target database:

```sql
CREATE EXTENSION IF NOT EXISTS age CASCADE;
```

## Install

With `uv`:

```bash
uv init your_project
cd your_project
uv add age_mcp_server
```

With a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install age_mcp_server
```

With Homebrew:

```bash
brew install rioriost/tap/age_mcp_server
```

## Configure an MCP client

Avoid placing a database password in command-line arguments. Supply a connection
string through `PG_CONNECTION_STRING` and use one of libpq's credential mechanisms,
such as `PGPASSWORD` or a protected PostgreSQL password file.

```json
{
  "mcpServers": {
    "age_manager": {
      "command": "age_mcp_server",
      "env": {
        "PG_CONNECTION_STRING": "host=db.example port=5432 dbname=postgres user=age_reader sslmode=require",
        "PGPASSWORD": "replace-with-a-secret"
      }
    }
  }
}
```

Treat the MCP client configuration as a secret if it contains `PGPASSWORD`. A
PostgreSQL password file or the client's secret store is preferable.

The connection string can still be supplied explicitly when necessary:

```bash
age_mcp_server --pg-con-str "host=db.example dbname=postgres user=age_reader sslmode=require"
```

For Microsoft Entra authentication to Azure Database for PostgreSQL, first sign in
with the Azure CLI, then opt in to token acquisition:

```bash
age_mcp_server \
  --pg-con-str "host=server.postgres.database.azure.com dbname=postgres user=identity sslmode=require" \
  --azure-identity
```

## Tools

Read-only mode is the default:

| Tool | Purpose |
| --- | --- |
| `read-age-cypher` | Run a validated, parameterized, paginated read-only Cypher query |
| `list-age-graphs` | List Apache AGE graphs |
| `get-age-schema` | Inspect counts, directions, and sampled property types |

Write tools are only advertised and accepted when the server starts with
`--allow-write`:

| Tool | Purpose |
| --- | --- |
| `write-age-cypher` | Run Cypher containing a mutating clause |
| `create-age-graph` | Create a graph |
| `drop-age-graph` | Permanently drop a graph |

```bash
age_mcp_server --allow-write
```

Use a separate, least-privileged database role for write mode. Enabling the flag
does not grant PostgreSQL privileges that the configured role does not already have.

## Safety limits

- Cypher, graph names, return aliases, and graph-management arguments are safely
  quoted or parameterized before reaching PostgreSQL.
- Read tools run inside PostgreSQL read-only transactions.
- `CALL` is considered side-effecting and requires write mode.
- Read pages contain at most 50 rows. Opaque HMAC-authenticated cursors are bound to
  the graph, query, and parameters, with a maximum offset of 100,000.
- Cypher `$parameters` are accepted only when placeholder names exactly match a
  JSON parameter object. The object is capped at 100,000 bytes and passed to AGE
  through a prepared statement.
- Write queries execute fully and return an affected-row count instead of result
  rows.
- Statements time out after 30 seconds by default.
- Queries are limited to 100,000 characters and must contain one explicit `RETURN`
  clause per query branch.
- Raw database errors, query contents, and connection credentials are not returned
  to MCP clients or written to normal logs.

Change the timeout when needed:

```bash
age_mcp_server --statement-timeout-ms 60000
```

The timeout must be between 1 millisecond and 1 hour.

Tune the asynchronous connection pool or load the AGE library for every newly
opened pooled connection:

```bash
age_mcp_server --pool-min-size 2 --pool-max-size 8 --load-age
```

The pool must satisfy `1 <= min <= max <= 64`. `RETURN *` remains unsupported;
list return values explicitly so Apache AGE's SQL result types can be declared.

Example tool input with parameters and pagination:

```json
{
  "graph_name": "people",
  "query": "MATCH (n:Person) WHERE n.age >= $minimum RETURN n.name AS name ORDER BY name",
  "parameters": {"minimum": 18},
  "page_size": 25
}
```

Pass the returned `nextCursor` as `cursor` to fetch the next page.

## OpenTelemetry

Install the optional exporter dependencies and enable OTLP export:

```bash
python3 -m pip install "age_mcp_server[telemetry]"
age_mcp_server --enable-telemetry --otel-service-name age-production
```

The exporter follows standard `OTEL_EXPORTER_OTLP_*` environment variables.
Traces and metrics record operation latency, counts, and failures. Connection
details, Cypher text, parameter values, and raw database errors are excluded.

## Development

Install all development dependencies and run the release gate:

```bash
make sync
make check
```

`make check` runs Ruff, the 80% coverage gate, Bandit, the locked dependency audit,
and package builds. The test suite includes a live Apache AGE integration test:

```bash
AGE_TEST_CONNECTION_STRING="host=127.0.0.1 dbname=postgres user=postgres password=postgres" \
  make integration
```

CI runs this test against the official Apache AGE PostgreSQL container. See
[the 0.3.0 review](docs/release-0.3.0-review.md) for the completed security and
feature review.

## License

[MIT](LICENSE)
