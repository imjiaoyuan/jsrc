import functools
import http.server

from jsrc.grn.viewer import sync_viewer_assets


def cmd(args):
    view_mode = "expand" if args.some else "auto"
    sync_viewer_assets(
        args.dir,
        init_empty_json=False,
        view_mode=view_mode,
        full_view_threshold=args.threshold,
    )
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=args.dir)
    with http.server.ThreadingHTTPServer(("0.0.0.0", args.port), handler) as httpd:
        print(f"Serving {args.dir} at http://127.0.0.1:{args.port}")
        httpd.serve_forever()
