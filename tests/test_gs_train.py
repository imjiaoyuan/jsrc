import numpy as np
import pytest

from jsrc.gs.build import _simulate_with_genetic_basis


class TestGSSimulate:
    def test_simulation_produces_correct_shapes(self):
        rng = np.random.default_rng(42)
        n_real, n_features = 50, 100
        x_real = rng.integers(0, 3, size=(n_real, n_features)).astype(np.float32)
        y_real = rng.integers(0, 2, size=n_real).astype(np.float32)
        n_sim = 20

        x_sim, y_sim = _simulate_with_genetic_basis(
            x_real=x_real,
            y_real=y_real,
            rng=rng,
            n_sim=n_sim,
            top_k=10,
            h2=0.5,
        )

        assert x_sim.shape == (n_sim, n_features)
        assert y_sim.shape == (n_sim,)
        assert set(np.unique(y_sim)).issubset({0.0, 1.0})

    def test_simulation_top_k_capped_by_features(self):
        rng = np.random.default_rng(7)
        n_real, n_features = 10, 5
        x_real = rng.integers(0, 3, size=(n_real, n_features)).astype(np.float32)
        y_real = rng.integers(0, 2, size=n_real).astype(np.float32)

        x_sim, y_sim = _simulate_with_genetic_basis(
            x_real=x_real,
            y_real=y_real,
            rng=rng,
            n_sim=5,
            top_k=999,  # capped to n_features=5
            h2=0.5,
        )
        assert x_sim.shape == (5, 5)

    def test_simulation_zero_variance_handled(self):
        rng = np.random.default_rng(42)
        x_real = np.ones((20, 5), dtype=np.float32)
        y_real = np.ones(20, dtype=np.float32)

        x_sim, y_sim = _simulate_with_genetic_basis(
            x_real=x_real,
            y_real=y_real,
            rng=rng,
            n_sim=5,
            top_k=3,
            h2=0.5,
        )
        assert x_sim.shape == (5, 5)
        assert y_sim.shape == (5,)

    def test_simulation_deterministic_with_seed(self):
        x_real = np.random.default_rng(0).integers(0, 3, size=(30, 20)).astype(np.float32)
        y_real = np.random.default_rng(0).integers(0, 2, size=30).astype(np.float32)

        x1, y1 = _simulate_with_genetic_basis(
            x_real=x_real,
            y_real=y_real,
            rng=np.random.default_rng(123),
            n_sim=10,
            top_k=5,
            h2=0.5,
        )
        x2, y2 = _simulate_with_genetic_basis(
            x_real=x_real,
            y_real=y_real,
            rng=np.random.default_rng(123),
            n_sim=10,
            top_k=5,
            h2=0.5,
        )
        np.testing.assert_array_equal(x1, x2)
        np.testing.assert_array_equal(y1, y2)


