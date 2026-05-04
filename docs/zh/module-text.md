# jsrc text

## wc

快速检查文本大小时的好工具，它能统计文件或标准输入的行数、词数和字符数。

```bash
jsrc text wc -i notes.txt --json
```

- `-i, --input`：输入文本文件（默认：标准输入）。
- `--json`：打印 JSON 格式输出。

## dedup

需要稳定、保持顺序的去重时，这个命令很对手，能保持首次出现的顺序。

```bash
jsrc text dedup -i lines.txt -o uniq.txt --count
```

- `-i, --input`：输入文本文件（默认：标准输入）。
- `-o, --output`：可选输出文件（默认：标准输出）。
- `--count`：打印每行出现次数。

## grep

用正则表达式快速过滤文本，配合便利的标志位非常适合日志切片和轻量级文本筛选。

```bash
jsrc text grep -p "error|warn" -i app.log -o out.txt -I -v -n
```

- `-p, --pattern`：正则表达式模式（必需）。
- `-i, --input`：输入文本文件（默认：标准输入）。
- `-o, --output`：可选输出文件（默认：标准输出）。
- `-I, --ignore-case`：大小写不敏感匹配。
- `-v, --invert`：反向匹配（保留不匹配的行）。
- `-n, --line-number`：输出带行号前缀。

## cut

用来快速按列索引切片分隔表格，特别是在 TSV/CSV 预处理时很方便。

```bash
jsrc text cut -f 1,3,5 -i table.tsv -d $'\t' --out-delimiter ","
```

- `-f, --fields`：1-based 列索引，逗号分隔。
- `-i, --input`：输入文本文件（默认：标准输入）。
- `-o, --output`：可选输出文件（默认：标准输出）。
- `-d, --delimiter`：输入分隔符（默认：制表符）。
- `--out-delimiter`：输出分隔符（默认：与输入分隔符相同）。

## replace

需要批量替换时，这个命令逐行应用正则查找替换，支持大小写不敏感和替换次数限制。

```bash
jsrc text replace -p "foo" -r "bar" -i file.txt -o out.txt -I --count 1
```

- `-p, --pattern`：正则表达式模式（必需）。
- `-r, --repl`：替换文本（必需）。
- `-i, --input`：输入文本文件（默认：标准输入）。
- `-o, --output`：可选输出文件（默认：标准输出）。
- `-I, --ignore-case`：大小写不敏感替换。
- `--count`：每行最大替换次数（默认：`0`，无限制）。
