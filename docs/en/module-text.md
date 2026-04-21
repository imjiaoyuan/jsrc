# jsrc text

## wc

Use this for quick text-size checks in pipelines or shell sessions. It reports lines, words, and characters from file or stdin.

```bash
jsrc text wc -i notes.txt --json
```

- `-i, --input`: input text file (default: stdin).
- `--json`: print JSON output.

## dedup

Perfect when you need stable, order-preserving deduplication without losing first-seen order.

```bash
jsrc text dedup -i lines.txt -o uniq.txt --count
```

- `-i, --input`: input text file (default: stdin).
- `-o, --output`: optional output file (default: stdout).
- `--count`: print occurrence counts for each unique line.

## grep

Regex filtering with common convenience flags. Great for log slicing and lightweight text triage.

```bash
jsrc text grep -p "error|warn" -i app.log -o out.txt -I -v -n
```

- `-p, --pattern`: regex pattern (required).
- `-i, --input`: input text file (default: stdin).
- `-o, --output`: optional output file (default: stdout).
- `-I, --ignore-case`: case-insensitive matching.
- `-v, --invert`: invert match (keep non-matching lines).
- `-n, --line-number`: prefix output with line number.

## cut

Use it to slice delimited tables quickly by column index, especially in TSV/CSV pre-processing.

```bash
jsrc text cut -f 1,3,5 -i table.tsv -d $'\t' --out-delimiter ","
```

- `-f, --fields`: 1-based field indices, comma-separated.
- `-i, --input`: input text file (default: stdin).
- `-o, --output`: optional output file (default: stdout).
- `-d, --delimiter`: input delimiter (default: tab).
- `--out-delimiter`: output delimiter (default: same as input delimiter).

## replace

When bulk replacement is needed, this command applies regex find/replace line by line with optional case-insensitive behavior and replacement caps.

```bash
jsrc text replace -p "foo" -r "bar" -i file.txt -o out.txt -I --count 1
```

- `-p, --pattern`: regex pattern (required).
- `-r, --repl`: replacement text (required).
- `-i, --input`: input text file (default: stdin).
- `-o, --output`: optional output file (default: stdout).
- `-I, --ignore-case`: case-insensitive replacement.
- `--count`: max replacements per line (default: `0`, unlimited).
