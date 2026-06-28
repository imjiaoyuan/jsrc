from __future__ import annotations

import json
import logging
from argparse import Namespace
from typing import Any

from Bio import SeqIO

logger = logging.getLogger(__name__)

GENETIC_CODE = {
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


def _calculate_kaks(seq1: str, seq2: str) -> dict[str, Any]:

    seq1 = seq1.upper().replace("U", "T")
    seq2 = seq2.upper().replace("U", "T")

    if len(seq1) != len(seq2) or len(seq1) % 3 != 0:
        raise ValueError("Sequences must be aligned and length must be multiple of 3")

    synonymous_sites = 0.0
    nonsynonymous_sites = 0.0
    synonymous_subs = 0
    nonsynonymous_subs = 0

    for i in range(0, len(seq1), 3):
        codon1 = seq1[i : i + 3]
        codon2 = seq2[i : i + 3]

        if len(codon1) != 3 or len(codon2) != 3:
            continue
        if not all(b in "ACGT" for b in codon1 + codon2):
            continue

        aa1 = GENETIC_CODE.get(codon1)
        aa2 = GENETIC_CODE.get(codon2)

        if aa1 is None or aa2 is None or aa1 == "*" or aa2 == "*":
            continue

        diffs = sum(c1 != c2 for c1, c2 in zip(codon1, codon2, strict=True))

        if diffs == 0:
            synonymous_sites += 1.0
            nonsynonymous_sites += 2.0
        elif diffs == 1:
            if aa1 == aa2:
                synonymous_subs += 1
                synonymous_sites += 1.0
                nonsynonymous_sites += 2.0
            else:
                nonsynonymous_subs += 1
                synonymous_sites += 1.0
                nonsynonymous_sites += 2.0
        else:
            synonymous_sites += 1.0
            nonsynonymous_sites += 2.0
            if aa1 != aa2:
                nonsynonymous_subs += diffs

    Ks = synonymous_subs / synonymous_sites if synonymous_sites > 0 else 0.0
    Ka = nonsynonymous_subs / nonsynonymous_sites if nonsynonymous_sites > 0 else 0.0

    if Ks > 0:
        omega = Ka / Ks
    else:
        omega = float("inf") if Ka > 0 else 0.0

    return {
        "Ka": Ka,
        "Ks": Ks,
        "omega": omega,
        "synonymous_subs": synonymous_subs,
        "nonsynonymous_subs": nonsynonymous_subs,
        "synonymous_sites": synonymous_sites,
        "nonsynonymous_sites": nonsynonymous_sites,
    }


def cmd(args: Namespace) -> None:
    sequences = []
    for rec in SeqIO.parse(args.fa, "fasta"):
        sequences.append((rec.id, str(rec.seq)))

    if len(sequences) != 2:
        raise ValueError("Exactly 2 sequences required for Ka/Ks calculation")

    id1, seq1 = sequences[0]
    id2, seq2 = sequences[1]

    result = _calculate_kaks(seq1, seq2)
    result["seq1"] = id1
    result["seq2"] = id2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    logger.info("seq1\t%s", id1)
    logger.info("seq2\t%s", id2)
    logger.info("Ka\t%.6f", result["Ka"])
    logger.info("Ks\t%.6f", result["Ks"])
    omega_str = f"{result['omega']:.6f}" if result["omega"] != float("inf") else "inf"
    logger.info("omega (Ka/Ks)\t%s", omega_str)
    logger.info("synonymous_subs\t%d", result["synonymous_subs"])
    logger.info("nonsynonymous_subs\t%d", result["nonsynonymous_subs"])
    logger.info("synonymous_sites\t%.1f", result["synonymous_sites"])
    logger.info("nonsynonymous_sites\t%.1f", result["nonsynonymous_sites"])


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "kaks", help="Calculate Ka/Ks ratio for two aligned CDS sequences"
    )
    p.add_argument(
        "-fa", required=True, help="Aligned CDS FASTA file (exactly 2 sequences)"
    )
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
