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
        raise ValueError("At least 2 sequences are required.")
    tree = _build_tree(records, args.a)
    Phylo.write(tree, args.o, "newick")
    print(f"Phylogenetic tree ({args.a}) saved to {args.o}")
