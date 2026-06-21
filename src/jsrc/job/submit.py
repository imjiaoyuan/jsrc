import os
import shlex
import shutil
import subprocess
from argparse import Namespace
from pathlib import Path
from typing import Any

from jsrc.core import DependencyError
from jsrc.job.core import (
    default_log_dir,
    ensure_dirs,
    get_rss_kb_from_status,
    load_jobs,
    next_job_id,
    now_iso,
    parse_env,
    state_file,
    write_jobs,
)


def cmd(args: Namespace) -> None:
    ensure_dirs()
    if not shutil.which("nohup"):
        raise DependencyError(
            "'nohup' command not found on this system; install coreutils"
        )
    if not shutil.which(args.shell):
        raise DependencyError(
            f"shell '{args.shell}' not found on this system; "
            "use -S to specify an installed shell"
        )
    rows = load_jobs()
    job_id = str(next_job_id(rows))
    cwd = str(Path(args.cwd).expanduser().resolve())
    log_path = args.log
    if not log_path:
        log_path = str((default_log_dir() / f"{job_id}.log").resolve())
    else:
        log_path = str(Path(log_path).expanduser().resolve())
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.update(parse_env(args.env))

    mode = "a" if args.append else "w"
    state_path = state_file(job_id).resolve()
    wrapped = (
        f"{args.command}\n"
        f"__jsrc_ec=$?\n"
        f'printf "%s\\n" "$__jsrc_ec" > {shlex.quote(str(state_path))}\n'
        'exit "$__jsrc_ec"\n'
    )
    with open(log_path, mode, encoding="utf-8") as logfh:
        proc = subprocess.Popen(
            ["nohup", args.shell, "-lc", wrapped],
            stdin=subprocess.DEVNULL,
            stdout=logfh,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            env=env,
            start_new_session=True,
            text=True,
        )

    rss_kb = get_rss_kb_from_status(proc.pid)
    now = now_iso()
    row = {
        "job_id": job_id,
        "submit_time": now,
        "start_time": now,
        "end_time": "",
        "status": "running",
        "pid": str(proc.pid),
        "exit_code": "",
        "cwd": cwd,
        "log_path": log_path,
        "rss_kb_last": str(rss_kb),
        "rss_kb_min": str(rss_kb),
        "rss_kb_peak": str(rss_kb),
        "rss_kb_sum": str(max(rss_kb, 0)),
        "rss_samples": "1",
        "runtime_sec": "0",
        "command": args.command,
        "name": args.name,
    }
    rows.append(row)
    write_jobs(rows)
    print(f"job_id\t{job_id}")
    print(f"pid\t{proc.pid}")
    print(f"log\t{log_path}")
    print("status\trunning")


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "submit", help='Submit a job: jsrc job submit "cmd" "log"'
    )
    p.add_argument(
        "command",
        help='Command to run, wrapped by nohup (e.g. "Rscript 02.harmony2.R")',
    )
    p.add_argument("log", nargs="?", help="Log file path (optional)")
    p.add_argument("-N", "--name", default="", help="Optional job name")
    p.add_argument("-C", "--cwd", default=".", help="Working directory")
    p.add_argument("-S", "--shell", default="bash", help="Shell binary used with -lc")
    p.add_argument(
        "-A",
        "--append",
        action="store_true",
        help="Append to log file instead of overwrite",
    )
    p.add_argument(
        "-E",
        "--env",
        action="append",
        default=[],
        help="Extra env KEY=VAL (repeatable)",
    )
    p.set_defaults(func=cmd)
