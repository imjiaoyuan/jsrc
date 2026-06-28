from __future__ import annotations

import json
import math
from argparse import Namespace
from typing import Any

from Bio import SeqIO

from jsrc.core import DataFormatError


def _shannon_entropy(seq: str) -> float:
    n = len(seq)
    if n == 0:
        return 0.0
    from collections import Counter

    counts = Counter(seq)
    return -sum((c / n) * math.log2(c / n) for c in counts.values() if c > 0)


def _linguistic_complexity(seq: str, max_k: int = 6) -> float:
    n = len(seq)
    if n == 0:
        return 0.0
    observed = sum(
        len({seq[i : i + k] for i in range(n - k + 1)})
        for k in range(1, min(max_k, n) + 1)
    )
    alphabet = len(set(seq))
    if alphabet <= 1:
        return 0.0
    possible = sum(min(alphabet**k, n - k + 1) for k in range(1, min(max_k, n) + 1))
    return observed / possible if possible > 0 else 0.0


def _dust_score(seq: str, window: int = 64) -> float:
    seq = seq.upper()
    n = len(seq)
    if n < 3:
        return 0.0
    scores = []
    for i in range(0, max(1, n - window + 1), window):
        sub = seq[i : i + window]
        from collections import Counter

        tri = Counter(sub[j : j + 3] for j in range(len(sub) - 2))
        s = sum(c * (c - 1) // 2 for c in tri.values())
        sub_len = len(sub) - 2
        scores.append(s / sub_len if sub_len > 0 else 0.0)
    return round(sum(scores) / len(scores), 4) if scores else 0.0


def cmd(args: Namespace) -> None:
    records = list(SeqIO.parse(args.fa, "fasta"))
    if not records:
        raise DataFormatError("No sequences found in FASTA")
    results = []
    for rec in records:
        seq = str(rec.seq).upper().replace("U", "T")
        clean = "".join(c for c in seq if c in "ACGTN")
        results.append(
            {
                "id": rec.id,
                "length": len(clean),
                "shannon_entropy": round(_shannon_entropy(clean), 6),
                "linguistic_complexity": round(_linguistic_complexity(clean), 6),
                "dust_score": _dust_score(clean),
            }
        )

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    print("id\tlength\tshannon_entropy\tlinguistic_complexity\tdust_score")
    for r in results:
        print(
            f"{r['id']}\t{r['length']}\t{r['shannon_entropy']}\t"
            f"{r['linguistic_complexity']}\t{r['dust_score']}"
        )


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("complexity", help="Sequence complexity metrics")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
