import json
import os
from pathlib import Path


def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def write_text(path: str, content: str):
    ensure_dir(os.path.dirname(path) or ".")
    Path(path).write_text(content, encoding="utf-8")


def write_json(path: str, data):
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

