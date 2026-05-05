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


def cmd(args) -> None:
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
        else list(view.keys())
    )
    print_rows([view], columns, args.format)
