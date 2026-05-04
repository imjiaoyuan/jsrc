# jsrc gs

## build

Start here to assemble a genomic-selection dataset from phenotype + PLINK genotype inputs. It prepares model-ready arrays and IDs so later split/train steps can run directly.

```bash
jsrc gs build -pheno phenotype.txt -plink /path/to/hap1_plink -o data/hap1 --plink-bin plink --n-sim 500 --top-k 2000 --h2 0.5 --seed 42
```

- `-pheno`: phenotype file containing at least `IID` and `PHENO`.
- `-plink`: PLINK prefix (without `.bed/.bim/.fam`).
- `-o`: output dataset directory.
- `--plink-bin`: plink executable path (default: `plink`).
- `--n-sim`: number of simulated samples (default: `500`).
- `--top-k`: top markers used as candidate causal loci (default: `2000`).
- `--h2`: target heritability in simulation (default: `0.5`).
- `--seed`: random seed (default: `42`).

## split

After build, this creates cross-validation splits so evaluation is consistent and reproducible.

```bash
jsrc gs split -i data/hap1 --folds 5 --seed 2024
```

- `-i, --input`: dataset directory containing `y.npy` and `sample_ids.txt`.
- `--folds`: number of CV folds (default: `5`).
- `--seed`: random seed (default: `2024`).

## train

This runs model training and evaluation across CV folds, then writes comparable result tables for model selection.

```bash
jsrc gs train -i data/hap1 -o data/hap1/results --folds 5 --select-k 1000 --models gbdt,rf,et,lr,svm,nb --seed 42
```

- `-i, --input`: dataset directory containing `X.npy`, `y.npy`, and `cv_indices/`.
- `-o, --output`: optional output directory for result CSV files.
- `--folds`: folds to run (default: `5`).
- `--select-k`: top K features selected by ANOVA (default: `1000`).
- `--models`: comma-separated model list from `gbdt,rf,et,ada,dt,lr,svm,nb`.
- `--seed`: random seed (default: `42`).
