# jsrc vision

基于 OpenCV 的图像处理工具集，主要面向植物表型相关的图像分析：轮廓提取、椭圆傅里叶描述子（EFD）、形态特征计算。

## extract

从图像中提取目标轮廓。支持灰度、Lab（a 通道）、HSV（s/v 通道）等多种色彩空间下的阈值分割。可调参数包括高斯模糊、形态学开闭运算、面积和宽高比过滤。输出按 x 或 y 坐标排序的子图，可选择保存二值掩膜。

```bash
jsrc vision extract -i sample.png -o extracted/ \
  --channel a --invert --blur 5 --kernel 3 \
  --open-iters 2 --close-iters 2 \
  --min-area-ratio 0.0005 --max-area-ratio 0.8 \
  --min-aspect-ratio 0.1 --max-aspect-ratio 10 \
  --sort-by x --save-mask
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

对提取的轮廓进行椭圆傅里叶描述子分析，将形状信息压缩成一组谐波系数。系数可用于后续的形状聚类或分类。支持批量处理目录中的 `.npy` 轮廓文件，可选生成重建预览图。

```bash
jsrc vision efd -i extracted/ -o descriptors/ \
  --harmonics 20 --points 300 --no-plot
```

- `-i, --input`：输入 `.npy` 文件或目录。
- `-o, --output`：输出目录。
- `--harmonics`：EFD 谐波数，默认 `20`。
- `--points`：重建预览点数，默认 `300`。
- `--no-plot`：不生成预览图。

## traits

一步提取形态特征：给定原始图像，经阈值分割后计算轮廓的面积、周长、长宽、圆度、离心率等性状指标。适合快速批量获取形态参数。

```bash
jsrc vision traits -i sample.png --channel a --invert --blur 5 --kernel 3
```

- `-i, --input`：输入图像路径。
- `--channel`：阈值通道，可选 `gray,a,b,s,v`（默认 `gray`）。
- `--invert`：反转阈值。
- `--blur`：高斯模糊大小（奇数），默认 `5`。
- `--kernel`：形态学核大小，默认 `3`。
