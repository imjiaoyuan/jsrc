"""Core job data management functions."""

import csv
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

from .config import (
    _migrate_old_history,
    config_home,
    data_home,
    default_log_dir,
    ensure_dirs,
    history_path,
    state_dir,
)
from .format import (
    build_live,
    collect_render_rows,
    etime_to_seconds,
    filter_rows,
    format_duration,
    now_iso,
    parse_env,
    parse_iso,
    print_rows,
    print_table,
    runtime_seconds,
    sort_rows,
    tail_lines,
    to_float,
    to_int,
    to_row_view,
)
from .process import (
    IS_LINUX,
    _PLATFORM_NOTE_EMITTED,
    get_rss_kb_from_status,
    process_alive,
    ps_row,
    read_exit_code,
    warn_portability_limits,
)

logger = logging.getLogger(__name__)

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


def load_jobs() -> list[dict[str, str]]:
    """Load all jobs from history file."""
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
    """Write jobs to history file."""
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
    """Get next job ID."""
    if not rows:
        return 1
    return max(to_int(r.get("job_id", "0")) for r in rows) + 1


def state_file(job_id: str) -> Path:
    """Get state file path for job."""
    return state_dir() / f"{job_id}.exit"


def refresh_jobs(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], bool]:
    """Refresh running job statuses."""
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


def find_row(rows: list[dict[str, str]], target: str) -> dict[str, str] | None:
    """Find row by job_id, pid, or name."""
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


# Re-export functions for backward compatibility
__all__ = [
    "FIELDS",
    "DEFAULT_KEEP",
    "IS_LINUX",
    "_PLATFORM_NOTE_EMITTED",
    "load_jobs",
    "write_jobs",
    "next_job_id",
    "state_file",
    "refresh_jobs",
    "find_row",
    "collect_render_rows",
    "ensure_dirs",
    "default_log_dir",
    "warn_portability_limits",
    "print_rows",
    "print_table",
    "tail_lines",
    "to_int",
    "to_float",
    "now_iso",
    "config_home",
    "data_home",
    "history_path",
    "state_dir",
    "etime_to_seconds",
    "parse_env",
    "parse_iso",
    "format_duration",
    "runtime_seconds",
    "build_live",
    "to_row_view",
    "ps_row",
    "get_rss_kb_from_status",
    "process_alive",
    "os",
    "subprocess",
]