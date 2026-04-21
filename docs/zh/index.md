# jsrc 中文文档

## 快速开始

```bash
git clone https://github.com/imjiaoyuan/jsrc.git
cd jsrc
uv venv
uv sync --extra dev
uv run jsrc --help
```

或：

```bash
pip install -e .
jsrc --help
```

运行格式：

```bash
jsrc <模块> <子命令> [参数]
```

## 模块文档

- [序列模块](./module-seq.md)
- [分析模块](./module-analyze.md)
- [绘图模块](./module-plot.md)
- [GS 模块](./module-gs.md)
- [GRN 模块](./module-grn.md)
- [视觉模块](./module-vision.md)
- [文本模块](./module-text.md)
- [任务模块](./module-job.md)
