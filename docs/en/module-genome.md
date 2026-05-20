# jsrc genome

Genome-level analysis tools. `jsrc genome` covers genome statistics, feature detection, comparative analysis, evolutionary analysis, and annotation utilities.

## cpg

CpG islands are genomic regions with high CpG dinucleotide density and GC content, typically located near gene promoters and associated with gene regulation. This command predicts CpG islands using the classic sliding window method (Gardiner-Garden & Frommer 1987).

A window is considered a candidate CpG island if GC% ≥ 50% and observed/expected CpG ratio ≥ 0.6. Adjacent qualifying windows are merged, and regions shorter than `--min-len` are filtered out.

```bash
jsrc genome cpg -fa genome.fa
jsrc genome cpg -fa genome.fa --window 200 --min-len 200 --min-gc 55 --json
```

## orf

ORF finding is the first step in gene prediction for unannotated sequences. Given a FASTA file, this command scans for open reading frames from ATG to stop codons, reporting coordinates, length, frame, and translated protein sequence.

By default, only frame 1 is searched, reporting ORFs ≥ 100 nt. Use `--all-frames` to search all three forward frames, `--min-len` to adjust length threshold, and `--top N` to keep only the longest N ORFs per sequence.

```bash
jsrc genome orf -fa genome.fa --min-len 300 --all-frames
jsrc genome orf -fa contigs.fa --top 5 --json
```

## promoter

When studying gene regulation, you often need to examine promoter regions. For example, to check if several genes have a transcription factor binding site in their upstream 2kb region, you first need to extract these regions in batch.

This command does exactly that: given a genome, GFF, and gene ID list, it automatically calculates coordinates and extracts upstream/downstream sequences.

Example input (`genes.txt`):

```txt
GENE001
GENE002
GENE003
```

By default, it extracts 2000bp upstream and 0bp downstream. You can adjust with `-up` and `-down`.

```bash
jsrc genome promoter -fa genome.fa -gff genes.gff -ids genes.txt -o promoters.fa -up 1500 -down 500
```

If your GFF uses a different feature label than `gene` (e.g., `mRNA`), set `-feature` accordingly.

## repeat

Find simple sequence repeats (SSR / microsatellites / STR) in genomic sequences. Scans for tandem repeat motifs within specified unit length range and minimum repeat count.

Default settings search for mono- to hexa-nucleotide repeats (unit length 1–6) with at least 3 repetitions. Commonly used for microsatellite marker development and repeat annotation.

```bash
jsrc genome repeat -fa genome.fa
jsrc genome repeat -fa genome.fa --min-unit 2 --max-unit 4 --min-reps 5 --json
```

## island

Genomic island detection identifies regions with deviant GC content that may indicate horizontal gene transfer, pathogenicity islands, or other foreign DNA. This command uses a sliding window approach to scan for GC content anomalies.

Windows exceeding the GC threshold are marked as candidate islands. Adjacent candidate windows are merged into a single island. Use `--min-length` to filter out short regions.

```bash
jsrc genome island -fa genome.fa
jsrc genome island -fa genome.fa --window 5000 --step 1000 --gc-threshold 0.6 --min-length 10000 --json
```

## palindrome

Palindromic sequences (inverted repeats) are often associated with transposons, restriction enzyme recognition sites, and hairpin structures. This command finds palindromic structures in sequences.

A palindrome consists of two reverse-complementary arms separated by a gap. You can set arm length range (`--min-arm`, `--max-arm`) and maximum gap length (`--max-gap`).

```bash
jsrc genome palindrome -fa genome.fa
jsrc genome palindrome -fa genome.fa --min-arm 8 --max-arm 30 --max-gap 20 --top 100 --json
```

## stats

Basic genome assembly quality metrics. This command calculates N50/L50, total length, sequence count, gap statistics, and GC content.

N50 is the weighted median length—sort all sequences by length, sum from longest to shortest, and N50 is the length when cumulative sum reaches half the total. L50 is the number of sequences needed to reach N50. Higher values indicate better assembly contiguity.

```bash
jsrc genome stats -fa assembly.fa
jsrc genome stats -fa assembly.fa --json
```

## gc-skew

Cumulative GC skew analysis is used to predict replication origin (oriC) and terminus (ter) in bacterial genomes. GC skew is defined as (G-C)/(G+C), typically showing a distinct minimum near the replication origin.

