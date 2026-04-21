# Sequence Module

```bash
jsrc seq extract -fa genome.fa -gff genes.gff -ids ids.txt -o out.fa [-feature CDS] [-match Parent]
```

Use this when you need to extract a specific set of sequences from a genome and annotation. The input is a genome FASTA (`-fa`), a GFF annotation (`-gff`), and an ID list (`-ids`, one ID per line). You can choose another feature type with `-feature` and another matching key with `-match`. The output is a FASTA file (`-o`) that can be used directly for alignment, translation, or motif analysis.

---

```bash
jsrc seq rename -fa in.fa -mode csv -map mapping.csv -o out.fa
jsrc seq rename -fa in.fa -mode gff -gff genes.gff -parent Parent -o out.fa
```

Use this to standardize FASTA IDs before downstream analysis. In CSV mode, the mapping file should be `old_id,new_id`; in GFF mode, IDs are inferred from annotation relationships. The command writes a renamed FASTA to `-o`, which is helpful when combining datasets from different sources.

---

```bash
jsrc seq translate -fa genome.fa -gff genes.gff -id ID -o proteins.fa
```

Use this to generate protein FASTA from genomic annotation. Input is genome FASTA plus GFF, and `-id` tells the command which GFF attribute should be used as the output record ID. The output file (`-o`) can be used directly for protein-domain analysis and homology searches.

---

```bash
jsrc seq promoter -fa genome.fa -gff genes.gff -ids genes.txt -o promoters.fa [-up 2000] [-down 0]
```

Use this when you want promoter regions for a target gene set. The command reads genome FASTA, GFF, and a plain-text gene ID list, then extracts the configured upstream/downstream range (`-up`, `-down`). The output FASTA (`-o`) is suitable for motif enrichment and cis-element scanning.

---

```bash
jsrc seq qc -fa assembly.fa
jsrc seq qc -fq r1.fq.gz r2.fq.gz -gs 520000000
jsrc seq qc -fa assembly.fa -fq r1.fq.gz r2.fq.gz --json
```

Use this for quick QC summaries from FASTA and/or FASTQ. FASTA input gives assembly-style metrics such as sequence counts and N50/N90, while FASTQ input gives read/base totals and depth estimates when `-gs` is supplied. Output is printed to terminal by default; add `--json` for machine-readable output.

---

```bash
jsrc seq codon -fa cds.fa --top 20
```

Use this to inspect codon usage and RSCU from CDS sequences. Input is CDS FASTA, and output reports codon count/frequency/RSCU in terminal form; with `--json` it returns structured data for downstream plotting or comparison.

---

```bash
jsrc seq kmer -fa sample.fa -k 5
jsrc seq kmer -fa a.fa b.fa c.fa -k 7
```

Use this for k-mer composition profiling. With one FASTA input, it reports top k-mers and frequencies; with multiple FASTA inputs, it returns a cosine-distance matrix between samples. This is useful for quick similarity checks before heavier analyses.

---

```bash
jsrc seq window -fa genome.fa -id chr1 -w 1000 -s 200 --head 20
```

Use this to compute sliding-window sequence statistics. Input is FASTA plus optional target sequence ID, and window behavior is controlled with `-w` and `-s`. Output is a table of window coordinates and metrics (GC%, AT-skew, GC-skew) that can be inspected directly or reused in external plotting tools.
