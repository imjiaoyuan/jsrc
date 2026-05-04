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

    p = grn_sub.add_parser("to_json", help="Convert GRN text files to JSON")
    p.add_argument("-i", "--input", required=True, help="Input file")
    p.add_argument("-o", "--output", required=True, help="Output JSON")
    p.add_argument("-t", "--type", choices=["network", "annotation"], required=True, help="Input type")
    p.set_defaults(func=_dispatch("jsrc.grn.convert"))

    p = grn_sub.add_parser("init", help="Create a local GRN viewer scaffold")
    p.add_argument("-o", "--outdir", required=True, help="Output directory")
    p.set_defaults(func=_dispatch("jsrc.grn.viewer", "cmd_init"))

    p = grn_sub.add_parser("serve", help="Serve viewer directory via HTTP")
    p.add_argument("-d", "--dir", required=True, help="Viewer directory")
    p.add_argument("-p", "--port", type=int, default=8000, help="Port")
    p.set_defaults(func=_dispatch("jsrc.grn.serve"))
