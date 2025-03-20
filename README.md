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
        "--graph-name",
        "FROM_AGEFREIGHTER",
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
        "--graph-name",
        "FROM_AGEFREIGHTER",
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
        "--graph-name",
        "FROM_AGEFREIGHTER",
      ]
    }
  }
}
```

After saving `claude_desktop_config.json`, start Claude Desktop Client.

![Show me a graph schema](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_1.png)
![Can you pick up a customer and calculate the sum of purchases?](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_2.png)
![Can you find another customer buying more than Lisa?](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_3.png)
![Can you find another product that Lisa didn't buy?](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_4.png)
![Can you add a fact that Lisa bought a product, ID 10?](https://raw.githubusercontent.com/rioriost/homebrew-age-mcp-server/main/images/query_5.png)

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
        "--graph-name",
        "FROM_AGEFREIGHTER",
        "--allow-write"
      ]
    }
  }
}
```

## Release Notes

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
