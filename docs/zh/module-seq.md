# jsrc seq

序列操作是日常最绕不开的事。`jsrc seq` 涵盖了提取、重命名、翻译、启动子、质控、密码子偏好、k-mer 指纹、Entrez 下载、酶切模拟、滑窗统计这些常用功能。

## extract

做基因组注释的时候最常遇到的一个场景：你手里有完整的基因组 FASTA 和 GFF 注释，但你想专门把某几个基因的 CDS 提出来做后续分析。手动去 GFF 里找坐标然后取序列，偶尔一两个还行，多了简直折磨。

这个命令就是干这个的。给基因组、GFF、和一份目标 ID 列表（一行一个），它就按特征类型去提取对应的序列。默认是提 CDS，你也可以用 `-feature` 改成 mRNA 或者其他类型。匹配 ID 的逻辑默认查 GFF 的 `Parent` 属性，如果你的 GFF 用的是别的字段，改 `-match` 就行。

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

## promoter

研究基因调控的时候经常要看启动子区域。比如你想知道某几个基因上游 2kb 有没有某个转录因子结合位点——这时候就得先把这些区域批量提取出来。

这个命令就是干这个的：给基因组、GFF、基因 ID 列表，它自动计算坐标并把上下游序列取出来。默认向上游取 2000bp，下游不取（设为 0）。你也可以用 `-up` 和 `-down` 自由调整。

```bash
jsrc seq promoter -fa genome.fa -gff genes.gff -ids genes.txt -o promoters.fa -up 1500 -down 500
```

如果你的 GFF 里基因特征的标签名不叫 `gene`（比如有的数据集用 `mRNA`），记得设一下 `-feature`。

## qc

做大规模分析前我总是习惯先看一眼数据质量。这个命令就是用来快速"体检"的——它不替代 FastQC 那些深度报告，但胜在快，一条命令下去基本概况就有了。

支持 FASTA 和 FASTQ（包括 gzip 压缩）。对 FASTA 它会统计序列条数、总长度、N50/N90、GC 含量、N 比率。对 FASTQ 它会算 reads 数、总碱基数、平均读长。如果给了基因组大小（`-gs`），还会估算测序深度。

```bash
jsrc seq qc -fa assembly.fa
jsrc seq qc -fq r1.fq.gz r2.fq.gz -gs 520000000 --json
```

## codon

密码子偏好是一个很有意思的角度。不同物种、甚至同一个基因组上的不同基因，密码子使用模式都可能不一样。这种偏好背后有选择压力、突变偏好、tRNA 丰度各种因素。

这个命令就是算密码子使用频率的。输入 CDS 序列的 FASTA，它会统计每个密码子的出现次数并计算 RSCU（相对同义密码子使用度）。默认显示使用频率最高的 20 个，想看更多用 `--top` 调整。

```bash
jsrc seq codon -fa cds.fa --top 20 --json
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

## window

这个命令解决的是一个很经典的问题：全局的 GC 含量是一个平均值，但基因组上的 GC 分布往往不均匀——某些区域（比如 CpG 岛附近）GC 含量就高，着丝粒附近就低。滑窗分析就是在一个个局部窗口里看这些变化。

命令的逻辑很简单：指定窗口大小和步长，程序从序列起始位置开始滑动，在每个窗口里算 GC 含量和 GC 偏斜（(G-C)/(G+C)）。默认取最长的序列来分析，你也可以用 `-id` 指定某条序列。`--head` 可以只预览前 N 个窗口。

```bash
jsrc seq window -fa genome.fa -w 100000 -s 20000 --head 20
jsrc seq window -fa genome.fa -id chr1 -w 1000 -s 200 --json
```
