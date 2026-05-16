from __future__ import annotations

import csv
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

IS_LINUX = sys.platform.startswith("linux")
_PLATFORM_NOTE_EMITTED = False

FIELDS = [
    "job_id",
    "submit_time",
    "start_time",
    "end_time",
    "status",
    "pid",
    "exit_code",
    "cwd",
    "log_path",
    "rss_kb_last",
    "rss_kb_min",
    "rss_kb_peak",
    "rss_kb_sum",
    "rss_samples",
    "runtime_sec",
    "command",
]

DEFAULT_KEEP = 100


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def to_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def config_home() -> Path:
    xdg = os.getenv("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg).expanduser() / "jsrc"
    return Path.home() / ".config" / "jsrc"


def data_home() -> Path:
    xdg = os.getenv("XDG_DATA_HOME")
    if xdg:
        return Path(xdg).expanduser() / "jsrc"
    return Path.home() / ".local" / "share" / "jsrc"


def history_path() -> Path:
    override = os.getenv("JSRC_JOBS_FILE", "")
    if override:
        return Path(override).expanduser()
    return config_home() / "job" / "history"


def default_log_dir() -> Path:
    return data_home() / "job-logs"


def state_dir() -> Path:
    return data_home() / "job-state"


def ensure_dirs() -> None:
    history_path().parent.mkdir(parents=True, exist_ok=True)
    default_log_dir().mkdir(parents=True, exist_ok=True)
    state_dir().mkdir(parents=True, exist_ok=True)


def _migrate_old_history() -> None:
    old = data_home() / "jobs"
    new = history_path()
    if old.exists() and not new.exists():
        new.parent.mkdir(parents=True, exist_ok=True)
        old.rename(new)


def load_jobs() -> list[dict[str, str]]:
    _migrate_old_history()
    path = history_path()
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        rows.extend({k: row_data.get(k, "") for k in FIELDS} for row_data in reader)
    return rows


def write_jobs(rows: list[dict[str, str]], keep: int | None = None) -> None:
    if keep is None:
        keep = DEFAULT_KEEP
    if keep > 0 and len(rows) > keep:
        rows = rows[-keep:]
    path = history_path()
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in FIELDS})


def next_job_id(rows: list[dict[str, str]]) -> int:
    if not rows:
        return 1
    return max(to_int(r.get("job_id", "0")) for r in rows) + 1


def state_file(job_id: str) -> Path:
    return state_dir() / f"{job_id}.exit"


def read_exit_code(job_id: str) -> str:
    path = state_file(job_id)
    if not path.exists():
        return ""
    value = path.read_text(encoding="utf-8").strip()
    return value


