import functools
import http.server
import os
import shutil

from jsrc.grn.core import ensure_dir, write_json
from jsrc.grn.viewer import sync_viewer_assets


def cmd(args):
    view_mode = "expand" if args.some else "auto"
    sync_viewer_assets(
        args.dir,
        init_empty_json=False,
        view_mode=view_mode,
        full_view_threshold=args.threshold,
    )
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
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=args.dir)
    with http.server.ThreadingHTTPServer(("0.0.0.0", args.port), handler) as httpd:
        print(f"Serving {args.dir} at http://127.0.0.1:{args.port}")
        httpd.serve_forever()
