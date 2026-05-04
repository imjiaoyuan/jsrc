# jsrc plot

## gene

Use this when you want clean gene-structure figures from annotation and an ID list. It is ideal for paper-ready panels showing CDS/intron layouts across selected genes.

```bash
jsrc plot gene -gff genes.gff -ids ids.txt -o gene.png -dpi 300
```

- `-gff`: GFF annotation file.
- `-ids`: gene ID list file.
- `-o`: output PNG path.
- `-dpi`: output DPI (default: `300`).

## exon

For exon-focused structure comparison, this command gives a simpler exon-centric view while keeping the same input pattern as gene plotting.

```bash
jsrc plot exon -gff genes.gff -ids ids.txt -o exon.png -dpi 300
```

- `-gff`: GFF annotation file.
- `-ids`: gene ID list file.
- `-o`: output PNG path.
- `-dpi`: output DPI (default: `300`).

## chromosome

When you need a genome-level map, this command plots gene positions on chromosomes. Add an ID list if you want to focus on a subset.

```bash
jsrc plot chromosome -gff genes.gff -ids ids.txt -o chr.png -dpi 300
```

- `-gff`: GFF annotation file.
- `-ids`: optional gene ID filter file.
- `-o`: output PNG path.
- `-dpi`: output DPI (default: `300`).

## domain

This command draws domain architecture from tabular domain annotations, making it easy to inspect domain order and span along proteins.

```bash
jsrc plot domain -tsv domains.tsv -o domain.png -dpi 300
```

- `-tsv`: domain table input.
- `-o`: output PNG path.
- `-dpi`: output DPI (default: `300`).

## cis

Great for promoter-level element mapping, this command visualizes cis-regulatory positions from BED-style input.

```bash
jsrc plot cis -bed motifs.bed -o cis.png -dpi 300
```

- `-bed`: BED input file.
- `-o`: output PNG path.
- `-dpi`: output DPI (default: `300`).

## heart

Use it for quick interactive curve rendering demos.

```bash
jsrc plot heart
```

- no command-specific parameters.

## rose

Use it for interactive 3D rose visualization demos.

```bash
jsrc plot rose
```

- no command-specific parameters.

## dotplot

When comparing two sequences visually, this command plots exact k-mer matches as a dotplot. It is excellent for spotting repeats and coarse structural similarity.

```bash
jsrc plot dotplot -fa1 a.fa -fa2 b.fa -k 10 -o d.png -dpi 300
```

- `-fa1`: FASTA file 1.
- `-fa2`: FASTA file 2.
- `-k`: k-mer size (default: `10`).
- `-o`: optional output PNG (omit for interactive display).
- `-dpi`: output DPI (default: `300`).

## circoslite

For a lightweight circular genome view with window-based tracks, this command offers a compact circos-style summary from FASTA.

```bash
jsrc plot circoslite -fa genome.fa -w 100000 -o c.png -dpi 300
```

- `-fa`: genome FASTA input.
- `-w`: window size (default: `100000`).
- `-o`: optional output PNG (omit for interactive display).
- `-dpi`: output DPI (default: `300`).
