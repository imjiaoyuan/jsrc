# jsrc plot

## gene

如果你想把基因结构做成可直接汇报/发文的图，这个命令很好用。它根据 GFF 和目标 ID 列表生成清晰的基因结构图。

```bash
jsrc plot gene -gff genes.gff -ids ids.txt -o gene.png -dpi 300
```

- `-gff`：GFF 注释文件。
- `-ids`：基因 ID 列表文件。
- `-o`：输出 PNG 路径。
- `-dpi`：输出分辨率（默认 `300`）。

## exon

当你只想聚焦 exon 层面的结构差异时，用这个命令更直观。

```bash
jsrc plot exon -gff genes.gff -ids ids.txt -o exon.png -dpi 300
```

- `-gff`：GFF 注释文件。
- `-ids`：基因 ID 列表文件。
- `-o`：输出 PNG 路径。
- `-dpi`：输出分辨率（默认 `300`）。

## chromosome

要做染色体尺度分布图时，用它可以快速看到基因在各染色体上的整体布局；也可只画目标子集。

```bash
jsrc plot chromosome -gff genes.gff -ids ids.txt -o chr.png -dpi 300
```

- `-gff`：GFF 注释文件。
- `-ids`：可选基因 ID 过滤文件。
- `-o`：输出 PNG 路径。
- `-dpi`：输出分辨率（默认 `300`）。

## domain

用于展示蛋白结构域排布，适合快速检查结构域顺序、边界和是否存在异常分段。

```bash
jsrc plot domain -tsv domains.tsv -o domain.png -dpi 300
```

- `-tsv`：结构域表格输入。
- `-o`：输出 PNG 路径。
- `-dpi`：输出分辨率（默认 `300`）。

## cis

做顺式元件定位图时，这个命令能快速把 BED 里的位点可视化出来。

```bash
jsrc plot cis -bed motifs.bed -o cis.png -dpi 300
```

- `-bed`：BED 输入文件。
- `-o`：输出 PNG 路径。
- `-dpi`：输出分辨率（默认 `300`）。

## heart

用于快速显示心形曲线的交互式示例。

```bash
jsrc plot heart
```

- 无命令专属参数。

## rose

用于快速显示 3D 玫瑰曲线的交互式示例。

```bash
jsrc plot rose
```

- 无命令专属参数。

## dotplot

想比较两条序列的整体相似性分布，这个命令非常高效。通过精确 k-mer 匹配画点图，可快速发现重复和大尺度结构关系。

```bash
jsrc plot dotplot -fa1 a.fa -fa2 b.fa -k 10 -o d.png -dpi 300
```

- `-fa1`：序列 FASTA 1。
- `-fa2`：序列 FASTA 2。
- `-k`：k-mer 长度（默认 `10`）。
- `-o`：可选输出 PNG（不填则交互显示）。
- `-dpi`：输出分辨率（默认 `300`）。

## circoslite

想快速做一个轻量级环形基因组视图时，用它最方便。输入 FASTA 即可得到窗口化统计的环形可视化。

```bash
jsrc plot circoslite -fa genome.fa -w 100000 -o c.png -dpi 300
```

- `-fa`：基因组 FASTA 输入。
- `-w`：窗口大小（默认 `100000`）。
- `-o`：可选输出 PNG（不填则交互显示）。
- `-dpi`：输出分辨率（默认 `300`）。
