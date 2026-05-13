# jsrc job

长时间任务的后台作业管理。提交、查看、日志追踪、终止、历史回溯、清理——针对无集群环境（比如自己的工作站）的 nohup 类任务做了专门设计。

> 兼容性说明：当前仅在 **Arch Linux** 测试。

## submit

提交命令并在后台运行（通过 nohup），同时记录命令、日志路径、运行状态和内存占用。支持设置工作目录、执行 shell、环境变量。日志可追加也可覆盖写。

```bash
jsrc job submit "Rscript 02.harmony2.R" "logs/02.harmony2.log" \
  -N harmony -C . -S bash -A -E KEY=VAL
```

- `command`（位置参数）：在 nohup 下执行的命令字符串。
- `log`（位置参数，可选）：日志文件路径。
- `-N, --name`：任务名称（可选）。
- `-C, --cwd`：工作目录（默认当前目录）。
- `-S, --shell`：执行 shell（默认 `bash`）。
- `-A, --append`：日志追加写入，不覆盖。
- `-E, --env`：附加环境变量 `KEY=VAL`（可重复）。

## ls

实时任务看板。列出所有任务，可按运行时长或内存排序，按关键词过滤。输出格式支持 table/tsv/json，默认显示部分列，可用 `-c` 自定义。

```bash
jsrc job ls -c PID,S,mem,time,command -f table -s runtime -r -a -l 50 -q harmony
```

- `-c, --cols`：显示列（逗号分隔，默认 `pid,s,mem,time,command`）。
- `-f, --format`：输出格式 `table|tsv|json`（默认 `table`）。
- `-s, --sort`：排序字段（`submit_time|time|elapsed|runtime|runtime_sec|rss_mb|rss|rss_min_mb|rss_avg_mb|rss_peak_mb|pid|job_id|status|s|mem`）。
- `-r, --reverse`：倒序。
- `-a, --all`：显示全部记录。
- `-l, --limit`：不使用 `--all` 时的最大行数（默认 `20`）。
- `-q, --query`：按命令/名称/日志路径过滤。

## logs

不用手动找日志文件路径，按任务 ID 或 PID 直接查。支持 `-F` 实时跟随日志输出，类似 tail -f。

```bash
jsrc job logs 12 -n 200 -F
```

- `target`（位置参数）：任务 ID 或 PID。
- `-n, --lines`：显示尾部行数（默认 `100`）。
- `-F, --follow`：实时跟随日志。

## kill

任务卡住或不需要了，直接终止。默认发 TERM 信号，也支持 KILL 和 INT。`-g` 按进程组杀掉整批子进程。

```bash
jsrc job kill 12 -s TERM -g
```

- `target`（位置参数）：任务 ID 或 PID。
- `-s, --signal`：信号 `TERM|KILL|INT`（默认 `TERM`）。
- `-g, --group`：按进程组终止。

## history

回溯历史执行记录。适合排查是否重复跑了某个任务，或者整理一段时间内的作业清单。可按关键词过滤，输出 table/tsv/json。

```bash
jsrc job history -l 100 -f tsv -q harmony
```

- `-l, --limit`：历史行数上限（默认 `50`）。
- `-f, --format`：输出格式 `table|tsv|json`（默认 `table`）。
- `-q, --query`：按命令/名称/日志路径过滤。

## gc

"保洁"命令。控制历史记录上限（`-k`），标记日志文件已丢失的记录，清理陈旧的状态文件，避免追踪系统长期运行后越来越臃肿。

```bash
jsrc job gc -k 1000 --prune-missing-log --remove-dead-state
```

- `-k, --keep-history`：保留最近 N 条历史（默认 `1000`）。
- `--prune-missing-log`：标记日志文件丢失的记录。
- `--remove-dead-state`：清理陈旧状态文件。
