# jsrc vision

## extract

```bash
jsrc vision extract -i sample.png -o extracted/ --channel a --invert --blur 5 --kernel 3 --open-iters 2 --close-iters 2 --min-area-ratio 0.0005 --max-area-ratio 0.8 --min-aspect-ratio 0.1 --max-aspect-ratio 10 --sort-by x --save-mask
```

- `-i, --input`：输入图像路径。
- `-o, --output`：输出目录。
- `--channel`：阈值通道，可选 `gray,a,b,s,v`（默认 `gray`）。
- `--invert`：反转阈值结果。
- `--blur`：高斯模糊核大小（奇数），默认 `5`。
- `--kernel`：形态学核大小，默认 `3`。
- `--open-iters`：开运算次数，默认 `2`。
- `--close-iters`：闭运算次数，默认 `2`。
- `--min-area-ratio`：最小轮廓面积比例，默认 `0.0005`。
- `--max-area-ratio`：最大轮廓面积比例，默认 `0.8`。
- `--min-aspect-ratio`：最小宽高比，默认 `0.1`。
- `--max-aspect-ratio`：最大宽高比，默认 `10.0`。
- `--sort-by`：输出排序，`x` 或 `y`（默认 `x`）。
- `--save-mask`：保存二值掩膜图。

## efd

```bash
jsrc vision efd -i extracted/ -o descriptors/ --harmonics 20 --points 300 --no-plot
```

- `-i, --input`：输入 `.npy` 文件或目录。
- `-o, --output`：输出目录。
- `--harmonics`：EFD 谐波数，默认 `20`。
- `--points`：重建预览点数，默认 `300`。
- `--no-plot`：不生成预览图。

## traits

```bash
jsrc vision traits -i sample.png --channel a --invert --blur 5 --kernel 3
```

- `-i, --input`：输入图像路径。
- `--channel`：阈值通道，可选 `gray,a,b,s,v`（默认 `gray`）。
- `--invert`：反转阈值。
- `--blur`：高斯模糊大小（奇数），默认 `5`。
- `--kernel`：形态学核大小，默认 `3`。
