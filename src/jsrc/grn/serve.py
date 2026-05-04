import functools
import http.server


def cmd(args):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=args.dir)
    with http.server.ThreadingHTTPServer(("0.0.0.0", args.port), handler) as httpd:
        print(f"Serving {args.dir} at http://127.0.0.1:{args.port}")
        httpd.serve_forever()

