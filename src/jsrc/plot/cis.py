from jsrc.plot.core import natural_sort_key, setup_matplotlib

plt = setup_matplotlib()


def cmd(args):
    elements = []
    with open(args.bed, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 4:
                elements.append({"chr": parts[0], "start": int(parts[1]), "end": int(parts[2]), "name": parts[3]})

    chromosomes = sorted(set(e["chr"] for e in elements), key=natural_sort_key)
    fig, ax = plt.subplots(figsize=(12, max(6, len(chromosomes) * 0.5)))
    for i, chrom in enumerate(chromosomes):
        y = len(chromosomes) - i - 1
        chr_elements = [e for e in elements if e["chr"] == chrom]
        if not chr_elements:
            continue
        max_pos = max(e["end"] for e in chr_elements)
        ax.plot([0, max_pos], [y, y], "k-", linewidth=1)
        for elem in chr_elements:
            mid = (elem["start"] + elem["end"]) / 2
            ax.plot([mid, mid], [y - 0.3, y + 0.3], "b-", linewidth=2)
            ax.text(mid, y + 0.35, elem["name"], ha="center", fontsize=7, rotation=45)
    ax.set_yticks(range(len(chromosomes)))
    ax.set_yticklabels(chromosomes[::-1])
    ax.set_xlabel("Position (bp)")
    ax.set_title("Cis-regulatory Elements")
    plt.tight_layout()
    plt.savefig(args.o, dpi=args.dpi, bbox_inches="tight")
    plt.close()
    print(f"Cis-element plot saved to {args.o}")

