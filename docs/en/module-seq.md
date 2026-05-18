# jsrc seq

Sequence manipulation is the most routine task in bioinformatics. `jsrc seq` covers extraction, renaming, translation, promoter extraction, QC, codon usage, k-mer profiling, Entrez fetching, restriction digestion, sliding-window analysis, ORF finding, CpG island prediction, primer analysis, tandem repeat finding, sequence complexity, and MSA entropy.

## extract

Common scenario: you have a genome FASTA and GFF annotation, but you only want the CDS of a few specific genes for downstream analysis. Digging through the GFF for coordinates and extracting sequences manually is fine for one or two genes, but it gets tedious fast.

Given a genome, GFF, and target ID list (one per line), this command extracts sequences by feature type. CDS by default, but `-feature` lets you switch to mRNA or others. ID matching uses `Parent` in GFF by default — change it with `-match` if your GFF uses a different attribute.

Example input (`ids.txt`):

```txt
GENE001
GENE002
GENE003
```

```bash
jsrc seq extract -fa genome.fa -gff genes.gff -ids ids.txt -o out.fa
```

For mRNA:

```bash
jsrc seq extract -fa genome.fa -gff genes.gff -ids ids.txt -feature mRNA -match ID -o mrnas.fa
```

## rename

FASTA headers from different sources are rarely consistent. One dataset uses GenBank accessions, another uses custom names. If you want to analyze them together, standardizing IDs is the first step.

Two modes. `csv` is straightforward — a two-column CSV mapping old IDs to new ones, and the program replaces them. `gff` mode is smarter: given a GFF file, it renames sequences based on parent-child relationships (e.g., mapping sequence IDs to gene names). Use `-parent` to specify which attribute links them.

Example input (`mapping.csv`):

```csv
old_id,new_id
GENE001,AT1G01010
GENE002,AT1G01020
GENE003,AT1G01030
```

```bash
jsrc seq rename -fa in.fa -mode csv -map mapping.csv -o out.fa
jsrc seq rename -fa in.fa -mode gff -gff genes.gff -parent Parent -o out.fa
```

## translate

When doing cross-species comparison or looking for protein domains, what you actually need is amino acid sequences. This command handles the genome-annotation-to-protein conversion: read genome FASTA and GFF, extract CDS, translate, output protein FASTA.

```bash
jsrc seq translate -fa genome.fa -gff genes.gff -id ID -o proteins.fa
```

## promoter

Studying gene regulation often means looking at promoter regions. Say you want to check whether a transcription factor binding site exists 2kb upstream of a set of genes — you need to extract those regions in bulk first.

This command does exactly that. Given genome, GFF, and gene IDs, it automatically calculates coordinates and extracts flanking sequences.

Example input (`genes.txt`):

```txt
GENE001
GENE002
GENE003
```

Default is 2000bp upstream, 0bp downstream. Adjust with `-up` and `-down`.

```bash
jsrc seq promoter -fa genome.fa -gff genes.gff -ids genes.txt -o promoters.fa -up 1500 -down 500
```

If your GFF uses a different feature label (some datasets use `mRNA` instead of `gene`), set `-feature` accordingly.

## qc

I always check data quality before diving into large-scale analysis. This command is for a quick health check — it won't replace FastQC's deep reports, but it's fast and gives you the essentials in one go.

Supports FASTA and FASTQ (including gzip). For FASTA: sequence count, total length, N50/N90, GC content, N ratio. For FASTQ: read count, total bases, mean read length. If genome size is provided via `-gs`, it also estimates sequencing depth.

```bash
jsrc seq qc -fa assembly.fa
jsrc seq qc -fq r1.fq.gz r2.fq.gz -gs 520000000 --json
```

## codon

Codon bias is an interesting angle. Different species, and even different genes within the same genome, display distinct codon usage patterns — shaped by selection pressure, mutation bias, and tRNA abundance.

This command calculates codon usage frequencies from CDS FASTA. It counts each codon and computes RSCU (Relative Synonymous Codon Usage). Shows the top 20 by default; increase with `--top`.

```bash
jsrc seq codon -fa cds.fa --top 20 --json
```

## kmer

k-mer is one of the most fundamental yet powerful features in sequence analysis. It's useful for assessing sequence complexity, generating genomic fingerprints, and quickly comparing similarity between samples.

With a single FASTA, it reports high-frequency k-mers and their frequencies. With multiple FASTA files, it computes a pairwise cosine distance matrix — useful for spotting which samples are similar at a glance. Set k-mer length with `-k` (default 5).

```bash
jsrc seq kmer -fa genome.fa --top 30
jsrc seq kmer -fa a.fa b.fa c.fa -k 7
```

## fetch

Fetching sequences from NCBI through a browser gets old fast — open the page, search, tick boxes, download. This command pulls sequences by accession ID directly from the terminal, supporting FASTA and GenBank formats.

