import functools
import http.server
import os
import shutil
from argparse import Namespace
from typing import Any

from jsrc.grn.build import _sync_assets
from jsrc.grn.core import ensure_dir, write_json


def cmd(args: Namespace) -> None:
    view_mode = "full" if args.all else "expand" if args.expand else "auto"
    _sync_assets(args.dir, view_mode, args.threshold, 0)
    ensure_dir(f"{args.dir}/json")
    src_grn = os.path.abspath(args.grn_json)
    dst_grn = os.path.abspath(f"{args.dir}/json/grn.json")
    if src_grn != dst_grn:
        shutil.copy2(src_grn, dst_grn)
    if args.annotation_json:
        src_anno = os.path.abspath(args.annotation_json)
        dst_anno = os.path.abspath(f"{args.dir}/json/annotation.json")
        if src_anno != dst_anno:
            shutil.copy2(src_anno, dst_anno)
    elif not os.path.exists(f"{args.dir}/json/annotation.json"):
        write_json(f"{args.dir}/json/annotation.json", {})
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=args.dir
    )
    with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler) as httpd:
        print(f"Serving {args.dir} at http://127.0.0.1:{args.port}")
        httpd.serve_forever()


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("serve", help="Start GRN viewer service")
    p.add_argument(
        "-d", "--dir", default=".", help="Viewer directory (default: current directory)"
    )
    p.add_argument("-p", "--port", type=int, default=8000, help="Port")
    p.add_argument("-g", "--grn-json", required=True, help="Path to grn.json")
    p.add_argument(
        "-n",
        "--annotation-json",
        default=None,
        help="Path to annotation.json (optional)",
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Mode all: auto full-view when gene count <= threshold",
    )
    mode.add_argument(
        "-e",
        "--expand",
        action="store_true",
        help="Click-to-expand mode",
    )
    p.set_defaults(all=True, expand=False)
    p.add_argument(
        "-t",
        "--threshold",
        type=int,
        default=300,
        help="In all mode, auto full-view when gene count <= this value",
    )
    p.set_defaults(func=cmd)
