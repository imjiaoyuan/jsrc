from __future__ import annotations

import logging
import random
from argparse import Namespace
from typing import Any

from Bio import Phylo, SeqIO
from Bio.Align import MultipleSeqAlignment
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from jsrc.analyze.core import pad_alignment
from jsrc.core import ValidationError

logger = logging.getLogger(__name__)


def _tree_from_alignment(aln, algo: str):
    calculator = DistanceCalculator("identity")
    dm = calculator.get_distance(aln)
    constructor = DistanceTreeConstructor(calculator)
    if algo == "upgma":
        return constructor.upgma(dm)
    return constructor.nj(dm)


def _resample_columns(aln, rng: random.Random):
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


def _apply_bootstrap_support(base_tree, aln, n_replicates: int, algo: str, rng):
    """Annotate ``base_tree`` internal clades with bootstrap support percentages."""
    support_counts: dict[tuple[str, ...], int] = {}
    total_taxa = len(base_tree.get_terminals())
    for _ in range(n_replicates):
        rep_aln = _resample_columns(aln, rng)
        rep_tree = _tree_from_alignment(rep_aln, algo)
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
        clade.confidence = support_counts.get(key, 0) / n_replicates * 100.0


def cmd(args: Namespace) -> None:
    records = list(SeqIO.parse(args.fa, "fasta"))
    if len(records) < 2:
        raise ValidationError("At least 2 sequences are required.")
    if args.bootstrap < 0:
        raise ValidationError("-n/--bootstrap must be >= 0")

    aln = pad_alignment(records)
    base_tree = _tree_from_alignment(aln, args.a)

    if args.bootstrap >= 1:
        if len(records) < 3:
            raise ValidationError("At least 3 sequences are required for bootstrap.")
        rng = random.Random(args.seed)
        _apply_bootstrap_support(base_tree, aln, args.bootstrap, args.a, rng)
        # Clear auto-generated internal names so support values serialize as
        # the node label (standard Newick bootstrap convention).
        for clade in base_tree.get_nonterminals():
            if clade.name and str(clade.name).startswith("Inner"):
                clade.name = None

    if args.o:
        Phylo.write(base_tree, args.o, "newick")
        logger.info("Phylogenetic tree (%s) saved to %s", args.a, args.o)
    else:
        print(base_tree.format("newick").strip())


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("phylo", help="Build phylogenetic tree")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument("-o", help="Output Newick tree (default: stdout)")
    p.add_argument(
        "-a", choices=["nj", "upgma"], default="nj", help="Algorithm (default: nj)"
    )
    p.add_argument(
        "-n",
        "--bootstrap",
        type=int,
        default=0,
        help="Bootstrap replicates for branch support (0 = off, default: 0)",
    )
    p.add_argument(
        "-seed", type=int, default=42, help="Random seed for bootstrap (default: 42)"
    )
    p.set_defaults(func=cmd)
