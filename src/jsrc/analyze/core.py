from Bio.Align import MultipleSeqAlignment
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


def normalize_sequence(seq: str) -> str:
    cleaned = []
    for ch in seq.upper():
        if ch == "U":
            ch = "T"
        if ch in {"A", "C", "G", "T", "N"}:
            cleaned.append(ch)
    return "".join(cleaned)


def pad_alignment(records: list[SeqRecord]) -> MultipleSeqAlignment:
    max_len = max(len(r.seq) for r in records)
    aligned = []
    for r in records:
        seq = normalize_sequence(str(r.seq))
        if len(seq) < max_len:
            seq += "-" * (max_len - len(seq))
        aligned.append(SeqRecord(Seq(seq), id=r.id, description=""))
    return MultipleSeqAlignment(aligned)
