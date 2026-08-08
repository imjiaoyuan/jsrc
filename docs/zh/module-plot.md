# jsrc plot

基因结构图、染色体分布、蛋白结构域、顺式元件、dotplot、环形基因组视图。全部基于 matplotlib，输出可直接用于汇报或论文配图。

## gene

根据 GFF 注释和目标基因 ID 列表，画出基因的结构示意图（含 UTR、CDS、内含子）。适合展示某个基因家族或一组基因的结构比较。

示例输入（`ids.txt`）：

```txt
GENE001
GENE002
GENE003
```

```bash
jsrc plot gene -gff genes.gff -ids ids.txt -o gene.png -dpi 300
```

- `-gff`：GFF 注释文件。
- `-ids`：基因 ID 列表文件。
- `-o`：输出 PNG 路径。
- `-dpi`：输出分辨率（默认 `300`）。

## exon

跟 gene 类似但聚焦在外显子层面的结构差异。比 gene 图更精细，适合看可变剪接或外显子获得/丢失。

```bash
jsrc plot exon -gff genes.gff -ids ids.txt -o exon.png -dpi 300
```

- `-gff`：GFF 注释文件。
- `-ids`：基因 ID 列表文件。
- `-o`：输出 PNG 路径。
- `-dpi`：输出分辨率（默认 `300`）。

## chromosome

染色体尺度的分布图。可以展示所有基因在染色体上的布局，或者只高亮一部分目标基因。适合做基因组层面 overview。

```bash
jsrc plot chromosome -gff genes.gff -ids ids.txt -o chr.png -dpi 300
```

- `-gff`：GFF 注释文件。
- `-ids`：可选基因 ID 过滤文件。
- `-o`：输出 PNG 路径。
- `-dpi`：输出分辨率（默认 `300`）。

## domain

展示蛋白结构域的排布。输入表格需包含序列 ID、结构域名称、起始和终止位置，程序按比例画出每个蛋白的结构域排列。适合批量检查结构域顺序、边界和异常分段。

示例输入（`domains.tsv`）：

```tsv
protein	domain	start	end
ProteinA	Pkinase	10	260
ProteinA	WD40	300	400
ProteinB	LRR	5	80
```

```bash
jsrc plot domain -tsv domains.tsv -o domain.png -dpi 300
```

- `-tsv`：结构域表格输入。
- `-o`：输出 PNG 路径。
- `-dpi`：输出分辨率（默认 `300`）。

## cis

把 BED 格式的顺式元件位点可视化到序列坐标上，适合展示启动子区域的 motif 分布。

示例输入（`motifs.bed`）：

```bed
chr1	100	150	MOTIF1
chr1	300	320	MOTIF2
chr2	50	80	MOTIF1
```

```bash
jsrc plot cis -bed motifs.bed -o cis.png -dpi 300
```

- `-bed`：BED 输入文件。
- `-o`：输出 PNG 路径。
- `-dpi`：输出分辨率（默认 `300`）。

## dotplot

通过精确 k-mer 匹配比较两条序列的整体相似性。每条序列的 k-mer 位置作为坐标轴，匹配点形成点图模式——对角线表示共线性，散点或重复模式提示重排或重复。适合快速发现结构变异和大尺度序列关系。

```bash
jsrc plot dotplot -fa1 a.fa -fa2 b.fa -k 10 -o d.png -dpi 300
```

- `-fa1`：序列 FASTA 1。
- `-fa2`：序列 FASTA 2。
- `-k`：k-mer 长度（默认 `10`）。
- `-o`：可选输出 PNG（不填则交互显示）。
- `-dpi`：输出分辨率（默认 `300`）。

## circoslite

轻量级环形基因组视图。输入 FASTA，按窗口统计 GC 含量等指标，生成环形图。不需要复杂的配置——一个 FASTA 文件就够了。

```bash
jsrc plot circoslite -fa genome.fa -w 100000 -o c.png -dpi 300
```

- `-fa`：基因组 FASTA 输入。
- `-w`：窗口大小（默认 `100000`）。
- `-o`：可选输出 PNG（不填则交互显示）。
- `-dpi`：输出分辨率（默认 `300`）。
