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

# Build package
uv build

# Format / lint
uv run ruff check src/ tests/
uv run black src/ tests/
uv run mypy src/jsrc/           # Type checking (configured in pyproject.toml)

# Test
uv run pytest tests/
uv run pytest tests/test_specific_file.py  # Run single test file
uv run pytest tests/test_specific_file.py::test_function  # Run specific test
uv run pytest --cov=jsrc --cov-report=html  # With coverage HTML report
```

Note: There is no Makefile, tox.ini, or Dockerfile — all tooling is configured through `pyproject.toml`.

## Dependencies by module

Extras in `pyproject.toml`:

| Extra | Packages | Used by module |
|-------|----------|----------------|
| (core) | biopython, numpy | seq, analyze, plot, vision |
| plot | matplotlib | plot, vision |
| vision | opencv-python, matplotlib | vision |
| all | all of the above | — |
| dev | pytest, pytest-cov, black, ruff, mypy | — |

## CI/CD

- CI (`.github/workflows/ci.yml`): lint (ruff + black on Python 3.12) + test (pytest + build on Python 3.10, 3.11, 3.12, 3.13) on push/PR to main; runs on ubuntu-latest, macos-latest, windows-latest
- Publishing (`.github/workflows/publish.yml`): triggers on `v*` tags, uses PyPI trusted publishing (OIDC)

## Platform support

| Platform | Status | Notes |
|----------|--------|-------|
| Linux | Full support, CI tested | All modules including `job` |
| macOS | Supported, CI tested | All modules; `job` uses `ps` fallback instead of `/proc` |
| Windows | Supported (except `job`) | `job` module is disabled — requires Unix commands |

Configuration paths follow each platform's conventions:

| Platform | Config dir | Data dir |
|----------|-----------|----------|
| Linux | `$XDG_CONFIG_HOME/jsrc` / `~/.config/jsrc` | `$XDG_DATA_HOME/jsrc` / `~/.local/share/jsrc` |
| macOS | `~/Library/Preferences/jsrc` | `~/Library/Application Support/jsrc` |
| Windows | `%APPDATA%/jsrc` | `%LOCALAPPDATA%/jsrc` |

## Architecture

`jsrc` is a modular CLI toolkit organized as a namespace package under `src/jsrc/`.

### Module discovery / CLI

- Entry point: `jsrc.cli:main` (argparse-based)
- `cli.py` defines a `MODULES` dict mapping CLI command names to Python packages
- Two-phase parsing: `_probe_route()` does a lightweight pre-parse to detect the requested module and optional subcommand, enabling lazy loading of only the needed subcommand file rather than all 61 at once
- Each module's `__init__.py` must expose a `register_subparser(subparsers, selected_subcommand=None)` function — `selected_subcommand` is set when `_probe_route` detected one
- Modules are loaded lazily via `importlib.import_module`
- Environment variable control: `JSRC_MODULES` (whitelist) / `JSRC_DISABLE_MODULES` (blacklist) — comma-separated module names; `JSRC_JOBS_FILE` overrides the job history file path (default: `$XDG_DATA_HOME/jsrc/jobs.csv`)

### Module structure pattern

Every module follows this convention (subcommand counts as of v0.3.0):

| Module | Subcommands | Internal modules |
|--------|------------|-----------------|
| `seq` | 14 | `core.py` |
| `genome` | 17 | `core.py` |
| `plot` | 9 | `core.py` (bundles `sources/`) |
| `analyze` | 6 | `core.py` |
| `grn` | 5 | `core.py` (bundles `sources/`) |
| `vision` | 3 | `core.py` |
| `job` | 7 | `core.py`, `config.py`, `format.py`, `process.py` |

Each module follows this file layout:

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

- Two modules bundle static web assets (HTML/CSS/JS) via `[tool.setuptools.package-data]`: `jsrc.grn` (`sources/index.html`, `script.js`, `style.css`) and `jsrc.plot` (`sources/heart.html`, `rose.html`). After modifying these files, verify with `uv build`
- Each subcommand file should own its argparse options in `register(subparsers)` and execution logic in `cmd(args)`
- Argparse `set_defaults(_group_parser=...)` is used so that typing a parent command (e.g. `jsrc seq`) prints its subcommand help instead of falling through to the root parser. Each module-level parser sets this on itself: `seq_parser.set_defaults(_group_parser=seq_parser)`. When `cli.py` detects a module was invoked without a subcommand, it reads `_group_parser` from the namespace and calls `.print_help()` on it — this is the mechanism that gives per-module help rather than the root help
- Each module-level parser also sets `dest="{module}_cmd"` on its subparser (e.g., `dest="seq_cmd"`) — the dest value is available on `Namespace` for conditional logic but rarely used in practice
- Every module `__init__.py` exposes `register_subparser` as its public API — the CLI layer discovers it via `getattr(mod, "register_subparser", None)`; an explicit `__all__` is not required by the lazy-loading mechanism but should be added for new modules
- Version is derived at runtime from `importlib.metadata.version("jsrc")` — no hardcoded version string in source

### Central shared utilities (`src/jsrc/core.py`)

This is the primary shared module used across the codebase:

| Function/Class | Purpose |
|----------------|---------|
| `parse_gff_attributes(attr_string)` | Parse GFF/GTF attribute column into a dict (handles both `key=value` and `key value` formats) |
| `setup_matplotlib()` | Configure Agg backend for headless operation, returns `plt` |
| `open_text(path)` | Open a file as UTF-8 text, transparently handling `.gz` compression — prefer this over `open()` for all user-provided files |
| `load_fasta(path)` | Canonical FASTA loader: parse into list of SeqRecord, raise `DataFormatError` if empty — use this instead of raw `SeqIO.parse()` in subcommands |
| `nxx(lengths, pct)` | N50/N90/etc. calculation — the smallest contig length at which cumulative sum reaches `pct` of total |
| `progressbar` | Custom progress bar (context manager + `iter()` wrapper), writes to stderr, self-disables when stderr is not a TTY |

### Custom exception hierarchy (`src/jsrc/core.py`)

All exceptions inherit from `JsrcError`:

```
JsrcError                   # Base — caught as a general fallback
├── ValidationError         # Input validation failures
├── DataFormatError         # Invalid/unparseable data
├── ResourceNotFoundError   # Missing files, IDs, etc.
├── DependencyError         # Missing/failed external tools
└── ConfigurationError      # Invalid/incomplete configuration
```

These are caught by `cli.py` and formatted as `Error: <message>` to stderr. Use `raise ValidationError("…")` rather than `sys.exit(…)` inside subcommand `cmd()` functions.

**`FileNotFoundError` vs `ResourceNotFoundError`:** The codebase uses both for missing things:
- `FileNotFoundError` (Python builtin) — user-provided input files that don't exist on disk
- `ResourceNotFoundError` (custom) — runtime resources like job IDs, log files, database entries

**Note:** `FileNotFoundError` is not caught by a specific handler in `cli.py` — it falls through to the generic `Exception` handler producing `"Error: Unexpected error"`. Prefer `ResourceNotFoundError` for new code, or update `cli.py` if `FileNotFoundError` should get a dedicated handler.

### Module-specific shared utilities

- `src/jsrc/plot/core.py` — `natural_sort_key()`, `get_gene_structure()`, `plot_gene_track()` (re-exports GFF parser and matplotlib setup from `jsrc.core`)
- `src/jsrc/analyze/core.py` — `normalize_sequence()`, `pad_alignment()`
- `src/jsrc/grn/core.py` — `ensure_dir()`, `write_text()`, `write_json()`, `sync_assets()`
- `src/jsrc/job/core.py` — background job management utilities (re-exports from `config.py`, `format.py`, `process.py` — internal support modules not exposed as subcommands)
- `src/jsrc/genome/core.py` — `normalize_sequence()`, `AA_TABLE` (codon→amino acid), `iter_codons()`, `calculate_cai()`, `gc_content()`, `gc_skew()`, `at_skew()`

### Error handling conventions

- Subcommand `cmd()` functions should raise exceptions from the hierarchy above rather than calling `sys.exit()` directly
- `cli.py:main()` catches each exception type with a specific prefix: `ValidationError` → `"Error: Invalid input"`, `ResourceNotFoundError` → `"Error: Resource not found"`, `DataFormatError` → `"Error: Data format error"`, `DependencyError` → `"Error: External dependency error"`, `ConfigurationError` → `"Error: Configuration error"`, `PermissionError` → `"Error: Permission denied"`, `ValueError` → `"Error: Invalid value"`, generic `JsrcError` → `"Error: <msg>"`, bare `Exception` → `"Error: Unexpected error"`; `SystemExit` is reformatted if its message doesn't already start with `"Error:"`; `KeyboardInterrupt` → `"Interrupted by user"`
- `--debug` flag suppresses the catch-all and lets exceptions propagate with full traceback; also enables DEBUG-level logging (same as `--verbose` for logging purposes)
- `--verbose` sets logging to DEBUG level but keeps exception catching active — use it to see detailed log output without raw tracebacks
- Use `shutil.which()` to check for external tools and raise `DependencyError` if missing

### Code style conventions

- Use `from __future__ import annotations` in all files — enables PEP 604 (`X | Y`) and deferred annotation evaluation
- Use the `logging` module (configured by `cli.setup_logging()`), **not** `print()`, for output to stderr. `print()` is only acceptable for stdout data output (e.g., writing tables, JSON, or sequences the user may pipe elsewhere)
- Use `logger = logging.getLogger(__name__)` at module level in subcommand files — the CLI's `setup_logging()` configures the root logger with format and level; child loggers inherit this configuration
- Python 3.10+ compatibility required — features like `match`/`case` (3.10), `StrEnum` (3.11), and PEP 695 (3.12) are off-limits
- Ruff config: `line-length = 88`, selected rules `E, W, F, I, B, C4, UP`, ignores `E501`
- Mypy config: `check_untyped_defs = true`, `ignore_missing_imports = true`, disabled error codes: `no-any-return, type-var, assignment, operator, attr-defined`

### Subcommand pattern

```python
from argparse import Namespace
from typing import Any

