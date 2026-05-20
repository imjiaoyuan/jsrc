import json
import logging
from argparse import Namespace
from typing import Any

from Bio import SeqIO

logger = logging.getLogger(__name__)


def _find_palindromes(seq: str, min_length: int, max_length: int, max_gap: int) -> list[dict[str, Any]]:
    seq = seq.upper()
    n = len(seq)
    palindromes = []
    complement = {"A": "T", "T": "A", "G": "C", "C": "G"}

    for i in range(n):
        for arm_len in range(min_length, max_length + 1):
            if i + arm_len > n:
                break
            left_arm = seq[i : i + arm_len]
            if not all(b in complement for b in left_arm):
                continue

            for gap in range(0, max_gap + 1):
                right_start = i + arm_len + gap
                right_end = right_start + arm_len
                if right_end > n:
                    break
                right_arm = seq[right_start:right_end]
                if not all(b in complement for b in right_arm):
                    continue

                expected_right = "".join(complement.get(b, "N") for b in reversed(left_arm))
                if right_arm == expected_right:
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
        palindromes = _find_palindromes(str(rec.seq), args.min_arm, args.max_arm, args.max_gap)
        results.append({"seq_id": rec.id, "length": len(rec.seq), "palindromes": palindromes})

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    for item in results:
        logger.info("seq_id\t%s\tlength\t%s\tpalindromes\t%d", item["seq_id"], item["length"], len(item["palindromes"]))
        if item["palindromes"]:
            print(f"# {item['seq_id']}")
            print("start\tend\tarm_length\tgap\ttotal_length\tsequence")
            for pal in item["palindromes"][: args.top]:
                print(
                    f"{pal['start']}\t{pal['end']}\t{pal['arm_length']}\t{pal['gap']}\t{pal['total_length']}\t{pal['sequence']}"
                )


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("palindrome", help="Find palindromic sequences (inverted repeats)")
    p.add_argument("-fa", required=True, help="Genome FASTA file")
    p.add_argument("--min-arm", type=int, default=6, help="Minimum arm length")
    p.add_argument("--max-arm", type=int, default=20, help="Maximum arm length")
    p.add_argument("--max-gap", type=int, default=10, help="Maximum gap between arms")
    p.add_argument("--top", type=int, default=50, help="Show top N palindromes per sequence")
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
