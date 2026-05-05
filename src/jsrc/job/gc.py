import logging
from argparse import Namespace
from pathlib import Path
from typing import Any

from jsrc.job.core import load_jobs, now_iso, runtime_seconds, state_dir, write_jobs

logger = logging.getLogger(__name__)


def cmd(args: Namespace) -> None:
    rows = load_jobs()
    if args.prune_missing_log:
        for row in rows:
            log_path = row.get("log_path", "")
            if (
                log_path
                and not Path(log_path).expanduser().exists()
                and row.get("status", "") == "running"
            ):
                row["status"] = "lost"
                row["end_time"] = now_iso()
                row["runtime_sec"] = str(runtime_seconds(row, {}))
    write_jobs(rows, keep=max(1, args.keep_history))
    removed = 0
    if args.remove_dead_state:
        active = {r.get("job_id", "") for r in rows}
        for item in state_dir().glob("*.exit"):
            jid = item.stem
            if jid not in active:
                item.unlink(missing_ok=True)
                removed += 1
    print(f"kept_history\t{max(1, args.keep_history)}")
    print(f"state_files_removed\t{removed}")


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("gc", help="Trim history/log metadata")
    p.add_argument(
        "-k",
        "--keep-history",
        type=int,
        default=1000,
        help="Keep last N history records",
    )
    p.add_argument(
        "--prune-missing-log",
        action="store_true",
        help="Mark records whose log file no longer exists",
    )
    p.add_argument(
        "--remove-dead-state", action="store_true", help="Remove stale job state files"
    )
    p.set_defaults(func=cmd)
