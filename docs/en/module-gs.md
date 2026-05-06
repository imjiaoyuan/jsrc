# jsrc gs

Genomic selection simulation and modeling pipeline. Uses PLINK genotype data and phenotype files through data construction, cross-validation splitting, model training, and evaluation. Supports GBDT, random forest, elastic net, SVM, and naive Bayes.

## build

Integrates PLINK genotypes (bed/bim/fam) with phenotype data into a modeling-ready dataset. Simulates phenotypes based on heritability (`--h2`), selects tag markers from candidate loci, and outputs `.npy` matrices and sample IDs. `--plink-bin` specifies the plink executable, `--n-sim` controls simulated sample size.

Example input (`phenotype.txt`):

```txt
IID	PHENO
sample1	1
sample2	0
sample3	1
```

```bash
jsrc gs build -pheno phenotype.txt -plink /path/to/hap1_plink \
  -o data/hap1 --plink-bin plink --n-sim 500 --top-k 2000 --h2 0.5 --seed 42
```

- `-pheno`: phenotype file with at least `IID` and `PHENO` columns.
- `-plink`: PLINK prefix (without `.bed/.bim/.fam`).
- `-o`: output data directory.
- `--plink-bin`: plink executable path (default: `plink`).
- `--n-sim`: number of simulated samples (default: `500`).
- `--top-k`: top markers considered as candidate causal loci (default: `2000`).
- `--h2`: target heritability (default: `0.5`).
- `--seed`: random seed (default: `42`).

## split

Creates cross-validation folds after data construction, ensuring consistent and reproducible evaluation across runs. Default is 5 folds.

```bash
jsrc gs split -i data/hap1 --folds 5 --seed 2024
```

- `-i, --input`: dataset directory containing `y.npy` and `sample_ids.txt`.
- `--folds`: number of CV folds (default: `5`).
- `--seed`: random seed (default: `2024`).

## train

Trains and evaluates models across CV folds. Runs specified models on each fold, computes prediction performance, and outputs results for comparison. Model list is comma-separated; available options include gbdt, rf, et, ada, dt, lr, svm, nb. `--select-k` controls input dimensionality via ANOVA feature selection.

```bash
jsrc gs train -i data/hap1 -o data/hap1/results \
  --folds 5 --select-k 1000 --models gbdt,rf,et,lr,svm,nb --seed 42
```

- `-i, --input`: dataset directory containing `X.npy`, `y.npy`, and `cv_indices/`.
- `-o, --output`: optional output directory.
- `--folds`: folds to run (default: `5`).
- `--select-k`: top K features selected by ANOVA (default: `1000`).
- `--models`: comma-separated model list, options: `gbdt,rf,et,ada,dt,lr,svm,nb`.
- `--seed`: random seed (default: `42`).
