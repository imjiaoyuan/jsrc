import logging
from argparse import Namespace
from typing import Any

from jsrc.plot.core import (
    get_gene_structure,
    natural_sort_key,
    plot_gene_track,
    setup_matplotlib,
)

logger = logging.getLogger(__name__)
plt = setup_matplotlib()


def cmd(args: Namespace) -> None:
    with open(args.ids, encoding="utf-8") as f:
        gene_ids = [line.strip() for line in f if line.strip()]
    coords = get_gene_structure(args.gff, gene_ids, feature_types=["exon"])
    gene_ids_sorted = sorted(gene_ids, key=natural_sort_key)
    fig, ax = plt.subplots(figsize=(12, max(6, len(gene_ids_sorted) * 0.5)))
    plot_gene_track(
        ax,
        coords,
        gene_ids_sorted,
        rect_height=0.4,
        color="green",
        title="Exon Structure",
    )
    plt.tight_layout()
    plt.savefig(args.o, dpi=args.dpi, bbox_inches="tight")
    plt.close()
    logger.info("Exon structure plot saved to %s", args.o)


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("exon", help="Plot exon structure diagram")
    p.add_argument("-gff", required=True, help="GFF annotation file")
    p.add_argument("-ids", required=True, help="Gene ID list file")
    p.add_argument("-o", required=True, help="Output PNG file")
    p.add_argument("-dpi", type=int, default=300, help="DPI")
    p.set_defaults(func=cmd)
