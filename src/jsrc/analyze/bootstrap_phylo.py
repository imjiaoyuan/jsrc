import random

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


def _tree_from_alignment(aln: MultipleSeqAlignment):
    calculator = DistanceCalculator("identity")
    dm = calculator.get_distance(aln)
    return DistanceTreeConstructor(calculator).nj(dm)


def _resample_columns(aln: MultipleSeqAlignment, rng: random.Random):
    n = aln.get_alignment_length()
    picks = [rng.randrange(n) for _ in range(n)]
    resampled = []
    for rec in aln:
        seq = "".join(rec.seq[i] for i in picks)
        resampled.append(SeqRecord(Seq(seq), id=rec.id, description=""))
    return MultipleSeqAlignment(resampled)


def _clade_key(clade):
    leaves = sorted(t.name for t in clade.get_terminals() if t.name is not None)
    return tuple(leaves)


def cmd(args):
    records = list(SeqIO.parse(args.fa, "fasta"))
    if len(records) < 3:
        raise SystemExit("Need at least three sequences for bootstrap phylogeny")
    if args.n < 1:
        raise SystemExit("-n must be >= 1")
    aln = _pad_alignment(records)
    base_tree = _tree_from_alignment(aln)
    rng = random.Random(args.seed)

    support_counts = {}
    total_taxa = len(base_tree.get_terminals())
    for _ in range(args.n):
        rep_aln = _resample_columns(aln, rng)
        rep_tree = _tree_from_alignment(rep_aln)
        for clade in rep_tree.get_nonterminals():
            leaves = clade.get_terminals()
            if len(leaves) <= 1 or len(leaves) >= total_taxa:
                continue
            key = _clade_key(clade)
            support_counts[key] = support_counts.get(key, 0) + 1

    for clade in base_tree.get_nonterminals():
        leaves = clade.get_terminals()
        if len(leaves) <= 1 or len(leaves) >= total_taxa:
            continue
        key = _clade_key(clade)
        clade.confidence = support_counts.get(key, 0) / args.n * 100.0

    if args.o:
        Phylo.write(base_tree, args.o, "newick")
        print(f"Bootstrap NJ tree saved to {args.o}")
    else:
        print(base_tree.format("newick").strip())
    print(f"bootstrap_replicates\t{args.n}")
