# Vision Module

```bash
jsrc vision extract -i sample.png -o extracted/
jsrc vision extract -i sample.png -o extracted/ --channel a --invert --save-mask
```

Use this to segment an image and export object contours. Input is a single image file, and output goes to the target directory as contour arrays (`.npy`) plus edge previews (`.png`), with optional mask export when `--save-mask` is enabled.

---

```bash
jsrc vision efd -i extracted/ -o descriptors/ --harmonics 20
```

Use this to convert extracted contour files into elliptic Fourier descriptors. Input can be one `.npy` file or a directory of `.npy` files, and output includes descriptor CSV files plus optional reconstruction plots.

---

```bash
jsrc vision traits -i sample.png --channel a
```

Use this for quick morphology metrics from the primary segmented object in an image. Input is a single image, and output is a terminal summary including area, perimeter, aspect ratio, circularity, extent, and solidity.
