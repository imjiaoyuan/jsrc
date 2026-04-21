# jsrc seq

## extract

Need to pull specific feature sequences from genome annotation quickly? This command links FASTA, GFF, and your ID list, then writes a clean output FASTA for downstream analysis.

```bash
jsrc seq extract -fa genome.fa -gff genes.gff -ids ids.txt -o out.fa [-feature CDS] [-match Parent]
```

- `-fa`: genome FASTA input.
- `-gff`: GFF annotation input.
- `-ids`: ID list file (one ID per line).
- `-o`: output FASTA path.
- `-feature`: feature type in GFF to extract (default: `CDS`).
- `-match`: GFF attribute key used to match IDs (default: `Parent`).

## rename

When FASTA headers are inconsistent across datasets, use this command to normalize them. You can rename through a CSV map or infer mapping relationships from GFF.

```bash
jsrc seq rename -fa in.fa -mode csv -map mapping.csv -o out.fa
jsrc seq rename -fa in.fa -mode gff -gff genes.gff -parent Parent -o out.fa
```

- `-fa`: input FASTA.
- `-mode`: rename mode, `csv` or `gff` (default: `csv`).
- `-map`: CSV mapping file `old_id,new_id` (used in `csv` mode).
- `-gff`: GFF file (used in `gff` mode).
- `-parent`: parent attribute key in GFF (used in `gff` mode).
- `-o`: output FASTA.

## translate

This is the bridge from genome annotation to protein space. It extracts CDS regions and translates them, producing a protein FASTA ready for domain and homology analysis.

```bash
jsrc seq translate -fa genome.fa -gff genes.gff -id ID -o proteins.fa
```

- `-fa`: genome FASTA.
- `-gff`: GFF annotation.
- `-id`: GFF attribute key used as gene ID.
- `-o`: output protein FASTA.

## promoter

Use this when you want promoter windows around selected genes. It is especially handy for motif scanning pipelines where upstream sequence context matters.

```bash
jsrc seq promoter -fa genome.fa -gff genes.gff -ids genes.txt -o promoters.fa -up 2000 -down 0
```

- `-fa`: genome FASTA.
- `-gff`: GFF annotation.
- `-ids`: target gene IDs.
- `-o`: output promoter FASTA.
- `-id`: ID key in GFF attributes (default: `ID`).
- `-feature`: GFF feature type (default: `gene`).
- `-up`: upstream length in bp (default: `2000`).
- `-down`: downstream length in bp (default: `0`).

## qc

For a quick sequence-level status report, this command gives assembly and read summaries in one place, with optional JSON for scripting workflows.

```bash
jsrc seq qc -fa assembly.fa
jsrc seq qc -fq r1.fq.gz r2.fq.gz -gs 520000000 --json
```

- `-fa`: FASTA input for assembly metrics.
- `-fq`: one or more FASTQ/FASTQ.GZ files.
- `-gs`: genome size (bp), used with FASTQ for depth estimate.
- `--json`: print JSON output.

## codon

When codon bias is the focus, this command gives codon usage and RSCU summaries straight from CDS FASTA.

```bash
jsrc seq codon -fa cds.fa --top 20 --json
```

- `-fa`: CDS FASTA input.
- `--top`: number of top codons to show (default: `20`).
- `--json`: print JSON output.

## kmer

Great for composition fingerprints and quick similarity checks. With one input it reports top k-mers; with multiple inputs it supports cross-sample comparison.

```bash
jsrc seq kmer -fa a.fa b.fa -k 7 --top 30 --json
```

- `-fa`: one or more FASTA files.
- `-k`: k-mer size (default: `5`).
- `--top`: top N k-mers for single-file mode (default: `20`).
- `--json`: print JSON output.

## window

This command computes sliding-window sequence metrics like GC and skew values. It is useful for regional pattern scanning without opening a full plotting pipeline.

```bash
jsrc seq window -fa genome.fa -id chr1 -w 1000 -s 200 --head 20 --json
```

- `-fa`: FASTA input.
- `-id`: target sequence ID (default behavior: longest sequence).
- `-w`: window size (default: `1000`).
- `-s`: step size (default: `200`).
- `--head`: print first N windows (default: `10`).
- `--json`: print JSON output.
