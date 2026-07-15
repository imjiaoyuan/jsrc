"""Job module configuration and path management."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _is_windows() -> bool:
    return sys.platform == "win32"


def _is_macos() -> bool:
    return sys.platform == "darwin"


def config_home() -> Path:
    if _is_windows():
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "jsrc"
        return Path.home() / "AppData" / "Roaming" / "jsrc"
    if _is_macos():
        return Path.home() / "Library" / "Preferences" / "jsrc"
    xdg = os.getenv("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg).expanduser() / "jsrc"
    return Path.home() / ".config" / "jsrc"


def data_home() -> Path:
    if _is_windows():
        localappdata = os.getenv("LOCALAPPDATA")
        if localappdata:
            return Path(localappdata) / "jsrc"
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "jsrc"
        return Path.home() / "AppData" / "Local" / "jsrc"
    if _is_macos():
        return Path.home() / "Library" / "Application Support" / "jsrc"
    xdg = os.getenv("XDG_DATA_HOME")
    if xdg:
        return Path(xdg).expanduser() / "jsrc"
    return Path.home() / ".local" / "share" / "jsrc"


def history_path() -> Path:
    override = os.getenv("JSRC_JOBS_FILE", "")
    if override:
        return Path(override).expanduser()
    return config_home() / "job" / "history"


def default_log_dir() -> Path:
    return data_home() / "job-logs"


def state_dir() -> Path:
    return data_home() / "job-state"


def ensure_dirs() -> None:
    history_path().parent.mkdir(parents=True, exist_ok=True)
    default_log_dir().mkdir(parents=True, exist_ok=True)
    state_dir().mkdir(parents=True, exist_ok=True)


def _migrate_old_history() -> None:
    old_xdg = Path.home() / ".local" / "share" / "jsrc" / "jobs"
    new = history_path()
    if old_xdg.exists() and not new.exists():
        new.parent.mkdir(parents=True, exist_ok=True)
        old_xdg.rename(new)
