import subprocess
from pathlib import Path

from jsrc.job.core import find_row, load_jobs, tail_lines


def cmd(args) -> None:
    rows = load_jobs()
    row = find_row(rows, str(args.target))
    if row is None:
        raise SystemExit(f"job not found: {args.target}")
    path = Path(row.get("log_path", "")).expanduser()
    if not path.exists():
        raise SystemExit(f"log file not found: {path}")
    if args.follow:
        subprocess.run(["tail", "-n", str(args.lines), "-f", str(path)], check=False)
        return
    for line in tail_lines(path, args.lines):
        print(line)


def register(subparsers):
    p = subparsers.add_parser("logs", help="Show job log by job_id or pid")
    p.add_argument("target", help="Job ID or PID")
    p.add_argument("-F", "--follow", action="store_true", help="Follow log output")
    p.add_argument("-n", "--lines", type=int, default=100, help="Tail line count")
    p.set_defaults(func=cmd)
