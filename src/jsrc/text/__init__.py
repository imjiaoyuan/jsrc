import importlib


def _dispatch(module_name: str):
    def _runner(args):
        module = importlib.import_module(module_name)
        module.cmd(args)

    return _runner


def register_subparser(subparsers):
    text_parser = subparsers.add_parser("text", help="Text processing utilities")
    text_sub = text_parser.add_subparsers(dest="text_cmd")
    text_parser.set_defaults(_group_parser=text_parser)

    p = text_sub.add_parser("wc", help="Count lines/words/chars")
    p.add_argument("-i", "--input", help="Input text file (default: stdin)")
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=_dispatch("jsrc.text.wc"))

    p = text_sub.add_parser("dedup", help="Deduplicate lines while preserving order")
    p.add_argument("-i", "--input", help="Input text file (default: stdin)")
    p.add_argument("-o", "--output", help="Optional output file (default: stdout)")
    p.add_argument("--count", action="store_true", help="Print occurrence counts")
    p.set_defaults(func=_dispatch("jsrc.text.dedup"))

    p = text_sub.add_parser("grep", help="Filter lines by regex pattern")
    p.add_argument("-p", "--pattern", required=True, help="Regex pattern")
    p.add_argument("-i", "--input", help="Input text file (default: stdin)")
    p.add_argument("-o", "--output", help="Optional output file (default: stdout)")
    p.add_argument("-I", "--ignore-case", action="store_true", help="Ignore case")
    p.add_argument("-v", "--invert", action="store_true", help="Invert match")
    p.add_argument("-n", "--line-number", action="store_true", help="Prefix output with line number")
    p.set_defaults(func=_dispatch("jsrc.text.grep"))

    p = text_sub.add_parser("cut", help="Select delimited columns")
    p.add_argument("-f", "--fields", required=True, help="1-based field indices, comma-separated (e.g. 1,3,5)")
    p.add_argument("-i", "--input", help="Input text file (default: stdin)")
    p.add_argument("-o", "--output", help="Optional output file (default: stdout)")
    p.add_argument("-d", "--delimiter", default="\t", help="Input delimiter (default: tab)")
    p.add_argument("--out-delimiter", help="Output delimiter (default: same as input)")
    p.set_defaults(func=_dispatch("jsrc.text.cut"))

    p = text_sub.add_parser("replace", help="Regex find/replace")
    p.add_argument("-p", "--pattern", required=True, help="Regex pattern")
    p.add_argument("-r", "--repl", required=True, help="Replacement text")
    p.add_argument("-i", "--input", help="Input text file (default: stdin)")
    p.add_argument("-o", "--output", help="Optional output file (default: stdout)")
    p.add_argument("-I", "--ignore-case", action="store_true", help="Ignore case")
    p.add_argument("--count", type=int, default=0, help="Max replacements per line (0 means unlimited)")
    p.set_defaults(func=_dispatch("jsrc.text.replace"))
