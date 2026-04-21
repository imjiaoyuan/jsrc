# GRN Module

```bash
jsrc grn net2json -i grn.tsv -o viewer/json/grn.json
jsrc grn net2json -i grn.tsv -o viewer/json/grn.json -a -t 200
jsrc grn net2json -i grn.tsv -o viewer/json/grn.json -s
jsrc grn net2json -i grn.tsv -o viewer/json/grn.json -n annotation.tsv -z viewer.zip
```

Use this to convert a tabular GRN edge list into viewer-ready JSON. Mode `-a/--all` enables auto full-network view when gene count is below `-t/--threshold`; mode `-s/--some` keeps the original click-to-expand behavior. Add `-z/--zip-output` to package HTML/CSS/JS + JSON into one ZIP.

---

```bash
jsrc grn anno2json -i annotation.tsv -o viewer/json/annotation.json
```

Use this to convert node annotation tables into JSON metadata dictionaries. Input is a tab-delimited annotation file, and output is JSON used by the viewer to display node-level details.

---

```bash
jsrc grn serve -d viewer -p 8000
jsrc grn serve -d viewer -p 8000 -a -t 200
jsrc grn serve -d viewer -p 8000 -s
```

Use this to host the viewer directory locally for browser access, with the same two display modes (`-a` or `-s`).

---

```bash
jsrc grn centrality -i grn.tsv --top 30
```

Use this to rank nodes by degree-style centrality from an edge table. Input lines should be `source target` with optional weight, and output is a terminal table containing in-degree, out-degree, and total-degree summaries.
