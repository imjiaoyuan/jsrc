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


def parse_gff_attributes(attr_string: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for item in attr_string.strip().strip(";").split(";"):
        if "=" in item:
            key, value = item.strip().split("=", 1)
            attrs[key] = value.strip('"')
        elif " " in item:
            parts = item.strip().split(None, 1)
            if len(parts) == 2:
                attrs[parts[0]] = parts[1].strip('"')
    return attrs
