"""Job module configuration and path management."""

from __future__ import annotations

import os
from pathlib import Path


def config_home() -> Path:
    """Get XDG config home directory."""

    xdg = os.getenv("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg).expanduser() / "jsrc"
    return Path.home() / ".config" / "jsrc"


def data_home() -> Path:
    """Get XDG data home directory."""
    xdg = os.getenv("XDG_DATA_HOME")
    if xdg:
        return Path(xdg).expanduser() / "jsrc"
    return Path.home() / ".local" / "share" / "jsrc"


def history_path() -> Path:
    """Get job history file path."""
    override = os.getenv("JSRC_JOBS_FILE", "")
    if override:
        return Path(override).expanduser()
    return config_home() / "job" / "history"


def default_log_dir() -> Path:
    """Get default directory for job log files."""
    return data_home() / "job-logs"


def state_dir() -> Path:
    """Get directory for job state files."""
    return data_home() / "job-state"


def ensure_dirs() -> None:
    """Create all required directories if they don't exist."""
    history_path().parent.mkdir(parents=True, exist_ok=True)
    default_log_dir().mkdir(parents=True, exist_ok=True)
    state_dir().mkdir(parents=True, exist_ok=True)


def _migrate_old_history() -> None:
    """Migrate old history file to new location."""
    old = data_home() / "jobs"
    new = history_path()
    if old.exists() and not new.exists():
        new.parent.mkdir(parents=True, exist_ok=True)
        old.rename(new)
