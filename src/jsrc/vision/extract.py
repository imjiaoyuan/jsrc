from pathlib import Path

import cv2
import numpy as np
from jsrc.vision.core import ensure_odd, get_channel_image

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


def _validate_image_file(input_path: str) -> Path:
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input path not found: {input_path}")
    if not path.is_file():
        raise ValueError(f"Input must be a single image file, got directory: {input_path}")
    if path.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError(f"Unsupported image format: {path.suffix}")
    return path


def _extract_contours(args, image_path: Path, output_dir: Path):
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"Skip unreadable image: {image_path}")
        return

    blur_ksize = ensure_odd(args.blur)
    blurred = cv2.GaussianBlur(img, (blur_ksize, blur_ksize), 0)
    channel_img = get_channel_image(blurred, args.channel)

    threshold_mode = cv2.THRESH_BINARY_INV if args.invert else cv2.THRESH_BINARY
    _, binary = cv2.threshold(channel_img, 0, 255, threshold_mode + cv2.THRESH_OTSU)

    kernel_size = max(1, args.kernel)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=max(0, args.open_iters))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=max(0, args.close_iters))

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

    print(f"{image_path.name}: extracted {len(valid_contours)} contour(s)")


def cmd(args):
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = _validate_image_file(args.input)
    _extract_contours(args, image_path, output_dir)
