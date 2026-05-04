# jsrc analyze

## phylo

想快速看一组序列的进化关系，这个命令最直接。输入 FASTA，选择算法，输出 Newick 树文件，后续用任意树可视化工具都能打开。

```bash
jsrc analyze phylo -fa sequences.fa -o tree.nwk -a nj
```

- `-fa`：输入 FASTA。
- `-o`：输出 Newick 树文件。
- `-a`：算法，`nj` 或 `upgma`（默认 `nj`）。

## motif

需要在启动子或序列集合里找 motif 时，用这个命令很顺手。你可以同时控制 motif 数量和长度范围，适合先粗筛再细化。

```bash
jsrc analyze motif -fa promoters.fa -o motif_out -nmotifs 5 -minw 6 -maxw 12
```

- `-fa`：输入 FASTA。
- `-o`：输出目录。
- `-nmotifs`：motif 数量，默认 `5`。
- `-minw`：最小 motif 宽度，默认 `6`。
- `-maxw`：最大 motif 宽度，默认 `12`。

## qc

把它当成数据体检入口就行：组装、比对、变异、测序深度都能一次性给出概览。适合在进入复杂分析前先看整体质量。

```bash
jsrc analyze qc -fa assembly.fa -sam aln.sam -vcf variants.vcf.gz -fq r1.fq.gz r2.fq.gz -gs 520000000 --json
```

- `-fa`：组装 FASTA（contig/N50/GC 等统计）。
- `-sam`：SAM/SAM.GZ（比对率与深度统计）。
- `-vcf`：VCF/VCF.GZ（SNP/INDEL 统计）。
- `-fq`：FASTQ/FASTQ.GZ（reads/bases/depth 统计）。
- `-gs`：基因组大小 bp（与 `-fq` 配合使用）。
- `--json`：以 JSON 输出。

## msa_consensus

做完多序列比对后，想看共识序列和保守性分布，用它可以很快得到一个清晰摘要，方便判断比对质量是否稳定。

```bash
jsrc analyze msa_consensus -fa aligned.fa --json
```

- `-fa`：输入 FASTA（通常为比对结果）。
- `--json`：JSON 输出。

## snpindel

如果你只想比较两条序列差异，它会直接给出 SNP/INDEL 的核心统计，省去额外流程搭建，特别适合样本间快速对比。

```bash
jsrc analyze snpindel -fa pair.fa -id1 sampleA -id2 sampleB --json
```

- `-fa`：至少包含两条序列的 FASTA。
- `-id1`：序列 1 的 ID（默认第一条）。
- `-id2`：序列 2 的 ID（默认第二条）。
- `--json`：JSON 输出。

## bootstrap_phylo

当你希望系统树不只是“长得像”，而是带有分支置信度时，就用这个命令。它会做 bootstrap 重采样并输出带支持值的树。

```bash
jsrc analyze bootstrap_phylo -fa seqs.fa -n 200 -seed 42 -o boot.nwk
```

- `-fa`：输入 FASTA。
- `-n`：bootstrap 重采样次数，默认 `100`。
- `-seed`：随机种子，默认 `42`。
- `-o`：可选输出 Newick 文件。
