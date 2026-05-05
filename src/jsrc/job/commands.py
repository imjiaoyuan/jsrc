from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

IS_LINUX = sys.platform.startswith("linux")
_PLATFORM_NOTE_EMITTED = False


def _to_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _ps_rss_kb(pid: int) -> int:
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
    return _to_int(text.split()[0], 0)


def _get_rss_kb_from_status(pid: int) -> int:
    if not IS_LINUX:
        return _ps_rss_kb(pid)
    status = Path(f"/proc/{pid}/status")
    if not status.exists():
        return _ps_rss_kb(pid)
    try:
        for line in status.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("VmRSS:"):
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    return int(parts[1])
    except OSError:
        return _ps_rss_kb(pid)
    return _ps_rss_kb(pid)


def _process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if IS_LINUX:
        return Path(f"/proc/{pid}").exists()
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False


def _ps_row(pid: int) -> tuple[bool, str, float, str]:
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
    return True, etime, _to_float(pcpu, 0.0), stat


def _warn_portability_limits() -> None:
    global _PLATFORM_NOTE_EMITTED
    if IS_LINUX or _PLATFORM_NOTE_EMITTED:
        return
    print(
        "Note: non-Linux platform detected; /proc-based metrics may be limited.",
        file=sys.stderr,
    )
    _PLATFORM_NOTE_EMITTED = True


def cmd_submit(args) -> None:
    from jsrc.job.submit import cmd

    cmd(args)


def cmd_ls(args) -> None:
    from jsrc.job.ls import cmd

    cmd(args)


def cmd_show(args) -> None:
    from jsrc.job.show import cmd

    cmd(args)


def cmd_logs(args) -> None:
    from jsrc.job.logs import cmd

    cmd(args)


def cmd_kill(args) -> None:
    from jsrc.job.kill import cmd

    cmd(args)


def cmd_history(args) -> None:
    from jsrc.job.history import cmd

    cmd(args)


def cmd_gc(args) -> None:
    from jsrc.job.gc import cmd

    cmd(args)
