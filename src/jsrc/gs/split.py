from pathlib import Path

import numpy as np


def cmd(args):
    if args.folds < 2:
        raise SystemExit("--folds must be >= 2")
    data_dir = Path(args.input)
    y_path = data_dir / "y.npy"
    id_path = data_dir / "sample_ids.txt"
    if not y_path.exists() or not id_path.exists():
        raise SystemExit("Input directory must contain y.npy and sample_ids.txt")

    sample_ids = [line.strip() for line in id_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not sample_ids:
        raise SystemExit("sample_ids.txt is empty")
    _ = np.load(y_path)

    real_indices = np.array([i for i, sid in enumerate(sample_ids) if not sid.startswith("sim_")], dtype=int)
    sim_indices = np.array([i for i, sid in enumerate(sample_ids) if sid.startswith("sim_")], dtype=int)
    if len(real_indices) < args.folds:
        raise SystemExit("Number of real samples must be >= number of folds")

    rng = np.random.default_rng(args.seed)
    shuffled_real = real_indices.copy()
    rng.shuffle(shuffled_real)
    folds = np.array_split(shuffled_real, args.folds)

    cv_dir = data_dir / "cv_indices"
    cv_dir.mkdir(parents=True, exist_ok=True)

    for i in range(args.folds):
        test_idx = folds[i]
        train_real_idx = np.setdiff1d(real_indices, test_idx)
        train_idx = np.concatenate([train_real_idx, sim_indices])
        rng.shuffle(train_idx)
        np.savetxt(cv_dir / f"fold_{i}_train.txt", train_idx, fmt="%d")
        np.savetxt(cv_dir / f"fold_{i}_test.txt", test_idx, fmt="%d")

    print(f"CV indices written to {cv_dir}")
    print(f"folds\t{args.folds}")
    print(f"real_samples\t{len(real_indices)}")
    print(f"sim_samples\t{len(sim_indices)}")
