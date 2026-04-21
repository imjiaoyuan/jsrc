import math

from Bio import SeqIO

from jsrc.plot.core import setup_matplotlib

plt = setup_matplotlib()


def _iter_windows(seq: str, w: int):
    seq = seq.upper()
    for start in range(0, len(seq), w):
        end = min(start + w, len(seq))
        sub = seq[start:end]
        gc = sub.count("G") + sub.count("C")
        yield (start, end, gc / len(sub) if sub else 0.0)


def cmd(args):
    if args.w < 1:
        raise SystemExit("-w must be >= 1")
    records = list(SeqIO.parse(args.fa, "fasta"))
    if not records:
        raise SystemExit("No sequences found")
    total = sum(len(r.seq) for r in records)
    if total == 0:
        raise SystemExit("Empty sequences found")

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"projection": "polar"})
    ax.set_theta_direction(-1)
    ax.set_theta_offset(math.pi / 2)
    ax.set_axis_off()

    start_bp = 0
    ring_bottom = 1.0
    ring_height = 0.15
    gc_bottom = 0.65
    gc_scale = 0.25

    for rec in records:
        seq = str(rec.seq)
        theta0 = 2 * math.pi * (start_bp / total)
        theta1 = 2 * math.pi * ((start_bp + len(seq)) / total)
        ax.bar(
            x=(theta0 + theta1) / 2,
            height=ring_height,
            width=(theta1 - theta0),
            bottom=ring_bottom,
            color="#D9D9D9",
            edgecolor="white",
            linewidth=0.5,
            align="center",
        )

        for wstart, wend, gc in _iter_windows(seq, args.w):
            abs_start = start_bp + wstart
            abs_end = start_bp + wend
            t0 = 2 * math.pi * (abs_start / total)
            t1 = 2 * math.pi * (abs_end / total)
            ax.bar(
                x=(t0 + t1) / 2,
                height=gc * gc_scale,
                width=t1 - t0,
                bottom=gc_bottom,
                color="#4682B4",
                alpha=0.9,
                edgecolor="none",
            )
        start_bp += len(seq)

    ax.set_title("CircosLite: chromosome ring + GC track", y=1.08)
    plt.tight_layout()
    if args.o:
        plt.savefig(args.o, dpi=args.dpi, bbox_inches="tight")
        plt.close(fig)
        print(f"CircosLite plot saved to {args.o}")
        return
    plt.show()
