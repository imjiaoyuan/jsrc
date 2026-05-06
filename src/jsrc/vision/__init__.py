import importlib
from typing import Any

_SUBCOMMANDS: dict[str, tuple[str, str]] = {
    "extract": ("jsrc.vision.extract", "Extract objects from images"),
    "efd": ("jsrc.vision.efd", "Elliptic Fourier descriptor analysis"),
    "traits": ("jsrc.vision.traits", "Measure morphology traits"),
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
    vision_parser = subparsers.add_parser(
        "vision", help="Image recognition and shape descriptors"
    )
    vision_sub = vision_parser.add_subparsers(dest="vision_cmd")
    vision_parser.set_defaults(_group_parser=vision_parser)
    if selected_subcommand and _register_selected_subcommand(
        vision_sub, selected_subcommand
    ):
        return
    _register_stub_subcommands(vision_sub)
