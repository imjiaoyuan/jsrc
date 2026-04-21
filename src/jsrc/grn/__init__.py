import importlib


def _dispatch(module_name: str, func_name: str = "cmd"):
    def _runner(args):
        module = importlib.import_module(module_name)
        getattr(module, func_name)(args)

    return _runner


def register_subparser(subparsers):
    grn_parser = subparsers.add_parser("grn", help="GRN conversion and local viewer")
    grn_sub = grn_parser.add_subparsers(dest="grn_cmd")
    grn_parser.set_defaults(_group_parser=grn_parser)

    p = grn_sub.add_parser("net2json", help="Convert GRN edge table to grn.json")
    p.add_argument("-i", "--input", required=True, help="Input file")
    p.add_argument("-o", "--output", required=True, help="Output JSON")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("-a", "--all", action="store_true", help="Mode all: auto full-view when gene count <= threshold")
    mode.add_argument("-s", "--some", action="store_true", help="Mode some: manual click-to-expand only")
    p.set_defaults(all=True, some=False)
    p.add_argument(
        "-t",
        "--threshold",
        type=int,
        default=300,
        help="In all mode, auto full-view when gene count <= this value",
    )
    p.add_argument(
        "-d",
        "--viewer-dir",
        help="Optional viewer output directory. If omitted, infer from -o (e.g. viewer/json/grn.json -> viewer)",
    )
    p.add_argument("-n", "--annotation-input", help="Optional annotation TSV to generate json/annotation.json for package")
    p.add_argument("-z", "--zip-output", help="Optional ZIP output path containing html/css/js/json viewer package")
    p.set_defaults(func=_dispatch("jsrc.grn.convert", "cmd_network"))

    p = grn_sub.add_parser("anno2json", help="Convert annotation table to annotation.json")
    p.add_argument("-i", "--input", required=True, help="Input file")
    p.add_argument("-o", "--output", required=True, help="Output JSON")
    p.set_defaults(func=_dispatch("jsrc.grn.convert", "cmd_annotation"))

    p = grn_sub.add_parser("serve", help="Start GRN viewer service")
    p.add_argument("-d", "--dir", default=".", help="Viewer directory (default: current directory)")
    p.add_argument("-p", "--port", type=int, default=8000, help="Port")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("-a", "--all", action="store_true", help="Mode all: auto full-view when gene count <= threshold")
    mode.add_argument("-s", "--some", action="store_true", help="Mode some: manual click-to-expand only")
    p.set_defaults(all=True, some=False)
    p.add_argument(
        "-t",
        "--threshold",
        type=int,
        default=300,
        help="In all mode, auto full-view when gene count <= this value",
    )
    p.set_defaults(func=_dispatch("jsrc.grn.serve"))

    p = grn_sub.add_parser("centrality", help="Compute GRN node centrality summary")
    p.add_argument("-i", "--input", required=True, help="Edge table (source target [weight])")
    p.add_argument("--sep", default=None, help="Column separator (default: auto whitespace/tab)")
    p.add_argument("--top", type=int, default=20, help="Top N nodes to print")
    p.set_defaults(func=_dispatch("jsrc.grn.centrality"))
