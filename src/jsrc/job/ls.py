from __future__ import annotations

from argparse import Namespace
from typing import Any

from jsrc.job.core import (
    collect_render_rows,
    print_rows,
    warn_portability_limits,
)


def cmd(args: Namespace) -> None:
    warn_portability_limits()
    columns = [c.strip() for c in args.cols.split(",") if c.strip()]
    if not columns:
        columns = [
            "pid",
            "s",
            "mem",
            "time",
            "command",
        ]

    rows = collect_render_rows(args, refresh=True)
    print_rows(rows, columns, args.format)


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("ls", help="List tracked jobs")
    p.add_argument(
        "-c",
        "--cols",
        default="pid,s,mem,time,command",
        help="Columns to print, comma-separated",
    )
    p.add_argument(
        "-f",
        "--format",
        choices=["table", "tsv", "json"],
        default="table",
        help="Output format",
    )
    p.add_argument(
        "-s",
        "--sort",
        choices=[
            "submit_time",
            "time",
            "elapsed",
            "runtime",
            "runtime_sec",
            "rss_mb",
            "rss",
            "rss_min_mb",
            "rss_avg_mb",
            "rss_peak_mb",
            "pid",
            "job_id",
            "status",
            "s",
            "mem",
        ],
        default="submit_time",
        help="Sort field",
    )
    p.add_argument("-r", "--reverse", action="store_true", help="Reverse sort order")
    p.add_argument("-a", "--all", action="store_true", help="Show all records")
    p.add_argument(
        "-l", "--limit", type=int, default=20, help="Max rows when --all is not set"
    )
    p.add_argument("-q", "--query", default="", help="Filter by command/name/log path")
    p.set_defaults(func=cmd)
