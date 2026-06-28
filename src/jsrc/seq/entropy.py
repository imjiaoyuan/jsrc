import json
import math
from argparse import Namespace
from collections import Counter
from typing import Any

from Bio import SeqIO

from jsrc.core import ValidationError

RowDict = dict[str, float | int | str]


def _col_entropy(col: list[str]) -> float:
    n = len(col)
    if n == 0:
        return 0.0
    counts = Counter(col)
    return -sum((c / n) * math.log2(c / n) for c in counts.values() if c > 0)


def _conservation(col: list[str]) -> float:
    if not col:
        return 0.0
    top = Counter(col).most_common(1)[0][1]
    return top / len(col)


def cmd(args: Namespace) -> None:
    records = list(SeqIO.parse(args.fa, "fasta"))
    if len(records) < 2:
        raise ValidationError("Need at least 2 sequences for entropy analysis")
    seqs = [str(r.seq).upper() for r in records]
    aln_len = max(len(s) for s in seqs)
    seqs = [s.ljust(aln_len, "-") for s in seqs]

    rows: list[RowDict] = []
    for i in range(aln_len):
        col = [s[i] for s in seqs if s[i] != "-"]
        if not col:
            continue
        rows.append(
            {
                "position": i + 1,
                "entropy": round(_col_entropy(col), 6),
                "conservation": round(_conservation(col), 6),
                "gap_fraction": round((aln_len - len(col)) / len(seqs), 6),
                "dominant": Counter(col).most_common(1)[0][0],
            }
        )

    mean_entropy = sum(float(r["entropy"]) for r in rows) / len(rows) if rows else 0.0
    mean_cons = sum(float(r["conservation"]) for r in rows) / len(rows) if rows else 0.0

    if args.json:
        print(
            json.dumps(
                {
                    "sequence_count": len(records),
                    "alignment_length": aln_len,
                    "mean_entropy": round(mean_entropy, 6),
                    "mean_conservation": round(mean_cons, 6),
                    "columns": rows,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    print(f"sequence_count\t{len(records)}")
    print(f"alignment_length\t{aln_len}")
    print(f"mean_entropy\t{mean_entropy:.6f}")
    print(f"mean_conservation\t{mean_cons:.6f}")
    if not args.summary:
        print("position\tentropy\tconservation\tgap_fraction\tdominant")
        for r in rows:
            print(
                f"{r['position']}\t{r['entropy']}\t{r['conservation']}\t"
                f"{r['gap_fraction']}\t{r['dominant']}"
            )


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("entropy", help="Per-column Shannon entropy of MSA")
    p.add_argument("-fa", required=True, help="Input aligned FASTA file")
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print summary stats only, skip per-column output",
    )
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
