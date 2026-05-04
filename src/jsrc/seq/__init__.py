import importlib


def _dispatch(module_name: str, func_name: str):
    def _runner(args):
        module = importlib.import_module(module_name)
        getattr(module, func_name)(args)

    return _runner


def register_subparser(subparsers):
    seq_parser = subparsers.add_parser("seq", help="Sequence operations")
    seq_sub = seq_parser.add_subparsers(dest="seq_cmd")
    seq_parser.set_defaults(_group_parser=seq_parser)

    p = seq_sub.add_parser("extract", help="Extract feature sequences by IDs from genome+GFF")
    p.add_argument("-fa", required=True, help="Genome FASTA file")
    p.add_argument("-gff", required=True, help="GFF annotation file")
    p.add_argument("-ids", required=True, help="ID list file")
    p.add_argument("-o", required=True, help="Output FASTA file")
    p.add_argument("-feature", default="CDS", help="Feature type in GFF (e.g. CDS,gene,exon,mRNA)")
    p.add_argument("-match", default="Parent", help="Attribute key used to match IDs (e.g. Parent,ID,gene_id)")
    p.set_defaults(func=_dispatch("jsrc.seq.extract", "cmd"))

    p = seq_sub.add_parser("rename", help="Rename FASTA IDs (CSV or GFF mapping)")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument("-mode", choices=["csv", "gff"], default="csv", help="Mapping mode")
    p.add_argument("-map", help="CSV mapping file old,new (for mode=csv)")
    p.add_argument("-gff", help="GFF annotation file (for mode=gff)")
    p.add_argument("-parent", help="Parent attribute field name (for mode=gff)")
    p.add_argument("-o", required=True, help="Output FASTA file")
    p.set_defaults(func=_dispatch("jsrc.seq.rename", "cmd"))

    p = seq_sub.add_parser("translate", help="Extract CDS and translate to protein")
    p.add_argument("-fa", required=True, help="Genome FASTA file")
    p.add_argument("-gff", required=True, help="GFF annotation file")
    p.add_argument("-id", required=True, help="Gene ID field in GFF")
    p.add_argument("-o", required=True, help="Output protein FASTA")
    p.set_defaults(func=_dispatch("jsrc.seq.translate", "cmd"))

    p = seq_sub.add_parser("promoter", help="Extract promoter sequences from genome and GFF")
    p.add_argument("-fa", required=True, help="Genome FASTA file")
    p.add_argument("-gff", required=True, help="GFF annotation file")
    p.add_argument("-ids", required=True, help="Target gene ID list file")
    p.add_argument("-o", required=True, help="Output promoter FASTA file")
    p.add_argument("-id", default="ID", help="ID field in GFF attributes")
    p.add_argument("-feature", default="gene", help="GFF feature type to use")
    p.add_argument("-up", type=int, default=2000, help="Upstream bp")
    p.add_argument("-down", type=int, default=0, help="Downstream bp")
    p.set_defaults(func=_dispatch("jsrc.seq.promoter", "cmd"))
