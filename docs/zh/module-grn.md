# jsrc grn

## net2json

这是 GRN 数据进入可视化的主入口：边表转 JSON、选择展示模式、可选打包 ZIP，一次走完最常见流程。

```bash
jsrc grn net2json -i grn.tsv -o viewer/json/grn.json -a -t 200 -n annotation.tsv -z viewer.zip --max-nodes 200
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

只需要转换注释信息时，用它最省事。它把注释表直接转成 viewer 可读的 annotation.json。

```bash
jsrc grn anno2json -i annotation.tsv -o viewer/json/annotation.json
```

- `-i, --input`：注释 TSV 输入。
- `-o, --output`：输出 annotation.json。

## serve

数据准备好后，用这个命令本地启动浏览器服务。你可以沿用 all/some 两种展示模式做快速检查或演示。

```bash
jsrc grn serve -d viewer -g viewer/json/grn.json -p 8000 -a -t 200
jsrc grn serve -d viewer -g viewer/json/grn.json -n viewer/json/annotation.json -s
```

- `-d, --dir`：要服务的 viewer 目录（默认当前目录）。
- `-g, --grn-json`：grn.json 路径（必填）。
- `-n, --annotation-json`：annotation.json 路径（可选）。
- `-p, --port`：HTTP 端口，默认 `8000`。
- `-a, --all`：all 模式（小网络自动全显示）。
- `-s, --some`：some 模式（点击展开）。
- `-t, --threshold`：`-a` 模式阈值，默认 `300`。

## centrality

想快速知道哪些基因节点更“关键”，直接跑这个命令即可，输出入度/出度/总度的排序摘要。

```bash
jsrc grn centrality -i grn.tsv --sep "\t" --top 30
```

- `-i, --input`：边表输入。
- `--sep`：列分隔符（默认自动识别空白/tab）。
- `--top`：输出前 N 个节点，默认 `20`。
