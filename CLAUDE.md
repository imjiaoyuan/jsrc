# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run

```bash
# Setup
uv venv
uv sync --extra dev

# Run CLI
uv run jsrc --help
uv run jsrc <module> <subcommand> [options]

# Install from local source
pip install -e .

# Format / lint
uv run ruff check src/
uv run black src/

# Tests (none yet)
# No test framework is set up — run individual modules manually with uv run
```

## CI/CD

- Publishing: GitHub Actions (`.github/workflows/publish.yml`) triggers on `v*` tags
- Builds via `uv build`, publishes to PyPI with trusted publishing (OIDC)

## Architecture

`jsrc` is a modular CLI toolkit organized as a namespace package under `src/jsrc/`.

### Module discovery / CLI

- Entry point: `jsrc.cli:main` (argparse-based)
- `cli.py` defines a `MODULES` dict mapping CLI command names to Python packages
- Each module's `__init__.py` must expose a `register_subparser(subparsers)` function
- Modules are loaded lazily (via `importlib.import_module`) at CLI startup
- Environment variable control: `JSRC_MODULES` (whitelist) / `JSRC_DISABLE_MODULES` (blacklist) — comma-separated module names

### Module structure pattern

Every module follows this convention:

```
src/jsrc/<module>/
├── __init__.py    # register_subparser() — argparse setup + dispatch
├── core.py        # (optional) shared utilities for the module
└── <subcmd>.py    # each subcommand in its own file, exports a cmd(args) function
```

- `register_subparser()` defines subcommands via `add_subparsers` and wires them to dispatch functions
- Dispatch uses either `_dispatch("jsrc.module.file")` (calls `module.cmd(args)`) or `_dispatch("jsrc.module.file", "func_name")` (calls `module.func_name(args)`)
- Each subcommand file exposes a `cmd(args)` function (or a named function for modules like `job` which uses `cmd_submit`, `cmd_ls`, etc.)
- Argparse `set_defaults(_group_parser=...)` is used so that typing a parent command (e.g. `jsrc seq`) prints its subcommand help instead of falling through to the root parser

### Modules

| Module    | Purpose | Key dependencies |
|-----------|---------|-----------------|
| `seq`     | Sequence ops (extract, rename, translate, promoter, qc, codon, kmer, window) | Biopython, numpy |
| `plot`    | Visualization (gene, exon, chromosome, domain, cis, heart, rose, dotplot, circoslite) | matplotlib, numpy |
| `analyze` | Analysis (phylo, motif, qc, msa_consensus, snpindel, bootstrap_phylo) | numpy, scikit-learn |
| `gs`      | Genomic selection dataset/model workflows (build, split, train) | pandas, pandas-plink, scikit-learn |
| `grn`     | Gene regulatory network conversion, viewer, centrality | — |
| `vision`  | Image processing (extract, efd, traits) | opencv-python, numpy |
| `text`    | Text processing (wc, dedup, grep, cut, replace) | — |
| `job`     | Background job submission, monitoring, logs | — |

### Shared utilities

- `src/jsrc/seq/core.py` — `parse_gff_attributes()` for GFF attribute parsing
- `src/jsrc/plot/core.py` — `setup_matplotlib()` (sets Agg backend), `parse_gff_attributes()`, `natural_sort_key()`, `get_gene_structure()`
- `src/jsrc/grn/core.py` — `ensure_dir()`, `write_text()`, `write_json()` for file I/O
- `src/jsrc/analyze/core.py` — `normalize_sequence()` for DNA/RNA normalization

### Documentation

Bilingual docs in `docs/en/` and `docs/zh/` — one markdown file per module (`module-<name>.md`).
