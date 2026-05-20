import json
import logging
import math
from argparse import Namespace
from collections import Counter, defaultdict
from collections.abc import Iterator
from typing import Any

from Bio import SeqIO

logger = logging.getLogger(__name__)

AA_TABLE = {
    "TTT": "F",
    "TTC": "F",
    "TTA": "L",
    "TTG": "L",
    "CTT": "L",
    "CTC": "L",
    "CTA": "L",
    "CTG": "L",
    "ATT": "I",
    "ATC": "I",
    "ATA": "I",
    "ATG": "M",
    "GTT": "V",
    "GTC": "V",
    "GTA": "V",
    "GTG": "V",
    "TCT": "S",
    "TCC": "S",
    "TCA": "S",
    "TCG": "S",
    "CCT": "P",
    "CCC": "P",
    "CCA": "P",
    "CCG": "P",
    "ACT": "T",
    "ACC": "T",
    "ACA": "T",
    "ACG": "T",
    "GCT": "A",
    "GCC": "A",
    "GCA": "A",
    "GCG": "A",
    "TAT": "Y",
    "TAC": "Y",
    "TAA": "*",
    "TAG": "*",
    "CAT": "H",
    "CAC": "H",
    "CAA": "Q",
    "CAG": "Q",
    "AAT": "N",
    "AAC": "N",
    "AAA": "K",
    "AAG": "K",
    "GAT": "D",
    "GAC": "D",
    "GAA": "E",
    "GAG": "E",
    "TGT": "C",
    "TGC": "C",
    "TGA": "*",
    "TGG": "W",
    "CGT": "R",
    "CGC": "R",
    "CGA": "R",
    "CGG": "R",
    "AGT": "S",
    "AGC": "S",
    "AGA": "R",
    "AGG": "R",
    "GGT": "G",
    "GGC": "G",
    "GGA": "G",
    "GGG": "G",
}


def _iter_codons(seq: str) -> Iterator[str]:
    seq = seq.upper().replace("U", "T")
    for i in range(0, len(seq) - 2, 3):
        c = seq[i : i + 3]
        if len(c) == 3 and set(c) <= {"A", "C", "G", "T"}:
            yield c


def _calculate_cai(counts: Counter[str], ref_counts: Counter[str], aa_to_codons: dict[str, list[str]]) -> float:
    w_values = {}
    for aa, codons in aa_to_codons.items():
        max_count = max((ref_counts[c] for c in codons), default=0)
        if max_count == 0:
            for c in codons:
                w_values[c] = 1.0
        else:
            for c in codons:
                w_values[c] = ref_counts[c] / max_count

    log_sum = 0.0
    total = 0
    for codon, count in counts.items():
        if codon in w_values and count > 0:
            log_sum += count * math.log(w_values[codon]) if w_values[codon] > 0 else 0
            total += count

    return math.exp(log_sum / total) if total > 0 else 0.0


def _calculate_enc(counts: Counter[str], aa_to_codons: dict[str, list[str]]) -> float:
    def homozygosity(codons: list[str]) -> float:
        total = sum(counts[c] for c in codons)
        if total == 0:
            return 0.0
        return sum((counts[c] / total) ** 2 for c in codons)

    families = defaultdict(list)
    for aa, codons in aa_to_codons.items():
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
    aa_to_codons: dict[str, list[str]] = defaultdict(list)
    for codon, aa in AA_TABLE.items():
        if aa != "*":
            aa_to_codons[aa].append(codon)

    total_codons = 0
    for rec in SeqIO.parse(args.fa, "fasta"):
        for codon in _iter_codons(str(rec.seq)):
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
            for codon in _iter_codons(str(rec.seq)):
                if AA_TABLE.get(codon) != "*":
                    ref_counts[codon] += 1
        cai_value = _calculate_cai(counts, ref_counts, aa_to_codons)

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
