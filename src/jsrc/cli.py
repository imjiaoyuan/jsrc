from __future__ import annotations

import argparse
import importlib
import inspect
import logging
import os
import sys

from jsrc import __version__
from jsrc.core import (
    ConfigurationError,
    DataFormatError,
    DependencyError,
    JsrcError,
    ResourceNotFoundError,
    ValidationError,
)


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(message)s", stream=sys.stderr, force=True
    )


MODULES = {
    "seq": "jsrc.seq",
    "genome": "jsrc.genome",
    "plot": "jsrc.plot",
    "analyze": "jsrc.analyze",
    "grn": "jsrc.grn",
    "vision": "jsrc.vision",
    "job": "jsrc.job",
}

MODULE_HELP = {
    "seq": "Sequence tools",
    "genome": "Genome-level analysis",
    "plot": "Visualization",
    "analyze": "Analysis workflows",
    "grn": "GRN tools",
    "vision": "Image analysis",
    "job": "Background jobs",
}


def _iter_enabled_modules() -> list[str]:
    only = [x.strip() for x in os.getenv("JSRC_MODULES", "").split(",") if x.strip()]
    disabled = {
        x.strip() for x in os.getenv("JSRC_DISABLE_MODULES", "").split(",") if x.strip()
    }
    names = only if only else list(MODULES.keys())
    result = [n for n in names if n in MODULES and n not in disabled]
    if sys.platform == "win32" and "job" in result:
        result.remove("job")
    return result


def _build_base_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jsrc", description="General-purpose bioinformatics and data toolkit"
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show traceback for module loading and runtime errors",
    )
    return parser


def _register_stub_modules(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    enabled_modules: list[str],
) -> None:
    for name in enabled_modules:
        subparsers.add_parser(name, help=MODULE_HELP.get(name, f"{name} module"))


def _register_one_module(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    module_name: str,
    *,
    selected_subcommand: str | None = None,
    debug: bool = False,
) -> bool:
    try:
        mod = importlib.import_module(MODULES[module_name])
    except ImportError:
        if debug:
            raise
        logging.exception("Error: failed to load module '%s'", module_name)
        return False
    reg = getattr(mod, "register_subparser", None)
    if reg is None:
        if debug:
            raise AttributeError("missing register_subparser")
        logging.error(
            "Error: failed to load module '%s': missing register_subparser", module_name
        )
        return False
    params = inspect.signature(reg).parameters
    if "selected_subcommand" in params:
        reg(subparsers, selected_subcommand=selected_subcommand)
    else:
        reg(subparsers)
    return True


def _probe_route(argv: list[str]) -> tuple[str | None, str | None]:
    probe = argparse.ArgumentParser(add_help=False)
    probe.add_argument("--verbose", action="store_true")
    probe.add_argument("--debug", action="store_true")
    probe.add_argument("-v", "--version", action="store_true")
    probe.add_argument("command", nargs="?")
    probe.add_argument("subcommand", nargs="?")
    args, _ = probe.parse_known_args(argv)
    return args.command, args.subcommand


def main() -> None:
    argv = sys.argv[1:]
    debug_mode = "--debug" in argv
    verbose = "--verbose" in argv or debug_mode
    setup_logging(verbose=verbose)
    enabled_modules = _iter_enabled_modules()
    if not enabled_modules:
        logging.error("no module loaded")
        sys.exit(2)

    requested_module, requested_subcommand = _probe_route(argv)
    if requested_module == "job" and sys.platform == "win32":
        logging.error(
            "Error: 'job' module is not supported on Windows. "
            "Background job management requires Unix commands (nohup, bash, ps, tail)."
        )
        sys.exit(2)
    parser = _build_base_parser()
    subparsers = parser.add_subparsers(dest="command", help="Available modules")
    if requested_module and requested_module in enabled_modules:
        if not _register_one_module(
            subparsers,
            requested_module,
            selected_subcommand=requested_subcommand,
            debug=debug_mode,
        ):
            sys.exit(2)
    else:
        _register_stub_modules(subparsers, enabled_modules)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    if hasattr(args, "func"):
        try:
            args.func(args)
        except SystemExit as exc:
            if args.debug:
                raise
            code = exc.code
            if code is None:
                return
            if isinstance(code, int):
                sys.exit(code)
            msg = str(code).strip()
            if not msg.startswith("Error:"):
                msg = f"Error: {msg}"
            logging.error(msg)
            sys.exit(2)
        except ValidationError as exc:
            if args.debug:
                raise
            logging.error("Error: Invalid input - %s", exc)
            sys.exit(2)
        except ResourceNotFoundError as exc:
            if args.debug:
                raise
            logging.error("Error: Resource not found - %s", exc)
            sys.exit(2)
        except DataFormatError as exc:
            if args.debug:
                raise
            logging.error("Error: Data format error - %s", exc)
            sys.exit(2)
        except DependencyError as exc:
            if args.debug:
                raise
            logging.error("Error: External dependency error - %s", exc)
            sys.exit(2)
        except ConfigurationError as exc:
            if args.debug:
                raise
            logging.error("Error: Configuration error - %s", exc)
            sys.exit(2)
        except PermissionError as exc:
            if args.debug:
                raise
            logging.error("Error: Permission denied - %s", exc)
            sys.exit(2)
        except ValueError as exc:
            if args.debug:
                raise
            logging.error("Error: Invalid value - %s", exc)
            sys.exit(2)
        except JsrcError as exc:
            if args.debug:
                raise
            logging.error("Error: %s", exc)
            sys.exit(2)
        except KeyboardInterrupt:
            logging.error("\nInterrupted by user")
            sys.exit(130)
        except Exception as exc:
            if args.debug:
                raise
            logging.error("Error: Unexpected error - %s", exc)
            sys.exit(2)
        return
    group_parser = getattr(args, "_group_parser", None)
    if group_parser is not None:
        group_parser.print_help()
    else:
        parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
