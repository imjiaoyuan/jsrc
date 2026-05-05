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
