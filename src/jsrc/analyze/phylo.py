from Bio import Phylo, SeqIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor

from jsrc.analyze.core import pad_alignment


def _build_tree(records, algo: str):
    alignment = pad_alignment(records)
    calculator = DistanceCalculator("identity")
    dm = calculator.get_distance(alignment)
    constructor = DistanceTreeConstructor(calculator)
    if algo == "upgma":
        return constructor.upgma(dm)
    return constructor.nj(dm)


def cmd(args):
    records = list(SeqIO.parse(args.fa, "fasta"))
    if len(records) < 2:
        raise SystemExit("At least 2 sequences are required.")
    tree = _build_tree(records, args.a)
    Phylo.write(tree, args.o, "newick")
    print(f"Phylogenetic tree ({args.a}) saved to {args.o}")


def register(subparsers):
    p = subparsers.add_parser("phylo", help="Build phylogenetic tree")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument("-o", required=True, help="Output Newick tree")
    p.add_argument("-a", choices=["nj", "upgma"], default="nj", help="Algorithm")
    p.set_defaults(func=cmd)
