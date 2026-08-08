# jsrc analyze

序列分析层面的常用工具集合：进化树构建（支持 bootstrap）、motif 鉴定、QC 汇总、保守性分析和变异比较。

## phylo

给一组序列，选个算法，就能得到一棵 Newick 树。支持邻接法（NJ）和 UPGMA 两种建树方式，结果可以导出直接用任何树可视化工具打开。适合快速看序列间的聚类关系，或者给更复杂的进化分析打个底。

内置 bootstrap 支持：用 `-n`/`--bootstrap` 指定重采样次数（0 = 关闭，默认 0），`-seed` 指定随机种子（默认 42）。当 bootstrap ≥ 1 时，树的分支会标注支持值。

```bash
jsrc analyze phylo -fa sequences.fa -o tree.nwk -a nj
jsrc analyze phylo -fa seqs.fa -n 200 -seed 42 -o tree.nwk
```

- `-fa`：输入 FASTA。
- `-o`：输出 Newick 树文件。
- `-a`：算法，`nj` 或 `upgma`（默认 `nj`）。
- `-n`/`--bootstrap`：bootstrap 重采样次数（默认 `0`，0 = 关闭）。
- `-seed`：随机种子（默认 `42`）。

## motif

在启动子或者一组序列里找保守的短 motif。可以控制数量（`-nmotifs`）和长度范围（`-minw`/`-maxw`），先粗筛再调参。

```bash
jsrc analyze motif -fa promoters.fa -o motif_out -nmotifs 5 -minw 6 -maxw 12
```

- `-fa`：输入 FASTA。
- `-o`：输出目录。
- `-nmotifs`：motif 数量，默认 `5`。
- `-minw`：最小 motif 宽度，默认 `6`。
- `-maxw`：最大 motif 宽度，默认 `12`。

## qc

组装质量（FASTA）、比对统计（SAM）、变异概览（VCF）、测序深度（FASTQ）一次全出，适合快速判断数据能不能往下走。

```bash
jsrc analyze qc -fa assembly.fa -sam aln.sam -vcf variants.vcf.gz \
  -fq r1.fq.gz r2.fq.gz -gs 520000000 --json
```

- `-fa`：组装 FASTA（contig/N50/GC 等统计）。
- `-sam`：SAM/SAM.GZ（比对率与深度统计）。
- `-vcf`：VCF/VCF.GZ（SNP/INDEL 统计）。
- `-fq`：FASTQ/FASTQ.GZ（reads/bases/depth 统计）。
- `-gs`：基因组大小 bp（与 `-fq` 配合使用估算深度）。
- `--json`：以 JSON 输出。

## msa_consensus

多序列比对完成后，想看共识序列长什么样、每列保守性如何。它会逐列统计碱基频率，输出 consensus 序列和各位置的平均保守度。同时会检查输入序列长度是否差异过大，必要时用 gap 补齐。

```bash
jsrc analyze msa_consensus -fa aligned.fa --json
```

- `-fa`：输入 FASTA（通常为比对结果）。
- `--json`：JSON 输出。

## snpindel

只想比较两条序列的差异，不需要走完整的变异 calling 流程。输入一个含两条序列的 FASTA，直接出 SNP/INDEL 统计结果，适合样本间快速对比。

```bash
jsrc analyze snpindel -fa pair.fa -id1 sampleA -id2 sampleB --json
```

- `-fa`：至少包含两条序列的 FASTA。
- `-id1`：序列 1 的 ID（默认第一条）。
- `-id2`：序列 2 的 ID（默认第二条）。
- `--json`：JSON 输出。
