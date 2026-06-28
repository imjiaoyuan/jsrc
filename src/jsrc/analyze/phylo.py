import logging
from argparse import Namespace
from typing import Any

from Bio import Phylo, SeqIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor

from jsrc.analyze.core import pad_alignment
from jsrc.core import ValidationError

logger = logging.getLogger(__name__)


def _build_tree(records, algo: str):
    alignment = pad_alignment(records)
    calculator = DistanceCalculator("identity")
    dm = calculator.get_distance(alignment)
    constructor = DistanceTreeConstructor(calculator)
    if algo == "upgma":
        return constructor.upgma(dm)
    return constructor.nj(dm)


def cmd(args: Namespace) -> None:
    records = list(SeqIO.parse(args.fa, "fasta"))
    if len(records) < 2:
        raise ValidationError("At least 2 sequences are required.")
    tree = _build_tree(records, args.a)
    Phylo.write(tree, args.o, "newick")
    logger.info("Phylogenetic tree (%s) saved to %s", args.a, args.o)


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("phylo", help="Build phylogenetic tree")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument("-o", required=True, help="Output Newick tree")
    p.add_argument("-a", choices=["nj", "upgma"], default="nj", help="Algorithm")
    p.set_defaults(func=cmd)
