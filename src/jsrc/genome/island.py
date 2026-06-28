from __future__ import annotations

import json
import logging
from argparse import Namespace
from typing import Any

from Bio import SeqIO

logger = logging.getLogger(__name__)


def _detect_islands(
    seq: str, window: int, step: int, gc_threshold: float
) -> list[dict[str, Any]]:
    seq = seq.upper()
    n = len(seq)
    islands = []
    in_island = False
    island_start = 0

    for i in range(0, max(1, n - window + 1), step):
        sub = seq[i : i + window]
        gc_count = sub.count("G") + sub.count("C")
        at_count = sub.count("A") + sub.count("T")
        total = gc_count + at_count
        gc_content = gc_count / total if total > 0 else 0.0

        if gc_content >= gc_threshold:
            if not in_island:
                island_start = i
                in_island = True
        else:
            if in_island:
                islands.append(
                    {"start": island_start, "end": i, "length": i - island_start}
                )
                in_island = False

    if in_island:
        islands.append({"start": island_start, "end": n, "length": n - island_start})

    return islands


def cmd(args: Namespace) -> None:
    results = []
    for rec in SeqIO.parse(args.fa, "fasta"):
        islands = _detect_islands(
            str(rec.seq), args.window, args.step, args.gc_threshold
        )
        if args.min_length:
            islands = [isl for isl in islands if isl["length"] >= args.min_length]
        results.append({"seq_id": rec.id, "length": len(rec.seq), "islands": islands})

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    for item in results:
        logger.info(
            "seq_id\t%s\tlength\t%s\tislands\t%d",
            item["seq_id"],
            item["length"],
            len(item["islands"]),
        )
        if item["islands"]:
            print(f"# {item['seq_id']}")
            print("start\tend\tlength")
            for isl in item["islands"]:
                print(f"{isl['start']}\t{isl['end']}\t{isl['length']}")


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "island", help="Detect genomic islands by GC content deviation"
    )
    p.add_argument("-fa", required=True, help="Genome FASTA file")
    p.add_argument("--window", type=int, default=5000, help="Window size")
    p.add_argument("--step", type=int, default=1000, help="Step size")
    p.add_argument(
        "--gc-threshold", type=float, default=0.55, help="GC content threshold"
    )
    p.add_argument("--min-length", type=int, help="Minimum island length")
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
