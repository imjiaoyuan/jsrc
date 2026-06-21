import math
from collections import Counter, defaultdict
from collections.abc import Iterator


def normalize_sequence(seq: str) -> str:
    return seq.upper().replace("U", "T")


AA_TABLE: dict[str, str] = {
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


def iter_codons(seq: str) -> Iterator[str]:
    seq = seq.upper().replace("U", "T")
    for i in range(0, len(seq) - 2, 3):
        c = seq[i : i + 3]
        if len(c) == 3 and set(c) <= {"A", "C", "G", "T"}:
            yield c


def make_aa_to_codons(
    codon_table: dict[str, str] | None = None,
) -> dict[str, list[str]]:
    if codon_table is None:
        codon_table = AA_TABLE
    result: dict[str, list[str]] = defaultdict(list)
    for codon, aa in codon_table.items():
        if aa != "*":
            result[aa].append(codon)
    return dict(result)


def calculate_cai(
    counts: Counter[str],
    ref_counts: Counter[str],
    aa_to_codons: dict[str, list[str]],
) -> float:
    w_values: dict[str, float] = {}
    for _aa, codons in aa_to_codons.items():
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


def gc_content(seq: str) -> float:
    seq = normalize_sequence(seq)
    g = seq.count("G")
    c = seq.count("C")
    total = len(seq)
    return (g + c) / total * 100.0 if total > 0 else 0.0


def gc_skew(seq: str) -> float:
    seq = normalize_sequence(seq)
    g = seq.count("G")
    c = seq.count("C")
    gc = g + c
    return (g - c) / gc if gc > 0 else 0.0


def at_skew(seq: str) -> float:
    seq = normalize_sequence(seq)
    a = seq.count("A")
    t = seq.count("T")
    at = a + t
    return (a - t) / at if at > 0 else 0.0
