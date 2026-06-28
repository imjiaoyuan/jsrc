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
        shutil.copy(Path(d) / "rose.html", tmp / "rose.html")
        webbrowser.open((tmp / "rose.html").as_uri())


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("rose", help="Plot 3D rose model")
    p.set_defaults(func=cmd)
