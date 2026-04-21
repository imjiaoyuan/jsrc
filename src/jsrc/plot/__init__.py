import importlib


def _dispatch(module_name: str):
    def _runner(args):
        module = importlib.import_module(module_name)
        module.cmd(args)

    return _runner


def register_subparser(subparsers):
    plot_parser = subparsers.add_parser("plot", help="Visualization")
    plot_sub = plot_parser.add_subparsers(dest="plot_cmd")
    plot_parser.set_defaults(_group_parser=plot_parser)

    p = plot_sub.add_parser("gene", help="Plot gene structure diagram")
    p.add_argument("-gff", required=True, help="GFF annotation file")
    p.add_argument("-ids", required=True, help="Gene ID list file")
    p.add_argument("-o", required=True, help="Output PNG file")
    p.add_argument("-dpi", type=int, default=300, help="DPI")
    p.set_defaults(func=_dispatch("jsrc.plot.gene"))

    p = plot_sub.add_parser("exon", help="Plot exon structure diagram")
    p.add_argument("-gff", required=True, help="GFF annotation file")
    p.add_argument("-ids", required=True, help="Gene ID list file")
    p.add_argument("-o", required=True, help="Output PNG file")
    p.add_argument("-dpi", type=int, default=300, help="DPI")
    p.set_defaults(func=_dispatch("jsrc.plot.exon"))

    p = plot_sub.add_parser("chromosome", help="Plot chromosome map")
    p.add_argument("-gff", required=True, help="GFF annotation file")
    p.add_argument("-ids", help="Optional gene ID list file")
    p.add_argument("-o", required=True, help="Output PNG file")
    p.add_argument("-dpi", type=int, default=300, help="DPI")
    p.set_defaults(func=_dispatch("jsrc.plot.chromosome"))

    p = plot_sub.add_parser("domain", help="Plot protein domain architecture")
    p.add_argument("-tsv", required=True, help="Domain TSV file")
    p.add_argument("-o", required=True, help="Output PNG file")
    p.add_argument("-dpi", type=int, default=300, help="DPI")
    p.set_defaults(func=_dispatch("jsrc.plot.domain"))

    p = plot_sub.add_parser("cis", help="Plot cis-regulatory elements")
    p.add_argument("-bed", required=True, help="BED file")
    p.add_argument("-o", required=True, help="Output PNG file")
    p.add_argument("-dpi", type=int, default=300, help="DPI")
    p.set_defaults(func=_dispatch("jsrc.plot.cis"))

    p = plot_sub.add_parser("heart", help="Plot heart curve")
    p.set_defaults(func=_dispatch("jsrc.plot.heart"))

    p = plot_sub.add_parser("rose", help="Plot 3D rose model")
    p.set_defaults(func=_dispatch("jsrc.plot.rose"))
