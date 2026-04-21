from __future__ import annotations

import os
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import f_classif
from sklearn.linear_model import RidgeCV


def _run_ld_pruning(plink_bin: str, input_prefix: str, out_dir: Path) -> str:
    prune_out = out_dir / "pruning"
    cmd_prune = [
        plink_bin,
        "--bfile",
        input_prefix,
        "--indep-pairwise",
        "50",
        "5",
        "0.2",
        "--allow-extra-chr",
        "--out",
        str(prune_out),
    ]
    subprocess.run(cmd_prune, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    pruned_prefix = out_dir / "pruned_data"
    cmd_extract = [
        plink_bin,
        "--bfile",
        input_prefix,
        "--extract",
        str(prune_out) + ".prune.in",
        "--make-bed",
        "--allow-extra-chr",
        "--out",
        str(pruned_prefix),
    ]
    subprocess.run(cmd_extract, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return str(pruned_prefix)


def _simulate_with_genetic_basis(
    x_real: np.ndarray,
    y_real: np.ndarray,
    rng: np.random.Generator,
    n_sim: int,
    top_k: int,
    h2: float,
) -> tuple[np.ndarray, np.ndarray]:
    n_samples, n_features = x_real.shape
    actual_top_k = min(top_k, n_features)

    f_vals, _ = f_classif(x_real, y_real)
    f_vals = np.nan_to_num(f_vals)
    causal_indices = np.argsort(f_vals)[-actual_top_k:]

    x_causal_real = x_real[:, causal_indices]
    ridge = RidgeCV(alphas=[0.1, 1.0, 10.0, 100.0])
    ridge.fit(x_causal_real, y_real)
    marker_effects = ridge.coef_

    x_sim = np.zeros((n_sim, n_features), dtype=np.float32)
    for i in range(n_sim):
        p1, p2 = rng.choice(n_samples, 2, replace=False)
        mask = rng.integers(0, 2, size=n_features).astype(bool)
        x_sim[i, mask] = x_real[p1, mask]
        x_sim[i, ~mask] = x_real[p2, ~mask]

    x_causal_sim = x_sim[:, causal_indices]
    gbv_sim = x_causal_sim.dot(marker_effects)

    vg = float(np.var(gbv_sim))
    if vg <= 0:
        vg = 1e-6
    ve = vg * (1.0 - h2) / h2
    noise = rng.normal(0.0, np.sqrt(ve), size=n_sim)
    liability_sim = gbv_sim + noise

    prevalence = float(np.mean(y_real))
    threshold = float(np.percentile(liability_sim, 100.0 * (1.0 - prevalence)))
    y_sim = (liability_sim >= threshold).astype(np.float32)
    return x_sim, y_sim


def cmd(args):
    try:
        from pandas_plink import read_plink
    except ImportError as exc:
        raise SystemExit("Missing dependency: pandas_plink. Install it first.") from exc

    if not (0 < args.h2 < 1):
        raise SystemExit("--h2 must be in (0, 1)")
    if args.n_sim < 0 or args.top_k < 1:
        raise SystemExit("--n-sim must be >=0 and --top-k must be >=1")

    out_dir = Path(args.o)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    pheno = pd.read_csv(args.pheno, sep=r"\s+")
    if "IID" not in pheno.columns or "PHENO" not in pheno.columns:
        raise SystemExit("Phenotype file must contain IID and PHENO columns")
    pheno["IID"] = pheno["IID"].astype(str)
    pheno = pheno.set_index("IID")

    pruned_prefix = _run_ld_pruning(args.plink_bin, args.plink, out_dir)
    bim, fam, bed = read_plink(pruned_prefix, verbose=False)

    fam["iid"] = fam["iid"].astype(str)
    common_fam = fam[fam["iid"].isin(pheno.index)]
    keep_indices = common_fam.index.values
    valid_iids = common_fam["iid"].values

    y_real = pheno.loc[valid_iids, "PHENO"].values.astype(np.float32)
    if set(np.unique(y_real)).issubset({1.0, 2.0}):
        y_real = y_real - 1.0
    x_real = bed[:, keep_indices].compute().T.astype(np.float32)

    col_means = np.nanmean(x_real, axis=0)
    col_means = np.nan_to_num(col_means, nan=0.0)
    inds = np.where(np.isnan(x_real))
    x_real[inds] = np.take(col_means, inds[1])

    x_sim, y_sim = _simulate_with_genetic_basis(
        x_real=x_real,
        y_real=y_real,
        rng=rng,
        n_sim=args.n_sim,
        top_k=args.top_k,
        h2=args.h2,
    )

    x_final = np.vstack([x_real, x_sim])
    y_final = np.concatenate([y_real, y_sim])

    snp_ids = bim["snp"].values
    sample_ids = list(valid_iids) + [f"sim_{i}" for i in range(len(y_sim))]

    np.save(out_dir / "X.npy", x_final)
    np.save(out_dir / "y.npy", y_final)
    (out_dir / "sample_ids.txt").write_text("\n".join(sample_ids) + "\n", encoding="utf-8")
    (out_dir / "snp_ids.txt").write_text("\n".join(snp_ids) + "\n", encoding="utf-8")

    print(f"Dataset built in {out_dir}")
    print(f"samples\t{x_final.shape[0]}")
    print(f"snps\t{x_final.shape[1]}")
    print(f"real_samples\t{len(valid_iids)}")
    print(f"sim_samples\t{len(y_sim)}")
