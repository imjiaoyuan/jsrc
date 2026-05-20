# jsrc seq

Sequence manipulation is the most routine task in bioinformatics. `jsrc seq` covers extraction, renaming, translation, QC, k-mer profiling, Entrez fetching, restriction digestion, sequence complexity, and MSA entropy.

Genome-level analysis features (such as ORF finding, CpG island prediction, promoter extraction, tandem repeats, codon usage, sliding-window analysis, etc.) have been moved to the [genome module](./module-genome.md).

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

## qc

I always check data quality before diving into large-scale analysis. This command is for a quick health check — it won't replace FastQC's deep reports, but it's fast and gives you the essentials in one go.

Supports FASTA and FASTQ (including gzip). For FASTA: sequence count, total length, N50/N90, GC content, N ratio. For FASTQ: read count, total bases, mean read length. If genome size is provided via `-gs`, it also estimates sequencing depth.

```bash
jsrc seq qc -fa assembly.fa
jsrc seq qc -fq r1.fq.gz r2.fq.gz -gs 520000000 --json
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
