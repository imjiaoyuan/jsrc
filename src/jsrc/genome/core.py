def normalize_sequence(seq: str) -> str:
    return seq.upper().replace("U", "T")


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


from jsrc.core import parse_gff_attributes
