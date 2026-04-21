# Plot Module

```bash
jsrc plot gene -gff genes.gff -ids ids.txt -o gene.png
```

Use this to generate CDS-based gene structure diagrams for selected IDs. Input is a GFF file plus an ID list file (one gene ID per line). Output is a PNG (`-o`) suitable for reports and figures.

---

```bash
jsrc plot exon -gff genes.gff -ids ids.txt -o exon.png
```

Use this when you need exon-level structure plots from the same style of annotation input. The output PNG gives a cleaner exon-focused view for structure comparison.

---

```bash
jsrc plot chromosome -gff genes.gff -o chr.png
jsrc plot chromosome -gff genes.gff -ids ids.txt -o chr_selected.png
```

Use this to create chromosome-scale maps from annotation. You can render all genes or restrict plotting with an ID file. Output is a PNG that works well for genome-level overview slides.

---

```bash
jsrc plot domain -tsv domains.tsv -o domain.png
```

Use this to draw protein domain architecture from tab-delimited domain annotation input. Output is a PNG figure summarizing domain order and span.

---

```bash
jsrc plot cis -bed motifs.bed -o cis.png
```

Use this to visualize cis-element positions from BED input. The output PNG helps with quick motif distribution inspection across loci.

---

```bash
jsrc plot heart
```

Use this for interactive curve display. It opens a visualization window directly and does not require an output file.

---

```bash
jsrc plot rose
```

Use this for interactive 3D rose rendering. Like `plot heart`, it is display-first and opens directly in an interactive window.

---

```bash
jsrc plot dotplot -fa1 a.fa -fa2 b.fa -k 10
jsrc plot dotplot -fa1 a.fa -fa2 b.fa -k 10 -o d.png
```

Use this to compare two FASTA sequences through exact k-mer match dotplots. You can view interactively or write a PNG with `-o`. It is useful for spotting large repeats or structural similarity patterns quickly.

---

```bash
jsrc plot circoslite -fa genome.fa -w 100000
jsrc plot circoslite -fa genome.fa -w 100000 -o c.png
```

Use this to create a lightweight circular genome view with a GC track. Input is FASTA and window size is set by `-w`; output can be interactive or saved to PNG.
