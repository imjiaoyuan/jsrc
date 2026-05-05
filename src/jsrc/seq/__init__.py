import importlib
from typing import Any

_SUBCOMMANDS: dict[str, tuple[str, str]] = {
    "extract": ("jsrc.seq.extract", "Extract sequences by IDs"),
    "fetch": ("jsrc.seq.fetch", "Fetch sequences from remote databases"),
    "digest": ("jsrc.seq.digest", "Simulate restriction enzyme digestion"),
    "rename": ("jsrc.seq.rename", "Rename FASTA headers"),
    "translate": ("jsrc.seq.translate", "Translate CDS/DNA to protein"),
    "promoter": ("jsrc.seq.promoter", "Extract promoter sequences"),
    "qc": ("jsrc.seq.qc", "Sequence quality statistics"),
    "codon": ("jsrc.seq.codon", "Codon usage analysis"),
    "kmer": ("jsrc.seq.kmer", "Count k-mer frequencies"),
    "window": ("jsrc.seq.window", "Sliding-window sequence statistics"),
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
    seq_parser = subparsers.add_parser("seq", help="Sequence operations")
    seq_sub = seq_parser.add_subparsers(dest="seq_cmd")
    seq_parser.set_defaults(_group_parser=seq_parser)
    if selected_subcommand and _register_selected_subcommand(seq_sub, selected_subcommand):
        return
    _register_stub_subcommands(seq_sub)
