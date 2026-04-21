from __future__ import annotations

import sys
from pathlib import Path


def read_text(input_path: str | None) -> str:
    if input_path:
        return Path(input_path).read_text(encoding="utf-8")
    return sys.stdin.read()


def write_text(output_path: str | None, content: str) -> None:
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
        print(f"Wrote output to {output_path}")
        return
    print(content, end="")
