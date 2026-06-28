from __future__ import annotations

from argparse import Namespace
from typing import Any

from jsrc.job.core import (
    filter_rows,
    load_jobs,
    print_rows,
    refresh_jobs,
    to_row_view,
    warn_portability_limits,
)


def cmd(args: Namespace) -> None:
    warn_portability_limits()
    rows = load_jobs()
    rows, _ = refresh_jobs(rows)
    rows = filter_rows(rows, args.query)
    if args.limit > 0:
        rows = rows[-args.limit :]
    rendered = []
    for row in rows:
        view = to_row_view(row, {})
        rendered.append(view)
    cols = [
        "pid",
        "s",
        "mem",
        "time",
        "command",
    ]
    print_rows(rendered, cols, args.format)


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("history", help="Print job history")
    p.add_argument("-l", "--limit", type=int, default=50, help="Limit rows")
    p.add_argument(
        "-f",
        "--format",
        choices=["table", "tsv", "json"],
        default="table",
        help="Output format",
    )
    p.add_argument("-q", "--query", default="", help="Filter by command/name/log path")
    p.set_defaults(func=cmd)
