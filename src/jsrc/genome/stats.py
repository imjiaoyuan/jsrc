from __future__ import annotations

import json
import logging
from argparse import Namespace
from typing import Any

from Bio import SeqIO

from jsrc.core import DataFormatError

logger = logging.getLogger(__name__)


def _calculate_n50_l50(lengths: list[int]) -> tuple[int, int]:
    if not lengths:
        return 0, 0
    sorted_lengths = sorted(lengths, reverse=True)
    total = sum(sorted_lengths)
    half = total / 2
    cumsum = 0
    for i, length in enumerate(sorted_lengths, 1):
        cumsum += length
        if cumsum >= half:
            return length, i
    return 0, 0


def _count_gaps(seq: str) -> dict[str, int | float | list[int]]:
    seq = seq.upper()
    n_count = seq.count("N")
    gap_count = 0
    gap_lengths: list[int] = []
    in_gap = False
    gap_start = 0

    for i, base in enumerate(seq):
        if base == "N":
            if not in_gap:
                in_gap = True
                gap_start = i
        else:
            if in_gap:
                in_gap = False
                gap_count += 1
                gap_lengths.append(i - gap_start)
    if in_gap:
        gap_count += 1
        gap_lengths.append(len(seq) - gap_start)

    return {
        "n_count": n_count,
        "gap_count": gap_count,
        "gap_lengths": gap_lengths,
        "min_gap": min(gap_lengths) if gap_lengths else 0,
        "max_gap": max(gap_lengths) if gap_lengths else 0,
        "mean_gap": sum(gap_lengths) / len(gap_lengths) if gap_lengths else 0.0,
    }


def cmd(args: Namespace) -> None:
    # Single streaming pass: hold one record at a time instead of loading the
    # whole FASTA into memory (important for large genomes).
    lengths: list[int] = []
    total_length = 0
    total_gc = 0
    total_n = 0
    gap_count = 0
    gap_lengths_all: list[int] = []

    num_records = 0
    for rec in SeqIO.parse(str(args.fa), "fasta"):
        num_records += 1
        seq = str(rec.seq).upper()
        length = len(seq)
        lengths.append(length)
        total_length += length
        total_gc += seq.count("G") + seq.count("C")

        gap_info = _count_gaps(seq)
        total_n += int(gap_info["n_count"])
        gap_count += int(gap_info["gap_count"])
        rec_gap_lengths = gap_info.get("gap_lengths", [])
        if isinstance(rec_gap_lengths, list):
            gap_lengths_all.extend(rec_gap_lengths)

    if num_records == 0:
        raise DataFormatError(f"No sequences found in FASTA: {args.fa}")

    n50, l50 = _calculate_n50_l50(lengths)
    gc_percent = (total_gc / total_length * 100.0) if total_length > 0 else 0.0

    stats = {
        "num_sequences": num_records,
        "total_length": total_length,
        "min_length": min(lengths),
        "max_length": max(lengths),
        "mean_length": total_length / num_records if num_records else 0.0,
        "n50": n50,
        "l50": l50,
        "gc_percent": round(gc_percent, 4),
        "n_count": total_n,
        "n_percent": round(
            (total_n / total_length * 100.0) if total_length > 0 else 0.0, 4
        ),
        "gap_count": gap_count,
        "min_gap_length": min(gap_lengths_all) if gap_lengths_all else 0,
        "max_gap_length": max(gap_lengths_all) if gap_lengths_all else 0,
        "mean_gap_length": (
            round(sum(gap_lengths_all) / len(gap_lengths_all), 2)
            if gap_lengths_all
            else 0.0
        ),
    }

    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return

    logger.info("Genome statistics for: %s", args.fa)
    print(f"{'Number of sequences':30} : {stats['num_sequences']:>15,}")
    print(f"{'Total length (bp)':30} : {stats['total_length']:>15,}")
    print(f"{'Min length (bp)':30} : {stats['min_length']:>15,}")
    print(f"{'Max length (bp)':30} : {stats['max_length']:>15,}")
    print(f"{'Mean length (bp)':30} : {stats['mean_length']:>15,.2f}")
    print(f"{'N50 (bp)':30} : {stats['n50']:>15,}")
    print(f"{'L50':30} : {stats['l50']:>15,}")
    print(f"{'GC content (%)':30} : {stats['gc_percent']:>15.4f}")
    print(f"{'N bases':30} : {stats['n_count']:>15,}")
    print(f"{'N percent (%)':30} : {stats['n_percent']:>15.4f}")
    print(f"{'Number of gaps':30} : {stats['gap_count']:>15,}")
    if stats["gap_count"] > 0:
        print(f"{'Min gap length (bp)':30} : {stats['min_gap_length']:>15,}")
        print(f"{'Max gap length (bp)':30} : {stats['max_gap_length']:>15,}")
        print(f"{'Mean gap length (bp)':30} : {stats['mean_gap_length']:>15.2f}")


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "stats", help="Genome statistics (N50/L50, gaps, GC content)"
    )
    p.add_argument("-fa", required=True, help="Input genome FASTA file")
    p.add_argument("--json", action="store_true", help="Print JSON output")
    p.set_defaults(func=cmd)
