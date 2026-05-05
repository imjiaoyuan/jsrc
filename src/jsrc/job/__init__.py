import importlib
from typing import Any

_SUBCOMMANDS: dict[str, tuple[str, str]] = {
    "submit": ("jsrc.job.submit", "Submit a background job"),
    "ls": ("jsrc.job.ls", "List jobs"),
    "show": ("jsrc.job.show", "Show one job"),
    "logs": ("jsrc.job.logs", "Show job logs"),
    "kill": ("jsrc.job.kill", "Terminate a running job"),
    "history": ("jsrc.job.history", "Show job history"),
    "gc": ("jsrc.job.gc", "Garbage-collect old job artifacts"),
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
    job_parser = subparsers.add_parser("job", help="Track and manage background jobs")
    job_sub = job_parser.add_subparsers(dest="job_cmd")
    job_parser.set_defaults(_group_parser=job_parser)
    if selected_subcommand and _register_selected_subcommand(job_sub, selected_subcommand):
        return
    _register_stub_subcommands(job_sub)
