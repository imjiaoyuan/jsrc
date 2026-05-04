# GRN Module

```bash
jsrc grn net2json -i grn.tsv -o viewer/json/grn.json
```

Use this to convert a tabular GRN edge list into viewer-ready JSON. Input is a text table of network edges, and output is a JSON file that can be loaded by the GRN frontend.

---

```bash
jsrc grn anno2json -i annotation.tsv -o viewer/json/annotation.json
```

Use this to convert node annotation tables into JSON metadata dictionaries. Input is a tab-delimited annotation file, and output is JSON used by the viewer to display node-level details.

---

```bash
jsrc grn serve -d viewer -p 8000
```

Use this to host the viewer directory locally for browser access. Input is the directory path and optional port, and output is a running local HTTP service that serves the GRN page and assets.

---

```bash
jsrc grn centrality -i grn.tsv --top 30
```

Use this to rank nodes by degree-style centrality from an edge table. Input lines should be `source target` with optional weight, and output is a terminal table containing in-degree, out-degree, and total-degree summaries.
