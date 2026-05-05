from typing import Any

from jsrc.plot import (
    chromosome,
    circoslite,
    cis,
    domain,
    dotplot,
    exon,
    gene,
    heart,
    rose,
)


def register_subparser(subparsers: Any) -> None:
    plot_parser = subparsers.add_parser("plot", help="Visualization")
    plot_sub = plot_parser.add_subparsers(dest="plot_cmd")
    plot_parser.set_defaults(_group_parser=plot_parser)

    gene.register(plot_sub)
    exon.register(plot_sub)
    chromosome.register(plot_sub)
    domain.register(plot_sub)
    cis.register(plot_sub)
    heart.register(plot_sub)
    rose.register(plot_sub)
    dotplot.register(plot_sub)
    circoslite.register(plot_sub)
