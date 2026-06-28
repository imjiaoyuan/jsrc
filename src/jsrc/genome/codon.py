from __future__ import annotations

import json
import logging
from argparse import Namespace
from collections import Counter, defaultdict
from typing import Any

from Bio import SeqIO

from jsrc.genome.core import (
    AA_TABLE,
    calculate_cai,
    iter_codons,
    make_aa_to_codons,
)

logger = logging.getLogger(__name__)


def _calculate_enc(counts: Counter[str], aa_to_codons: dict[str, list[str]]) -> float:
    def homozygosity(codons: list[str]) -> float:
        total = sum(counts[c] for c in codons)
        if total == 0:
            return 0.0
        return sum((counts[c] / total) ** 2 for c in codons)

    families = defaultdict(list)
    for _aa, codons in aa_to_codons.items():
        k = len(codons)
        if k > 1:
            families[k].append(codons)

    f_values = {}
    for k, codon_groups in families.items():
        h_sum = sum(homozygosity(codons) for codons in codon_groups)
        n = len(codon_groups)
        if n > 0 and h_sum > 0:
            f_values[k] = n / h_sum

    enc = 2.0
    if 2 in f_values:
        enc += 9.0 / f_values[2]
    if 3 in f_values:
        enc += 1.0 / f_values[3]
    if 4 in f_values:
        enc += 5.0 / f_values[4]
    if 6 in f_values:
        enc += 3.0 / f_values[6]

    return enc


def cmd(args: Namespace) -> None:
    counts: Counter[str] = Counter()
    aa_to_codons = make_aa_to_codons(AA_TABLE)

    total_codons = 0
    for rec in SeqIO.parse(args.fa, "fasta"):
        for codon in iter_codons(str(rec.seq)):
            if AA_TABLE.get(codon) == "*":
                continue
            counts[codon] += 1
            total_codons += 1

    rscu = {}
    for codons in aa_to_codons.values():
        aa_total = sum(counts[c] for c in codons)
        if aa_total == 0:
            for c in codons:
                rscu[c] = 0.0
            continue
        expected = aa_total / len(codons)
        for c in codons:
            rscu[c] = counts[c] / expected if expected else 0.0

    cai_value = None
    if args.cai:
        ref_counts: Counter[str] = Counter()
        for rec in SeqIO.parse(args.cai, "fasta"):
            for codon in iter_codons(str(rec.seq)):
                if AA_TABLE.get(codon) != "*":
                    ref_counts[codon] += 1
        cai_value = calculate_cai(counts, ref_counts, aa_to_codons)

    enc_value = None
    if args.enc:
        enc_value = _calculate_enc(counts, aa_to_codons)

    if args.json:
        payload: dict[str, Any] = {
            "total_codons": total_codons,
            "top_codons": counts.most_common(args.top),
            "rscu": rscu,
        }
        if cai_value is not None:
            payload["cai"] = cai_value
        if enc_value is not None:
            payload["enc"] = enc_value
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    logger.info("total_codons\t%s", f"{total_codons:,}")
    if cai_value is not None:
        logger.info("CAI\t%.4f", cai_value)
    if enc_value is not None:
        logger.info("ENC\t%.4f", enc_value)

    print("codon\tcount\tfreq\trscu")
    for codon, count in counts.most_common(args.top):
        freq = count / total_codons if total_codons else 0.0
        print(f"{codon}\t{count}\t{freq:.6f}\t{rscu[codon]:.4f}")


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("codon", help="Codon usage and RSCU from CDS FASTA")
    p.add_argument("-fa", required=True, help="CDS FASTA file")
    p.add_argument("--top", type=int, default=20, help="Show top N codons")
    p.add_argument("--cai", help="Reference CDS FASTA for CAI calculation")
    p.add_argument("--enc", action="store_true", help="Calculate ENC")
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
