# jsrc math

数学与统计工具——全部基于 Python 标准库实现，无第三方依赖。

## 子命令

| 子命令 | 说明 |
|--------|------|
| `statistics` | 描述统计：mean, median, mode, min, max, range, var, sd, se, q1, q3, iqr, skewness, kurtosis, cv, 几何均值, 调和均值, 百分位数 |
| `correlation` | Pearson / Spearman 相关系数 + p-value, 协方差 |
| `regression` | 线性/多项式回归 — 系数, R², adj-R², SE, F 检验, t 检验 |
| `ttest` | 单样本 / 独立 (equal/Welch) / 配对 t 检验 |
| `chisquare` | 拟合优度 / 独立性 卡方检验 |
| `anova` | 单因素方差分析 — SS, MS, F, p-value, eta² |
| `nonparametric` | Mann-Whitney U, Wilcoxon 符号秩检验 |
| `distribution` | Normal / t / F / Chi² 的 PDF 和 CDF |
| `kmeans` | K-均值聚类 (K-means++ 初始化) |
| `hcluster` | 凝聚层次聚类 (single/complete/average) |
| `knn` | K 近邻分类/回归 |
| `naivebayes` | 高斯朴素贝叶斯分类 |
| `decisiontree` | 决策树 (Gini / 方差缩减) |
| `randomforest` | 随机森林 (Bagging + 特征子采样) |
| `gbm` | 梯度提升机 (回归) |
| `survival` | Kaplan-Meier 生存估计 + Log-rank 检验 |
| `simulate` | ODE 模拟: SIR, Lotka-Volterra, 一房室 PK, Emax, Gompertz, Logistic |
| `montecarlo` | 蒙特卡洛抽样 (正态分布) |
| `mcmc` | Metropolis-Hastings MCMC |
| `hmm` | 隐马尔可夫模型 — forward / backward / Viterbi |

## 使用示例

```bash
# 描述统计
jsrc math statistics -i data.tsv -c expression

# 相关性
jsrc math correlation -i data.tsv -c age expression -m pearson

# 线性回归
jsrc math regression -i data.tsv -c x y

# 多项式回归 (3 次)
jsrc math regression -i data.tsv -c x y -d 3

# t 检验
jsrc math ttest -i data.tsv -c group1 group2

# 方差分析
jsrc math anova -i data.tsv -g treatment -v response

# K-均值聚类
jsrc math kmeans -i data.tsv -k 5

# 决策树
jsrc math decisiontree --train train.tsv --test test.tsv --target-col y --print-tree

# 随机森林
jsrc math randomforest --train train.tsv --test test.tsv --target-col y -n 100

# 梯度提升
jsrc math gbm --train train.tsv --test test.tsv --target-col y -n 50 --lr 0.1

# 生存分析 (KM + Log-rank)
jsrc math survival -i survival.tsv --time-col time --event-col status --group-col treatment

# SIR 模型模拟
jsrc math simulate -m sir --params 0.3 0.1 --tmax 200 --init 990 10 0

# 一房室 PK 模型
jsrc math simulate -m pk1 --params 0.5 0.05 100 --tmax 48

# MCMC
jsrc math mcmc --data 1.2 1.8 2.1 1.5 --prior-mean 1.5 --prior-sd 2.0 -n 10000

# HMM Viterbi 解码
jsrc math hmm --states Sunny Rainy --observations Walk Shop Clean \
  --trans-probs 0.7 0.3 0.4 0.6 \
  --emit-probs 0.6 0.3 0.1 0.1 0.4 0.5 \
  --start-probs 0.6 0.4
```
