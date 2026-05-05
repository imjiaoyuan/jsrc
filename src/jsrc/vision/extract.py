import logging
from argparse import Namespace
from pathlib import Path
from typing import Any

import cv2

import numpy as np

from jsrc.vision.core import ensure_odd, get_channel_image

logger = logging.getLogger(__name__)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


def _validate_image_file(input_path: str) -> Path:
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input path not found: {input_path}")
    if not path.is_file():
        raise SystemExit(
            f"Input must be a single image file, got directory: {input_path}"
        )
    if path.suffix.lower() not in IMAGE_SUFFIXES:
        raise SystemExit(f"Unsupported image format: {path.suffix}")
    return path


def _extract_contours(args: Namespace, image_path: Path, output_dir: Path) -> None:
    img = cv2.imread(str(image_path))
    if img is None:
        logger.warning("Skip unreadable image: %s", image_path)
        return

    blur_ksize = ensure_odd(args.blur)
    blurred = cv2.GaussianBlur(img, (blur_ksize, blur_ksize), 0)
    channel_img = get_channel_image(blurred, args.channel)

    threshold_mode = cv2.THRESH_BINARY_INV if args.invert else cv2.THRESH_BINARY
    _, binary = cv2.threshold(channel_img, 0, 255, threshold_mode + cv2.THRESH_OTSU)

    kernel_size = max(1, args.kernel)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    binary = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, kernel, iterations=max(0, args.open_iters)
    )
    binary = cv2.morphologyEx(
        binary, cv2.MORPH_CLOSE, kernel, iterations=max(0, args.close_iters)
    )

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h_img, w_img = binary.shape
    total_area = float(h_img * w_img)

    min_area = total_area * args.min_area_ratio
    max_area = total_area * args.max_area_ratio
    valid_contours = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area or area > max_area:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        if h <= 0:
            continue
        aspect_ratio = float(w) / float(h)
        if aspect_ratio < args.min_aspect_ratio or aspect_ratio > args.max_aspect_ratio:
            continue
        valid_contours.append(cnt)

    if args.sort_by == "x":
        valid_contours = sorted(valid_contours, key=lambda c: cv2.boundingRect(c)[0])
    else:
        valid_contours = sorted(valid_contours, key=lambda c: cv2.boundingRect(c)[1])

    base = image_path.stem
    if args.save_mask:
        cv2.imwrite(str(output_dir / f"{base}_mask.png"), binary)

    for i, cnt in enumerate(valid_contours, start=1):
        x, y, w, h = cv2.boundingRect(cnt)
        edge_canvas = np.zeros((h, w), dtype=np.uint8)
        cnt_shifted = cnt.copy()
        cnt_shifted[:, :, 0] -= x
        cnt_shifted[:, :, 1] -= y

        cv2.drawContours(edge_canvas, [cnt_shifted], -1, 255, 1)
        cv2.imwrite(str(output_dir / f"{base}_{i}_edge.png"), edge_canvas)
        np.save(output_dir / f"{base}_{i}.npy", cnt)

    logger.info("%s: extracted %d contour(s)", image_path.name, len(valid_contours))


def cmd(args: Namespace) -> None:
    if (
        args.min_area_ratio < 0
        or args.max_area_ratio < 0
        or args.min_area_ratio > args.max_area_ratio
    ):
        raise SystemExit(
            "Invalid area ratio range: require 0 <= min_area_ratio <= max_area_ratio"
        )
    if args.max_area_ratio > 1:
        raise SystemExit("Invalid max_area_ratio: must be <= 1")
    if (
        args.min_aspect_ratio <= 0
        or args.max_aspect_ratio <= 0
        or args.min_aspect_ratio > args.max_aspect_ratio
    ):
        raise SystemExit(
            "Invalid aspect ratio range: require 0 < min_aspect_ratio <= max_aspect_ratio"
        )
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = _validate_image_file(args.input)
    _extract_contours(args, image_path, output_dir)


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "extract", help="Extract object contours from a single image"
    )
    p.add_argument("-i", "--input", required=True, help="Input image file")
    p.add_argument("-o", dest="output", required=True, help="Output directory")
    p.add_argument(
        "--channel",
        choices=["gray", "a", "b", "s", "v"],
        default="gray",
        help="Channel used for Otsu thresholding",
    )
    p.add_argument("--invert", action="store_true", help="Invert threshold result")
    p.add_argument(
        "--blur", type=int, default=5, help="Gaussian blur kernel size (odd)"
    )
    p.add_argument("--kernel", type=int, default=3, help="Morphology kernel size")
    p.add_argument(
        "--open-iters", type=int, default=2, help="Open operation iterations"
    )
    p.add_argument(
        "--close-iters", type=int, default=2, help="Close operation iterations"
    )
    p.add_argument(
        "--min-area-ratio",
        type=float,
        default=0.0005,
        help="Minimum contour area ratio",
    )
    p.add_argument(
        "--max-area-ratio", type=float, default=0.8, help="Maximum contour area ratio"
    )
    p.add_argument(
        "--min-aspect-ratio", type=float, default=0.1, help="Minimum width/height ratio"
    )
    p.add_argument(
        "--max-aspect-ratio",
        type=float,
        default=10.0,
        help="Maximum width/height ratio",
    )
    p.add_argument(
        "--sort-by",
        choices=["x", "y"],
        default="x",
        help="Sort extracted objects by x or y",
    )
    p.add_argument("--save-mask", action="store_true", help="Save binary mask image")
    p.set_defaults(func=cmd)
