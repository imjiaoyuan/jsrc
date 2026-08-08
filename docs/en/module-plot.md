# jsrc plot

Gene structure diagrams, chromosome maps, protein domains, cis-element visualization, dotplots, and circular genome views. All based on matplotlib, output suitable for reports or publications.

## gene

Draws gene structure diagrams (UTR, CDS, introns) from GFF annotation and a target gene ID list. Useful for visualizing structural comparisons across a gene family or a set of selected genes.

Example input (`ids.txt`):

```txt
GENE001
GENE002
GENE003
```

```bash
jsrc plot gene -gff genes.gff -ids ids.txt -o gene.png -dpi 300
```

- `-gff`: GFF annotation file.
- `-ids`: gene ID list file.
- `-o`: output PNG path.
- `-dpi`: output DPI (default: `300`).

## exon

Similar to gene but focused on exon-level structural differences. Finer-grained than the gene view, useful for looking at alternative splicing or exon gain/loss.

```bash
jsrc plot exon -gff genes.gff -ids ids.txt -o exon.png -dpi 300
```

- `-gff`: GFF annotation file.
- `-ids`: gene ID list file.
- `-o`: output PNG path.
- `-dpi`: output DPI (default: `300`).

## chromosome

Chromosome-scale distribution maps. Plots all genes across chromosomes, or highlights a specific subset. Good for genome-level overviews.

```bash
jsrc plot chromosome -gff genes.gff -ids ids.txt -o chr.png -dpi 300
```

- `-gff`: GFF annotation file.
- `-ids`: optional gene ID filter file.
- `-o`: output PNG path.
- `-dpi`: output DPI (default: `300`).

## domain

Draws protein domain architecture. Input table needs sequence ID, domain name, start and end positions. Scales each protein proportionally. Good for batch-checking domain order, boundaries, and anomalies.

Example input (`domains.tsv`):

```tsv
protein	domain	start	end
ProteinA	Pkinase	10	260
ProteinA	WD40	300	400
ProteinB	LRR	5	80
```

```bash
jsrc plot domain -tsv domains.tsv -o domain.png -dpi 300
```

- `-tsv`: domain table input.
- `-o`: output PNG path.
- `-dpi`: output DPI (default: `300`).

## cis

Visualizes cis-regulatory element positions from BED-format input onto sequence coordinates. Useful for displaying motif distributions in promoter regions.

Example input (`motifs.bed`):

```bed
chr1	100	150	MOTIF1
chr1	300	320	MOTIF2
chr2	50	80	MOTIF1
```

```bash
jsrc plot cis -bed motifs.bed -o cis.png -dpi 300
```

- `-bed`: BED input file.
- `-o`: output PNG path.
- `-dpi`: output DPI (default: `300`).

## dotplot

Compares two sequences by plotting exact k-mer matches. Each sequence's k-mer positions form the axes; matching points form patterns — a diagonal indicates collinearity, while scattered or repeated patterns suggest rearrangements or repeats. Useful for spotting structural variation quickly.

```bash
jsrc plot dotplot -fa1 a.fa -fa2 b.fa -k 10 -o d.png -dpi 300
```

- `-fa1`: sequence FASTA 1.
- `-fa2`: sequence FASTA 2.
- `-k`: k-mer length (default: `10`).
- `-o`: optional output PNG (omit for interactive display).
- `-dpi`: output DPI (default: `300`).

## circoslite

A lightweight circular genome view. Input a single FASTA, and it computes window-based statistics (e.g., GC content) and generates a circular plot. No complicated configuration needed — just give it a FASTA.

```bash
jsrc plot circoslite -fa genome.fa -w 100000 -o c.png -dpi 300
```

- `-fa`: genome FASTA input.
- `-w`: window size (default: `100000`).
- `-o`: optional output PNG (omit for interactive display).
- `-dpi`: output DPI (default: `300`).
