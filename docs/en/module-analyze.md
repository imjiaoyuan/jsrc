# jsrc analyze

## phylo

When you want a quick evolutionary snapshot from sequence data, start here. It reads a FASTA file, builds a tree with your chosen method, and writes a Newick result you can open in any tree viewer.

```bash
jsrc analyze phylo -fa sequences.fa -o tree.nwk -a nj
```

- `-fa`: Input FASTA file.
- `-o`: Output Newick tree file.
- `-a`: Algorithm, `nj` or `upgma` (default: `nj`).

## motif

Use this for motif hunting in promoter or sequence sets. You control how many motifs to find and the motif width range, so it is easy to tune for exploratory vs stricter runs.

```bash
jsrc analyze motif -fa promoters.fa -o motif_out -nmotifs 5 -minw 6 -maxw 12
```

- `-fa`: Input FASTA file for motif discovery.
- `-o`: Output directory.
- `-nmotifs`: Number of motifs to detect (default: `5`).
- `-minw`: Minimum motif width (default: `6`).
- `-maxw`: Maximum motif width (default: `12`).

## qc

Think of this as a one-stop health check for your data. It can summarize assembly quality, mapping results, variant counts, and read-depth signals in a single run.

```bash
jsrc analyze qc -fa assembly.fa -sam aln.sam -vcf variants.vcf.gz -fq r1.fq.gz r2.fq.gz -gs 520000000 --json
```

- `-fa`: Assembly FASTA for contig, N50/N90, and GC metrics.
- `-sam`: SAM or SAM.GZ for mapping-rate and depth summary.
- `-vcf`: VCF or VCF.GZ for SNP/INDEL summary.
- `-fq`: FASTQ or FASTQ.GZ files for read/base/depth stats.
- `-gs`: Genome size in bp, used with `-fq` to estimate depth.
- `--json`: Print JSON output instead of text table.

## msa_consensus

After alignment, this helps you quickly see the consensus and how conserved each position is. It is great for fast alignment sanity checks before downstream modeling.

```bash
jsrc analyze msa_consensus -fa aligned.fa --json
```

- `-fa`: Input FASTA file, usually aligned sequences.
- `--json`: Print JSON output.

## snpindel

For pairwise sequence comparison, this command gives a compact SNP/INDEL summary without extra workflow overhead. Great for sample-vs-sample difference checks.

```bash
jsrc analyze snpindel -fa pair.fa -id1 sampleA -id2 sampleB --json
```

- `-fa`: FASTA containing at least two sequences.
- `-id1`: Sequence 1 ID (default: first sequence).
- `-id2`: Sequence 2 ID (default: second sequence).
- `--json`: Print JSON output.

## bootstrap_phylo

If you need branch-confidence support, this is the go-to command. It runs bootstrap replicates and produces a tree that includes support information.

```bash
jsrc analyze bootstrap_phylo -fa seqs.fa -n 200 -seed 42 -o boot.nwk
```

- `-fa`: Input FASTA file.
- `-n`: Bootstrap replicate count (default: `100`).
- `-seed`: Random seed for reproducibility (default: `42`).
- `-o`: Optional output Newick file.
