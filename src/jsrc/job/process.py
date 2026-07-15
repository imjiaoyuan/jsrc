"""Process monitoring utilities for job module."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
IS_LINUX = sys.platform.startswith("linux")
IS_MACOS = sys.platform == "darwin"
IS_WINDOWS = sys.platform == "win32"
_PLATFORM_NOTE_EMITTED = False


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
    for token in text.split():
        if token.isdigit():
            return int(token)
    return 0


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
    if IS_WINDOWS:
        return False
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
    global _PLATFORM_NOTE_EMITTED
    if _PLATFORM_NOTE_EMITTED:
        return
    _PLATFORM_NOTE_EMITTED = True
    if IS_WINDOWS:
        logger.warning(
            "Windows detected; job module is not supported on this platform."
        )
    elif IS_MACOS:
        logger.info(
            "macOS detected; /proc-based process metrics unavailable. "
            "Using ps fallback."
        )
    elif not IS_LINUX:
        logger.warning(
            "non-Linux platform detected; /proc-based metrics may be limited."
        )


def read_exit_code(job_id: str) -> str:
    from .config import state_dir

    path = state_dir() / f"{job_id}.exit"
    if not path.exists():
        return ""
    value = path.read_text(encoding="utf-8").strip()
    return value
