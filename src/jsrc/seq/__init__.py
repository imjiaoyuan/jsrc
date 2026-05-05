from jsrc.seq import codon, extract, kmer, promoter, qc, rename, translate, window


def register_subparser(subparsers):
    seq_parser = subparsers.add_parser("seq", help="Sequence operations")
    seq_sub = seq_parser.add_subparsers(dest="seq_cmd")
    seq_parser.set_defaults(_group_parser=seq_parser)

    extract.register(seq_sub)
    rename.register(seq_sub)
    translate.register(seq_sub)
    promoter.register(seq_sub)
    qc.register(seq_sub)
    codon.register(seq_sub)
    kmer.register(seq_sub)
    window.register(seq_sub)
