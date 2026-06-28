from __future__ import annotations

import shutil
import zipfile
from argparse import Namespace
from pathlib import Path
from typing import Any

from jsrc.grn.core import sync_assets


def _zip_viewer(viewer_dir: Path, zip_output: str) -> None:
    zip_path = Path(zip_output).expanduser().resolve()
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    wanted = [
        viewer_dir / "index.html",
        viewer_dir / "css" / "style.css",
        viewer_dir / "js" / "script.js",
        viewer_dir / "json" / "grn.json",
        viewer_dir / "json" / "annotation.json",
    ]
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in wanted:
            if f.exists():
                zf.write(f, arcname=str(f.relative_to(viewer_dir)))


def cmd(args: Namespace) -> None:
    root = Path(args.dir).expanduser().resolve()
    view_mode = "full" if args.all else "expand" if args.expand else "auto"
    sync_assets(str(root), view_mode, args.threshold, args.max_nodes)
    if args.grn_json:
        shutil.copy(args.grn_json, root / "json" / "grn.json")
    if args.annotation_json:
        shutil.copy(args.annotation_json, root / "json" / "annotation.json")
    if args.zip_output:
        _zip_viewer(root, args.zip_output)


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("build", help="Build GRN viewer package")
    p.add_argument("-d", "--dir", default=".", help="Output directory (default: .)")
    p.add_argument("-g", "--grn-json", help="grn.json to copy into package")
    p.add_argument(
        "-n", "--annotation-json", help="annotation.json to copy into package"
    )
    p.add_argument("-z", "--zip-output", help="ZIP output path")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("-a", "--all", action="store_true", help="Full view mode")
    mode.add_argument(
        "-e", "--expand", action="store_true", help="Click-to-expand mode"
    )
    p.set_defaults(all=True)
    p.add_argument(
        "-t", "--threshold", type=int, default=300, help="Auto full-view threshold"
    )
    p.add_argument("--max-nodes", type=int, default=0, help="Max nodes (0 = all)")
    p.set_defaults(func=cmd)
