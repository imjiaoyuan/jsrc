import importlib
from typing import Any

_SUBCOMMANDS: dict[str, tuple[str, str]] = {
    "cpg": ("jsrc.genome.cpg", "Predict CpG islands"),
    "orf": ("jsrc.genome.orf", "Find open reading frames"),
    "promoter": ("jsrc.genome.promoter", "Extract promoter sequences"),
    "repeat": ("jsrc.genome.repeat", "Find simple tandem repeats (SSR/STR)"),
    "island": ("jsrc.genome.island", "Detect genomic islands by GC content deviation"),
    "palindrome": ("jsrc.genome.palindrome", "Find palindromic sequences (inverted repeats)"),
    "stats": ("jsrc.genome.stats", "Genome statistics (N50/L50, gaps, GC)"),
    "gc-skew": ("jsrc.genome.gc_skew", "Cumulative GC skew for replication origin"),
    "window": ("jsrc.genome.window", "Sliding-window GC and AT skew"),
    "codon": ("jsrc.genome.codon", "Codon usage and RSCU analysis"),
    "distance": ("jsrc.genome.distance", "Calculate pairwise genetic distances"),
    "kaks": ("jsrc.genome.kaks", "Calculate Ka/Ks ratio for two aligned CDS sequences"),
    "density": ("jsrc.genome.density", "Calculate gene/feature density along genome"),
    "motif-scan": ("jsrc.genome.motif_scan", "Scan for DNA motifs (supports IUPAC codes)"),
    "ani": ("jsrc.genome.ani", "Average Nucleotide Identity (k-mer based)"),
    "compare": ("jsrc.genome.compare", "Genome alignment and differences (requires edlib)"),
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
    genome_parser = subparsers.add_parser("genome", help="Genome-level analysis")
    genome_sub = genome_parser.add_subparsers(dest="genome_cmd")
    genome_parser.set_defaults(_group_parser=genome_parser)
    if selected_subcommand and _register_selected_subcommand(
        genome_sub, selected_subcommand
    ):
        return
    _register_stub_subcommands(genome_sub)
