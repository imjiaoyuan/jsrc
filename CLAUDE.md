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
- Each module's `__init__.py` must expose a `register_subparser(subparsers)` function
- Modules are loaded lazily (via `importlib.import_module`) at CLI startup
- Environment variable control: `JSRC_MODULES` (whitelist) / `JSRC_DISABLE_MODULES` (blacklist) — comma-separated module names

### Module structure pattern

Every module follows this convention:

```
src/jsrc/<module>/
├── __init__.py    # register_subparser() — creates module parser and aggregates subcommands
├── core.py        # (optional) shared utilities for the module
└── <subcmd>.py    # each subcommand file defines register(subparsers) + cmd(args)
```

- `register_subparser()` should only create the module-level parser and call each subcommand file's `register()`
- Each subcommand file should own its argparse options in `register(subparsers)` and execution logic in `cmd(args)`
- Argparse `set_defaults(_group_parser=...)` is used so that typing a parent command (e.g. `jsrc seq`) prints its subcommand help instead of falling through to the root parser

### Shared utilities

- `src/jsrc/seq/core.py` — `parse_gff_attributes()` for GFF attribute parsing
- `src/jsrc/plot/core.py` — `setup_matplotlib()` (sets Agg backend), `parse_gff_attributes()`, `natural_sort_key()`, `get_gene_structure()`
- `src/jsrc/grn/core.py` — `ensure_dir()`, `write_text()`, `write_json()` for file I/O
- `src/jsrc/analyze/core.py` — `normalize_sequence()` for DNA/RNA normalization

### Documentation

Bilingual docs in `docs/en/` and `docs/zh/` — one markdown file per module (`module-<name>.md`).
