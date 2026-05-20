import json
import logging
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

    if args.json:
        payload = {
            "total_codons": total_codons,
            "top_codons": counts.most_common(args.top),
            "rscu": rscu,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    logger.info("total_codons\t%s", f"{total_codons:,}")
    print("codon\tcount\tfreq\trscu")
    for codon, count in counts.most_common(args.top):
        freq = count / total_codons if total_codons else 0.0
        print(f"{codon}\t{count}\t{freq:.6f}\t{rscu[codon]:.4f}")


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("codon", help="Codon usage and RSCU from CDS FASTA")
    p.add_argument("-fa", required=True, help="CDS FASTA file")
    p.add_argument("--top", type=int, default=20, help="Show top N codons")
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
