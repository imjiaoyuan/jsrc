from Bio import SeqIO

from jsrc.plot.core import setup_matplotlib

plt = setup_matplotlib()


def _first_seq(path: str) -> str:
    rec = next(SeqIO.parse(path, "fasta"), None)
    if rec is None:
        raise ValueError(f"No sequence found in {path}")
    return str(rec.seq).upper().replace("U", "T")


def cmd(args):
    if args.k < 1:
        raise SystemExit("-k must be >= 1")
    s1 = _first_seq(args.fa1)
    s2 = _first_seq(args.fa2)
    if len(s1) < args.k or len(s2) < args.k:
        raise SystemExit("Sequence length must be >= k")

    index = {}
    for j in range(0, len(s2) - args.k + 1):
        kmer = s2[j : j + args.k]
        index.setdefault(kmer, []).append(j)

    xs = []
    ys = []
    for i in range(0, len(s1) - args.k + 1):
        kmer = s1[i : i + args.k]
        for j in index.get(kmer, []):
            xs.append(i)
            ys.append(j)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(xs, ys, s=1, alpha=0.6, color="black")
    ax.set_xlabel("Sequence 1 position")
    ax.set_ylabel("Sequence 2 position")
    ax.set_title(f"Dotplot (k={args.k}, matches={len(xs)})")
    plt.tight_layout()
    if args.o:
        plt.savefig(args.o, dpi=args.dpi, bbox_inches="tight")
        plt.close(fig)
        print(f"Dotplot saved to {args.o}")
        return
    plt.show()
