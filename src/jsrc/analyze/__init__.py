import importlib


def _dispatch(module_name: str):
    def _runner(args):
        module = importlib.import_module(module_name)
        module.cmd(args)

    return _runner


def register_subparser(subparsers):
    analyze_parser = subparsers.add_parser("analyze", help="Analysis tools")
    analyze_sub = analyze_parser.add_subparsers(dest="analyze_cmd")
    analyze_parser.set_defaults(_group_parser=analyze_parser)

    p = analyze_sub.add_parser("phylo", help="Build phylogenetic tree")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument("-o", required=True, help="Output Newick tree")
    p.add_argument("-a", choices=["nj", "upgma"], default="nj", help="Algorithm")
    p.set_defaults(func=_dispatch("jsrc.analyze.phylo"))

    p = analyze_sub.add_parser("motif", help="Motif analysis")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument("-o", required=True, help="Output directory")
    p.add_argument("-nmotifs", type=int, default=5, help="Number of motifs")
    p.add_argument("-minw", type=int, default=6, help="Min motif width")
    p.add_argument("-maxw", type=int, default=12, help="Max motif width")
    p.set_defaults(func=_dispatch("jsrc.analyze.motif"))
