# Stability Policy

jsrc follows Semantic Versioning.

## Pre-1.0 (0.x)

No stability guarantees. Anything may change between releases:
CLI flags, subcommand names, output format, default values.

## Post-1.0

The following are stable and only change with a MAJOR version bump:

- CLI structure: `jsrc <module> <subcommand> [options]`
- Documented long flags (e.g. --input, --output)
- Tabular output on stdout, JSON output where documented
- Error messages prefixed with "Error: " on stderr
- Exit codes: 0 (success), 1 (usage error), 2 (runtime error)
- Documented input formats (FASTA, GFF, CSV, TSV, etc.)

Deprecation process:
1. Marked deprecated in a MINOR release with a stderr notice
2. Removed in the next MAJOR release

Always exempt (may change anytime):
help text, internal flags, non-error diagnostics, performance,
experimental modules, --verbose / --debug output.

## Module Maturity

Each module has a maturity level in its docs:

- Stable — all post-1.0 guarantees apply
- Mature — interface settled, pending promotion
- Experimental — may change without notice
- Deprecated — scheduled for removal
