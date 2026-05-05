import importlib
from typing import Any

_SUBCOMMANDS: dict[str, tuple[str, str]] = {
    "gene": ("jsrc.plot.gene", "Plot gene structure diagram"),
    "exon": ("jsrc.plot.exon", "Plot exon structure diagram"),
    "chromosome": ("jsrc.plot.chromosome", "Plot chromosome map"),
    "domain": ("jsrc.plot.domain", "Plot protein domain architecture"),
    "cis": ("jsrc.plot.cis", "Plot cis-regulatory elements"),
    "heart": ("jsrc.plot.heart", "Plot heart curve"),
    "rose": ("jsrc.plot.rose", "Plot 3D rose model"),
    "dotplot": ("jsrc.plot.dotplot", "Sequence dotplot by exact k-mer matches"),
    "circoslite": ("jsrc.plot.circoslite", "Simple circular tracks for genome stats"),
}


def _register_stub_subcommands(subparsers: Any) -> None:
    for name, (_, help_text) in _SUBCOMMANDS.items():
        subparsers.add_parser(name, help=help_text)


def _register_selected_subcommand(subparsers: Any, selected: str) -> bool:
    module_path, _ = _SUBCOMMANDS.get(selected, ("", ""))
    if not module_path:
        return False
    mod = importlib.import_module(module_path)
    reg = getattr(mod, "register", None)
    if reg is None:
        raise AttributeError(f"{module_path}: missing register")
    reg(subparsers)
    return True


def register_subparser(
    subparsers: Any, selected_subcommand: str | None = None
) -> None:
    plot_parser = subparsers.add_parser("plot", help="Visualization")
    plot_sub = plot_parser.add_subparsers(dest="plot_cmd")
    plot_parser.set_defaults(_group_parser=plot_parser)
    if selected_subcommand and _register_selected_subcommand(plot_sub, selected_subcommand):
        return
    _register_stub_subcommands(plot_sub)
