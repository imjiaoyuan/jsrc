from __future__ import annotations

import json
import logging
from argparse import Namespace
from typing import Any

from jsrc.core import load_fasta

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


def _count_gaps(seq: str) -> dict[str, int | float]:
    seq = seq.upper()
    n_count = seq.count("N")
    gap_count = 0
    gap_lengths = []
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
        "min_gap": min(gap_lengths) if gap_lengths else 0,
        "max_gap": max(gap_lengths) if gap_lengths else 0,
        "mean_gap": sum(gap_lengths) / len(gap_lengths) if gap_lengths else 0.0,
    }


def cmd(args: Namespace) -> None:
    records = load_fasta(args.fa)

    lengths = [len(rec.seq) for rec in records]
    total_length = sum(lengths)
    n50, l50 = _calculate_n50_l50(lengths)

    all_gaps = {
        "n_count": 0,
        "gap_count": 0,
        "min_gap": 0,
        "max_gap": 0,
        "mean_gap": 0.0,
    }
    gap_lengths_all = []
    for rec in records:
        gap_info = _count_gaps(str(rec.seq))
        all_gaps["n_count"] += gap_info["n_count"]
        all_gaps["gap_count"] += gap_info["gap_count"]
        if gap_info["gap_count"] > 0:
            seq = str(rec.seq).upper()
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
                        gap_lengths_all.append(i - gap_start)
            if in_gap:
                gap_lengths_all.append(len(seq) - gap_start)

    if gap_lengths_all:
        all_gaps["min_gap"] = min(gap_lengths_all)
        all_gaps["max_gap"] = max(gap_lengths_all)
        all_gaps["mean_gap"] = sum(gap_lengths_all) / len(gap_lengths_all)

    total_gc = sum(
        str(rec.seq).upper().count("G") + str(rec.seq).upper().count("C")
        for rec in records
    )
    gc_percent = (total_gc / total_length * 100.0) if total_length > 0 else 0.0

    stats = {
        "num_sequences": len(records),
        "total_length": total_length,
        "min_length": min(lengths),
        "max_length": max(lengths),
        "mean_length": total_length / len(lengths) if lengths else 0.0,
        "n50": n50,
        "l50": l50,
        "gc_percent": round(gc_percent, 4),
        "n_count": all_gaps["n_count"],
        "n_percent": round(
            (all_gaps["n_count"] / total_length * 100.0) if total_length > 0 else 0.0, 4
        ),
        "gap_count": all_gaps["gap_count"],
        "min_gap_length": all_gaps["min_gap"],
        "max_gap_length": all_gaps["max_gap"],
        "mean_gap_length": round(all_gaps["mean_gap"], 2),
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
