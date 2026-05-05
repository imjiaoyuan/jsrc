# jsrc grn

基因调控网络（GRN）的分析和交互可视化。从边表到可交互的力导向图，支持展开/搜索/导出。

## net2json

GRN 可视化的入口。把边表转换成 viewer 所需的 JSON 格式，同时控制网络的展示模式。支持两种模式：`-a`（全视图，节点数低于阈值时自动全网展示）和 `-s`（缩略模式，保持手动点击展开）。还可以附带注释文件（`-n`），生成 annotation.json，网络节点上会显示基因的附加信息。

```bash
jsrc grn net2json -i grn.tsv -o viewer/json/grn.json -a -t 200 \
  -n annotation.tsv --max-nodes 200
jsrc grn net2json -i grn.tsv -o viewer/json/grn.json -s
```

- `-i, --input`：GRN 边表输入（tab 分隔）。
- `-o, --output`：输出 grn.json 路径。
- `-a, --all`：all 模式。基因数小于等于阈值时自动全网显示。
- `-s, --some`：some 模式。保持手动点击展开。
- `-t, --threshold`：`-a` 模式阈值，默认 `300`。
- `-d, --viewer-dir`：viewer 输出目录；不填则根据 `-o` 推断。
- `-n, --annotation-input`：可选注释 TSV，生成 annotation.json。
- `-z, --zip-output`：可选 ZIP 输出路径，打包 index.html、CSS/JS 和 JSON。
- `--max-nodes`：全视图模式下最多显示的基因数（默认 `0` = 全部显示）。

## anno2json

如果只需要转换注释信息、网络 JSON 已经准备好了，用这个命令单独生成 annotation.json。输入注释 TSV，输出给 viewer 用。

```bash
jsrc grn anno2json -i annotation.tsv -o viewer/json/annotation.json
```

- `-i, --input`：注释 TSV 输入。
- `-o, --output`：输出 annotation.json。

## serve

数据准备好后，本地启动一个 HTTP 服务来展示 GRN 网络。同样支持 all/some 两种展示模式，默认端口 8000。带注释的网络会额外显示节点分组信息。

```bash
jsrc grn serve -d viewer -g viewer/json/grn.json -p 8000 -a -t 200
jsrc grn serve -d viewer -g viewer/json/grn.json \
  -n viewer/json/annotation.json -s
```

- `-d, --dir`：要服务的 viewer 目录（默认当前目录）。
- `-g, --grn-json`：grn.json 路径（必填）。
- `-n, --annotation-json`：annotation.json 路径（可选）。
- `-p, --port`：HTTP 端口，默认 `8000`。
- `-a, --all`：all 模式（小网络自动全显示）。
- `-s, --some`：some 模式（点击展开）。
- `-t, --threshold`：`-a` 模式阈值，默认 `300`。

## centrality

网络构建完后，经常要问"哪些基因是关键节点"。这个命令算每个节点的入度、出度和总度，按总度排序输出，快速定位网络中的 hub 基因。

```bash
jsrc grn centrality -i grn.tsv --sep "\t" --top 30
```

- `-i, --input`：边表输入。
- `--sep`：列分隔符（默认自动识别空白/tab）。
- `--top`：输出前 N 个节点，默认 `20`。
