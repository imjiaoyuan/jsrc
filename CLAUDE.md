# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dev dependencies
uv sync --extra dev --extra all

# Run all tests with coverage
uv run pytest tests/

# Run a single test file
uv run pytest tests/test_seq_extract.py

# Run a single test function
uv run pytest tests/test_seq_extract.py -k "test_extract_cds"

# Lint
uv run ruff check src tests

# Format
uv run black src/ tests/

# Type check
uv run mypy src/

# Build package
uv build
```

## Architecture

`jsrc` is a CLI bioinformatics toolkit with 7 modules. Entry point: `jsrc = "jsrc.cli:main"`. The package uses a `src/` layout with setuptools (`where = ["src"]`).

### How the CLI dispatches (`src/jsrc/cli.py`)

1. `_iter_enabled_modules()` filters the `MODULES` dict by `JSRC_MODULES` / `JSRC_DISABLE_MODULES` env vars and disables `job` on Windows.
2. `_probe_route(argv)` parses `command` and `subcommand` positional args to decide what to import.
3. If the requested module is known, `_register_one_module()` imports only that module's top-level package and calls its `register_subparser()`. If the subcommand is also known, only that subcommand module is imported; otherwise stub parsers are registered for all subcommands.
4. After parsing, `args.func(args)` dispatches to the subcommand's `cmd()`.
5. The `--debug` flag re-raises exceptions with full traceback; without it, exceptions are caught and formatted as `Error: <type> - <message>`.

### Module registration pattern (lazy loading)

Each module's `__init__.py` must contain:

- **`_SUBCOMMANDS`**: a dict mapping subcommand name → `("full.module.path", "help text")`. Example:
  ```python
  _SUBCOMMANDS: dict[str, tuple[str, str]] = {
      "extract": ("jsrc.seq.extract", "Extract sequences by IDs"),
      "qc": ("jsrc.seq.qc", "Sequence quality statistics"),
  }
  ```
- **`register_subparser(subparsers, selected_subcommand=None)`**: creates a subparser for the module, optionally loads only the selected subcommand, otherwise registers stubs for all entries in `_SUBCOMMANDS`.
- **`_register_stub_subcommands(subparsers)`**: registers a bare `add_parser(name, help=...)` for every subcommand (no args — just enough for `--help`).
- **`_register_selected_subcommand(subparsers, selected)`**: imports the specific subcommand module and calls its `register()`.
- **`parser.set_defaults(_group_parser=parser)`**: set on the module-level parser so the CLI can print module help when no subcommand is given.

Every subcommand module (e.g., `seq/extract.py`) exposes two functions:
- **`register(subparsers)`** — adds a subparser with arguments and **must** call `p.set_defaults(func=cmd)` to wire the command function.
- **`cmd(args: Namespace)`** — the actual command implementation.

### Module list

| module | package | notes |
|--------|---------|-------|
| `seq` | `jsrc.seq` | Sequence extraction, QC, k-mer, translation, alignment, digestion |
| `genome` | `jsrc.genome` | Genome stats, CpG islands, ORF finding, ANI, Ka/Ks, codon usage |
| `plot` | `jsrc.plot` | Gene/exon/chromosome/dotplot/circos diagrams (requires matplotlib) |
| `analyze` | `jsrc.analyze` | Phylogeny, MSA consensus, SNP/INDEL, motif discovery |
| `grn` | `jsrc.grn` | Gene regulatory network conversion, centrality, local viewer |
| `vision` | `jsrc.vision` | Image object extraction, EFD, morphology traits (requires opencv) |
| `job` | `jsrc.job` | Background job submit/monitor/log/kill (Linux/macOS only, disabled on Windows) |

### Exception hierarchy

All custom exceptions live in `src/jsrc/core.py` and are **sibling subclasses of `JsrcError`** (a flat family — each inherits directly from `JsrcError`, *not* a chain): `ValidationError`, `DataFormatError`, `ResourceNotFoundError`, `DependencyError`, `ConfigurationError`.

The CLI's `main()` catches each in its own `except` branch and prints a type-specific line to stderr, e.g. `Error: Invalid input - <message>` (ValidationError), `Error: Resource not found -` (ResourceNotFoundError), `Error: Data format error -` (DataFormatError), `Error: External dependency error -` (DependencyError), `Error: Configuration error -` (ConfigurationError). `ValueError` → `Error: Invalid value -` and `PermissionError` → `Error: Permission denied -` are also caught; any other `Exception` becomes `Error: Unexpected error - <message>`. Error exits use code `2` (130 for `KeyboardInterrupt`, 1 when no command is given). Subcommands should raise `JsrcError` subclasses (not `SystemExit`). The `--debug` flag re-raises so the full traceback prints.

### Key shared utilities (`src/jsrc/core.py`)

- `load_fasta(path)` — parse FASTA with Biopython, raises `DataFormatError` if empty
- `open_text(path)` — open text files, transparently handles `.gz` (gzip)
- `check_input(path, label=None)` — return `Path(path)` if it exists, else raise `ResourceNotFoundError`; use this for all input-file checks (not `FileNotFoundError`)
- `parse_gff_attributes(attr_string)` — parse GFF/GTF attribute column into dict (URL-unescapes GFF3 values like `%3B`)
- `setup_matplotlib()` — configure Agg backend for headless plotting; call this at the top of `cmd()` in any subcommand that uses matplotlib
- `progressbar` — context manager / iterable wrapper for stderr progress bars; use `with progressbar(total=N, desc="...") as pb:` or `for item in pb.iter(items):`
- `nxx(lengths, pct)` — compute N50/N90-style metrics

### Optional dependency pattern

Subcommands in `plot` and `vision` (and any that need optional extras) should:
1. Call `setup_matplotlib()` at the top of `cmd()` (for matplotlib).
2. Import optional libraries (e.g., `cv2`) inline inside `cmd()`.
3. Raise `DependencyError` with a clear install hint if the import fails:
   ```python
   try:
       import cv2
   except ImportError:
       raise DependencyError("opencv-python is required. Install with: pip install jsrc[vision]")
   ```

### Testing

Tests live in `tests/` and mirror the module structure (e.g., `tests/test_seq_extract.py` for `src/jsrc/seq/extract.py`). There are **no committed fixture files** — every test builds its inputs on the fly with pytest's `tmp_path` plus inline strings, so the data-definition lives at the top of each test function (don't look for a `test/` data directory; the `test/...` paths in the README are illustrative examples, not real files). `tests/conftest.py` adds `src/` to `sys.path`. Coverage is enforced on every run via `addopts = "--cov=jsrc ..."` in `pyproject.toml`, so `uv run pytest` always emits `htmlcov/`, `coverage.xml`, and `.coverage`.

### CI

`.github/workflows/ci.yml` — lint (ruff + black) on ubuntu; test matrix: [ubuntu, macos, windows] × [3.10, 3.11, 3.12, 3.13], plus `uv build` on every test job. `.github/workflows/publish.yml` — PyPI publish on `v*` tags via trusted publishing.

### Environment variable controls

- `JSRC_MODULES` — comma-separated list of modules to enable (whitelist)
- `JSRC_DISABLE_MODULES` — comma-separated list of modules to disable
- `JSRC_JOBS_FILE` — override path for job history file

### Module-specific conventions

- The `job` module uses `/proc` on Linux for RSS metrics; on macOS it falls back to `ps`. It is automatically disabled on Windows.
- `plot` and `vision` modules have optional dependencies (matplotlib, opencv-python). Subcommands that need them should call `setup_matplotlib()` or import opencv inline and raise `DependencyError` with a clear install hint if missing.
- `grn` and `plot` modules package static assets (HTML/CSS/JS in `sources/`) via `[tool.setuptools.package-data]` in `pyproject.toml`.
