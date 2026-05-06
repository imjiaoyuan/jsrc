# jsrc grn

Gene regulatory network (GRN) analysis and interactive visualization. From edge tables to force-directed graphs with expand, search, and export.

## net2json

Converts a GRN edge table (TSV) to JSON for downstream use.

Example input (`grn.tsv`):

```tsv
GENE_A	GENE_B	0.82
GENE_B	GENE_C	1.15
```

```bash
jsrc grn net2json -i grn.tsv -o json/grn.json
```

- `-i, --input`: GRN edge table (tab-delimited).
- `-o, --output`: output JSON path.

## anno2json

Converts an annotation TSV to JSON.

Example input (`annotation.tsv`):

```tsv
GENE_A	Anthranilate synthase	AT1G01010
GENE_B	Transcription factor	Potri.001G000100
```

```bash
jsrc grn anno2json -i annotation.tsv -o json/annotation.json
```

- `-i, --input`: annotation TSV.
- `-o, --output`: output annotation.json.

## build

Builds a static viewer page from a grn JSON file and an optional annotation JSON, optionally packaged as a ZIP for deployment. `-a` for full-view mode (auto-display when node count is under threshold), `-e` for click-to-expand mode.

```bash
jsrc grn build -d viewer -g json/grn.json -n json/annotation.json -a -t 200
jsrc grn build -d viewer -g json/grn.json -z viewer.zip -e
```

- `-d, --dir`: output directory (default: current directory).
- `-g, --grn-json`: path to grn.json, copied to `json/` in output.
- `-n, --annotation-json`: path to annotation.json (optional).
- `-z, --zip-output`: ZIP output path.
- `-a, --all`: full-view mode.
- `-e, --expand`: click-to-expand mode.
- `-t, --threshold`: auto full-view threshold (default: `300`).
- `--max-nodes`: max nodes in full view (`0` = all).

## serve

Starts a local HTTP server to serve the GRN viewer. Supports all/expand modes. Default port 8000.

```bash
jsrc grn serve -d viewer -g viewer/json/grn.json -p 8000 -a -t 200
jsrc grn serve -d viewer -g viewer/json/grn.json \
  -n viewer/json/annotation.json -e
```

- `-d, --dir`: viewer directory (default: current directory).
- `-g, --grn-json`: path to grn.json (required).
- `-n, --annotation-json`: path to annotation.json (optional).
- `-p, --port`: HTTP port (default: `8000`).
- `-a, --all`: full-view mode.
- `-e, --expand`: click-to-expand mode.
- `-t, --threshold`: auto full-view threshold (default: `300`).

## centrality

Computes in-degree, out-degree, and total degree for each node, sorted by total degree to identify hub genes.

```bash
jsrc grn centrality -i grn.tsv --sep "\t" --top 30
```

- `-i, --input`: edge table.
- `--sep`: column separator (default: auto whitespace/tab).
- `--top`: output top N nodes (default: `20`).
