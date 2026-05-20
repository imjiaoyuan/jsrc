# jsrc

用于生物信息学分析和科学计算的 Python 库。

## 安装

推荐（使用 `uv tool` 全局安装命令行）：
```bash
uv tool install jsrc
```

使用 `uv` 虚拟环境安装：
```bash
uv venv
source .venv/bin/activate
uv pip install jsrc
```

使用 Conda 创建虚拟环境并通过 pip 安装：
```bash
conda create -n jsrc python=3.11 -y
conda activate jsrc
pip install jsrc
```

## 快速开始

```bash
jsrc --help
jsrc <module> --help
jsrc <module> <subcommand> --help
```

## 模块总览

| 模块 | 说明 |
|---|---|
| `seq` | 序列提取、重命名、翻译、QC、k-mer、滑窗分析 |
| `genome` | 基因组统计、特征检测、比较分析、进化分析 |
| `plot` | 基因/外显子/染色体/结构域等可视化 |
| `analyze` | 系统发育、motif、一致序列、SNP/INDEL、QC |
| `gs` | 基因组选择数据构建、划分与训练流程 |
| `grn` | GRN 转换、中心性分析、build 打包与服务 |
| `vision` | 图像轮廓提取、EFD 描述子、形态指标 |
| `job` | 后台任务提交、查看、日志、终止、历史清理 |

## 错误输出约定

- 用户输入/参数错误统一输出为 `Error: <message>`。
- 缺失文件、参数非法、输入不匹配等场景尽量保持同一风格。

## 模块文档

- [序列模块](./module-seq.md)
- [基因组模块](./module-genome.md)
- [分析模块](./module-analyze.md)
- [绘图模块](./module-plot.md)
- [GS 模块](./module-gs.md)
- [GRN 模块](./module-grn.md)
- [视觉模块](./module-vision.md)
- [任务模块](./module-job.md)
