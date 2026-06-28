from __future__ import annotations

import sys
import time
from argparse import Namespace
from typing import Any

from jsrc.job.core import (
    build_live,
    load_jobs,
    now_iso,
    print_rows,
    refresh_jobs,
    sort_rows,
    to_int,
    to_row_view,
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

    try:
        while True:
            rows = load_jobs()
            rows, _ = refresh_jobs(rows)
            if not args.all:
                rows = [r for r in rows if r.get("status") == "running"]
            rendered = []
            for row in rows:
                live = (
                    build_live(to_int(row.get("pid", "0"), 0))
                    if row.get("status") == "running"
                    else {}
                )
                view = to_row_view(row, live)
                view["_etime"] = live.get("etime", "")
                rendered.append(view)
            rendered = sort_rows(rendered, args.sort, args.reverse)
            sys.stdout.write("\033[2J\033[H")
            mode = "all" if args.all else "running"
            print(
                f"# jsrc job top  mode={mode}  interval={args.interval}s  time={now_iso()}"
            )
            print_rows(rendered, columns, "table")
            sys.stdout.flush()
            time.sleep(max(args.interval, 0.2))
    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h")
        return


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("top", help="Live monitoring (like top)")
    p.add_argument(
        "-n", "--interval", type=float, default=2.0, help="Refresh interval seconds"
    )
    p.add_argument(
        "-c",
        "--cols",
        default="pid,s,mem,time,command",
        help="Columns to print, comma-separated",
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
    p.add_argument(
        "-a", "--all", action="store_true", help="Show all jobs (default: running only)"
    )
    p.set_defaults(func=cmd)
