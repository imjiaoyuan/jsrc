import json
from collections import Counter

from Bio import SeqIO


def _pad(records):
    max_len = max(len(r.seq) for r in records)
    padded = []
    for r in records:
        seq = str(r.seq).upper().replace("U", "T")
        if len(seq) < max_len:
            seq += "-" * (max_len - len(seq))
        padded.append(seq)
    return padded


def cmd(args):
    records = list(SeqIO.parse(args.fa, "fasta"))
    if len(records) < 2:
        raise SystemExit("Need at least two sequences")
    lengths = [len(r.seq) for r in records]
    min_len, max_len = min(lengths), max(lengths)
    if max_len > min_len * 1.2:
        print(f"Warning: Sequence lengths differ significantly (min={min_len}, max_len={max_len}). "
              f"Input may not be pre-aligned; shorter sequences will be padded with gaps.")
    seqs = _pad(records)
    consensus_chars = []
    conservation = []
    for i in range(len(seqs[0])):
        col = [s[i] for s in seqs if s[i] != "-"]
        if not col:
            consensus_chars.append("N")
            conservation.append(0.0)
            continue
        cnt = Counter(col)
        base, c = cnt.most_common(1)[0]
        consensus_chars.append(base)
        conservation.append(c / len(col))
    consensus = "".join(consensus_chars)
    avg_cons = sum(conservation) / len(conservation) if conservation else 0.0
    payload = {
        "sequence_count": len(records),
        "alignment_length": len(seqs[0]),
        "consensus": consensus,
        "mean_conservation": avg_cons,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(f"sequence_count\t{payload['sequence_count']}")
    print(f"alignment_length\t{payload['alignment_length']}")
    print(f"mean_conservation\t{payload['mean_conservation']:.6f}")
    print(f"consensus\t{payload['consensus']}")
