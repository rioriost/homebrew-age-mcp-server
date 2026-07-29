# Security Policy

## Supported versions

Security fixes are provided for the latest released version. Versions before 0.3.0
should not be used with untrusted MCP clients because they do not contain the current
query-composition and read-only transaction protections.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting for this repository. Do not open
a public issue containing an exploit, credential, connection string, database
contents, or other sensitive information.

Include the affected version, impact, minimal reproduction, and any suggested
mitigation. A maintainer should acknowledge the report within seven days.

## Deployment guidance

- Run the server with a dedicated, least-privileged PostgreSQL role.
- Keep write mode disabled unless it is required.
- Require TLS for remote PostgreSQL connections.
- Keep passwords out of process arguments and logs.
- Do not use a PostgreSQL superuser or a role with broad function execution rights.
- Review and update `uv.lock` when dependency alerts are raised.
