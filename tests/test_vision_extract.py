import cv2
import numpy as np
import pytest

from jsrc.vision.core import ensure_odd, get_channel_image
from jsrc.vision.extract import _extract_contours, _validate_image_file


class TestVisionCore:
    def test_ensure_odd_odd_stays_same(self):
        assert ensure_odd(5) == 5
        assert ensure_odd(1) == 1

    def test_ensure_odd_even_rounded_up(self):
        assert ensure_odd(4) == 5
        assert ensure_odd(2) == 3
        assert ensure_odd(0) == 1

    def test_get_channel_image_gray(self):
        img = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
        gray = get_channel_image(img, "gray")
        assert gray.ndim == 2
        assert gray.shape == (10, 10)

    def test_get_channel_image_lab_a(self):
        img = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
        a_channel = get_channel_image(img, "a")
        assert a_channel.ndim == 2
        assert a_channel.shape == (10, 10)

    def test_get_channel_image_hsv_s(self):
        img = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
        s_channel = get_channel_image(img, "s")
        assert s_channel.ndim == 2
        assert s_channel.shape == (10, 10)

    def test_get_channel_image_hsv_v(self):
        img = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
        v_channel = get_channel_image(img, "v")
        assert v_channel.ndim == 2
        assert v_channel.shape == (10, 10)


class TestVisionExtractValidate:
    def test_validate_existing_file(self, tmp_path):
        img = tmp_path / "leaf.png"
        img.write_text("fake", encoding="utf-8")
        path = _validate_image_file(str(img))
        assert path == img

    def test_validate_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            _validate_image_file("/nonexistent/file.png")

    def test_validate_directory_raises(self, tmp_path):
        with pytest.raises(SystemExit, match="single image file"):
            _validate_image_file(str(tmp_path))

    def test_validate_unsupported_format_raises(self, tmp_path):
        bad = tmp_path / "data.txt"
        bad.write_text("stuff", encoding="utf-8")
        with pytest.raises(SystemExit, match="Unsupported image format"):
            _validate_image_file(str(bad))

    def test_validate_supported_formats(self, tmp_path):
        for ext in [".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"]:
            f = tmp_path / f"img{ext}"
            f.write_text("fake", encoding="utf-8")
            path = _validate_image_file(str(f))
            assert path == f


