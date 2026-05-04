from jsrc.common.gff import parse_gff_attributes
from jsrc.plot.core import natural_sort_key, setup_matplotlib

plt = setup_matplotlib()


def _load_ids(path: str | None):
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def cmd(args):
    target_ids = _load_ids(args.ids)
    chr_lengths = {}
    gene_positions = []
    with open(args.gff, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("##sequence-region"):
                parts = line.strip().split()
                if len(parts) >= 4:
                    chr_lengths[parts[1]] = int(parts[3])
            elif not line.startswith("#"):
                parts = line.strip().split("\t")
                if len(parts) >= 9 and parts[2] == "gene":
                    chrom = parts[0]
                    start = int(parts[3])
                    end = int(parts[4])
                    attr = parse_gff_attributes(parts[8])
                    gene_id = attr.get("ID", "")
                    if target_ids is not None and gene_id not in target_ids:
                        continue
                    gene_positions.append({"chr": chrom, "start": start, "end": end, "id": gene_id})
                    if chrom not in chr_lengths:
                        chr_lengths[chrom] = max(chr_lengths.get(chrom, 0), end)

    if target_ids is not None and not gene_positions:
        raise SystemExit("No matching genes found for provided -ids list.")

    chr_sorted = sorted(chr_lengths.keys(), key=natural_sort_key)
    fig, ax = plt.subplots(figsize=(12, max(6, len(chr_sorted) * 0.5)))
    for i, chrom in enumerate(chr_sorted):
        y = len(chr_sorted) - i - 1
        chr_len = chr_lengths[chrom]
        ax.add_patch(plt.Rectangle((0, y - 0.2), chr_len, 0.4, facecolor="lightgray", edgecolor="black"))
        for gene in (g for g in gene_positions if g["chr"] == chrom):
            mid = (gene["start"] + gene["end"]) / 2
            ax.plot([mid, mid], [y - 0.15, y + 0.15], "r-", linewidth=0.5, alpha=0.5)
    ax.set_yticks(range(len(chr_sorted)))
    ax.set_yticklabels(chr_sorted[::-1])
    ax.set_xlabel("Position (bp)")
    ax.set_title("Chromosome Map")
    plt.tight_layout()
    plt.savefig(args.o, dpi=args.dpi, bbox_inches="tight")
    plt.close()
    print(f"Chromosome map saved to {args.o}")
