# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Rules

- **Never commit code** — I must not directly create commits, push, or publish. The user handles all git operations, version bumps, and PyPI releases.
- **Only suggest changes** — I should present code changes and let the user decide when/how to commit them.

## Build & Run

```bash
# Setup (install all extras for development)
uv venv
uv sync --extra dev --extra all

# Minimal install (core only: biopython, numpy)
uv sync

# Install specific extras
uv sync --extra plot
uv sync --extra all
uv sync --extra vision

# Run CLI
uv run jsrc --help
uv run jsrc <module> <subcommand> [options]

# Install from local source
pip install -e .
pip install -e ".[plot,vision]"  # with extras

# Format / lint
uv run ruff check src/
uv run black src/

# Test
uv run pytest tests/
uv run pytest tests/test_specific_file.py  # Run single test file
uv run pytest tests/test_specific_file.py::test_function  # Run specific test
```

## Dependencies by module

Extras in `pyproject.toml`:

| Extra | Packages | Used by module |
|-------|----------|----------------|
| (core) | biopython, numpy | seq, analyze, plot, vision |
| plot | matplotlib, plotly | plot, vision |
| vision | opencv-python, matplotlib | vision |
| all | all of the above | — |
| dev | pytest, black, ruff | — |

## CI/CD

- CI (`.github/workflows/ci.yml`): lint + test + build on push/PR to main
- Publishing (`.github/workflows/publish.yml`): triggers on `v*` tags

## Architecture

`jsrc` is a modular CLI toolkit organized as a namespace package under `src/jsrc/`.

### Module discovery / CLI

- Entry point: `jsrc.cli:main` (argparse-based)
- `cli.py` defines a `MODULES` dict mapping CLI command names to Python packages
- Two-phase parsing: `_probe_route()` does a lightweight pre-parse to detect the requested module and optional subcommand, enabling lazy loading of only the needed subcommand file rather than all 56 at once
- Each module's `__init__.py` must expose a `register_subparser(subparsers, selected_subcommand=None)` function — `selected_subcommand` is set when `_probe_route` detected one
- Modules are loaded lazily via `importlib.import_module`
- Environment variable control: `JSRC_MODULES` (whitelist) / `JSRC_DISABLE_MODULES` (blacklist) — comma-separated module names

### Module structure pattern

Every module follows this convention:

```
src/jsrc/<module>/
├── __init__.py    # register_subparser() — creates module parser and aggregates subcommands
├── core.py        # (optional) shared utilities for the module
└── <subcmd>.py    # each subcommand file defines register(subparsers) + cmd(args)
```

Each `__init__.py` uses a `_SUBCOMMANDS` dict mapping subcommand name → `(dotted_module_path, help_text)`, plus two helpers:
- `_register_stub_subcommands(subparsers)` — adds all subcommands as help-only stubs (no `func`)
- `_register_selected_subcommand(subparsers, name)` — imports exactly one subcommand module via `importlib` and calls its `register()`; returns `False` if the name isn't found
- `register_subparser(subparsers, selected_subcommand=None)` — creates the module-level parser, sets `_group_parser`, then either registers one selected subcommand or all stubs

- Each subcommand file should own its argparse options in `register(subparsers)` and execution logic in `cmd(args)`
- Argparse `set_defaults(_group_parser=...)` is used so that typing a parent command (e.g. `jsrc seq`) prints its subcommand help instead of falling through to the root parser

### Central shared utilities (`src/jsrc/core.py`)

This is the primary shared module used across the codebase:

| Function/Class | Purpose |
|----------------|---------|
| `parse_gff_attributes(attr_string)` | Parse GFF/GTF attribute column into a dict (handles both `key=value` and `key value` formats) |
| `setup_matplotlib()` | Configure Agg backend for headless operation, returns `plt` |
| `open_text(path)` | Open a file as UTF-8 text, transparently handling `.gz` compression |
| `nxx(lengths, pct)` | N50/N90/etc. calculation — the smallest contig length at which cumulative sum reaches `pct` of total |
| `progressbar` | Custom progress bar (context manager + `iter()` wrapper), writes to stderr, respects `--verbose` |

### Custom exception hierarchy (`src/jsrc/core.py`)

All exceptions inherit from `JsrcError`:

```
JsrcError                   # Base — caught as a general fallback
├── ValidationError         # Input validation failures
├── DataFormatError         # Invalid/unparseable data
├── ResourceNotFoundError   # Missing files, IDs, etc.
├── DependencyError         # Missing/failed external tools (MAFFT, FastTree, MEME)
└── ConfigurationError      # Invalid/incomplete configuration
```

These are caught by `cli.py` and formatted as `Error: <message>` to stderr. Use `raise ValidationError("…")` rather than `sys.exit(…)` inside subcommand `cmd()` functions.

### Module-specific shared utilities

- `src/jsrc/plot/core.py` — `natural_sort_key()`, `get_gene_structure()`, `plot_gene_track()` (re-exports GFF parser and matplotlib setup from `jsrc.core`)
- `src/jsrc/analyze/core.py` — `normalize_sequence()`, `pad_alignment()`
- `src/jsrc/grn/core.py` — `ensure_dir()`, `write_text()`, `write_json()`
- `src/jsrc/seq/core.py` — re-exports `parse_gff_attributes` from `jsrc.core`
- `src/jsrc/job/core.py` — background job management utilities
- `src/jsrc/genome/core.py` — genome analysis shared helpers

### Error handling conventions

- Subcommand `cmd()` functions should raise exceptions from the hierarchy above rather than calling `sys.exit()` directly
- `cli.py:main()` catches all exceptions and formats them uniformly as `Error: <message>` to stderr
- `--debug` flag suppresses the catch-all and lets exceptions propagate with full traceback
- Use `shutil.which()` to check for external tools and raise `DependencyError` if missing

### Subcommand pattern

```python
def register(subparsers: Any) -> None:
    p = subparsers.add_parser("name", help="Short description")
    p.add_argument("-fa", "--fasta", required=True, help="Input FASTA file")
    p.add_argument("-o", "--output", required=True, help="Output file")
    p.set_defaults(func=cmd)

def cmd(args: Namespace) -> None:
    # implementation — raise JsrcError subclasses on failure, not sys.exit()
```

## Development Patterns

### Matplotlib configuration
For visualization modules (plot, vision), import from `jsrc.core` or `jsrc.plot.core` which already call `matplotlib.use('Agg')`. If writing new plotting code, use:
```python
from jsrc.core import setup_matplotlib
plt = setup_matplotlib()
```

### External dependencies
Some subcommands require external bioinformatics tools. Check with `shutil.which()` and raise `DependencyError` if missing:
- MAFFT (multiple sequence alignment)
- FastTree (maximum likelihood phylogenetic trees)
- MEME suite (motif discovery)

### Common argument patterns
- `-fa` / `--fasta` — FASTA file input
- `-gff` / `--gff` — GFF/GTF annotation file  
- `-i` / `--input` — General input file
- `-o` / `--output` — Output file
- `-ids` / `--ids` — ID list file (one per line)
- `-t` / `--threads` — Thread count for parallel operations

### Test configuration
- `tests/conftest.py` adds `src/` to `sys.path` so tests can import `jsrc` directly
- Coverage config is in `pyproject.toml` (`[tool.coverage.*]`): source under `src/`, HTML + term-missing + XML reports
- Test files are organized as `tests/test_<module>_<subcommand>.py` (with some variations)

### Documentation

Bilingual docs in `docs/en/` and `docs/zh/` — one markdown file per module (`module-<name>.md`).
