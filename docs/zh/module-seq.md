# jsrc seq

序列操作是日常最绕不开的事。`jsrc seq` 涵盖了提取、重命名、翻译、蛋白理化分析、k-mer 指纹、Entrez 下载、酶切模拟、序列复杂度、MSA 信息熵、双序列比对、格式转换和随机序列生成这些常用功能。（质控已迁移到 `jsrc analyze qc`。）

基因组级别的分析功能（如 ORF 查找、CpG 岛预测、启动子提取、串联重复、密码子使用、滑窗统计等）已迁移到 [genome 模块](./module-genome.md)。

## extract

做基因组注释的时候最常遇到的一个场景：你手里有完整的基因组 FASTA 和 GFF 注释，但你想专门把某几个基因的 CDS 提出来做后续分析。手动去 GFF 里找坐标然后取序列，偶尔一两个还行，多了简直折磨。

这个命令就是干这个的。给基因组、GFF、和一份目标 ID 列表（一行一个），它就按特征类型去提取对应的序列。默认是提 CDS，你也可以用 `-feature` 改成 mRNA 或者其他类型。匹配 ID 的逻辑默认查 GFF 的 `Parent` 属性，如果你的 GFF 用的是别的字段，改 `-match` 就行。

示例输入（`ids.txt`）：

```txt
GENE001
GENE002
GENE003
```

```bash
jsrc seq extract -fa genome.fa -gff genes.gff -ids ids.txt -o out.fa
```

想提 mRNA 的话：

```bash
jsrc seq extract -fa genome.fa -gff genes.gff -ids ids.txt -feature mRNA -match ID -o mrnas.fa
```

## rename

这个功能的起源挺实在的：不同来源的数据 ID 格式五花八门，有时候你从 NCBI 下的一个物种和自己测序的数据命名习惯完全不一样，但你想把它们放一起分析，这时候 ID 统一就是前提。

两种模式。`csv` 模式最直接——给个两列的 CSV，左边旧 ID，右边新 ID，程序照着替换。`gff` 模式更聪明一点：你给一个 GFF 文件，它根据父子关系来重命名（比如把序列 ID 改成基因名）。具体用什么属性来关联，用 `-parent` 指定。

示例输入（`mapping.csv`）：

```csv
old_id,new_id
GENE001,AT1G01010
GENE002,AT1G01020
GENE003,AT1G01030
```

```bash
jsrc seq rename -fa in.fa -mode csv -map mapping.csv -o out.fa
jsrc seq rename -fa in.fa -mode gff -gff genes.gff -parent Parent -o out.fa
```

## translate

做跨物种比较或者想找蛋白结构域的时候，你需要的其实是氨基酸序列而不是核苷酸。这个命令就是做"基因组注释→蛋白序列"的转换：读入基因组 FASTA 和 GFF，提取 CDS，翻译成蛋白，输出 FASTA。

它需要的参数很简洁，就是基因组、注释、基因 ID 对应的 GFF 属性键、输出文件。

```bash
jsrc seq translate -fa genome.fa -gff genes.gff -id ID -o proteins.fa
```

## kmer

k-mer 可以说是序列分析里最基础但也最强大的特征之一了。它能做的事情很多——评估序列复杂性、做基因组指纹、快速比较样本间的相似度。

处理单个 FASTA 时，它会统计高频 k-mer 及频率，让你快速了解序列组成特征。处理多个 FASTA 时，它会计算两两之间的余弦距离，形成一个距离矩阵——这在快速筛查哪些样本比较相似时非常直观。k-mer 长度用 `-k` 设，默认 5。

```bash
jsrc seq kmer -fa genome.fa --top 30
jsrc seq kmer -fa a.fa b.fa c.fa -k 7
```

## fetch

写这个功能主要是因为每次要在 NCBI 下载序列都有点烦——打开网页、搜索、勾选、下载，重复几次就很想拍桌子。这个命令直接在终端按 accession ID 拉数据，支持 fasta 和 genbank 两种格式。

用起来很简单，给 ID 就行，多个 ID 用空格隔开或者放在文件里一行一个。NCBI 要求传 `--email`，记得加上。不指定 `-o` 时默认输出到标准输出，适合接管道做进一步处理。

```bash
jsrc seq fetch -ids NM_001301717 NR_146152 --email me@example.com -o sequences.fa
jsrc seq fetch -ids ids.txt --format genbank --email me@example.com --json
```

## digest

