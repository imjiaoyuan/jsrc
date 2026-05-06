import importlib
from typing import Any

_SUBCOMMANDS: dict[str, tuple[str, str]] = {
    "build": ("jsrc.grn.build", "Build GRN viewer package"),
    "net2json": ("jsrc.grn.net2json", "Convert GRN edge table to grn.json"),
    "anno2json": ("jsrc.grn.anno2json", "Convert annotation table to annotation.json"),
    "serve": ("jsrc.grn.serve", "Start GRN viewer service"),
    "centrality": ("jsrc.grn.centrality", "Compute GRN centrality metrics"),
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


def register_subparser(subparsers: Any, selected_subcommand: str | None = None) -> None:
    grn_parser = subparsers.add_parser("grn", help="GRN conversion and local viewer")
    grn_sub = grn_parser.add_subparsers(dest="grn_cmd")
    grn_parser.set_defaults(_group_parser=grn_parser)
    if selected_subcommand and _register_selected_subcommand(
        grn_sub, selected_subcommand
    ):
        return
    _register_stub_subcommands(grn_sub)
