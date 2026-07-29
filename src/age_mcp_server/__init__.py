import argparse
import asyncio
import logging
import os
import shutil
import subprocess  # nosec B404

from psycopg import ProgrammingError
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from . import server
from .telemetry import Telemetry, configure_otel_exporters

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def _prepare_connection_string(pg_con_str: str, use_azure_identity: bool) -> str:
    """Validate libpq conninfo and optionally add an Azure access token."""
    connection_parameters = conninfo_to_dict(pg_con_str)
    if not use_azure_identity:
        return pg_con_str
    if connection_parameters.get("password") or os.environ.get("PGPASSWORD"):
        return pg_con_str

    azure_cli = shutil.which("az")
    if not azure_cli:
        raise RuntimeError("Azure CLI was not found in PATH")
    try:
        # The subprocess uses a resolved executable and a constant argument vector.
        completed = subprocess.run(  # nosec B603
            [
                azure_cli,
                "account",
                "get-access-token",
                "--resource",
                "https://ossrdbms-aad.database.windows.net",
                "--query",
                "accessToken",
                "--output",
                "tsv",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("Could not acquire an Azure Database access token") from exc

    token = completed.stdout.strip()
    if not token:
        raise RuntimeError("Azure CLI returned an empty access token")
    return make_conninfo(pg_con_str, password=token)


def main() -> None:
    """Main entry point as command line tool."""
    parser = argparse.ArgumentParser(description="Apache AGE MCP Server")
    parser.add_argument(
        "--pg-con-str",
        type=str,
        default=os.environ.get("PG_CONNECTION_STRING", ""),
        help="PostgreSQL libpq connection string (or PG_CONNECTION_STRING)",
    )
    parser.add_argument(
        "-w",
        "--allow-write",
        action="store_true",
        default=False,
        help="Allow write operations",
    )
    parser.add_argument("--debug", action="store_true", default=False, help="Enable debug logging")
    parser.add_argument(
        "--azure-identity",
        action="store_true",
        help="Acquire an Azure Database access token with the Azure CLI",
    )
    parser.add_argument(
        "--statement-timeout-ms",
        type=int,
        default=server.DEFAULT_STATEMENT_TIMEOUT_MS,
        help="Maximum database statement duration in milliseconds",
    )
    parser.add_argument(
        "--pool-min-size",
        type=int,
        default=server.DEFAULT_POOL_MIN_SIZE,
        help="Minimum number of asynchronous PostgreSQL connections",
    )
    parser.add_argument(
        "--pool-max-size",
        type=int,
        default=server.DEFAULT_POOL_MAX_SIZE,
        help="Maximum number of asynchronous PostgreSQL connections",
    )
    parser.add_argument(
        "--load-age",
        action="store_true",
        help="Run LOAD 'age' whenever a pooled connection is opened",
    )
    parser.add_argument(
        "--enable-telemetry",
        action="store_true",
        help="Export OpenTelemetry traces and metrics over OTLP",
    )
    parser.add_argument(
        "--otel-service-name",
        default="age-mcp-server",
        help="OpenTelemetry service.name value",
    )

    args = parser.parse_args()

    if not args.pg_con_str:
        parser.error("PostgreSQL connection string is required")
    if not 1 <= args.statement_timeout_ms <= 3_600_000:
        parser.error("--statement-timeout-ms must be between 1 and 3600000")
    if args.pool_min_size < 1 or args.pool_max_size < args.pool_min_size or args.pool_max_size > 64:
        parser.error("pool sizes must satisfy 1 <= min <= max <= 64")
    try:
        pg_con_str = _prepare_connection_string(args.pg_con_str, args.azure_identity)
    except (ProgrammingError, RuntimeError) as exc:
        parser.error(str(exc))
    if args.enable_telemetry:
        try:
            configure_otel_exporters(args.otel_service_name)
        except RuntimeError as exc:
            parser.error(str(exc))

    asyncio.run(
        server.main(
            pg_con_str=pg_con_str,
            allow_write=args.allow_write,
            log_level=logging.DEBUG if args.debug else logging.INFO,
            statement_timeout_ms=args.statement_timeout_ms,
            pool_min_size=args.pool_min_size,
            pool_max_size=args.pool_max_size,
            load_age=args.load_age,
            telemetry=Telemetry(),
        )
    )


__all__ = ["main", "server"]