这个功能完全是"当时做实验需要，干脆写一个"的产物。做克隆或者载体构建的时候，经常需要模拟酶切——你想用 EcoRI 和 HindIII 切一个质粒，想知道会得到哪些片段、长度分别是多少。以前我都是去网页上找工具，后来想，既然 Biopython 的 Restriction 模块本来就有上千种酶的数据库，为什么不直接在终端里做呢？

于是就有了这个命令。它用 Biopython 自带的 1088 种限制性内切酶数据，在序列上找酶切位点，然后计算片段长度。支持线性和环状两种模式——环状 DNA（质粒）的片段计算方式跟线性不一样，程序会自动处理。还可以设 `--min-size` 过滤掉太小的片段。

```bash
jsrc seq digest -fa plasmid.fa -e EcoRI,HindIII --circular --json
jsrc seq digest -fa seq.fa -e EcoRI --min-size 50
```

## complexity

计算每条序列的三种互补复杂度指标：

- **Shannon 熵** — 核苷酸组成的信息论多样性
- **语言复杂度** — 观测到的不同 k-mer 数占理论可能 k-mer 数的比例（k = 1–6）
- **DUST 分值** — 低复杂度屏蔽分值，大于 7 通常提示重复/低复杂度区域

适合在比对或组装前过滤低复杂度序列。

```bash
jsrc seq complexity -fa sequences.fa
jsrc seq complexity -fa sequences.fa --json
```

## entropy

计算多序列比对（MSA）每列的 Shannon 熵和保守性。熵值高的位置变异大，熵值低的位置保守。适合识别保守结构域、功能位点，或设计简并引物。

输入需要是已对齐的 FASTA（所有序列等长）。`--summary` 跳过逐列输出，只打印均值统计。

```bash
jsrc seq entropy -fa aligned.fa
jsrc seq entropy -fa aligned.fa --summary
jsrc seq entropy -fa aligned.fa --json
```

## protparam

翻译完蛋白之后，自然想知道它们的理化性质。给一个蛋白序列的 FASTA 文件，这个命令会输出每个蛋白的核心指标：分子量、等电点（pI）、消光系数、不稳定指数、脂肪族指数、GRAVY（亲水性）、芳香性、以及二级结构分数（螺旋/转角/折叠）。还可以指定 pH 值算净电荷。

底层用的是 Biopython 的 `ProteinAnalysis`，不需要额外依赖。

```bash
jsrc seq protparam -fa proteins.fa
jsrc seq protparam -fa proteins.fa --json
jsrc seq protparam -fa proteins.fa --ph 7.4           # 算 pH 7.4 时的净电荷
```

## primer

下单引物之前先看看质量——一次输出熔解温度、GC 含量、GC 夹和发卡风险。短引物（< 14 nt）用 Wallace 规则，长引物用最近邻热力学方法，可配置引物浓度。

```bash
jsrc seq primer -fa primers.fa
jsrc seq primer -fa primers.fa --conc 500 --json
```

- `-fa`：引物序列 FASTA 文件。
- `--conc`：最近邻 Tm 计算的引物浓度 nM（默认 `250`）。
- `--json`：JSON 输出。

## align

无需额外安装任何东西就能做双序列比对。用的是 Biopython 的 `PairwiseAligner`（C 实现，大多数场景下速度够用）。支持全局和局部比对，可自定义匹配/错配/空位罚分，也可以输出多个最优比对结果。

两种输入方式：两个独立的 FASTA 文件（`-fa1` + `-fa2`），或者一个包含至少两条序列的 FASTA（`-fa`）。`--score-only` 可以快速得到纯分值，方便批量比较。

```bash
jsrc seq align -fa1 seq1.fa -fa2 seq2.fa
jsrc seq align -fa both.fa --mode local --top 3
jsrc seq align -fa1 a.fa -fa2 b.fa --match 2 --mismatch -1 --gap-open -2 --score-only
```

## convert

工具箱里最简单的命令——就一行 `Bio.SeqIO.convert()`。在 Biopython 支持的所有格式之间互转：FASTA、GenBank、EMBL、Swiss-Prot 等等。不用记每个格式专用的转换工具。

```bash
jsrc seq convert -i genome.gbk --from genbank --to fasta -o genome.fa
jsrc seq convert -i proteins.swiss --from swiss --to fasta -o proteins.fa
```

## random

生成模拟序列，用于测试、基准测试或模拟分析。DNA 模式可精确控制 GC 含量，也支持生成蛋白序列。种子可复现，输出可选写入文件或打印到标准输出。

```bash
jsrc seq random -t dna -n 10 -l 1000 --gc 0.45 --seed 123 -o sim.fa
jsrc seq random -t protein -n 5 -l 300                    # 输出到标准输出
```
