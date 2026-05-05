from jsrc.analyze import bootstrap_phylo, motif, msa_consensus, phylo, qc, snpindel


def register_subparser(subparsers):
    analyze_parser = subparsers.add_parser("analyze", help="Analysis tools")
    analyze_sub = analyze_parser.add_subparsers(dest="analyze_cmd")
    analyze_parser.set_defaults(_group_parser=analyze_parser)

    phylo.register(analyze_sub)
    motif.register(analyze_sub)
    qc.register(analyze_sub)
    msa_consensus.register(analyze_sub)
    snpindel.register(analyze_sub)
    bootstrap_phylo.register(analyze_sub)
