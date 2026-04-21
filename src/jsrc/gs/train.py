from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import AdaBoostClassifier, ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, roc_auc_score
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


def _models(seed: int):
    return {
        "gbdt": lambda: GradientBoostingClassifier(n_estimators=200, learning_rate=0.05, max_depth=4, random_state=seed),
        "rf": lambda: RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=seed, n_jobs=-1),
        "et": lambda: ExtraTreesClassifier(n_estimators=300, class_weight="balanced", random_state=seed, n_jobs=-1),
        "ada": lambda: AdaBoostClassifier(n_estimators=100, random_state=seed),
        "dt": lambda: DecisionTreeClassifier(max_depth=5, class_weight="balanced", random_state=seed),
        "lr": lambda: LogisticRegression(max_iter=2000, class_weight="balanced", solver="lbfgs", n_jobs=-1),
        "svm": lambda: SVC(probability=True, kernel="rbf", class_weight="balanced", random_state=seed),
        "nb": lambda: GaussianNB(),
    }


def _predict(model, x_test):
    y_pred = model.predict(x_test)
    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(x_test)[:, 1]
    else:
        y_score = y_pred.astype(float)
    return y_pred, y_score


def _metrics(y_true: np.ndarray, y_pred: np.ndarray, y_score: np.ndarray) -> dict[str, float]:
    out = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "mse": float(mean_squared_error(y_true, y_score)),
    }
    if len(np.unique(y_true)) > 1:
        out["auc"] = float(roc_auc_score(y_true, y_score))
    else:
        out["auc"] = float("nan")
    return out


def cmd(args):
    data_dir = Path(args.input)
    x_path = data_dir / "X.npy"
    y_path = data_dir / "y.npy"
    cv_dir = data_dir / "cv_indices"
    if not x_path.exists() or not y_path.exists() or not cv_dir.exists():
        raise SystemExit("Input directory must contain X.npy, y.npy, and cv_indices/")

    x = np.load(x_path)
    y = np.load(y_path)
    if len(y.shape) != 1:
        y = y.reshape(-1)

    model_pool = _models(args.seed)
    selected = [m.strip().lower() for m in args.models.split(",") if m.strip()]
    invalid = [m for m in selected if m not in model_pool]
    if invalid:
        raise SystemExit(f"Unsupported models: {','.join(invalid)}")

    output_dir = Path(args.output) if args.output else data_dir / "gs_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for fold in range(args.folds):
        train_idx_path = cv_dir / f"fold_{fold}_train.txt"
        test_idx_path = cv_dir / f"fold_{fold}_test.txt"
        if not train_idx_path.exists() or not test_idx_path.exists():
            raise SystemExit(f"Missing fold files: fold_{fold}_train.txt / fold_{fold}_test.txt")
        train_idx = np.loadtxt(train_idx_path, dtype=int)
        test_idx = np.loadtxt(test_idx_path, dtype=int)
        if train_idx.ndim == 0:
            train_idx = np.array([int(train_idx)])
        if test_idx.ndim == 0:
            test_idx = np.array([int(test_idx)])

        x_train_raw, x_test_raw = x[train_idx], x[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        k_num = min(args.select_k, x_train_raw.shape[1], max(1, len(y_train) - 1))
        selector = SelectKBest(f_classif, k=k_num)
        x_train_sel = selector.fit_transform(x_train_raw, y_train)
        x_test_sel = selector.transform(x_test_raw)

        scaler = StandardScaler()
        x_train_scaled = scaler.fit_transform(x_train_sel)
        x_test_scaled = scaler.transform(x_test_sel)

        for name in selected:
            model = model_pool[name]()
            start = time.time()
            model.fit(x_train_scaled, y_train)
            y_pred, y_score = _predict(model, x_test_scaled)
            metric = _metrics(y_test, y_pred, y_score)
            metric.update(
                {
                    "model": name,
                    "fold": fold,
                    "runtime_sec": float(time.time() - start),
                }
            )
            results.append(metric)

    df = pd.DataFrame(results)
    results_path = output_dir / "results.csv"
    summary_path = output_dir / "summary.csv"
    df.to_csv(results_path, index=False)
    summary = df.groupby("model").agg(
        accuracy_mean=("accuracy", "mean"),
        accuracy_std=("accuracy", "std"),
        auc_mean=("auc", "mean"),
        auc_std=("auc", "std"),
        f1_mean=("f1", "mean"),
        f1_std=("f1", "std"),
        runtime_mean=("runtime_sec", "mean"),
        runtime_sum=("runtime_sec", "sum"),
    )
    summary.to_csv(summary_path)

    print(f"Training complete. Results: {results_path}")
    print(f"Summary: {summary_path}")