Just pass the IDs. Multiple IDs can be space-separated or placed in a file (one per line). NCBI requires `--email`. Without `-o`, output goes to stdout, convenient for piping into further processing.

```bash
jsrc seq fetch -ids NM_001301717 NR_146152 --email me@example.com -o sequences.fa
jsrc seq fetch -ids ids.txt --format genbank --email me@example.com --json
```

## digest

Simulate restriction enzyme digestion on a sequence. Common in cloning and vector construction: you want to cut a plasmid with EcoRI and HindIII and see what fragments you get. Instead of opening a web tool, this uses Biopython's Restriction module with 1088 enzymes built in.

Supports both linear and circular modes — circular DNA (plasmids) calculates fragments differently from linear, handled automatically. Use `--min-size` to filter out small fragments.

```bash
jsrc seq digest -fa plasmid.fa -e EcoRI,HindIII --circular --json
jsrc seq digest -fa seq.fa -e EcoRI --min-size 50
```

## window

Sliding-window analysis solves a common problem: global GC content is an average, but genomic GC distribution is uneven — high near CpG islands, low near centromeres. This command looks at these variations window by window.

Specify window size and step, and the program slides along the sequence, computing GC content and GC skew ((G-C)/(G+C)) in each window. By default it uses the longest sequence in the FASTA; target a specific sequence with `-id`. `--head` limits output to the first N windows.

```bash
jsrc seq window -fa genome.fa -w 100000 -s 20000 --head 20
jsrc seq window -fa genome.fa -id chr1 -w 1000 -s 200 --json
```

## orf

ORF finding is the first step in gene prediction from unannotated sequences. Given a FASTA file, this command scans for ATG-to-stop codon open reading frames and reports their coordinates, length, frame, and translated protein sequence.

By default it searches frame 1 only and reports ORFs ≥ 100 nt. Use `--all-frames` to search all three forward frames, and `--min-len` to adjust the length cutoff. `--top N` keeps only the N longest ORFs per sequence.

```bash
jsrc seq orf -fa genome.fa --min-len 300 --all-frames
jsrc seq orf -fa contigs.fa --top 5 --json
```

## cpg

CpG islands are genomic regions with elevated CpG dinucleotide density and GC content, typically found near gene promoters and associated with gene regulation. This command predicts them using the classical sliding-window approach (Gardiner-Garden & Frommer 1987).

A window is considered a CpG island candidate if GC% ≥ 50% and observed/expected CpG ratio ≥ 0.6. Adjacent qualifying windows are merged; merged regions shorter than `--min-len` are dropped.

```bash
jsrc seq cpg -fa genome.fa
jsrc seq cpg -fa genome.fa --window 200 --min-len 200 --min-gc 55 --json
```

## primer

Evaluates primer sequences for Tm, GC content, GC clamp, and hairpin risk. Two Tm models are provided: Wallace rule (fast estimate for short oligos) and the nearest-neighbor thermodynamic model (SantaLucia 1998, more accurate).

Input is a FASTA file where each record is one primer sequence. `--conc` sets the primer concentration for the nearest-neighbor calculation (default 250 nM).

```bash
jsrc seq primer -fa primers.fa
jsrc seq primer -fa primers.fa --conc 500 --json
```

## repeat

Finds simple sequence repeats (SSRs / microsatellites / STRs) in genomic sequences. Scans for tandemly repeated motifs of specified unit length range with a minimum number of repeat copies.

Default settings find mono- through hexanucleotide repeats (unit length 1–6) with at least 3 copies. Useful for microsatellite marker development and repeat annotation.

```bash
jsrc seq repeat -fa genome.fa
jsrc seq repeat -fa genome.fa --min-unit 2 --max-unit 4 --min-reps 5 --json
```

## complexity

Computes three complementary complexity metrics for each sequence:

- **Shannon entropy** — information-theoretic diversity of nucleotide composition
- **Linguistic complexity** — fraction of distinct k-mers observed vs theoretically possible (k = 1–6)
- **DUST score** — low-complexity masking score; values > 7 suggest repetitive/low-complexity regions

Useful for pre-filtering low-complexity sequences before alignment or assembly.

```bash
jsrc seq complexity -fa sequences.fa
jsrc seq complexity -fa sequences.fa --json
```

## entropy

Computes per-column Shannon entropy and conservation for a multiple sequence alignment (MSA). Entropy is high at variable positions, low at conserved ones. Useful for identifying conserved domains, functional residues, or designing degenerate primers.

Expects an aligned FASTA where all sequences are the same length. `--summary` skips per-column output and prints only mean entropy and conservation.

```bash
jsrc seq entropy -fa aligned.fa
jsrc seq entropy -fa aligned.fa --summary
jsrc seq entropy -fa aligned.fa --json
```
