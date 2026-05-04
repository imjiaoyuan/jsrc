from jsrc.plot.core import get_gene_structure, natural_sort_key, plot_gene_track, setup_matplotlib

plt = setup_matplotlib()


def cmd(args):
    with open(args.ids, "r", encoding="utf-8") as f:
        gene_ids = [line.strip() for line in f if line.strip()]
    coords = get_gene_structure(args.gff, gene_ids, feature_types=["exon"])
    gene_ids_sorted = sorted(gene_ids, key=natural_sort_key)
    fig, ax = plt.subplots(figsize=(12, max(6, len(gene_ids_sorted) * 0.5)))
    plot_gene_track(ax, coords, gene_ids_sorted, rect_height=0.4, color="green", title="Exon Structure")
    plt.tight_layout()
    plt.savefig(args.o, dpi=args.dpi, bbox_inches="tight")
    plt.close()
    print(f"Exon structure plot saved to {args.o}")
