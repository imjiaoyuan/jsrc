from jsrc.plot.core import get_gene_structure, natural_sort_key, setup_matplotlib

plt = setup_matplotlib()


def cmd(args):
    with open(args.ids, "r", encoding="utf-8") as f:
        gene_ids = [line.strip() for line in f if line.strip()]
    coords = get_gene_structure(args.gff, gene_ids, feature_types=["CDS"])
    gene_ids_sorted = sorted(gene_ids, key=natural_sort_key)
    fig, ax = plt.subplots(figsize=(12, max(6, len(gene_ids_sorted) * 0.5)))
    for i, gid in enumerate(gene_ids_sorted):
        y = len(gene_ids_sorted) - i - 1
        if gid not in coords or not coords[gid]:
            continue
        cds_list = sorted(coords[gid])
        gstart = min(c[0] for c in cds_list)
        gend = max(c[1] for c in cds_list)
        ax.plot([gstart, gend], [y, y], "k-", linewidth=1)
        for start, end in cds_list:
            ax.add_patch(plt.Rectangle((start, y - 0.15), end - start, 0.3, facecolor="steelblue", edgecolor="black"))
    ax.set_yticks(range(len(gene_ids_sorted)))
    ax.set_yticklabels(gene_ids_sorted[::-1])
    ax.set_xlabel("Genomic Position")
    ax.set_title("Gene Structure")
    plt.tight_layout()
    plt.savefig(args.o, dpi=args.dpi, bbox_inches="tight")
    plt.close()
    print(f"Gene structure plot saved to {args.o}")

