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


def cmd(args: Namespace) -> None:
    records = list(SeqIO.parse(args.fa, "fasta"))
    if len(records) < 3:
        raise ValidationError("Need at least three sequences for bootstrap phylogeny")
    if args.n < 1:
        raise ValidationError("-n must be >= 1")
    aln = pad_alignment(records)
    base_tree = _tree_from_alignment(aln)
    rng = random.Random(args.seed)

    support_counts: dict[tuple[str, ...], int] = {}
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
        logger.info("Bootstrap NJ tree saved to %s", args.o)
    else:
        print(base_tree.format("newick").strip())
    logger.info("Bootstrap replicates: %s", args.n)


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "bootstrap_phylo", help="Bootstrap support for NJ phylogeny"
    )
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument("-n", type=int, default=100, help="Bootstrap replicates")
    p.add_argument("-seed", type=int, default=42, help="Random seed")
    p.add_argument("-o", help="Optional output Newick file")
    p.set_defaults(func=cmd)
