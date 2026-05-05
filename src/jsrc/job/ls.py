import sys
import time

from jsrc.job.core import (
    collect_render_rows,
    now_iso,
    print_rows,
    warn_portability_limits,
)


def cmd(args) -> None:
    warn_portability_limits()
    columns = [c.strip() for c in args.cols.split(",") if c.strip()]
    if not columns:
        columns = [
            "job_id",
            "status",
            "pid",
            "runtime",
            "rss_mb",
            "rss_min_mb",
            "rss_avg_mb",
            "rss_peak_mb",
            "command",
        ]

    if args.watch:
        try:
            while True:
                rows = collect_render_rows(args, refresh=True)
                sys.stdout.write("\033[2J\033[H")
                print(
                    f"# jsrc job ls --watch  interval={args.interval}s  time={now_iso()}"
                )
                print_rows(rows, columns, args.format)
                sys.stdout.flush()
                time.sleep(max(args.interval, 0.2))
        except KeyboardInterrupt:
            return
    rows = collect_render_rows(args, refresh=True)
    print_rows(rows, columns, args.format)


def register(subparsers):
    p = subparsers.add_parser("ls", help="List tracked jobs")
    p.add_argument("-w", "--watch", action="store_true", help="Refresh continuously")
    p.add_argument(
        "-n", "--interval", type=float, default=2.0, help="Refresh interval seconds"
    )
    p.add_argument(
        "-c",
        "--cols",
        default="job_id,status,pid,runtime,rss_mb,rss_min_mb,rss_avg_mb,rss_peak_mb,submit_time,command",
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
            "elapsed",
            "runtime",
            "runtime_sec",
            "rss_mb",
            "rss_min_mb",
            "rss_avg_mb",
            "rss_peak_mb",
            "pid",
            "job_id",
            "status",
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