class TestVisionExtractContours:
    @staticmethod
    def _white_square(size=100, margin=10):
        img = np.zeros((size, size, 3), dtype=np.uint8)
        cv2.rectangle(
            img, (margin, margin), (size - margin, size - margin), (255, 255, 255), -1
        )
        return img

    def test_extract_single_contour(self, tmp_path):
        img = self._white_square(100, 10)
        img_path = tmp_path / "test.png"
        cv2.imwrite(str(img_path), img)
        out_dir = tmp_path / "output"
        out_dir.mkdir()

        class FakeArgs:
            blur = 5
            channel = "gray"
            invert = False
            kernel = 3
            open_iters = 1
            close_iters = 1
            min_area_ratio = 0.01
            max_area_ratio = 0.9
            min_aspect_ratio = 0.1
            max_aspect_ratio = 10.0
            sort_by = "x"
            save_mask = False

        _extract_contours(FakeArgs(), img_path, out_dir)
        npy_files = list(out_dir.glob("*.npy"))
        png_files = list(out_dir.glob("*_edge.png"))
        assert len(npy_files) == 1
        assert len(png_files) == 1

    def test_extract_with_mask_saved(self, tmp_path):
        img = self._white_square(100, 10)
        img_path = tmp_path / "test.png"
        cv2.imwrite(str(img_path), img)
        out_dir = tmp_path / "output"
        out_dir.mkdir()

        class FakeArgs:
            blur = 5
            channel = "gray"
            invert = False
            kernel = 3
            open_iters = 1
            close_iters = 1
            min_area_ratio = 0.01
            max_area_ratio = 0.9
            min_aspect_ratio = 0.1
            max_aspect_ratio = 10.0
            sort_by = "x"
            save_mask = True

        _extract_contours(FakeArgs(), img_path, out_dir)
        mask_files = list(out_dir.glob("*_mask.png"))
        assert len(mask_files) == 1

    def test_extract_area_filter_removes_all(self, tmp_path, capsys):
        img = self._white_square(100, 10)
        img_path = tmp_path / "test.png"
        cv2.imwrite(str(img_path), img)
        out_dir = tmp_path / "output"
        out_dir.mkdir()

        class FakeArgs:
            blur = 5
            channel = "gray"
            invert = False
            kernel = 3
            open_iters = 0
            close_iters = 0
            min_area_ratio = 0.9
            max_area_ratio = 0.99
            min_aspect_ratio = 0.1
            max_aspect_ratio = 10.0
            sort_by = "x"
            save_mask = False

        _extract_contours(FakeArgs(), img_path, out_dir)
        npy_files = list(out_dir.glob("*.npy"))
        assert len(npy_files) == 0

    def test_extract_sort_by_y(self, tmp_path):
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.rectangle(img, (10, 10), (50, 50), (255, 255, 255), -1)
        cv2.rectangle(img, (10, 100), (50, 150), (255, 255, 255), -1)
        img_path = tmp_path / "test.png"
        cv2.imwrite(str(img_path), img)
        out_dir = tmp_path / "output"
        out_dir.mkdir()

        class FakeArgs:
            blur = 5
            channel = "gray"
            invert = False
            kernel = 3
            open_iters = 0
            close_iters = 0
            min_area_ratio = 0.001
            max_area_ratio = 0.9
            min_aspect_ratio = 0.1
            max_aspect_ratio = 10.0
            sort_by = "y"
            save_mask = False

        _extract_contours(FakeArgs(), img_path, out_dir)
        npy_files = sorted(out_dir.glob("*.npy"))
        assert len(npy_files) == 2

    def test_extract_inverted_threshold(self, tmp_path):
        img = np.full((100, 100, 3), 255, dtype=np.uint8)
        cv2.rectangle(img, (30, 30), (70, 70), (0, 0, 0), -1)
        img_path = tmp_path / "test.png"
        cv2.imwrite(str(img_path), img)
        out_dir = tmp_path / "output"
        out_dir.mkdir()

        class FakeArgs:
            blur = 5
            channel = "gray"
            invert = True
            kernel = 3
            open_iters = 1
            close_iters = 1
            min_area_ratio = 0.01
            max_area_ratio = 0.9
            min_aspect_ratio = 0.1
            max_aspect_ratio = 10.0
            sort_by = "x"
            save_mask = False

        _extract_contours(FakeArgs(), img_path, out_dir)
        npy_files = list(out_dir.glob("*.npy"))
        assert len(npy_files) == 1


class TestVisionExtractCmd:
    def test_invalid_area_ratio_raises(self, tmp_path):
        from argparse import Namespace

        from jsrc.vision.extract import cmd

        args = Namespace(
            input="/dev/null",
            output=str(tmp_path),
            min_area_ratio=-1,
            max_area_ratio=0.5,
            max_aspect_ratio=10.0,
            min_aspect_ratio=0.1,
        )
        with pytest.raises(SystemExit, match="Invalid area ratio"):
            cmd(args)

    def test_invalid_aspect_ratio_raises(self, tmp_path):
        from argparse import Namespace

        from jsrc.vision.extract import cmd

        args = Namespace(
            input="/dev/null",
            output=str(tmp_path),
            min_area_ratio=0,
            max_area_ratio=0.5,
            max_aspect_ratio=0.05,
            min_aspect_ratio=0.1,
        )
        with pytest.raises(SystemExit, match="Invalid aspect ratio"):
            cmd(args)

    def test_max_area_ratio_too_high_raises(self, tmp_path):
        from argparse import Namespace

        from jsrc.vision.extract import cmd

        args = Namespace(
            input="/dev/null",
            output=str(tmp_path),
            min_area_ratio=0,
            max_area_ratio=1.5,
            max_aspect_ratio=10.0,
            min_aspect_ratio=0.1,
        )
        with pytest.raises(SystemExit, match="max_area_ratio"):
            cmd(args)
