from Bio.Align import MultipleSeqAlignment
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

_NORM_TABLE = str.maketrans("U", "T", "".join(
    c for c in map(chr, range(256)) if c not in "ACGTN"
))


def normalize_sequence(seq: str) -> str:
    return seq.upper().translate(_NORM_TABLE)


def pad_alignment(records: list[SeqRecord]) -> MultipleSeqAlignment:
    max_len = max(len(r.seq) for r in records)
    aligned = []
    for r in records:
        seq = normalize_sequence(str(r.seq))
        if len(seq) < max_len:
            seq += "-" * (max_len - len(seq))
        aligned.append(SeqRecord(Seq(seq), id=r.id, description=""))
    return MultipleSeqAlignment(aligned)
