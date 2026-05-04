# jsrc grn

## net2json

This is the main entry for turning edge tables into viewer-ready assets. It can stay in expandable mode, switch to small-network full display automatically, and package everything into a ZIP for sharing.

```bash
jsrc grn net2json -i grn.tsv -o viewer/json/grn.json -a -t 200 -n annotation.tsv -z viewer.zip
jsrc grn net2json -i grn.tsv -o viewer/json/grn.json -s
```

- `-i, --input`: GRN edge table input (tab-delimited).
- `-o, --output`: output grn.json path.
- `-a, --all`: all mode. Small networks auto-render as full graph when gene count is under threshold.
- `-s, --some`: some mode. Keep manual click-to-expand behavior.
- `-t, --threshold`: gene-count threshold used by `-a` (default: `300`).
- `-d, --viewer-dir`: viewer output directory. If omitted, inferred from `-o`.
- `-n, --annotation-input`: optional annotation TSV to generate annotation.json.
- `-z, --zip-output`: optional ZIP output path to package index.html, CSS/JS, and JSON files.

## anno2json

Use this when you only need to convert annotation metadata into viewer-compatible JSON without touching the network conversion pipeline.

```bash
jsrc grn anno2json -i annotation.tsv -o viewer/json/annotation.json
```

- `-i, --input`: annotation TSV input.
- `-o, --output`: output annotation.json.

## serve

Once your viewer files are ready, this starts a local HTTP service so you can inspect the graph in a browser with the same display-mode logic.

```bash
jsrc grn serve -d viewer -p 8000 -a -t 200
jsrc grn serve -d viewer -p 8000 -s
```

- `-d, --dir`: viewer directory to serve (default: current directory).
- `-p, --port`: HTTP port (default: `8000`).
- `-a, --all`: all mode (auto full-view for small networks).
- `-s, --some`: some mode (manual click-to-expand).
- `-t, --threshold`: gene-count threshold used by `-a` (default: `300`).

## centrality

Need a quick ranking of influential nodes? This command computes degree-style centrality summaries directly from your edge table.

```bash
jsrc grn centrality -i grn.tsv --sep "\t" --top 30
```

- `-i, --input`: edge table input.
- `--sep`: custom separator (default: auto whitespace/tab).
- `--top`: print top N nodes (default: `20`).
