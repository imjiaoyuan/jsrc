# jsrc vision

OpenCV-based image analysis tools for plant phenotyping: contour extraction, elliptic Fourier descriptors (EFD), and morphological trait calculation.

## extract

Extracts target contours from images. Supports thresholding in grayscale, Lab (a-channel), and HSV (s/v-channel). Adjustable parameters include Gaussian blur, morphological open/close operations, and area/aspect-ratio filters. Outputs sub-images sorted by x or y coordinate, optionally with a binary mask.

```bash
jsrc vision extract -i sample.png -o extracted/ \
  --channel a --invert --blur 5 --kernel 3 \
  --open-iters 2 --close-iters 2 \
  --min-area-ratio 0.0005 --max-area-ratio 0.8 \
  --min-aspect-ratio 0.1 --max-aspect-ratio 10 \
  --sort-by x --save-mask
```

- `-i, --input`: input image path.
- `-o, --output`: output directory.
- `--channel`: threshold channel, one of `gray,a,b,s,v` (default: `gray`).
- `--invert`: invert threshold result.
- `--blur`: Gaussian blur kernel size, odd integer (default: `5`).
- `--kernel`: morphology kernel size (default: `3`).
- `--open-iters`: open iterations (default: `2`).
- `--close-iters`: close iterations (default: `2`).
- `--min-area-ratio`: minimum contour area ratio (default: `0.0005`).
- `--max-area-ratio`: maximum contour area ratio (default: `0.8`).
- `--min-aspect-ratio`: minimum aspect ratio (default: `0.1`).
- `--max-aspect-ratio`: maximum aspect ratio (default: `10.0`).
- `--sort-by`: output order by `x` or `y` (default: `x`).
- `--save-mask`: save binary mask image.

## efd

Computes elliptic Fourier descriptors from extracted contours, compressing shape information into a set of harmonic coefficients. Coefficients can be used for shape clustering or classification. Supports batch processing of `.npy` contour files, with optional reconstruction preview plots.

```bash
jsrc vision efd -i extracted/ -o descriptors/ \
  --harmonics 20 --points 300 --no-plot
```

- `-i, --input`: input `.npy` file or directory.
- `-o, --output`: output directory.
- `--harmonics`: number of EFD harmonics (default: `20`).
- `--points`: reconstruction points for preview (default: `300`).
- `--no-plot`: skip preview plot generation.

## traits

Extracts morphological traits in one step. Given an image, it segments via thresholding and computes contour area, perimeter, dimensions, circularity, eccentricity, and other traits. Convenient for batch morphometric analysis.

```bash
jsrc vision traits -i sample.png --channel a --invert --blur 5 --kernel 3
```

- `-i, --input`: input image path.
- `--channel`: threshold channel, one of `gray,a,b,s,v` (default: `gray`).
- `--invert`: invert threshold.
- `--blur`: Gaussian blur kernel size, odd integer (default: `5`).
- `--kernel`: morphology kernel size (default: `3`).
