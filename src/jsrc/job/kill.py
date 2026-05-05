import os
import signal

from jsrc.job.core import (
    find_row,
    load_jobs,
    now_iso,
    runtime_seconds,
    to_int,
    write_jobs,
)


def cmd(args) -> None:
    rows = load_jobs()
    row = find_row(rows, str(args.target))
    if row is None:
        raise SystemExit(f"job not found: {args.target}")
    pid = to_int(row.get("pid", "0"), 0)
    if pid <= 0:
        raise SystemExit("invalid pid")
    sig = {"TERM": signal.SIGTERM, "KILL": signal.SIGKILL, "INT": signal.SIGINT}[
        args.signal
    ]
    try:
        if args.group:
            pgid = os.getpgid(pid)
            os.killpg(pgid, sig)
        else:
            os.kill(pid, sig)
    except ProcessLookupError:
        pass
    row["status"] = "killed"
    row["end_time"] = now_iso()
    row["runtime_sec"] = str(runtime_seconds(row, {}))
    write_jobs(rows, keep=1000)
    print(f"killed\t{pid}")
    print(f"signal\t{args.signal}")
