import importlib
from typing import Any

_SUBCOMMANDS: dict[str, tuple[str, str]] = {
    "build": ("jsrc.gs.build", "Build genomic selection datasets"),
    "split": ("jsrc.gs.split", "Split GS datasets into folds"),
    "train": ("jsrc.gs.train", "Train and evaluate GS models"),
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
    gs_parser = subparsers.add_parser(
        "gs", help="Genomic selection dataset and model workflows"
    )
    gs_sub = gs_parser.add_subparsers(dest="gs_cmd")
    gs_parser.set_defaults(_group_parser=gs_parser)
    if selected_subcommand and _register_selected_subcommand(gs_sub, selected_subcommand):
        return
    _register_stub_subcommands(gs_sub)
