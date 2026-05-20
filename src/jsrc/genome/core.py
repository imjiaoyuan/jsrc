"""Shared utilities for genome module."""


def normalize_sequence(seq: str) -> str:
    """Normalize DNA/RNA sequence to uppercase DNA (U->T)."""
    return seq.upper().replace("U", "T")


def gc_content(seq: str) -> float:
    """Calculate GC content percentage."""
    seq = normalize_sequence(seq)
    g = seq.count("G")
    c = seq.count("C")
    total = len(seq)
    return (g + c) / total * 100.0 if total > 0 else 0.0


def gc_skew(seq: str) -> float:
    """Calculate GC skew: (G-C)/(G+C)."""
    seq = normalize_sequence(seq)
    g = seq.count("G")
    c = seq.count("C")
    gc = g + c
    return (g - c) / gc if gc > 0 else 0.0


def at_skew(seq: str) -> float:
    """Calculate AT skew: (A-T)/(A+T)."""
    seq = normalize_sequence(seq)
    a = seq.count("A")
    t = seq.count("T")
    at = a + t
    return (a - t) / at if at > 0 else 0.0
