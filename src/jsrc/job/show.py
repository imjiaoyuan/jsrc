from argparse import Namespace
from typing import Any

from jsrc.job.core import (
    build_live,
    find_row,
    load_jobs,
    refresh_jobs,
    to_int,
    to_row_view,
    warn_portability_limits,
    write_jobs,
    print_rows,
)


def cmd(args: Namespace) -> None:
    warn_portability_limits()
    rows = load_jobs()
    rows, changed = refresh_jobs(rows)
    if changed:
        write_jobs(rows, keep=1000)
    row = find_row(rows, str(args.target))
    if row is None:
        raise SystemExit(f"job not found: {args.target}")
    live = (
        build_live(to_int(row.get("pid", "0"), 0))
        if row.get("status", "") == "running"
        else {}
    )
    view = to_row_view(row, live)
    columns = (
        [c.strip() for c in args.cols.split(",") if c.strip()]
        if args.cols
        else ["pid", "s", "mem", "time", "command"]
    )
    print_rows([view], columns, args.format)


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("show", help="Show details of a job by job_id or pid")
    p.add_argument("target", help="Job ID or PID")
    p.add_argument(
        "-f",
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format",
    )
    p.add_argument("-c", "--cols", default="", help="Columns to print, comma-separated")
    p.set_defaults(func=cmd)
