import numpy as np
import pytest

from jsrc.vision.efd import (
    EllipticFourier,
    _center_contour,
    _iter_contours,
)


class TestEllipticFourier:
    def test_calculate_square_contour(self):
        contour = np.array([[0, 0], [10, 0], [10, 10], [0, 10]], dtype=np.float32)
        coeffs = EllipticFourier.calculate(contour, order=5, normalize=False)
        assert coeffs.shape == (5, 4)
        assert not np.allclose(coeffs, 0)

    def test_calculate_too_few_points_returns_zeros(self):
        contour = np.array([[0, 0], [1, 1]], dtype=np.float32)
        coeffs = EllipticFourier.calculate(contour, order=5, normalize=False)
        assert np.allclose(coeffs, 0)

    def test_calculate_normalized(self):
        contour = np.array([[0, 0], [10, 0], [10, 10], [0, 10]], dtype=np.float32)
        coeffs_norm = EllipticFourier.calculate(contour, order=5, normalize=True)
        assert coeffs_norm.shape == (5, 4)

    def test_normalize_rotation_invariant(self):
        contour = np.array(
            [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]], dtype=np.float32
        )

        theta = np.radians(45)
        c, s = np.cos(theta), np.sin(theta)
        rot = np.array([[c, -s], [s, c]])
        contour_rot = contour @ rot.T

        coeffs1 = EllipticFourier.calculate(contour, order=10, normalize=True)
        coeffs2 = EllipticFourier.calculate(contour_rot, order=10, normalize=True)

        assert np.abs(coeffs1[0, 0] - coeffs2[0, 0]) < 1.0

    def test_normalize_empty_coeffs(self):
        result = EllipticFourier.normalize(np.array([]).reshape(0, 4))
        assert result.shape == (0, 4)

    def test_normalize_zero_scale_handled(self):
        coeffs = np.zeros((3, 4))

        result = EllipticFourier.normalize(coeffs)
        assert result.shape == (3, 4)
        assert not np.any(np.isnan(result))

    def test_reconstruct_basic(self):
        coeffs = np.zeros((5, 4))
        coeffs[0] = [10.0, 0.0, 0.0, 10.0]
        pts = EllipticFourier.reconstruct(coeffs, num_points=100)
        assert pts.shape == (100, 2)
        assert not np.any(np.isnan(pts))

    def test_reconstruct_multiple_harmonics(self):
        coeffs = np.array([[5.0, 0.0, 0.0, 5.0], [1.0, 0.0, 0.0, 1.0]], dtype=float)
        pts = EllipticFourier.reconstruct(coeffs, num_points=50)
        assert pts.shape == (50, 2)
        assert not np.any(np.isnan(pts))

    def test_calculate_and_reconstruct_roundtrip(self):
        contour = np.array(
            [
                [0, 0],
                [5, 0],
                [10, 0],
                [10, 5],
                [10, 10],
                [5, 10],
                [0, 10],
                [0, 5],
            ],
            dtype=np.float32,
        )
        coeffs = EllipticFourier.calculate(contour, order=8, normalize=False)
        reconstructed = EllipticFourier.reconstruct(coeffs, num_points=200)

        assert np.max(np.abs(reconstructed)) < 15
        assert not np.any(np.isnan(reconstructed))


class TestCenterContour:
    def test_center_basic(self):
        contour = np.array([[0, 0], [10, 0], [10, 10], [0, 10]], dtype=np.float32)
        centered = _center_contour(contour)
        assert centered.shape == (4, 2)

        assert np.mean(centered[:, 0]) == pytest.approx(0.0, abs=1e-10)

        assert np.mean(centered[:, 1]) == pytest.approx(0.0, abs=1e-10)

    def test_center_invalid_shape_raises(self):
        contour = np.zeros((10,), dtype=np.float32)
        with pytest.raises(SystemExit, match="Invalid contour shape"):
            _center_contour(contour)

    def test_center_1d_contour_raises(self):
        contour = np.array([1, 2, 3], dtype=np.float32)
        with pytest.raises(SystemExit, match="Invalid contour shape"):
            _center_contour(contour)


class TestIterContours:
    def test_single_npy_file(self, tmp_path):
        npy = tmp_path / "test.npy"
        np.save(npy, np.array([[0, 0]]))
        files = _iter_contours(str(npy))
        assert files == [npy]

    def test_non_npy_file_raises(self, tmp_path):
        txt = tmp_path / "data.txt"
        txt.write_text("hello", encoding="utf-8")
        with pytest.raises(SystemExit, match="must be .npy"):
            _iter_contours(str(txt))

    def test_directory_of_npy_files(self, tmp_path):
        for i in range(3):
            np.save(tmp_path / f"c{i}.npy", np.array([[0, 0]]))
        files = _iter_contours(str(tmp_path))
        assert len(files) == 3

    def test_nonexistent_path_raises(self):
        with pytest.raises(FileNotFoundError, match="not found"):
            _iter_contours("/nonexistent/file.npy")


class TestEFDCmd:
    def test_efd_cmd_basic(self, tmp_path):
        pytest.importorskip("matplotlib")
        from jsrc.vision.efd import cmd
        from argparse import Namespace

        contour = np.array(
            [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]], dtype=np.float32
        )
        npy_file = tmp_path / "leaf_01.npy"
        np.save(npy_file, contour)
        out_dir = tmp_path / "efd_output"

        args = Namespace(
            input=str(npy_file),
            output=str(out_dir),
            harmonics=10,
            points=100,
            no_plot=False,
        )
        cmd(args)

        csv_file = out_dir / "leaf_01_efd.csv"
        assert csv_file.exists()
        import csv as csv_mod

        with open(csv_file) as f:
            reader = csv_mod.DictReader(f)
            rows = list(reader)
        assert len(rows) == 10

    def test_efd_cmd_no_plot(self, tmp_path):
        from jsrc.vision.efd import cmd
        from argparse import Namespace

        contour = np.array(
            [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]], dtype=np.float32
        )
        npy_file = tmp_path / "leaf_01.npy"
        np.save(npy_file, contour)
        out_dir = tmp_path / "efd_output"

        args = Namespace(
            input=str(npy_file),
            output=str(out_dir),
            harmonics=5,
            points=50,
            no_plot=True,
        )
        cmd(args)

        csv_file = out_dir / "leaf_01_efd.csv"
        assert csv_file.exists()

        assert not list(out_dir.glob("*analysis*"))

    def test_efd_empty_directory_raises(self, tmp_path):
        from jsrc.vision.efd import cmd
        from argparse import Namespace

        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        args = Namespace(
            input=str(empty_dir),
            output=str(tmp_path / "out"),
            harmonics=5,
            points=50,
            no_plot=True,
        )
        with pytest.raises(SystemExit, match="No .npy files found"):
            cmd(args)
