import argparse
import importlib
import os
import sys

from jsrc import __version__

MODULES = {
    "seq": "jsrc.seq",
    "plot": "jsrc.plot",
    "analyze": "jsrc.analyze",
    "gs": "jsrc.gs",
    "grn": "jsrc.grn",
    "vision": "jsrc.vision",
    "text": "jsrc.text",
    "job": "jsrc.job",
}


def _iter_enabled_modules():
    only = [x.strip() for x in os.getenv("JSRC_MODULES", "").split(",") if x.strip()]
    disabled = {x.strip() for x in os.getenv("JSRC_DISABLE_MODULES", "").split(",") if x.strip()}
    names = only if only else list(MODULES.keys())
    return [n for n in names if n in MODULES and n not in disabled]


def _register_modules(subparsers):
    loaded = []
    errors = []
    for name in _iter_enabled_modules():
        try:
            mod = importlib.import_module(MODULES[name])
            reg = getattr(mod, "register_subparser", None)
            if reg is None:
                errors.append(f"{name}: missing register_subparser")
                continue
            reg(subparsers)
            loaded.append(name)
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    return loaded, errors


def main():
    parser = argparse.ArgumentParser(prog="jsrc", description="General-purpose bioinformatics and data toolkit")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", help="Available modules")

    loaded, errors = _register_modules(subparsers)
    if errors:
        print("Warning: some modules failed to load:", file=sys.stderr)
        for item in errors:
            print(f"  - {item}", file=sys.stderr)
    if not loaded:
        print("Error: no module loaded", file=sys.stderr)
        sys.exit(2)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    if hasattr(args, "func"):
        args.func(args)
        return
    group_parser = getattr(args, "_group_parser", None)
    if group_parser is not None:
        group_parser.print_help()
    else:
        parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
