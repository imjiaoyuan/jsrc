# jsrc 中文文档

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
| `plot` | 基因/外显子/染色体/结构域等可视化 |
| `analyze` | 系统发育、motif、一致序列、SNP/INDEL、QC |
| `gs` | 基因组选择数据构建、划分与训练流程 |
| `grn` | GRN 转换、中心性分析、viewer 打包与服务 |
| `vision` | 图像轮廓提取、EFD 描述子、形态指标 |
| `job` | 后台任务提交、查看、日志、终止、历史清理 |
| `math` | 统计与机器学习风格命令行工具 |

## 错误输出约定

- 用户输入/参数错误统一输出为 `Error: <message>`。
- 缺失文件、参数非法、输入不匹配等场景尽量保持同一风格。

## 模块文档

- [数学模块](./module-math.md)
- [序列模块](./module-seq.md)
- [分析模块](./module-analyze.md)
- [绘图模块](./module-plot.md)
- [GS 模块](./module-gs.md)
- [GRN 模块](./module-grn.md)
- [视觉模块](./module-vision.md)
- [任务模块](./module-job.md)
