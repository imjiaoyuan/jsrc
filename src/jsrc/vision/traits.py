from pathlib import Path

import cv2

from jsrc.vision.extract import _ensure_odd, _get_channel_image


def cmd(args):
    path = Path(args.input)
    img = cv2.imread(str(path))
    if img is None:
        raise SystemExit(f"Cannot read image: {args.input}")

    blur_ksize = _ensure_odd(args.blur)
    blurred = cv2.GaussianBlur(img, (blur_ksize, blur_ksize), 0)
    channel_img = _get_channel_image(blurred, args.channel)
    threshold_mode = cv2.THRESH_BINARY_INV if args.invert else cv2.THRESH_BINARY
    _, binary = cv2.threshold(channel_img, 0, 255, threshold_mode + cv2.THRESH_OTSU)

    kernel_size = max(1, args.kernel)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise SystemExit("No contour found")
    cnt = max(contours, key=cv2.contourArea)

    area = float(cv2.contourArea(cnt))
    perimeter = float(cv2.arcLength(cnt, True))
    x, y, w, h = cv2.boundingRect(cnt)
    bbox_area = float(w * h) if w > 0 and h > 0 else 0.0
    hull = cv2.convexHull(cnt)
    hull_area = float(cv2.contourArea(hull))

    circularity = (4.0 * 3.141592653589793 * area / (perimeter * perimeter)) if perimeter > 0 else 0.0
    aspect_ratio = (w / h) if h > 0 else 0.0
    extent = (area / bbox_area) if bbox_area > 0 else 0.0
    solidity = (area / hull_area) if hull_area > 0 else 0.0

    print(f"area\t{area:.4f}")
    print(f"perimeter\t{perimeter:.4f}")
    print(f"aspect_ratio\t{aspect_ratio:.6f}")
    print(f"circularity\t{circularity:.6f}")
    print(f"extent\t{extent:.6f}")
    print(f"solidity\t{solidity:.6f}")
