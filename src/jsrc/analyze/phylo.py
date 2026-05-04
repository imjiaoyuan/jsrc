from Bio import Phylo, SeqIO
from Bio.Align import MultipleSeqAlignment
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from jsrc.analyze.core import normalize_sequence


def _pad_alignment(records: list[SeqRecord]) -> MultipleSeqAlignment:
    max_len = max(len(r.seq) for r in records)
    aligned = []
    for r in records:
        seq = normalize_sequence(str(r.seq))
        if len(seq) < max_len:
            seq += "-" * (max_len - len(seq))
        aligned.append(SeqRecord(Seq(seq), id=r.id, description=""))
    return MultipleSeqAlignment(aligned)


def _build_tree(records: list[SeqRecord], algo: str):
    alignment = _pad_alignment(records)
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
