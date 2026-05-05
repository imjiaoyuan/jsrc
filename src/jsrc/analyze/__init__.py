import importlib
from typing import Any

_SUBCOMMANDS: dict[str, tuple[str, str]] = {
    "phylo": ("jsrc.analyze.phylo", "Build phylogenetic trees"),
    "motif": ("jsrc.analyze.motif", "Motif discovery and reporting"),
    "qc": ("jsrc.analyze.qc", "Alignment/sequence QC"),
    "msa_consensus": ("jsrc.analyze.msa_consensus", "MSA consensus statistics"),
    "snpindel": ("jsrc.analyze.snpindel", "SNP/INDEL analysis from alignments"),
    "bootstrap_phylo": ("jsrc.analyze.bootstrap_phylo", "Bootstrap phylogeny support"),
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
    analyze_parser = subparsers.add_parser("analyze", help="Analysis tools")
    analyze_sub = analyze_parser.add_subparsers(dest="analyze_cmd")
    analyze_parser.set_defaults(_group_parser=analyze_parser)
    if selected_subcommand and _register_selected_subcommand(
        analyze_sub, selected_subcommand
    ):
        return
    _register_stub_subcommands(analyze_sub)
