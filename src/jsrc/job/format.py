"""Data formatting and display utilities for job module."""

import json
from datetime import datetime
from typing import Any
from pathlib import Path


def to_int(value: str, default: int = 0) -> int:
    """Convert string to integer with default fallback."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_float(value: str, default: float = 0.0) -> float:
    """Convert string to float with default fallback."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def now_iso() -> str:
    """Get current timestamp in ISO format."""
    from datetime import timezone
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def etime_to_seconds(etime: str) -> int:
    """Convert ps etime format to seconds."""
    if not etime:
        return 0
    days = 0
    if "-" in etime:
        d, rest = etime.split("-", 1)
        days = to_int(d, 0)
        etime = rest
    parts = etime.split(":")
    if len(parts) == 3:
        h, m, s = (to_int(x, 0) for x in parts)
    elif len(parts) == 2:
        h = 0
        m, s = (to_int(x, 0) for x in parts)
    else:
        h = 0
        m = 0
        s = to_int(parts[0], 0)
    return days * 86400 + h * 3600 + m * 60 + s


def parse_iso(ts: str) -> datetime | None:
    """Parse ISO timestamp string."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except (TypeError, ValueError):
        return None


def runtime_seconds(row: dict[str, str], live: dict[str, str]) -> int:
    """Calculate runtime in seconds from row data."""
    if row.get("status", "") == "running":
        return etime_to_seconds(live.get("etime", ""))
    stored = to_int(row.get("runtime_sec", "0"), 0)
    if stored > 0:
        return stored
    start = parse_iso(row.get("start_time", ""))
    end = parse_iso(row.get("end_time", ""))
    if start and end:
        return max(0, int((end - start).total_seconds()))
    return 0


def format_duration(seconds: int) -> str:
    """Format seconds as human-readable duration."""
    if seconds <= 0:
        return "0s"
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    if days > 0:
        return f"{days}d{hours:02d}h{minutes:02d}m{secs:02d}s"
    if hours > 0:
        return f"{hours}h{minutes:02d}m{secs:02d}s"
    if minutes > 0:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


def to_row_view(row: dict[str, str], live: dict[str, str]) -> dict[str, str]:
    """Convert raw job data to display-friendly format."""
    rss_kb = to_int(row.get("rss_kb_last", "0"), 0)
    min_kb = to_int(row.get("rss_kb_min", "0"), 0)
    if min_kb <= 0 and rss_kb > 0:
        min_kb = rss_kb
    peak_kb = to_int(row.get("rss_kb_peak", "0"), 0)
    sum_kb = to_int(row.get("rss_kb_sum", "0"), 0)
    samples = to_int(row.get("rss_samples", "0"), 0)
    avg_kb = int(sum_kb / samples) if samples > 0 else rss_kb
    runtime_sec = runtime_seconds(row, live)
    out = dict(row)
    rss_mb_val = rss_kb / 1024
    rss_display = (
        f"{rss_mb_val:.1f}" if rss_mb_val < 1024 else f"{rss_mb_val / 1024:.1f}g"
    )
    out["rss_mb"] = rss_display
    out["rss"] = rss_display
    out["mem"] = rss_display
    out["rss_min_mb"] = f"{min_kb / 1024:.1f}"
    out["rss_avg_mb"] = f"{avg_kb / 1024:.1f}"
    out["rss_peak_mb"] = f"{peak_kb / 1024:.1f}"
    out["elapsed"] = live.get("etime", "")
    out["elapsed_sec"] = str(etime_to_seconds(live.get("etime", "")))
    out["runtime_sec"] = str(runtime_sec)
    out["runtime"] = format_duration(runtime_sec)
    out["cpu_pct"] = f"{to_float(live.get('pcpu', '0'), 0.0):.1f}"
    out["state"] = live.get("stat", "")
    st = row.get("status", "")
    out["s"] = {
        "running": "R",
        "exited": "E",
        "failed": "F",
        "killed": "K",
        "lost": "L",
    }.get(st, st)
    submit = row.get("submit_time", "")
    if submit:
        try:
            dt = datetime.fromisoformat(submit)
            out["time"] = f"{dt.strftime('%Y-%m-%d %H:%M')} / {out.get('runtime', '')}"
        except (TypeError, ValueError):
            out["time"] = f"{submit} / {out.get('runtime', '')}"
    else:
        out["time"] = f" / {out.get('runtime', '')}"
    return out


def filter_rows(rows: list[dict[str, str]], query: str) -> list[dict[str, str]]:
    """Filter rows by search query."""
    if not query:
        return rows
    q = query.lower()
    out = []
    for r in rows:
        text = " ".join(
            [r.get("command", ""), r.get("name", ""), r.get("log_path", "")]
        ).lower()
        if q in text:
            out.append(r)
    return out


def sort_rows(
    rows: list[dict[str, str]], key: str, reverse: bool
) -> list[dict[str, str]]:
    """Sort rows by specified key."""
    if key in {"submit_time", "time"}:
        return sorted(rows, key=lambda r: r.get("submit_time", ""), reverse=reverse)
    if key == "pid":
        return sorted(rows, key=lambda r: to_int(r.get("pid", "0")), reverse=reverse)
    if key == "job_id":
        return sorted(rows, key=lambda r: to_int(r.get("job_id", "0")), reverse=reverse)
    if key in {"status", "s"}:
        return sorted(rows, key=lambda r: r.get("status", ""), reverse=reverse)
    if key == "rss_mb":
        return sorted(
            rows, key=lambda r: to_float(r.get("rss_mb", "0"), 0.0), reverse=reverse
        )
    if key == "rss":
        return sorted(
            rows, key=lambda r: to_int(r.get("rss_kb_last", "0"), 0), reverse=reverse
        )
    if key == "mem":
        return sorted(
            rows, key=lambda r: to_int(r.get("rss_kb_last", "0"), 0), reverse=reverse
        )
    if key == "rss_min_mb":
        return sorted(
            rows, key=lambda r: to_float(r.get("rss_min_mb", "0"), 0.0), reverse=reverse
        )
    if key == "rss_avg_mb":
        return sorted(
            rows, key=lambda r: to_float(r.get("rss_avg_mb", "0"), 0.0), reverse=reverse
        )
    if key == "rss_peak_mb":
        return sorted(
            rows,
            key=lambda r: to_float(r.get("rss_peak_mb", "0"), 0.0),
            reverse=reverse,
        )
    if key in {"elapsed", "runtime", "runtime_sec"}:
        return sorted(
            rows, key=lambda r: to_int(r.get("runtime_sec", "0"), 0), reverse=reverse
        )
    return rows


def print_table(rows: list[dict[str, str]], columns: list[str]) -> None:
    """Print rows as formatted table."""
    if not rows:
        print("(no records)")
        return
    widths = {c: len(c.upper()) for c in columns}
    for row in rows:
        for c in columns:
            widths[c] = max(widths[c], len(str(row.get(c, ""))))
    header = " ".join(c.upper().ljust(widths[c]) for c in columns)
    print(header)
    print(" ".join("-" * widths[c] for c in columns))
    for row in rows:
        print(" ".join(str(row.get(c, "")).ljust(widths[c]) for c in columns))


def print_rows(rows: list[dict[str, str]], columns: list[str], fmt: str) -> None:
    """Print rows in specified format."""
    if fmt == "json":
        print(
            json.dumps(
                [{c: r.get(c, "") for c in columns} for r in rows],
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if fmt == "tsv":
        print("\t".join(columns))
        for row in rows:
            print("\t".join(str(row.get(c, "")) for c in columns))
        return
    print_table(rows, columns)


def tail_lines(path: Path, n: int) -> list[str]:
    """Get last n lines from file."""
    if n <= 0:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    return [x.rstrip("\n") for x in lines[-n:]]


def parse_env(items: list[str]) -> dict[str, str]:
    """Parse environment variable KEY=VAL items."""
    extra = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"invalid --env value: {item!r}, expected KEY=VAL")
        k, v = item.split("=", 1)
        if not k:
            raise SystemExit(f"invalid --env key in {item!r}")
        extra[k] = v
    return extra


def build_live(pid: int) -> dict[str, str]:
    """Build live process info dict."""
    from .process import ps_row
    ok, etime, pcpu, stat = ps_row(pid)
    if not ok:
        return {"etime": "", "pcpu": "0", "stat": ""}
    return {"etime": etime, "pcpu": str(pcpu), "stat": stat}


def collect_render_rows(args: Any, refresh: bool) -> list[dict[str, str]]:
    """Collect and render job rows for display."""
    from .core import load_jobs, refresh_jobs, write_jobs
    rows = load_jobs()
    changed = False
    if refresh:
        rows, changed = refresh_jobs(rows)
    if changed:
        write_jobs(rows)
    rows = filter_rows(rows, args.query)
    rendered = []
    for row in rows:
        live = (
            build_live(to_int(row.get("pid", "0"), 0))
            if row.get("status", "") == "running"
            else {}
        )
        view = to_row_view(row, live)
        view["_etime"] = live.get("etime", "")
        rendered.append(view)
    rendered = sort_rows(rendered, args.sort, args.reverse)
    if not args.all and args.limit > 0:
        rendered = rendered[-args.limit :]
    return rendered
