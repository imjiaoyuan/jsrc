# jsrc genome

基因组级别的分析功能。`jsrc genome` 涵盖了基因组统计、特征检测、比较分析、进化分析和注释辅助等常用功能。

## cpg

CpG 岛是基因组中 CpG 二核苷酸密度和 GC 含量较高的区域，通常位于基因启动子附近，与基因调控密切相关。这个命令使用经典滑窗法（Gardiner-Garden & Frommer 1987）预测 CpG 岛。

当一个窗口满足 GC% ≥ 50% 且观测/预期 CpG 比值 ≥ 0.6 时，被视为候选 CpG 岛区域。相邻满足条件的窗口会被合并，合并后长度不足 `--min-len` 的区域会被过滤掉。

```bash
jsrc genome cpg -fa genome.fa
jsrc genome cpg -fa genome.fa --window 200 --min-len 200 --min-gc 55 --json
```

## orf

ORF 查找是对未注释序列进行基因预测的第一步。给定 FASTA 文件，这个命令扫描 ATG 到终止密码子的开放阅读框，报告坐标、长度、读框和翻译蛋白序列。

默认只搜索读框 1，报告 ≥ 100 nt 的 ORF。用 `--all-frames` 搜索全部三个正链读框，用 `--min-len` 调整长度阈值。`--top N` 每条序列只保留最长的 N 个 ORF。

```bash
jsrc genome orf -fa genome.fa --min-len 300 --all-frames
jsrc genome orf -fa contigs.fa --top 5 --json
```

## promoter

研究基因调控的时候经常要看启动子区域。比如你想知道某几个基因上游 2kb 有没有某个转录因子结合位点——这时候就得先把这些区域批量提取出来。

这个命令就是干这个的：给基因组、GFF、基因 ID 列表，它自动计算坐标并把上下游序列取出来。

示例输入（`genes.txt`）：

```txt
GENE001
GENE002
GENE003
```

默认向上游取 2000bp，下游不取（设为 0）。你也可以用 `-up` 和 `-down` 自由调整。

```bash
jsrc genome promoter -fa genome.fa -gff genes.gff -ids genes.txt -o promoters.fa -up 1500 -down 500
```

如果你的 GFF 里基因特征的标签名不叫 `gene`（比如有的数据集用 `mRNA`），记得设一下 `-feature`。

## repeat

查找基因组序列中的简单串联重复（SSR / 微卫星 / STR）。扫描指定单元长度范围内、重复次数达到阈值的串联重复基序。

默认设置查找单核苷酸到六核苷酸重复（单元长度 1–6），至少重复 3 次。常用于微卫星标记开发和重复序列注释。

```bash
jsrc genome repeat -fa genome.fa
jsrc genome repeat -fa genome.fa --min-unit 2 --max-unit 4 --min-reps 5 --json
```

## island

基因组岛检测通过 GC 含量偏离来识别可能的水平基因转移区域、病原岛或其他外源 DNA 片段。这个命令使用滑窗法扫描 GC 含量异常的区域。

当窗口的 GC 含量超过设定阈值时，被标记为候选岛区域。相邻的候选窗口会被合并成一个岛。可以用 `--min-length` 过滤掉太短的区域。

```bash
jsrc genome island -fa genome.fa
jsrc genome island -fa genome.fa --window 5000 --step 1000 --gc-threshold 0.6 --min-length 10000 --json
```

## palindrome

回文序列（反向重复）在基因组中常与转座子、限制性内切酶识别位点、发夹结构等相关。这个命令查找序列中的回文结构。

回文结构由两个反向互补的臂和中间的间隔组成。可以设置臂长范围（`--min-arm`, `--max-arm`）和最大间隔长度（`--max-gap`）。

```bash
jsrc genome palindrome -fa genome.fa
jsrc genome palindrome -fa genome.fa --min-arm 8 --max-arm 30 --max-gap 20 --top 100 --json
```

## stats

基因组组装质量评估的基础指标。这个命令计算 N50/L50、总长度、序列数、gap 统计和 GC 含量。

N50 是加权中位数长度——把所有序列按长度排序，从长到短累加，当累加长度达到总长度一半时对应的序列长度就是 N50。L50 是达到 N50 时累加的序列条数。这两个指标越大，说明组装连续性越好。

```bash
jsrc genome stats -fa assembly.fa
jsrc genome stats -fa assembly.fa --json
```

## gc-skew

