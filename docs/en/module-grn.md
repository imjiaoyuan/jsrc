# jsrc grn

Gene regulatory network (GRN) analysis and interactive visualization. From edge tables to force-directed graphs with expand, search, and export.

## net2json

The entry point for GRN visualization. Converts an edge table into the JSON format the viewer expects, with control over display mode. Two modes: `-a` (full view — automatically shows the entire network when nodes are below a threshold) and `-s` (compact mode — manual click-to-expand). Optionally attach annotation data via `-n` to display extra info on each node.

```bash
jsrc grn net2json -i grn.tsv -o viewer/json/grn.json -a -t 200 \
  -n annotation.tsv --max-nodes 200
jsrc grn net2json -i grn.tsv -o viewer/json/grn.json -s
```

- `-i, --input`: GRN edge table (tab-delimited).
- `-o, --output`: output grn.json path.
- `-a, --all`: all mode. Auto-displays full network when gene count is at or below threshold.
- `-s, --some`: some mode. Manual click-to-expand.
- `-t, --threshold`: threshold for `-a` mode (default: `300`).
- `-d, --viewer-dir`: viewer output directory; inferred from `-o` if not given.
- `-n, --annotation-input`: optional annotation TSV to generate annotation.json.
- `-z, --zip-output`: optional ZIP output packaging index.html, CSS/JS, and JSON.
- `--max-nodes`: max nodes shown in full view (default: `0` = all).

## anno2json

Generates annotation.json separately when the network JSON is already prepared, without re-running the full conversion pipeline.

```bash
jsrc grn anno2json -i annotation.tsv -o viewer/json/annotation.json
```

- `-i, --input`: annotation TSV input.
- `-o, --output`: output annotation.json.

## serve

Start a local HTTP server to view the GRN graph in a browser. Supports the same all/some display modes. Annotated networks show node grouping information.

```bash
jsrc grn serve -d viewer -g viewer/json/grn.json -p 8000 -a -t 200
jsrc grn serve -d viewer -g viewer/json/grn.json \
  -n viewer/json/annotation.json -s
```

- `-d, --dir`: viewer directory to serve (default: current directory).
- `-g, --grn-json`: path to grn.json (required).
- `-n, --annotation-json`: path to annotation.json (optional).
- `-p, --port`: HTTP port (default: `8000`).
- `-a, --all`: all mode.
- `-s, --some`: some mode.
- `-t, --threshold`: threshold for `-a` mode (default: `300`).

## centrality

Once the network is built, the natural next question is which genes are the key players. This command computes in-degree, out-degree, and total degree for each node, sorting by total degree to quickly identify hub genes.

```bash
jsrc grn centrality -i grn.tsv --sep "\t" --top 30
```

- `-i, --input`: edge table.
- `--sep`: column separator (default: auto whitespace/tab).
- `--top`: output top N nodes (default: `20`).
