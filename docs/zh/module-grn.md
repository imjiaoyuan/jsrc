# jsrc grn

基因调控网络（GRN）的分析和交互可视化。从边表到可交互的力导向图，支持展开、搜索、导出。

## net2json

把 GRN 边表（TSV）转换成 JSON 格式，供后续展示使用。

示例输入（`grn.tsv`）：

```tsv
GENE_A	GENE_B	0.82
GENE_B	GENE_C	1.15
```

```bash
jsrc grn net2json -i grn.tsv -o json/grn.json
```

- `-i, --input`：GRN 边表输入（tab 分隔）。
- `-o, --output`：输出 JSON 路径。

## anno2json

把对应的注释 TSV 转换为 JSON。

示例输入（`annotation.tsv`）：

```tsv
GENE_A	Anthranilate synthase	AT1G01010
GENE_B	Transcription factor	Potri.001G000100
```

```bash
jsrc grn anno2json -i annotation.tsv -o json/annotation.json
```

- `-i, --input`：注释 TSV。
- `-o, --output`：输出 annotation.json。

## build

根据 grn 网络关系 JSON 文件和注释 JSON 文件（可选）构建的静态页面，可打包为 ZIP 用于部署。`-a` 为全视图模式（节点数低于阈值时自动全网展示），`-e` 为点击展开模式。

```bash
jsrc grn build -d public -g json/grn.json -n json/annotation.json -a -t 200
jsrc grn build -d public -g json/grn.json -z public.zip -e
```

- `-d, --dir`：输出目录（默认当前目录）。
- `-g, --grn-json`：grn.json 路径，复制到输出目录的 `json/` 下。
- `-n, --annotation-json`：annotation.json 路径（可选）。
- `-z, --zip-output`：ZIP 输出路径。
- `-a, --all`：全视图模式。
- `-e, --expand`：点击展开模式。
- `-t, --threshold`：`-a` 模式阈值（默认 `300`）。
- `--max-nodes`：全视图最多节点数（`0` = 全部）。

## serve

本地启动 HTTP 服务展示 GRN 网络。支持 all/expand 展示模式。默认端口 8000。

```bash
jsrc grn serve -d public -g json/grn.json -p 8000 -a -t 200
jsrc grn serve -d public -g json/grn.json \
  -n json/annotation.json -e
```

- `-d, --dir`：public 目录（默认当前目录）。
- `-g, --grn-json`：grn.json 路径（必填）。
- `-n, --annotation-json`：annotation.json 路径（可选）。
- `-p, --port`：HTTP 端口（默认 `8000`）。
- `-a, --all`：全视图模式。
- `-e, --expand`：点击展开模式。
- `-t, --threshold`：`-a` 模式阈值（默认 `300`）。

## centrality

计算网络中每个节点的入度、出度和总度，按总度排序输出 hub 基因。

```bash
jsrc grn centrality -i grn.tsv --sep "\t" --top 30
```

- `-i, --input`：边表。
- `--sep`：列分隔符（默认自动识别空白/tab）。
- `--top`：输出前 N 个节点（默认 `20`）。
