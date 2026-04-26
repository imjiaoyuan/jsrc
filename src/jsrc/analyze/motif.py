import collections
from pathlib import Path

from Bio import SeqIO
from jsrc.analyze.core import normalize_sequence


def _kmer_counts(seqs: list[str], k: int) -> collections.Counter:
    c = collections.Counter()
    for seq in seqs:
        seq = normalize_sequence(seq)
        if len(seq) < k:
            continue
        for i in range(0, len(seq) - k + 1):
            c[seq[i : i + k]] += 1
    return c


def cmd(args):
    output_dir = Path(args.o)
    output_dir.mkdir(parents=True, exist_ok=True)
    seqs = [str(rec.seq) for rec in SeqIO.parse(args.fa, "fasta")]
    combined = collections.Counter()
    for k in range(args.minw, args.maxw + 1):
        combined.update(_kmer_counts(seqs, k))
    top = combined.most_common(args.nmotifs)
    out_tsv = output_dir / "motifs.tsv"
    with open(out_tsv, "w", encoding="utf-8") as f:
        f.write("motif\tcount\tlength\n")
        for motif, count in top:
            f.write(f"{motif}\t{count}\t{len(motif)}\n")
    print(f"Motif analysis complete. Results in {out_tsv}")