累积 GC 偏斜分析用于预测细菌基因组的复制起点（oriC）和终点（ter）。GC 偏斜定义为 (G-C)/(G+C)，在复制起点附近通常有明显的极小值。

这个命令计算滑窗累积 GC 偏斜，输出每个窗口的位置和累积偏斜值。可以用绘图工具可视化，找到曲线的最低点。

```bash
jsrc genome gc-skew -fa genome.fa
jsrc genome gc-skew -fa genome.fa --window 10000 --step 5000 --json
```

## window

滑窗 GC 和 AT 偏斜分析。这个命令在指定窗口大小和步长下，计算每个窗口的 GC 含量、GC 偏斜和 AT 偏斜。

GC 偏斜 = (G-C)/(G+C)，AT 偏斜 = (A-T)/(A+T)。这些指标可以揭示基因组的局部组成特征和复制偏好。

```bash
jsrc genome window -fa genome.fa
jsrc genome window -fa genome.fa --window 50000 --step 10000 --json
```

## codon

密码子使用频率和 RSCU（相对同义密码子使用度）分析。输入 CDS 序列的 FASTA，统计每个密码子的出现次数并计算 RSCU。

RSCU = 观测频率 / 期望频率（假设同义密码子均匀使用）。RSCU > 1 表示该密码子使用频率高于平均，< 1 表示低于平均。

可选功能：
- `--cai`：计算 CAI（密码子适应指数），需要提供参考基因集（通常是高表达基因）
- `--enc`：计算 ENC（有效密码子数），范围 20-61，值越小表示密码子偏好性越强

```bash
jsrc genome codon -fa cds.fa --top 20
jsrc genome codon -fa cds.fa --cai highly_expressed.fa --enc --json
```

## distance

计算多序列比对中序列间的成对遗传距离。支持四种距离模型：

- **hamming**：汉明距离，不同位点的数量
- **p**：p-距离，不同位点的比例
- **jc**：Jukes-Cantor 距离，考虑多重替换的校正
- **k2p**：Kimura 2-参数距离，区分转换和颠换

输入必须是已对齐的序列（等长）。

```bash
jsrc genome distance -fa aligned.fa --method p
jsrc genome distance -fa aligned.fa --method k2p --json
```

## kaks

计算两条对齐 CDS 序列的 Ka/Ks 比率。Ka 是非同义替换率，Ks 是同义替换率，Ka/Ks（ω）反映选择压力：

- ω < 1：纯化选择（负选择）
- ω = 1：中性进化
- ω > 1：正选择

输入必须是恰好两条已对齐的 CDS 序列，长度必须是 3 的倍数。

```bash
jsrc genome kaks -fa aligned_cds.fa
jsrc genome kaks -fa aligned_cds.fa --json
```

## density

计算基因或其他特征沿基因组的密度分布。这个命令读取基因组 FASTA 和 GFF 注释，在滑窗中统计特征数量、密度（每 kb 特征数）和覆盖率。

可以用 `--feature-type` 指定要统计的特征类型（如 gene、CDS、exon）。适合可视化基因分布的不均匀性。

```bash
jsrc genome density -fa genome.fa -gff genes.gff
jsrc genome density -fa genome.fa -gff genes.gff --feature-type CDS --window 20000 --step 10000 --json
```

## motif-scan

扫描基因组中的 DNA motif。支持 IUPAC 简并碱基代码（R=A/G, Y=C/T, N=任意等），可以设置允许的错配数。

常用于转录因子结合位点预测、限制性内切酶位点查找等。

```bash
jsrc genome motif-scan -fa genome.fa -m TATAAA
jsrc genome motif-scan -fa genome.fa -m GCRWTG --mismatch 1 --top 50 --json
```

## ani

基于 k-mer 的平均核苷酸一致性（ANI）计算。ANI 是衡量两个基因组相似度的标准指标，常用于物种界定（ANI > 95% 通常认为是同一物种）。

这个命令使用 Jaccard 相似度（共享 k-mer 数 / 总 k-mer 数）作为 ANI 的近似估计，无需序列比对，速度快。

```bash
jsrc genome ani -fa genome1.fa genome2.fa
jsrc genome ani -fa genome1.fa genome2.fa -k 21 --json
```

## compare

基于全局比对的基因组比较和差异统计。使用 edlib 库进行高效的全局比对，计算编辑距离、一致性和差异位点。

**注意**：此命令需要安装 edlib：`pip install edlib`

```bash
jsrc genome compare -fa genome1.fa genome2.fa
jsrc genome compare -fa genome1.fa genome2.fa --json
```
