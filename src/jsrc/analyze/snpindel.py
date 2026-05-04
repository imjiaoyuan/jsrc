import json

from Bio import SeqIO
from Bio.Align import PairwiseAligner


def _pick(records, seq_id, index):
    if seq_id:
        for rec in records:
            if rec.id == seq_id or rec.id.split()[0] == seq_id:
                return rec
        raise ValueError(f"ID not found: {seq_id}")
    return records[index]


def _count_indel_events(a: str, b: str) -> int:
    in_gap = False
    events = 0
    for x, y in zip(a, b):
        gap = x == "-" or y == "-"
        if gap and not in_gap:
            events += 1
        in_gap = gap
    return events


def cmd(args):
    records = list(SeqIO.parse(args.fa, "fasta"))
    if len(records) < 2:
        raise SystemExit("Need at least two sequences in FASTA")
    r1 = _pick(records, args.id1, 0)
    r2 = _pick(records, args.id2, 1)
    s1 = str(r1.seq).upper().replace("U", "T")
    s2 = str(r2.seq).upper().replace("U", "T")
    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 1
    aligner.mismatch_score = -1
    aligner.open_gap_score = -3
    aligner.extend_gap_score = -1
    aln = aligner.align(s1, s2)[0]
    a1, a2 = str(aln[0]), str(aln[1])
    score = aln.score
    snp = 0
    indel_bases = 0
    match_bases = 0
    for x, y in zip(a1, a2):
        if x == "-" or y == "-":
            indel_bases += 1
        elif x == y:
            match_bases += 1
        else:
            snp += 1
    out = {
        "seq1": r1.id,
        "seq2": r2.id,
        "alignment_score": score,
        "aligned_length": len(a1),
        "match_bases": match_bases,
        "snp_count": snp,
        "indel_bases": indel_bases,
        "indel_events": _count_indel_events(a1, a2),
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return
    for k, v in out.items():
        print(f"{k}\t{v}")
