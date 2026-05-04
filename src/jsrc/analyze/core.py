def normalize_sequence(seq: str) -> str:
    cleaned = []
    for ch in seq.upper():
        if ch == "U":
            ch = "T"
        if ch in {"A", "C", "G", "T", "N"}:
            cleaned.append(ch)
    return "".join(cleaned)
