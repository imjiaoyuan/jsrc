from __future__ import annotations

import logging
import random as _random
import sys
from argparse import Namespace
from typing import Any

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from jsrc.core import ValidationError

logger = logging.getLogger(__name__)

DNA_BASES = "ACGT"
PROTEIN_LETTERS = "ACDEFGHIKLMNPQRSTVWY"


def _random_dna(length: int, gc: float, rng: _random.Random) -> str:
    gc_count = int(length * gc)
    at_count = length - gc_count
    bases = ["G", "C"] * gc_count + ["A", "T"] * at_count
    rng.shuffle(bases)
    return "".join(bases)


def _random_protein(length: int, rng: _random.Random) -> str:
    return "".join(rng.choice(PROTEIN_LETTERS) for _ in range(length))


def cmd(args: Namespace) -> None:
    if args.n < 1:
        raise ValidationError("-n must be >= 1")
    if args.l < 1:
        raise ValidationError("-l must be >= 1")
    if not 0.0 <= args.gc <= 1.0:
        raise ValidationError("--gc must be between 0 and 1")

    rng = _random.Random(args.seed)

    records = []
    for i in range(args.n):
        if args.type == "dna":
            seq = _random_dna(args.l, args.gc, rng)
        else:
            seq = _random_protein(args.l, rng)
        rec = SeqRecord(
            Seq(seq),
            id=f"random_{i + 1}",
            description=f"len={args.l} type={args.type} gc={args.gc:.2f} seed={args.seed}",
        )
        records.append(rec)

    from Bio import SeqIO

    if args.o:
        SeqIO.write(records, args.o, "fasta")
        logger.info("Wrote %d random %s sequences to %s", args.n, args.type, args.o)
    else:
        SeqIO.write(records, sys.stdout, "fasta")


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("random", help="Generate random sequences")
    p.add_argument(
        "-t",
        "--type",
        choices=["dna", "protein"],
        default="dna",
        help="Sequence type (default: dna)",
    )
    p.add_argument("-n", type=int, default=1, help="Number of sequences")
    p.add_argument("-l", type=int, default=100, help="Sequence length")
    p.add_argument(
        "--gc",
        type=float,
        default=0.5,
        help="GC content for DNA (0.0–1.0, default: 0.5)",
    )
    p.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    p.add_argument("-o", default=None, help="Output FASTA file (default: stdout)")
    p.set_defaults(func=cmd)
