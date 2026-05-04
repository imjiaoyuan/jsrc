# jsrc gs

## build

这个命令是 GS 流程的起点：把表型和 PLINK 基因型整合成可直接建模的数据集，后续 split/train 可以无缝接上。

```bash
jsrc gs build -pheno phenotype.txt -plink /path/to/hap1_plink -o data/hap1 --plink-bin plink --n-sim 500 --top-k 2000 --h2 0.5 --seed 42
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

数据构建后，用它生成交叉验证划分，保证后续评估流程可复现、可比较。

```bash
jsrc gs split -i data/hap1 --folds 5 --seed 2024
```

- `-i, --input`：数据目录（含 `y.npy` 与 `sample_ids.txt`）。
- `--folds`：交叉验证折数（默认 `5`）。
- `--seed`：随机种子（默认 `2024`）。

## train

这是模型训练与评估主命令，会在多折上运行并输出结果表，方便快速比较不同模型表现。

```bash
jsrc gs train -i data/hap1 -o data/hap1/results --folds 5 --select-k 1000 --models gbdt,rf,et,lr,svm,nb --seed 42
```

- `-i, --input`：数据目录（含 `X.npy`、`y.npy`、`cv_indices/`）。
- `-o, --output`：可选输出目录。
- `--folds`：运行折数（默认 `5`）。
- `--select-k`：ANOVA 选择特征数（默认 `1000`）。
- `--models`：模型列表（逗号分隔），可选 `gbdt,rf,et,ada,dt,lr,svm,nb`。
- `--seed`：随机种子（默认 `42`）。
