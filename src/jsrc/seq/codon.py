import json
from collections import Counter, defaultdict

from Bio import SeqIO

AA_TABLE = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}


def _iter_codons(seq: str):
    seq = seq.upper().replace("U", "T")
    for i in range(0, len(seq) - 2, 3):
        c = seq[i : i + 3]
        if len(c) == 3 and set(c) <= {"A", "C", "G", "T"}:
            yield c


def cmd(args):
    counts = Counter()
    aa_to_codons = defaultdict(list)
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
    for aa, codons in aa_to_codons.items():
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

    print(f"total_codons\t{total_codons:,}")
    print("codon\tcount\tfreq\trscu")
    for codon, count in counts.most_common(args.top):
        freq = count / total_codons if total_codons else 0.0
        print(f"{codon}\t{count}\t{freq:.6f}\t{rscu[codon]:.4f}")