def register(subparsers: Any) -> None:
    p = subparsers.add_parser("name", help="Short description")
    p.add_argument("-fa", "--fasta", required=True, help="Input FASTA file")
    p.add_argument("-o", "--output", required=True, help="Output file")
    p.set_defaults(func=cmd)

def cmd(args: Namespace) -> None:
    # implementation — raise JsrcError subclasses on failure, not sys.exit()
```

### Lazy-loading dispatch flow

`cli.py:main()` uses a two-branch dispatch after parsing:

```
args.func exists?  → call args.func(args)       # subcommand matched → run it
args.func missing? → check args._group_parser    # module typed without subcommand
                     → print module-level help   #   (e.g., "jsrc seq" shows seq subcommands)
                     → fallback: root help       #   (e.g., "jsrc" with no args)
```

This is why every module-level parser sets `_group_parser` on itself — it enables
per-module help when a user types `jsrc <module>` without a subcommand.

## Development Patterns

### Matplotlib configuration
For visualization modules (plot, vision), import from `jsrc.core` or `jsrc.plot.core` which already call `matplotlib.use('Agg')`. If writing new plotting code, use:
```python
from jsrc.core import setup_matplotlib
plt = setup_matplotlib()
```

### External dependencies

The `job` module requires Unix commands that are checked with `shutil.which()`:

| Command | Used by | Purpose |
|---------|---------|---------|
| `nohup` | `job submit` | Background job execution |
| shell (default: `bash`) | `job submit` | Job shell interpreter |
| `tail` | `job logs --follow` | Real-time log following |
| `ps` | `job top` | Process monitoring (RSS, CPU, status) |

The `job` module is **not supported on Windows** — the CLI automatically excludes the `job` command on Windows and shows an error if explicitly requested.

Other modules (seq, genome, plot, analyze, grn, vision) are pure Python and cross-platform.

### Common argument patterns
- `-fa` / `--fasta` — FASTA file input
- `-gff` / `--gff` — GFF/GTF annotation file  
- `-i` / `--input` — General input file
- `-o` / `--output` — Output file
- `-ids` / `--ids` — ID list file (one per line)
- `-t` / `--threads` — Thread count for parallel operations

## Test configuration
- `tests/conftest.py` adds `src/` to `sys.path` so tests can import `jsrc` directly
- Coverage config is in `pyproject.toml` (`[tool.coverage.*]`): source under `src/`, HTML + term-missing + XML reports
- Test files follow the convention `tests/test_<module>_<subcommand>.py` (e.g. `test_seq_extract.py`, `test_genome_stats.py`). Shared module-level tests use `tests/test_<module>_core.py`
- Some broader integration/CLI tests use descriptive names like `test_cli_error_behavior.py` and `test_cli_module_flows.py`

### Documentation

Bilingual docs in `docs/en/` and `docs/zh/` — one markdown file per module (`module-<name>.md`).
