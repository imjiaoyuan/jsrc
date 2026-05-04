import json

from Bio import SeqIO


def _pick_record(path: str, seq_id: str | None):
    if seq_id:
        for rec in SeqIO.parse(path, "fasta"):
            if rec.id == seq_id or rec.id.split()[0] == seq_id:
                return rec
        raise SystemExit(f"Sequence ID not found: {seq_id}")
    longest = None
    for rec in SeqIO.parse(path, "fasta"):
        if longest is None or len(rec.seq) > len(longest.seq):
            longest = rec
    if longest is None:
        raise SystemExit("No sequences found in FASTA")
    return longest


def _iter_windows(seq: str, w: int, s: int):
    seq = seq.upper().replace("U", "T")
    for start in range(0, max(1, len(seq) - w + 1), s):
        end = min(start + w, len(seq))
        sub = seq[start:end]
        a = sub.count("A")
        t = sub.count("T")
        g = sub.count("G")
        c = sub.count("C")
        gc = g + c
        at = a + t
        gc_pct = gc / len(sub) * 100.0 if sub else 0.0
        at_skew = (a - t) / at if at else 0.0
        gc_skew = (g - c) / gc if gc else 0.0
        yield {
            "start": start + 1,
            "end": end,
            "len": len(sub),
            "gc_percent": gc_pct,
            "at_skew": at_skew,
            "gc_skew": gc_skew,
        }
        if end >= len(seq):
            break


def cmd(args):
    if args.w < 1 or args.s < 1:
        raise SystemExit("-w and -s must be >= 1")
    rec = _pick_record(args.fa, args.id)
    window_count = 0
    windows_head = []
    head_limit = max(0, args.head)
    for row in _iter_windows(str(rec.seq), args.w, args.s):
        window_count += 1
        if len(windows_head) < head_limit:
            windows_head.append(row)
    payload = {
        "sequence_id": rec.id,
        "sequence_length": len(rec.seq),
        "window_size": args.w,
        "step_size": args.s,
        "window_count": window_count,
        "windows_head": windows_head,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(f"sequence_id\t{payload['sequence_id']}")
    print(f"sequence_length\t{payload['sequence_length']:,}")
    print(f"window_size\t{payload['window_size']}")
    print(f"step_size\t{payload['step_size']}")
    print(f"window_count\t{payload['window_count']:,}")
    print("start\tend\tlen\tgc_percent\tat_skew\tgc_skew")
    for row in payload["windows_head"]:
        print(
            f"{row['start']}\t{row['end']}\t{row['len']}\t"
            f"{row['gc_percent']:.4f}\t{row['at_skew']:.6f}\t{row['gc_skew']:.6f}"
        )
