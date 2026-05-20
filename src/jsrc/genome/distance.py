import json
import logging
from argparse import Namespace
from typing import Any

from Bio import SeqIO

logger = logging.getLogger(__name__)


def _hamming_distance(seq1: str, seq2: str) -> int:
    if len(seq1) != len(seq2):
        raise ValueError("Sequences must have equal length for Hamming distance")
    return sum(c1 != c2 for c1, c2 in zip(seq1, seq2, strict=True))


def _p_distance(seq1: str, seq2: str) -> float:
    if len(seq1) != len(seq2):
        raise ValueError("Sequences must have equal length for p-distance")
    n = len(seq1)
    if n == 0:
        return 0.0
    return _hamming_distance(seq1, seq2) / n


def _jukes_cantor_distance(seq1: str, seq2: str) -> float:
    import math

    p = _p_distance(seq1, seq2)
    if p >= 0.75:
        return float("inf")
    return -0.75 * math.log(1 - (4 * p / 3))


def _kimura_2p_distance(seq1: str, seq2: str) -> float:
    import math

    if len(seq1) != len(seq2):
        raise ValueError(
            "Sequences must have equal length for Kimura 2-parameter distance"
        )
    n = len(seq1)
    if n == 0:
        return 0.0

    transitions = 0
    transversions = 0
    for c1, c2 in zip(seq1, seq2, strict=True):
        if c1 == c2:
            continue
        if (c1 in "AG" and c2 in "AG") or (c1 in "CT" and c2 in "CT"):
            transitions += 1
        else:
            transversions += 1

    P = transitions / n
    Q = transversions / n

    if 1 - 2 * P - Q <= 0 or 1 - 2 * Q <= 0:
        return float("inf")

    return -0.5 * math.log((1 - 2 * P - Q) * math.sqrt(1 - 2 * Q))


def cmd(args: Namespace) -> None:
    sequences = []
    for rec in SeqIO.parse(args.fa, "fasta"):
        sequences.append((rec.id, str(rec.seq).upper().replace("U", "T")))

    if len(sequences) < 2:
        raise ValueError("At least 2 sequences required")

    results = []
    for i in range(len(sequences)):
        for j in range(i + 1, len(sequences)):
            id1, seq1 = sequences[i]
            id2, seq2 = sequences[j]

            try:
                if args.method == "hamming":
                    dist = _hamming_distance(seq1, seq2)
                elif args.method == "p":
                    dist = _p_distance(seq1, seq2)
                elif args.method == "jc":
                    dist = _jukes_cantor_distance(seq1, seq2)
                elif args.method == "k2p":
                    dist = _kimura_2p_distance(seq1, seq2)
                else:
                    raise ValueError(f"Unknown method: {args.method}")

                results.append({"seq1": id1, "seq2": id2, "distance": dist})
            except ValueError as e:
                logger.warning("Skipping %s vs %s: %s", id1, id2, e)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print("seq1\tseq2\tdistance")
    for item in results:
        dist_str = (
            f"{item['distance']:.6f}" if item["distance"] != float("inf") else "inf"
        )
        print(f"{item['seq1']}\t{item['seq2']}\t{dist_str}")


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("distance", help="Calculate pairwise genetic distances")
    p.add_argument("-fa", required=True, help="Aligned sequences FASTA file")
    p.add_argument(
        "--method",
        choices=["hamming", "p", "jc", "k2p"],
        default="p",
        help="Distance method: hamming, p (p-distance), jc (Jukes-Cantor), k2p (Kimura 2-parameter)",
    )
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
