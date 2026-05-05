from typing import Any

from jsrc.grn import anno2json, build, centrality, net2json, serve


def register_subparser(subparsers: Any) -> None:
    grn_parser = subparsers.add_parser("grn", help="GRN conversion and local viewer")
    grn_sub = grn_parser.add_subparsers(dest="grn_cmd")
    grn_parser.set_defaults(_group_parser=grn_parser)

    build.register(grn_sub)
    net2json.register(grn_sub)
    anno2json.register(grn_sub)
    serve.register(grn_sub)
    centrality.register(grn_sub)
