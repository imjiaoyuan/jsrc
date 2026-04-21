# Text Module

```bash
jsrc text wc -i notes.txt
cat notes.txt | jsrc text wc
jsrc text wc -i notes.txt --json
```

Use this for quick line/word/character counting from a file or stdin stream. Output is terminal text by default, and `--json` returns structured counts for scripts and pipelines.

---

```bash
jsrc text dedup -i lines.txt
jsrc text dedup -i lines.txt --count
jsrc text dedup -i lines.txt -o uniq.txt
```

Use this to remove duplicate lines while preserving first-seen order. Input can come from file or stdin, and output can go to stdout or a file; with `--count`, each unique line is prefixed by its occurrence count.

---

```bash
jsrc text grep -p "error|warn" -i app.log -I
jsrc text grep -p "DEBUG" -i app.log -v
jsrc text grep -p "sample" -i data.txt -n -o matched.txt
```

Use this for regex-based line filtering. Input is plain text from file or stdin, and options let you ignore case, invert matches, and keep line numbers. Output is either terminal text or a file if `-o` is provided.

---

```bash
jsrc text cut -f 1,3,5 -d "," -i table.csv
jsrc text cut -f 1,2 -d $'\t' --out-delimiter "," -i table.tsv
```

Use this to select columns from delimited text quickly. Input is a CSV/TSV-like text file, selected fields are 1-based via `-f`, and output delimiter can be adjusted for downstream tools.

---

```bash
jsrc text replace -p "chr([0-9]+)" -r "chromosome_\\1" -i ids.txt
jsrc text replace -p "foo" -r "bar" -i file.txt --count 1
```

Use this for line-by-line regex replacement. Input is text from file or stdin, replacement behavior is controlled by pattern/replacement/count options, and output can be printed or written to a file for reuse in later processing steps.
