from __future__ import annotations

import json
from argparse import Namespace
from typing import Any, cast

from jsrc.core import load_fasta


def _find_repeats(
    seq: str, min_unit: int, max_unit: int, min_reps: int
) -> list[dict[str, Any]]:
    seq = seq.upper().replace("U", "T")
    n = len(seq)
    results = []
    visited: set[tuple[int, int]] = set()
    for unit_len in range(min_unit, max_unit + 1):
        i = 0
        while i <= n - unit_len * min_reps:
            unit = seq[i : i + unit_len]
            if len(set(unit)) == 1 and unit_len > 1:
                i += 1
                continue
            j = i + unit_len
            while j + unit_len <= n and seq[j : j + unit_len] == unit:
                j += unit_len
            reps = (j - i) // unit_len
            if reps >= min_reps:
                key = (i, j)
                if key not in visited:
                    visited.add(key)
                    results.append(
                        {
                            "start": i + 1,
                            "end": j,
                            "unit": unit,
                            "unit_len": unit_len,
                            "repeats": reps,
                            "total_len": j - i,
                        }
                    )
                i = j
            else:
                i += 1
    results = sorted(results, key=lambda x: cast(int, x.get("start", 0)))
    return results


def cmd(args: Namespace) -> None:
    records = load_fasta(args.fa)
    all_results = []
    for rec in records:
        repeats = _find_repeats(
            str(rec.seq), args.min_unit, args.max_unit, args.min_reps
        )
        for r in repeats:
            r["seq_id"] = rec.id
        all_results.extend(repeats)

    if args.json:
        print(json.dumps(all_results, ensure_ascii=False, indent=2))
        return
    print("seq_id\tstart\tend\tunit\tunit_len\trepeats\ttotal_len")
    for r in all_results:
        print(
            f"{r['seq_id']}\t{r['start']}\t{r['end']}\t{r['unit']}\t"
            f"{r['unit_len']}\t{r['repeats']}\t{r['total_len']}"
        )


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("repeat", help="Find simple tandem repeats (SSR/STR)")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument(
        "--min-unit",
        type=int,
        default=1,
        help="Minimum repeat unit length (default: 1)",
    )
    p.add_argument(
        "--max-unit",
        type=int,
        default=6,
        help="Maximum repeat unit length (default: 6)",
    )
    p.add_argument(
        "--min-reps", type=int, default=3, help="Minimum number of repeats (default: 3)"
    )
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
