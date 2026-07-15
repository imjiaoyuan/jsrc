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

`jsrc` is a CLI bioinformatics toolkit with 7 modules. Entry point: `jsrc = "jsrc.cli:main"`.

### Module registration pattern (lazy loading)

Each module's `__init__.py` declares a `_SUBCOMMANDS` dict and a `register_subparser(subparsers, selected_subcommand=None)` function. The CLI probes argv to determine which module the user wants, then imports only that module's top-level package. If a specific subcommand is also known from argv, only that subcommand module is imported; otherwise stub parsers are registered for all subcommands.

Every subcommand module (e.g., `seq/extract.py`) exposes two functions:
- `register(subparsers)` — adds the subparser with arguments and sets `func=cmd`
- `cmd(args: Namespace)` — the actual command implementation

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

All custom exceptions live in `src/jsrc/core.py` and inherit from `JsrcError`:
`ValidationError` → `DataFormatError` → `ResourceNotFoundError` → `DependencyError` → `ConfigurationError`

The CLI's `main()` catches these in order and formats them as `Error: <type> - <message>`. Subcommands should raise these (not `SystemExit`).

### Key shared utilities (`src/jsrc/core.py`)

- `load_fasta(path)` — parse FASTA with Biopython, raises `DataFormatError` if empty
- `open_text(path)` — open text files, transparently handles `.gz` (gzip)
- `parse_gff_attributes(attr_string)` — parse GFF/GTF attribute column into dict
- `setup_matplotlib()` — configure Agg backend for headless plotting
- `progressbar` — context manager / iterable wrapper for stderr progress bars
- `nxx(lengths, pct)` — compute N50/N90-style metrics

### Testing

Tests live in `tests/` and mirror the module structure (e.g., `tests/test_seq_extract.py` for `src/jsrc/seq/extract.py`). `conftest.py` adds `src/` to `sys.path`. Tests use pytest; coverage is configured in `pyproject.toml`.

### CI

`.github/workflows/ci.yml` — lint (ruff + black) on ubuntu; test matrix: [ubuntu, macos, windows] × [3.10, 3.11, 3.12, 3.13]. `.github/workflows/publish.yml` — PyPI publish on `v*` tags via trusted publishing.

### Environment variable controls

- `JSRC_MODULES` — comma-separated list of modules to enable (whitelist)
- `JSRC_DISABLE_MODULES` — comma-separated list of modules to disable
- `JSRC_JOBS_FILE` — override path for job history file

### Module-specific conventions

- The `job` module uses `/proc` on Linux for RSS metrics; on macOS it falls back to `ps`. It is automatically disabled on Windows.
- `plot` and `vision` modules have optional dependencies (matplotlib, opencv-python). Subcommands that need them should call `setup_matplotlib()` or import opencv inline and raise `DependencyError` with a clear install hint if missing.
- `grn` and `plot` modules package static assets via `[tool.setuptools.package-data]` in `pyproject.toml`.