def ps_rss_kb(pid: int) -> int:
    try:
        proc = subprocess.run(
            ["ps", "-o", "rss=", "-p", str(pid)],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return 0
    if proc.returncode != 0:
        return 0
    text = proc.stdout.strip()
    if not text:
        return 0
    return to_int(text.split()[0], 0)


def get_rss_kb_from_status(pid: int) -> int:
    if not IS_LINUX:
        return ps_rss_kb(pid)
    status = Path(f"/proc/{pid}/status")
    if not status.exists():
        return ps_rss_kb(pid)
    try:
        for line in status.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("VmRSS:"):
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    return int(parts[1])
    except OSError:
        return ps_rss_kb(pid)
    return ps_rss_kb(pid)


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if IS_LINUX:
        return Path(f"/proc/{pid}").exists()
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    else:
        return True


def ps_row(pid: int) -> tuple[bool, str, float, str]:
    try:
        proc = subprocess.run(
            ["ps", "-o", "etime=,pcpu=,stat=", "-p", str(pid)],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False, "", 0.0, ""
    if proc.returncode != 0:
        return False, "", 0.0, ""
    line = proc.stdout.strip()
    if not line:
        return False, "", 0.0, ""
    parts = line.split(None, 2)
    if len(parts) < 3:
        return False, "", 0.0, ""
    etime, pcpu, stat = parts
    return True, etime, to_float(pcpu, 0.0), stat


def warn_portability_limits() -> None:
    global _PLATFORM_NOTE_EMITTED
    if IS_LINUX or _PLATFORM_NOTE_EMITTED:
        return
    logger.warning(
        "Note: non-Linux platform detected; /proc-based metrics may be limited."
    )
    _PLATFORM_NOTE_EMITTED = True


def etime_to_seconds(etime: str) -> int:
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
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except (TypeError, ValueError):
        return None


def runtime_seconds(row: dict[str, str], live: dict[str, str]) -> int:
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


def refresh_jobs(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], bool]:
    changed = False
    now = now_iso()
    for row in rows:
        pid = to_int(row.get("pid", "0"), 0)
        if pid <= 0:
            continue
        running = row.get("status", "") == "running"
        alive = process_alive(pid)
        if alive and running:
            rss_kb = get_rss_kb_from_status(pid)
            old_last = to_int(row.get("rss_kb_last", "0"), 0)
            old_peak = to_int(row.get("rss_kb_peak", "0"), 0)
            old_min = to_int(row.get("rss_kb_min", "0"), 0)
            old_sum = to_int(row.get("rss_kb_sum", "0"), 0)
            old_samples = to_int(row.get("rss_samples", "0"), 0)
            if old_samples <= 0:
                seed = old_last if old_last > 0 else rss_kb
                old_samples = 1 if seed >= 0 else 0
                old_sum = max(seed, 0)
                if old_min <= 0:
                    old_min = max(seed, 0)
            new_peak = max(old_peak, rss_kb)
            new_min = min(old_min, rss_kb) if old_min > 0 else rss_kb
            new_sum = old_sum + max(rss_kb, 0)
            new_samples = old_samples + 1
            if (
                rss_kb != old_last
                or new_peak != old_peak
                or new_min != old_min
                or new_sum != old_sum
                or new_samples != old_samples
            ):
                row["rss_kb_last"] = str(rss_kb)
                row["rss_kb_min"] = str(new_min)
                row["rss_kb_peak"] = str(new_peak)
                row["rss_kb_sum"] = str(new_sum)
                row["rss_samples"] = str(new_samples)
                changed = True
            continue
        if running and not alive:
            exit_code = read_exit_code(row.get("job_id", ""))
            if exit_code == "":
                row["status"] = "lost"
            elif to_int(exit_code, 1) == 0:
                row["status"] = "exited"
            else:
                row["status"] = "failed"
            row["exit_code"] = exit_code
            row["end_time"] = now
            row["runtime_sec"] = str(runtime_seconds(row, {}))
            changed = True
    return rows, changed


def filter_rows(rows: list[dict[str, str]], query: str) -> list[dict[str, str]]:
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


def build_live(pid: int) -> dict[str, str]:
    ok, etime, pcpu, stat = ps_row(pid)
    if not ok:
        return {"etime": "", "pcpu": "0", "stat": ""}
    return {"etime": etime, "pcpu": str(pcpu), "stat": stat}


def find_row(rows: list[dict[str, str]], target: str) -> dict[str, str] | None:
    if target.isdigit():
        for row in reversed(rows):
            if row.get("job_id", "") == target:
                return row
        for row in reversed(rows):
            if row.get("pid", "") == target:
                return row
        return None
    for row in reversed(rows):
        if row.get("name", "") == target:
            return row
    return None


def parse_env(items: list[str]) -> dict[str, str]:
    extra = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"invalid --env value: {item!r}, expected KEY=VAL")
        k, v = item.split("=", 1)
        if not k:
            raise SystemExit(f"invalid --env key in {item!r}")
        extra[k] = v
    return extra


def collect_render_rows(args: Any, refresh: bool) -> list[dict[str, str]]:
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


def tail_lines(path: Path, n: int) -> list[str]:
    if n <= 0:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    return [x.rstrip("\n") for x in lines[-n:]]