class TestGSTrain:
    def test_train_basic_flow(self, tmp_path):
        pytest.importorskip("sklearn")
        rng = np.random.default_rng(42)
        n_samples, n_features = 30, 20
        x = rng.integers(0, 3, size=(n_samples, n_features)).astype(np.float32)
        y = rng.integers(0, 2, size=n_samples).astype(np.float32)

        np.save(tmp_path / "X.npy", x)
        np.save(tmp_path / "y.npy", y)

        cv_dir = tmp_path / "cv_indices"
        cv_dir.mkdir()
        train_idx = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        test_idx = np.array([15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29])
        np.savetxt(cv_dir / "fold_0_train.txt", train_idx, fmt="%d")
        np.savetxt(cv_dir / "fold_0_test.txt", test_idx, fmt="%d")
        np.savetxt(cv_dir / "fold_1_train.txt", train_idx, fmt="%d")
        np.savetxt(cv_dir / "fold_1_test.txt", test_idx, fmt="%d")

        from jsrc.gs.train import cmd
        from argparse import Namespace

        args = Namespace(
            input=str(tmp_path),
            output=str(tmp_path / "results"),
            folds=2,
            select_k=10,
            models="rf",
            seed=42,
        )
        cmd(args)

        results_csv = tmp_path / "results" / "results.csv"
        summary_csv = tmp_path / "results" / "summary.csv"
        assert results_csv.exists()
        assert summary_csv.exists()

        import pandas as pd

        df = pd.read_csv(results_csv)
        assert len(df) == 2  # 2 folds
        assert list(df["model"]) == ["rf", "rf"]

    def test_train_invalid_folds_raises(self, tmp_path):
        from jsrc.gs.train import cmd
        from argparse import Namespace

        args = Namespace(input=str(tmp_path), output=None, folds=0, select_k=10, models="rf", seed=42)
        with pytest.raises(SystemExit, match="positive integer"):
            cmd(args)

    def test_train_invalid_select_k_raises(self, tmp_path):
        from jsrc.gs.train import cmd
        from argparse import Namespace

        args = Namespace(
            input=str(tmp_path), output=None, folds=2, select_k=0, models="rf", seed=42
        )
        with pytest.raises(SystemExit, match="positive integer"):
            cmd(args)

    def test_train_missing_data_raises(self, tmp_path):
        from jsrc.gs.train import cmd
        from argparse import Namespace

        args = Namespace(
            input=str(tmp_path), output=None, folds=2, select_k=10, models="rf", seed=42
        )
        with pytest.raises(SystemExit, match="must contain"):
            cmd(args)

    def test_train_unsupported_model_raises(self, tmp_path):
        from jsrc.gs.train import cmd
        from argparse import Namespace

        rng = np.random.default_rng(42)
        np.save(tmp_path / "X.npy", rng.integers(0, 3, (10, 5)).astype(np.float32))
        np.save(tmp_path / "y.npy", rng.integers(0, 2, 10).astype(np.float32))
        cv_dir = tmp_path / "cv_indices"
        cv_dir.mkdir()
        np.savetxt(cv_dir / "fold_0_train.txt", np.array([0, 1, 2, 3, 4]), fmt="%d")
        np.savetxt(cv_dir / "fold_0_test.txt", np.array([5, 6, 7, 8, 9]), fmt="%d")

        args = Namespace(
            input=str(tmp_path), output=None, folds=1, select_k=3, models="nonexistent", seed=42
        )
        with pytest.raises(SystemExit, match="Unsupported models"):
            cmd(args)

    def test_train_missing_fold_files_raises(self, tmp_path):
        from jsrc.gs.train import cmd
        from argparse import Namespace

        rng = np.random.default_rng(42)
        np.save(tmp_path / "X.npy", rng.integers(0, 3, (10, 5)).astype(np.float32))
        np.save(tmp_path / "y.npy", rng.integers(0, 2, 10).astype(np.float32))
        cv_dir = tmp_path / "cv_indices"
        cv_dir.mkdir()

        args = Namespace(
            input=str(tmp_path), output=None, folds=1, select_k=3, models="rf", seed=42
        )
        with pytest.raises(SystemExit, match="Missing fold"):
            cmd(args)

    def test_train_all_models(self, tmp_path):
        """Quick check that all 8 model types run without error."""
        pytest.importorskip("sklearn")
        rng = np.random.default_rng(42)
        np.save(tmp_path / "X.npy", rng.integers(0, 3, (20, 10)).astype(np.float32))
        np.save(tmp_path / "y.npy", rng.integers(0, 2, 20).astype(np.float32))
        cv_dir = tmp_path / "cv_indices"
        cv_dir.mkdir()
        np.savetxt(cv_dir / "fold_0_train.txt", np.array(range(10)), fmt="%d")
        np.savetxt(cv_dir / "fold_0_test.txt", np.array(range(10, 20)), fmt="%d")

        from jsrc.gs.train import cmd
        from argparse import Namespace

        args = Namespace(
            input=str(tmp_path),
            output=str(tmp_path / "results"),
            folds=1,
            select_k=5,
            models="gbdt,rf,et,ada,dt,lr,svm,nb",
            seed=42,
        )
        cmd(args)

        import pandas as pd
        df = pd.read_csv(tmp_path / "results" / "results.csv")
        assert len(df) == 8
