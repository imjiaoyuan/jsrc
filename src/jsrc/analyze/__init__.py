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

    p = analyze_sub.add_parser("qc", help="Assembly/mapping/variant quick stats")
    p.add_argument("-fa", help="Assembly FASTA for contig/N50/GC stats")
    p.add_argument("-sam", help="SAM/SAM.GZ for mapping rate and depth")
    p.add_argument("-vcf", help="VCF/VCF.GZ for SNP/INDEL counts")
    p.add_argument("-fq", nargs="+", help="FASTQ/FASTQ.GZ files for read/base/depth stats")
    p.add_argument("-gs", type=int, help="Genome size (bp), used with -fq for depth estimate")
    p.add_argument("--json", action="store_true", help="Print JSON instead of text table")
    p.set_defaults(func=_dispatch("jsrc.analyze.qc"))

    p = analyze_sub.add_parser("msa_consensus", help="Consensus and conservation from FASTA")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=_dispatch("jsrc.analyze.msa_consensus"))

    p = analyze_sub.add_parser("snpindel", help="Pairwise SNP/INDEL summary")
    p.add_argument("-fa", required=True, help="FASTA containing at least two sequences")
    p.add_argument("-id1", help="Sequence 1 ID (default: first record)")
    p.add_argument("-id2", help="Sequence 2 ID (default: second record)")
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=_dispatch("jsrc.analyze.snpindel"))

    p = analyze_sub.add_parser("bootstrap_phylo", help="Bootstrap support for NJ phylogeny")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument("-n", type=int, default=100, help="Bootstrap replicates")
    p.add_argument("-seed", type=int, default=42, help="Random seed")
    p.add_argument("-o", help="Optional output Newick file")
    p.set_defaults(func=_dispatch("jsrc.analyze.bootstrap_phylo"))
