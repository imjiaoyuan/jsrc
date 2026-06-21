import logging
from argparse import Namespace
from typing import Any

from Bio import SeqIO
from Bio.Align import PairwiseAligner

from jsrc.core import ValidationError

logger = logging.getLogger(__name__)


def _first_seq(path: str) -> str:
    rec = next(SeqIO.parse(path, "fasta"), None)
    if rec is None:
        raise ValidationError(f"No sequence found in {path}")
    return str(rec.seq).upper().replace("U", "T")


def cmd(args: Namespace) -> None:
    if args.fa1 and args.fa2:
        s1 = _first_seq(args.fa1)
        s2 = _first_seq(args.fa2)
    elif args.fa:
        records = list(SeqIO.parse(args.fa, "fasta"))
        if len(records) < 2:
            raise ValidationError("Need 2 sequences in FASTA (or use -fa1/-fa2)")
        s1 = str(records[0].seq).upper().replace("U", "T")
        s2 = str(records[1].seq).upper().replace("U", "T")
    else:
        raise ValidationError("Provide -fa1/-fa2 or -fa (with 2+ sequences)")

    if not s1 or not s2:
        raise ValidationError("Both sequences must be non-empty")

    aligner = PairwiseAligner()
    aligner.mode = args.mode
    if args.match is not None:
        aligner.match_score = args.match
    if args.mismatch is not None:
        aligner.mismatch_score = args.mismatch
    if args.gap_open is not None:
        aligner.open_gap_score = args.gap_open
    if args.gap_extend is not None:
        aligner.extend_gap_score = args.gap_extend

    score = aligner.score(s1, s2)
    logger.info(
        "Alignment mode=%s score=%.1f match=%.1f mismatch=%.1f gap_open=%.1f gap_extend=%.1f",
        args.mode,
        score,
        aligner.match_score,
        aligner.mismatch_score,
        aligner.open_gap_score,
        aligner.extend_gap_score,
    )

    if args.score_only:
        print(f"{score:.1f}")
        return

    alignments = sorted(aligner.align(s1, s2), key=lambda a: a.score, reverse=True)
    for i, aln in enumerate(alignments[: args.top]):
        if args.top > 1:
            print(f"# Alignment {i + 1} (score={aln.score:.1f})")
        prefix = s2[:50]
        print(aln.format()[:2000] if len(prefix) < 80 else aln.format())


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("align", help="Pairwise sequence alignment")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("-fa", help="FASTA file with 2+ sequences")
    group.add_argument("-fa1", help="First sequence FASTA")
    p.add_argument("-fa2", help="Second sequence FASTA (requires -fa1)")

    p.add_argument(
        "-a",
        "--mode",
        choices=["global", "local"],
        default="global",
        help="Alignment mode (default: global)",
    )
    p.add_argument("--match", type=float, default=None, help="Match score")
    p.add_argument("--mismatch", type=float, default=None, help="Mismatch score")
    p.add_argument("--gap-open", type=float, default=None, help="Open gap score")
    p.add_argument("--gap-extend", type=float, default=None, help="Extend gap score")
    p.add_argument(
        "--top",
        type=int,
        default=1,
        help="Number of top alignments to show (default: 1)",
    )
    p.add_argument(
        "--score-only",
        action="store_true",
        help="Print only the alignment score",
    )
    p.set_defaults(func=cmd)
