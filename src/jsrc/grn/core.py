from __future__ import annotations

import json
import os
import pathlib
from pathlib import Path
from typing import Any


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def write_text(path: str, content: str) -> None:
    ensure_dir(os.path.dirname(path) or ".")
    Path(path).write_text(content, encoding="utf-8")


def write_json(path: str, data: Any) -> None:
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


_SCRIPT_TEMPLATE = None
_INDEX_HTML = None
_STYLE_CSS = None


def _load_sources() -> None:
    global _SCRIPT_TEMPLATE, _INDEX_HTML, _STYLE_CSS
    if _SCRIPT_TEMPLATE is not None:
        return
    base = pathlib.Path(__file__).parent / "sources"
    _SCRIPT_TEMPLATE = (base / "script.js").read_text(encoding="utf-8")
    _INDEX_HTML = (base / "index.html").read_text(encoding="utf-8")
    _STYLE_CSS = (base / "style.css").read_text(encoding="utf-8")


def sync_assets(
    base: str,
    view_mode: str,
    threshold: int,
    max_nodes: int,
) -> None:
    _load_sources()
    ensure_dir(base)
    ensure_dir(os.path.join(base, "css"))
    ensure_dir(os.path.join(base, "js"))
    ensure_dir(os.path.join(base, "json"))
    write_text(os.path.join(base, "index.html"), _INDEX_HTML)
    write_text(os.path.join(base, "css/style.css"), _STYLE_CSS)
    script = (
        _SCRIPT_TEMPLATE.replace("__JSRC_VIEW_MODE__", view_mode)
        .replace("__JSRC_FULL_THRESHOLD__", str(threshold))
        .replace("__JSRC_MAX_DISPLAY_NODES__", str(max_nodes))
    )
    write_text(os.path.join(base, "js/script.js"), script)
