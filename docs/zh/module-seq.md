# jsrc seq

## extract

当你手里有基因组 FASTA、GFF 注释和目标 ID，这个命令能一步把目标特征序列提出来，直接得到后续可用的 FASTA。

```bash
jsrc seq extract -fa genome.fa -gff genes.gff -ids ids.txt -o out.fa [-feature CDS] [-match Parent]
```

- `-fa`：基因组 FASTA 文件。
- `-gff`：GFF 注释文件。
- `-ids`：目标 ID 列表（一行一个）。
- `-o`：输出 FASTA 文件。
- `-feature`：提取特征类型，默认 `CDS`。
- `-match`：匹配 ID 的 GFF 属性键，默认 `Parent`。

## rename

不同来源的 FASTA ID 经常不统一，这个命令专门做标准化重命名。既支持 CSV 映射，也支持根据 GFF 关系重命名。

```bash
jsrc seq rename -fa in.fa -mode csv -map mapping.csv -o out.fa
jsrc seq rename -fa in.fa -mode gff -gff genes.gff -parent Parent -o out.fa
```

- `-fa`：输入 FASTA。
- `-mode`：重命名模式，`csv` 或 `gff`（默认 `csv`）。
- `-map`：CSV 映射文件 `old_id,new_id`（`csv` 模式使用）。
- `-gff`：GFF 文件（`gff` 模式使用）。
- `-parent`：GFF 父字段名（`gff` 模式使用）。
- `-o`：输出 FASTA。

## translate

这个命令把“基因组注释空间”快速转到“蛋白空间”：提取 CDS 并翻译成蛋白序列，便于后续结构域和同源分析。

```bash
jsrc seq translate -fa genome.fa -gff genes.gff -id ID -o proteins.fa
```

- `-fa`：基因组 FASTA。
- `-gff`：GFF 注释。
- `-id`：用作基因 ID 的 GFF 属性键。
- `-o`：输出蛋白 FASTA。

## promoter

做顺式元件或启动子相关分析时，这个命令能按目标基因批量提取上下游区域，省去手工坐标处理。

```bash
jsrc seq promoter -fa genome.fa -gff genes.gff -ids genes.txt -o promoters.fa -up 2000 -down 0
```

- `-fa`：基因组 FASTA。
- `-gff`：GFF 注释。
- `-ids`：目标基因 ID 列表。
- `-o`：输出启动子 FASTA。
- `-id`：GFF 中 ID 字段名，默认 `ID`。
- `-feature`：GFF 特征类型，默认 `gene`。
- `-up`：上游长度（bp），默认 `2000`。
- `-down`：下游长度（bp），默认 `0`。

## qc

想先对序列数据做“体检”再进入复杂分析，这个命令很合适。它能快速给出组装与测序层面的核心摘要。

```bash
jsrc seq qc -fa assembly.fa
jsrc seq qc -fq r1.fq.gz r2.fq.gz -gs 520000000 --json
```

- `-fa`：FASTA 输入（组装统计）。
- `-fq`：一个或多个 FASTQ/FASTQ.GZ。
- `-gs`：基因组大小（bp），配合 `-fq` 估算深度。
- `--json`：JSON 输出。

## codon

关注密码子偏好时，用这个命令能直接得到使用频率和 RSCU 结果，适合做表达偏好与进化特征观察。

```bash
jsrc seq codon -fa cds.fa --top 20 --json
```

- `-fa`：CDS FASTA 输入。
- `--top`：显示前 N 个密码子，默认 `20`。
- `--json`：JSON 输出。

## kmer

它适合做序列组成指纹和样本间粗粒度相似性判断。单样本看高频 k-mer，多样本可用于快速比较。

```bash
jsrc seq kmer -fa a.fa b.fa -k 7 --top 30 --json
```

- `-fa`：一个或多个 FASTA 文件。
- `-k`：k-mer 长度，默认 `5`。
- `--top`：单样本时显示前 N 个，默认 `20`。
- `--json`：JSON 输出。

## window

当你需要看序列在局部窗口内的 GC 与偏斜变化，这个命令会给出可直接下游使用的滑窗统计结果。

```bash
jsrc seq window -fa genome.fa -id chr1 -w 1000 -s 200 --head 20 --json
```

- `-fa`：FASTA 输入。
- `-id`：目标序列 ID（默认用最长序列）。
- `-w`：窗口大小，默认 `1000`。
- `-s`：步长，默认 `200`。
- `--head`：只输出前 N 个窗口，默认 `10`。
- `--json`：JSON 输出。
