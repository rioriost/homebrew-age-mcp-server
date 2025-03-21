#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import asyncio
import logging
import os
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

    asyncio.run(
        server.main(
            pg_con_str=args.pg_con_str,
            allow_write=args.allow_write,
            log_level=logging.DEBUG if args.debug else logging.INFO,
        )
    )


__all__ = ["main", "server"]
