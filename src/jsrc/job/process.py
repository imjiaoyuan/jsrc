"""Process monitoring utilities for job module."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
IS_LINUX = sys.platform.startswith("linux")
_PLATFORM_NOTE_EMITTED = False


def ps_rss_kb(pid: int) -> int:
    """Get RSS memory in KB from ps command."""

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
    return int(text.split()[0]) if text.split()[0].isdigit() else 0


def get_rss_kb_from_status(pid: int) -> int:
    """Get RSS memory from /proc/pid/status (Linux) or ps (other platforms)."""
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
    """Check if a process is still alive."""
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


def ps_row(pid: int):
    """Get process info from ps command: (success, etime, pcpu, stat)."""
    try:
        proc = subprocess.run(
            ["ps", "-o", "etime=,pcpu=,stat=", "-p", str(pid)],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return (False, "", 0.0, "")
    if proc.returncode != 0:
        return (False, "", 0.0, "")
    parts = proc.stdout.strip().split(None, 2)
    if len(parts) < 3:
        return (False, "", 0.0, "")
    etime, pcpu_str, stat = parts[0], parts[1], parts[2]
    try:
        pcpu = float(pcpu_str)
    except ValueError:
        pcpu = 0.0
    return (True, etime, pcpu, stat)


def warn_portability_limits() -> None:
    """Warn about platform-specific limitations (Linux vs others)."""
    global _PLATFORM_NOTE_EMITTED
    if _PLATFORM_NOTE_EMITTED:
        return
    if not IS_LINUX:
        logger.warning(
            "non-Linux platform detected; /proc-based metrics may be limited."
        )
        _PLATFORM_NOTE_EMITTED = True


def read_exit_code(job_id: str) -> str:
    """Read exit code from state file."""
    from .config import state_dir

    path = state_dir() / f"{job_id}.exit"
    if not path.exists():
        return ""
    value = path.read_text(encoding="utf-8").strip()
    return value
