from __future__ import annotations

import importlib.resources
import shutil
import tempfile
import webbrowser
from argparse import Namespace
from pathlib import Path
from typing import Any


def cmd(args: Namespace) -> None:
    src_dir = importlib.resources.files("jsrc.plot") / "sources"
    with importlib.resources.as_file(src_dir) as d:
        tmp = Path(tempfile.mkdtemp())
        shutil.copy(Path(d) / "heart.html", tmp / "heart.html")
        webbrowser.open((tmp / "heart.html").as_uri())


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("heart", help="Plot heart curve animation")
    p.set_defaults(func=cmd)
