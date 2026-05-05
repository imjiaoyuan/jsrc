# jsrc gs

基因组选择（Genomic Selection）的模拟与建模流程。使用PLINK 基因型数据和表型文件，经过数据构建、交叉验证划分、模型训练与评估。支持 GBDT、随机森林、弹性网络、SVM、朴素贝叶斯等多种模型。

## build

把 PLINK 基因型（bed/bim/fam）和表型文件整合起来，生成可以直接建模的数据集。会根据遗传率（`--h2`）模拟表型，并从候选位点中筛选 tag marker，输出 `.npy` 格式的矩阵和样本列表。`--plink-bin` 指定 plink 可执行文件的路径，`--n-sim` 控制模拟样本数。

```bash
jsrc gs build -pheno phenotype.txt -plink /path/to/hap1_plink \
  -o data/hap1 --plink-bin plink --n-sim 500 --top-k 2000 --h2 0.5 --seed 42
```

- `-pheno`：表型文件，至少包含 `IID` 和 `PHENO` 列。
- `-plink`：PLINK 前缀（不含 `.bed/.bim/.fam`）。
- `-o`：输出数据目录。
- `--plink-bin`：plink 可执行文件路径（默认 `plink`）。
- `--n-sim`：模拟样本数（默认 `500`）。
- `--top-k`：候选因果位点 top marker 数（默认 `2000`）。
- `--h2`：模拟遗传率（默认 `0.5`）。
- `--seed`：随机种子（默认 `42`）。

## split

数据准备好后，用这个命令生成交叉验证的划分方案，保证每次训练/评估都在同样的 fold 上进行，结果可比。默认 5 折，可以调。

```bash
jsrc gs split -i data/hap1 --folds 5 --seed 2024
```

- `-i, --input`：数据目录（含 `y.npy` 与 `sample_ids.txt`）。
- `--folds`：交叉验证折数（默认 `5`）。
- `--seed`：随机种子（默认 `2024`）。

## train

训练与评估的主命令。会在各折上分别训练指定模型，计算预测性能，输出结果表。支持模型列表用逗号分隔，可选 gbdt、rf、et、ada、dt、lr、svm、nb。`--select-k` 用 ANOVA 筛选特征数控制输入维度。

```bash
jsrc gs train -i data/hap1 -o data/hap1/results \
  --folds 5 --select-k 1000 --models gbdt,rf,et,lr,svm,nb --seed 42
```

- `-i, --input`：数据目录（含 `X.npy`、`y.npy`、`cv_indices/`）。
- `-o, --output`：可选输出目录。
- `--folds`：运行折数（默认 `5`）。
- `--select-k`：ANOVA 选择特征数（默认 `1000`）。
- `--models`：模型列表（逗号分隔），可选 `gbdt,rf,et,ada,dt,lr,svm,nb`。
- `--seed`：随机种子（默认 `42`）。
