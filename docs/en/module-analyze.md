# jsrc analyze

Common analysis tools for sequences: phylogenetic tree construction (with optional bootstrap support), motif discovery, QC summary, consensus calling, and variant comparison.

## phylo

Pass in a FASTA, pick an algorithm, and get a Newick tree. Supports neighbor-joining (NJ) and UPGMA. The output works with any tree viewer. Good for a quick look at clustering relationships or as a starting point for more detailed phylogenetic analysis.

Bootstrap support is built in: pass `-n`/`--bootstrap` with the number of replicates (0 = off, default 0) and `-seed` for the random seed (default 42). When bootstrap ≥ 1, the tree is annotated with branch support values.

```bash
jsrc analyze phylo -fa sequences.fa -o tree.nwk -a nj
jsrc analyze phylo -fa seqs.fa -n 200 -seed 42 -o tree.nwk
```

- `-fa`: input FASTA.
- `-o`: output Newick tree file.
- `-a`: algorithm, `nj` or `upgma` (default: `nj`).
- `-n`/`--bootstrap`: number of bootstrap replicates (default `0`; 0 = off).
- `-seed`: random seed (default `42`).

## motif

Find conserved short motifs in promoters or sequence sets. Control the number of motifs and the width range. Useful for exploratory scans and iterative refinement.

```bash
jsrc analyze motif -fa promoters.fa -o motif_out -nmotifs 5 -minw 6 -maxw 12
```

- `-fa`: input FASTA.
- `-o`: output directory.
- `-nmotifs`: number of motifs to detect (default: `5`).
- `-minw`: minimum motif width (default: `6`).
- `-maxw`: maximum motif width (default: `12`).

## qc

Assembly quality (FASTA), mapping statistics (SAM), variant overview (VCF), read depth (FASTQ) — all in one command. A quick way to tell whether your data is usable before moving to more complex analyses.

```bash
jsrc analyze qc -fa assembly.fa -sam aln.sam -vcf variants.vcf.gz \
  -fq r1.fq.gz r2.fq.gz -gs 520000000 --json
```

- `-fa`: assembly FASTA for contig/N50/GC metrics.
- `-sam`: SAM/SAM.GZ for mapping rate and depth statistics.
- `-vcf`: VCF/VCF.GZ for SNP/INDEL summary.
- `-fq`: FASTQ/FASTQ.GZ for read/base/depth stats.
- `-gs`: genome size in bp, used with `-fq` for depth estimation.
- `--json`: print JSON output.

## msa_consensus

After multiple sequence alignment, this generates a consensus sequence and per-column conservation scores. It checks whether input sequence lengths differ significantly and pads shorter sequences with gaps if needed.

```bash
jsrc analyze msa_consensus -fa aligned.fa --json
```

- `-fa`: input FASTA (usually aligned sequences).
- `--json`: JSON output.

## snpindel

Compare two sequences for differences without going through a full variant calling pipeline. Input a FASTA with two sequences, output SNP/INDEL statistics. Convenient for quick sample-to-sample comparisons.

```bash
jsrc analyze snpindel -fa pair.fa -id1 sampleA -id2 sampleB --json
```

- `-fa`: FASTA containing at least two sequences.
- `-id1`: sequence 1 ID (default: first sequence).
- `-id2`: sequence 2 ID (default: second sequence).
- `--json`: JSON output.
