import json
import math
from collections import Counter

from Bio import SeqIO


def _kmer_counter(path: str, k: int) -> Counter:
    c = Counter()
    for rec in SeqIO.parse(path, "fasta"):
        seq = str(rec.seq).upper().replace("U", "T")
        for i in range(0, len(seq) - k + 1):
            kmer = seq[i : i + k]
            if set(kmer) <= {"A", "C", "G", "T"}:
                c[kmer] += 1
    return c


def _cosine_distance(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    dot = sum(a[k] * b[k] for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 1.0
    return 1.0 - (dot / (na * nb))


def cmd(args):
    if args.k < 1:
        raise SystemExit("-k must be >= 1")
    profiles = {fa: _kmer_counter(fa, args.k) for fa in args.fa}

    if len(args.fa) == 1:
        path = args.fa[0]
        total = sum(profiles[path].values())
        top = profiles[path].most_common(args.top)
        if args.json:
            print(json.dumps({"k": args.k, "file": path, "total_kmers": total, "top_kmers": top}, ensure_ascii=False, indent=2))
            return
        print(f"k\t{args.k}")
        print(f"file\t{path}")
        print(f"total_kmers\t{total:,}")
        print("kmer\tcount\tfreq")
        for kmer, count in top:
            freq = count / total if total else 0.0
            print(f"{kmer}\t{count}\t{freq:.6f}")
        return

    names = args.fa
    matrix = []
    for n1 in names:
        row = []
        for n2 in names:
            row.append(_cosine_distance(profiles[n1], profiles[n2]))
        matrix.append(row)

    if args.json:
        print(json.dumps({"k": args.k, "samples": names, "cosine_distance_matrix": matrix}, ensure_ascii=False, indent=2))
        return
    print(f"k\t{args.k}")
    print("sample\t" + "\t".join(names))
    for i, name in enumerate(names):
        vals = "\t".join(f"{v:.6f}" for v in matrix[i])
        print(f"{name}\t{vals}")
