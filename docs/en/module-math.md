# jsrc math

Mathematical and statistical tools — all implemented with zero external dependencies.

## commands

| subcommand | description |
|------------|-------------|
| `statistics` | mean, median, mode, min, max, range, var, sd, se, q1, q3, iqr, skewness, kurtosis, cv, geometric mean, harmonic mean, percentiles |
| `correlation` | Pearson / Spearman correlation with p-value, covariance |
| `regression` | Linear or polynomial regression — slope, intercept, R², adj-R², SE, F-test, t-tests |
| `ttest` | One-sample, independent (equal/Welch), paired t-test |
| `chisquare` | Goodness-of-fit and independence chi-squared test |
| `anova` | One-way ANOVA — SS, MS, F, p-value, eta² |
| `nonparametric` | Mann-Whitney U, Wilcoxon signed-rank |
| `distribution` | PDF and CDF for Normal, t, F, Chi² |
| `kmeans` | K-means clustering with K-means++ initialization |
| `hcluster` | Agglomerative hierarchical clustering (single/complete/average linkage) |
| `knn` | K-nearest neighbors classification/regression |
| `naivebayes` | Gaussian Naive Bayes classifier |
| `decisiontree` | Decision tree (Gini / variance reduction) |
| `randomforest` | Bagged random forest with feature subsampling |
| `gbm` | Gradient boosting machine for regression |
| `survival` | Kaplan-Meier estimator and Log-rank test |
| `simulate` | ODE simulation: SIR, Lotka-Volterra, PK one-compartment, Emax, Gompertz, Logistic |
| `montecarlo` | Monte Carlo sampling from normal distribution |
| `mcmc` | Metropolis-Hastings MCMC |
| `hmm` | Hidden Markov Model — forward, backward, Viterbi |

## Examples

```bash
# Descriptive statistics
jsrc math statistics -i data.tsv -c expression
jsrc math statistics -i data.tsv -c 2

# Correlation
jsrc math correlation -i data.tsv -c age expression -m pearson

# Linear regression
jsrc math regression -i data.tsv -c x y

# Polynomial regression (degree 3)
jsrc math regression -i data.tsv -c x y -d 3

# t-test
jsrc math ttest -i data.tsv -c group1 group2
jsrc math ttest -i data.tsv -c height --mu 170

# ANOVA
jsrc math anova -i data.tsv -g treatment -v response

# K-means clustering
jsrc math kmeans -i data.tsv -k 5

# Decision tree
jsrc math decisiontree --train train.tsv --test test.tsv --target-col y --print-tree

# Random forest
jsrc math randomforest --train train.tsv --test test.tsv --target-col y -n 100

# Gradient boosting
jsrc math gbm --train train.tsv --test test.tsv --target-col y -n 50 --lr 0.1

# Survival analysis
jsrc math survival -i survival.tsv --time-col time --event-col status

# Kaplan-Meier with Log-rank test
jsrc math survival -i survival.tsv --time-col time --event-col status --group-col treatment

# ODE model simulation (SIR)
jsrc math simulate -m sir --params 0.3 0.1 --tmax 200 --init 990 10 0

# PK model (one-compartment, oral dose)
jsrc math simulate -m pk1 --params 0.5 0.05 100 --tmax 48 -o pk.csv

# MCMC
jsrc math mcmc --data 1.2 1.8 2.1 1.5 --prior-mean 1.5 --prior-sd 2.0 -n 10000

# HMM Viterbi
jsrc math hmm --states Sunny Rainy --observations Walk Shop Clean \
  --trans-probs 0.7 0.3 0.4 0.6 \
  --emit-probs 0.6 0.3 0.1 0.1 0.4 0.5 \
  --start-probs 0.6 0.4
```
