# jsrc Documentation (EN)

## Quick Start

```bash
jsrc --help
jsrc <module> --help
jsrc <module> <subcommand> --help
```

## Module Map

| module | description |
|---|---|
| `seq` | Sequence extraction, renaming, translation, QC, k-mer, window |
| `plot` | Gene/exon/chromosome/domain and utility visualizations |
| `analyze` | Phylogeny, motif, consensus, SNP/INDEL, QC |
| `gs` | Genomic selection dataset build/split/train workflows |
| `grn` | GRN conversion, centrality calculation, viewer packaging/service |
| `vision` | Image contour extraction, EFD descriptors, morphology traits |
| `job` | Background job management (`submit/ls/show/logs/kill/history/gc`) |
| `math` | Statistics and machine-learning style command-line utilities |

## Error Behavior

- User/input errors are shown as `Error: <message>`.
- The same style is used across modules for missing files and invalid arguments.

## Modules

- [Math Module](./module-math.md)
- [Sequence Module](./module-seq.md)
- [Analyze Module](./module-analyze.md)
- [Plot Module](./module-plot.md)
- [GS Module](./module-gs.md)
- [GRN Module](./module-grn.md)
- [Vision Module](./module-vision.md)
- [Job Module](./module-job.md)

## Reference

- [Stability Policy](./stability.md)
- [Release Checklist](../../RELEASE.md)