This command calculates sliding window cumulative GC skew, outputting position and cumulative skew for each window. Visualize with plotting tools to find the curve's lowest point.

```bash
jsrc genome gc-skew -fa genome.fa
jsrc genome gc-skew -fa genome.fa --window 10000 --step 5000 --json
```

## window

Sliding window GC and AT skew analysis. This command calculates GC content, GC skew, and AT skew for each window at specified window size and step.

GC skew = (G-C)/(G+C), AT skew = (A-T)/(A+T). These metrics reveal local compositional features and replication bias.

```bash
jsrc genome window -fa genome.fa
jsrc genome window -fa genome.fa --window 50000 --step 10000 --json
```

## codon

Codon usage frequency and RSCU (Relative Synonymous Codon Usage) analysis. Input CDS sequences in FASTA format to count codon occurrences and calculate RSCU.

RSCU = observed frequency / expected frequency (assuming uniform synonymous codon usage). RSCU > 1 indicates higher-than-average usage, < 1 indicates lower.

Optional features:
- `--cai`: Calculate CAI (Codon Adaptation Index), requires reference gene set (typically highly expressed genes)
- `--enc`: Calculate ENC (Effective Number of Codons), range 20-61, lower values indicate stronger codon bias

```bash
jsrc genome codon -fa cds.fa --top 20
jsrc genome codon -fa cds.fa --cai highly_expressed.fa --enc --json
```

## distance

Calculate pairwise genetic distances in multiple sequence alignments. Supports four distance models:

- **hamming**: Hamming distance, number of differing sites
- **p**: p-distance, proportion of differing sites
- **jc**: Jukes-Cantor distance, corrects for multiple substitutions
- **k2p**: Kimura 2-parameter distance, distinguishes transitions and transversions

Input must be aligned sequences (equal length).

```bash
jsrc genome distance -fa aligned.fa --method p
jsrc genome distance -fa aligned.fa --method k2p --json
```

## kaks

Calculate Ka/Ks ratio for two aligned CDS sequences. Ka is the nonsynonymous substitution rate, Ks is the synonymous substitution rate, and Ka/Ks (ω) reflects selection pressure:

- ω < 1: purifying selection (negative selection)
- ω = 1: neutral evolution
- ω > 1: positive selection

Input must be exactly two aligned CDS sequences with length divisible by 3.

```bash
jsrc genome kaks -fa aligned_cds.fa
jsrc genome kaks -fa aligned_cds.fa --json
```

## density

Calculate gene or feature density distribution along the genome. This command reads genome FASTA and GFF annotation, counting features in sliding windows and calculating density (features per kb) and coverage.

Use `--feature-type` to specify which feature type to count (e.g., gene, CDS, exon). Useful for visualizing uneven gene distribution.

```bash
jsrc genome density -fa genome.fa -gff genes.gff
jsrc genome density -fa genome.fa -gff genes.gff --feature-type CDS --window 20000 --step 10000 --json
```

## motif-scan

Scan genomes for DNA motifs. Supports IUPAC degenerate base codes (R=A/G, Y=C/T, N=any, etc.) and allows mismatches.

Commonly used for transcription factor binding site prediction, restriction enzyme site finding, etc.

```bash
jsrc genome motif-scan -fa genome.fa -m TATAAA
jsrc genome motif-scan -fa genome.fa -m GCRWTG --mismatch 1 --top 50 --json
```

## ani

k-mer-based Average Nucleotide Identity (ANI) calculation. ANI is a standard metric for measuring genome similarity, commonly used for species delineation (ANI > 95% typically indicates same species).

This command uses Jaccard similarity (shared k-mers / total k-mers) as an ANI approximation, requiring no sequence alignment and running fast.

```bash
jsrc genome ani -fa genome1.fa genome2.fa
jsrc genome ani -fa genome1.fa genome2.fa -k 21 --json
```

## compare

Genome comparison and difference statistics based on global alignment. Uses the edlib library for efficient global alignment, calculating edit distance, identity, and difference sites.

**Note**: This command requires edlib: `pip install edlib`

```bash
jsrc genome compare -fa genome1.fa genome2.fa
jsrc genome compare -fa genome1.fa genome2.fa --json
```
