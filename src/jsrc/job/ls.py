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
