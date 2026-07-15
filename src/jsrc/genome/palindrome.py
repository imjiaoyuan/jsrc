from __future__ import annotations

import json
import logging
from argparse import Namespace
from typing import Any

from Bio import SeqIO

logger = logging.getLogger(__name__)


def _find_palindromes(
    seq: str, min_length: int, max_length: int, max_gap: int
) -> list[dict[str, Any]]:
    seq = seq.upper()
    n = len(seq)
    palindromes = []
    complement = str.maketrans("ATGC", "TACG")

    for arm_len in range(min_length, max_length + 1):
        rc_map: dict[str, list[int]] = {}
        for i in range(n - arm_len + 1):
            kmer = seq[i : i + arm_len]
            if not set(kmer) <= {"A", "T", "G", "C"}:
                continue
            rc = kmer.translate(complement)[::-1]
            rc_map.setdefault(rc, []).append(i)

        seen: set[tuple[int, int]] = set()
        for i in range(n - arm_len + 1):
            kmer = seq[i : i + arm_len]
            if kmer not in rc_map:
                continue
            for j in rc_map[kmer]:
                gap = j - (i + arm_len)
                if 0 <= gap <= max_gap and (i, j) not in seen:
                    seen.add((i, j))
                    right_end = j + arm_len
                    palindromes.append(
                        {
                            "start": i,
                            "end": right_end,
                            "arm_length": arm_len,
                            "gap": gap,
                            "total_length": right_end - i,
                            "sequence": seq[i:right_end],
                        }
                    )

    return palindromes


def cmd(args: Namespace) -> None:
    results = []
    for rec in SeqIO.parse(args.fa, "fasta"):
        palindromes = _find_palindromes(
            str(rec.seq), args.min_arm, args.max_arm, args.max_gap
        )
        results.append(
            {"seq_id": rec.id, "length": len(rec.seq), "palindromes": palindromes}
        )

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    for item in results:
        logger.info(
            "seq_id\t%s\tlength\t%s\tpalindromes\t%d",
            item["seq_id"],
            item["length"],
            len(item["palindromes"]),
        )
        if item["palindromes"]:
            print(f"# {item['seq_id']}")
            print("start\tend\tarm_length\tgap\ttotal_length\tsequence")
            for pal in item["palindromes"][: args.top]:
                print(
                    f"{pal['start']}\t{pal['end']}\t{pal['arm_length']}\t{pal['gap']}\t{pal['total_length']}\t{pal['sequence']}"
                )


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "palindrome", help="Find palindromic sequences (inverted repeats)"
    )
    p.add_argument("-fa", required=True, help="Genome FASTA file")
    p.add_argument("--min-arm", type=int, default=6, help="Minimum arm length")
    p.add_argument("--max-arm", type=int, default=20, help="Maximum arm length")
    p.add_argument("--max-gap", type=int, default=10, help="Maximum gap between arms")
    p.add_argument(
        "--top", type=int, default=50, help="Show top N palindromes per sequence"
    )
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
