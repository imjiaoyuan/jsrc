from jsrc.job.core import (
    filter_rows,
    load_jobs,
    print_rows,
    to_row_view,
    warn_portability_limits,
)


def cmd(args) -> None:
    warn_portability_limits()
    rows = load_jobs()
    rows = filter_rows(rows, args.query)
    if args.limit > 0:
        rows = rows[-args.limit :]
    rendered = []
    for row in rows:
        view = to_row_view(row, {})
        rendered.append(view)
    cols = [
        "job_id",
        "status",
        "pid",
        "submit_time",
        "end_time",
        "runtime",
        "runtime_sec",
        "rss_mb",
        "rss_min_mb",
        "rss_avg_mb",
        "rss_peak_mb",
        "log_path",
        "command",
    ]
    print_rows(rendered, cols, args.format)
