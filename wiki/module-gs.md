# GS Module

```bash
jsrc gs build -pheno phenotype.txt -plink /path/to/hap1_plink -o data/hap1
```

Use this to build genomic-selection training data from GWAS-style inputs. The phenotype file should be whitespace-delimited with at least `IID` and `PHENO` columns, and the PLINK prefix should point to matching `.bed/.bim/.fam` files. Output includes `X.npy`, `y.npy`, `sample_ids.txt`, and `snp_ids.txt`, ready for split and model training.

---

```bash
jsrc gs split -i data/hap1 --folds 5 --seed 2024
```

Use this to generate cross-validation index files after dataset construction. Input is the dataset directory containing `y.npy` and `sample_ids.txt`; real samples are distributed across folds while simulated samples stay in training indices. Output files are written to `cv_indices/fold_*_train.txt` and `cv_indices/fold_*_test.txt`.

---

```bash
jsrc gs train -i data/hap1 --folds 5 --select-k 1000 --models gbdt,rf,et,lr,svm,nb
```

Use this to train and evaluate models from prepared GS data and CV splits. Input is the dataset directory containing `X.npy`, `y.npy`, and `cv_indices/`; you can choose models and feature-selection size with `--models` and `--select-k`. Output is `results.csv` plus `summary.csv`, which can be used for model comparison and reporting.
