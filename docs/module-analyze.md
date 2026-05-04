# Analyze Module

```bash
jsrc analyze phylo -fa sequences.fa -o tree.nwk -a nj
jsrc analyze phylo -fa sequences.fa -o tree.nwk -a upgma
```

Use this to build a phylogenetic tree from FASTA sequences. Choose `nj` or `upgma` with `-a`, and the result is written as a Newick file (`-o`) that can be opened in any standard tree viewer.

---

```bash
jsrc analyze motif -fa promoters.fa -o motif_out -nmotifs 5 -minw 6 -maxw 12
```

Use this to perform motif discovery from sequence input. The FASTA file is provided with `-fa`, and motif count/size controls are set with `-nmotifs`, `-minw`, and `-maxw`. Results are written under the output directory (`-o`) for downstream interpretation.

---

```bash
jsrc analyze qc -fa assembly.fa
jsrc analyze qc -sam aln.sam
jsrc analyze qc -vcf variants.vcf.gz
jsrc analyze qc -fq r1.fq.gz r2.fq.gz -gs 520000000
jsrc analyze qc -fa assembly.fa -sam aln.sam -vcf variants.vcf.gz --json
```

Use this as a single entry point for assembly/mapping/variant/read-depth summaries. You can provide FASTA, SAM, VCF, and FASTQ in any useful combination, and add `-gs` for depth estimation from read bases. Output is terminal-first and `--json` gives structured output for workflow integration.

---

```bash
jsrc analyze msa_consensus -fa aligned.fa
```

Use this to get a consensus sequence and conservation summary from aligned FASTA input. The output reports consensus text and conservation-level statistics, which is helpful for checking alignment quality quickly.

---

```bash
jsrc analyze snpindel -fa pair.fa -id1 sampleA -id2 sampleB
```

Use this for pairwise sequence difference summaries. Input is a FASTA with at least two sequences, optionally selecting the target pair with `-id1` and `-id2`. Output includes SNP count, INDEL bases/events, and aligned-length metrics.

---

```bash
jsrc analyze bootstrap_phylo -fa seqs.fa -n 200 -seed 42 -o boot.nwk
```

Use this to add bootstrap support to NJ phylogeny estimation. Input is FASTA with at least three sequences, and bootstrap repetitions are controlled by `-n`. The output Newick file includes support values and can be used directly in tree-visualization tools.
