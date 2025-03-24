# AGE-MCP-Server

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.13%2B-blue)

Apache AGE MCP Server

[Apache AGE™](https://age.apache.org/) is a PostgreSQL Graph database compatible with PostgreSQL's distributed assets and leverages graph data structures to analyze and use relationships and patterns in data.

[Azure Database for PostgreSQL](https://azure.microsoft.com/en-us/services/postgresql/) is a managed database service that is based on the open-source Postgres database engine.

[Introducing support for Graph data in Azure Database for PostgreSQL (Preview)](https://techcommunity.microsoft.com/blog/adforpostgresql/introducing-support-for-graph-data-in-azure-database-for-postgresql-preview/4275628).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Install](#install)
- [Usage](#usage)
- [Write Operations](#write-operations)
- [Release Notes](#release-notes)
- [For More Information](#for-more-information)
- [License](#license)

## Prerequisites

- Python 3.13 and above
- This module runs on [psycopg](https://www.psycopg.org/)
- Enable the Apache AGE extension in your Azure Database for PostgreSQL instance. Login Azure Portal, go to 'server parameters' blade, and check 'AGE" on within 'azure.extensions' and 'shared_preload_libraries' parameters. See, above blog post for more information.
- Load the AGE extension in your PostgreSQL database.

```sql
CREATE EXTENSION IF NOT EXISTS age CASCADE;
```

- Claude
Download from [Claude Desktop Client](https://claude.ai/download) or,

```bash
brew install claude
```

For configuration, see [Add the Filesystem MCP Server](https://modelcontextprotocol.io/quickstart/user).

## Install

- with brew

```bash
brew tap rioriost/age-mcp-server
brew install age-mcp-server
```

- with uv

```bash
uv init your_project
cd your_project
uv venv
source .venv/bin/activate
uv add age-mcp-server
```

- with python venv on macOS / Linux

```bash
mkdir your_project
cd your_project
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install age-mcp-server
```

- with python venv on Windows

```bash
mkdir your_project
cd your_project
python -m venv venv
.\venv\Scripts\activate
python -m pip install age-mcp-server
```

## Usage

- on macOS
`claude_desktop_config.json` is located in `~/Library/Application Support/Claude/`.

- on Windows
You need to create a new `claude_desktop_config.json` under `%APPDATA%\Claude`.

- Homebrew on macOS

Homebrew installs `age-mcp-server` into $PATH.

```json
{
  "mcpServers": {
    "age-manager": {
      "command": "age-mcp-server",
      "args": [
        "--pg-con-str",
        "host=your_server.postgres.database.azure.com port=5432 dbname=postgres user=your_username password=your_password",
      ]
    }
  }
}
```

- uv / Pyhon venv

On macOS:

```json
{
  "mcpServers": {
    "age-manager": {
      "command": "/Users/your_username/.local/bin/uv",
      "args": [
        "--directory",
        "/path/to/your_project",
        "run",
        "age-mcp-server",
        "--pg-con-str",
        "host=your_server.postgres.database.azure.com port=5432 dbname=postgres user=your_username password=your_password",
      ]
    }
  }
}
```

On Windows:

```json
{
  "mcpServers": {
    "age-manager": {
      "command": "C:\\Users\\USER\\.local\\bin\\uv.exe",
      "args": [
        "--directory",
        "C:\\path\\to\\your_project",
        "run",
        "age-mcp-server",
        "--pg-con-str",
        "host=your_server.postgres.database.azure.com port=5432 dbname=postgres user=your_username password=your_password",
      ]
    }
  }
}
```

After saving `claude_desktop_config.json`, start Claude Desktop Client.

![Show me graphs on the server](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_01.png)
![Show me a graph schema of FROM_AGEFREIGHTER](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_02.png)
![Pick up a customer and calculate the amount of its purchase.](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_03.png)
![Find another customer buying more than Lisa](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_04.png)
![OK. Please make a new graph named MCP_Test](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_05.png)
![Make a node labeled 'Person' with properties, name=Rio, age=52](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_06.png)
![Please make an another node labeled 'Company' with properties, name=Microsoft](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_07.png)
![Can you put a relation, "Rio WORK at Microsoft"?](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_08.png)
![Delete the graph, MCP_Test](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_09.png)

![Claude on Windows](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/Claude_Win.png)

## Write Operations

AGE-MCP-Server prohibits write operations by default for safety. If you want to enable write operations, you can use the `--allow-write` flag.

```json
{
  "mcpServers": {
    "age-manager": {
      "command": "age-mcp-server",
      "args": [
        "--pg-con-str",
        "host=your_server.postgres.database.azure.com port=5432 dbname=postgres user=your_username password=your_password",
        "--allow-write"
      ]
    }
  }
}
```

## Release Notes

### 0.2.2 Release
- Drop a conditional test of `CREATE` operation by adding `RETURN` to the description for `write-age-cypher` tool.

### 0.2.1 Release
- Fix a bug in node/edge creation

### 0.2.0 Release
- Add multiple graph support
- Add graph creation and deletion support
- Obsolete `--graph-name` argument

### 0.1.8 Release
- Add `--allow-write` flag

### 0.1.7 Release
- Add Windows support

### 0.1.6 Release
- Fix parser for `RETURN` values

### 0.1.5 Release
- Draft release

### 0.1.4 Release
- Draft release

### 0.1.3 Release
- Draft release

### 0.1.2 Release
- Draft release

### 0.1.1 Release
- Draft release

### 0.1.0a1 Release
- Draft release

## For More Information

- Apache AGE : https://age.apache.org/
- GitHub : https://github.com/apache/age
- Document : https://age.apache.org/age-manual/master/index.html

## License

MIT License
