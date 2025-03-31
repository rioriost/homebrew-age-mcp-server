#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import asyncio
import logging
import os
import subprocess
import sys

from . import server

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:
    """Main entry point as command line tool."""
    parser = argparse.ArgumentParser(description="Apache AGE MCP Server")
    parser.add_argument(
        "--pg-con-str",
        type=str,
        default=os.environ.get("PG_CONNECTION_STRING", ""),
        help="Connection string of the Azure Database for PostgreSQL",
    )
    parser.add_argument(
        "-w",
        "--allow-write",
        action="store_true",
        default=False,
        help="Allow write operations",
    )
    parser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debug logging"
    )

    args = parser.parse_args()

    if not args.pg_con_str:
        print("Error: PostgreSQL connection string is required.")
        sys.exit(1)

    conn_dict = dict(item.split("=", 1) for item in args.pg_con_str.split())
    if not conn_dict.get("password"):
        # Try to get password from env variable
        conn_dict["password"] = os.environ.get("PGPASSWORD", "")
        log.info("env:" + conn_dict["password"])
        if not conn_dict["password"]:
            # Try to get password using azure cli
            conn_dict["password"] = subprocess.check_output(
                [
                    "az",
                    "account",
                    "get-access-token",
                    "--resource",
                    "https://ossrdbms-aad.database.windows.net",
                    "--query",
                    "accessToken",
                    "--output",
                    "tsv",
                ],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
            log.info("entra:" + conn_dict["password"])

    if not conn_dict["password"]:
        print(
            "Error: Could not find PGPASSOWRD env var or Entra ID token to connect the server."
        )
        sys.exit(1)

    asyncio.run(
        server.main(
            pg_con_str=" ".join({f"{k}={v}" for k, v in conn_dict.items()}),
            allow_write=args.allow_write,
            log_level=logging.DEBUG if args.debug else logging.INFO,
        )
    )


__all__ = ["main", "server"]
