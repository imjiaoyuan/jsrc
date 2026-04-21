# jsrc job

> 兼容性说明：当前仅在 **Arch Linux** 测试。

## submit

这个命令是提交与登记的一站式入口。任务一旦启动，就会同步记录命令、日志、运行状态和内存统计，后续追踪非常方便。

```bash
jsrc job submit "Rscript 02.harmony2.R" "logs/02.harmony2.log" -N harmony -C . -S bash -A -E KEY=VAL
```

- `command`（位置参数）：在 nohup 下执行的命令字符串。
- `log`（位置参数，可选）：日志文件路径。
- `-N, --name`：任务名称（可选）。
- `-C, --cwd`：工作目录（默认当前目录）。
- `-S, --shell`：执行 shell（默认 `bash`）。
- `-A, --append`：日志追加写入，不覆盖。
- `-E, --env`：附加环境变量 `KEY=VAL`（可重复）。

## ls

它就是你的实时任务看板：可持续刷新、按运行时长或内存排序、按关键词过滤，适合盯长期后台任务。

```bash
jsrc job ls -w -n 2 -c job_id,status,pid,runtime,rss_mb,rss_min_mb,rss_avg_mb,rss_peak_mb -f table -s runtime -r -a -l 50 -q harmony
```

- `-w, --watch`：持续刷新。
- `-n, --interval`：刷新间隔秒数（默认 `2.0`）。
- `-c, --cols`：显示列（逗号分隔）。
- `-f, --format`：输出格式 `table|tsv|json`（默认 `table`）。
- `-s, --sort`：排序字段（`submit_time|elapsed|runtime|runtime_sec|rss_mb|rss_min_mb|rss_avg_mb|rss_peak_mb|pid|job_id|status`）。
- `-r, --reverse`：倒序。
- `-a, --all`：显示全部记录。
- `-l, --limit`：不使用 `--all` 时的最大行数（默认 `20`）。
- `-q, --query`：按命令/名称/日志路径过滤。

## show

当你只关心某一个任务时，用这个命令最干脆，按任务 ID 或 PID 拉出完整详情。

```bash
jsrc job show 12 -f json -c job_id,status,pid,runtime,rss_mb,rss_avg_mb,command
```

- `target`（位置参数）：任务 ID 或 PID。
- `-f, --format`：输出格式 `table|json`（默认 `table`）。
- `-c, --cols`：显示列（逗号分隔）。

## logs

看日志不用再找文件路径，直接按任务 ID/PID 就能查看，配合 follow 模式可实时追踪输出。

```bash
jsrc job logs 12 -n 200 -F
```

- `target`（位置参数）：任务 ID 或 PID。
- `-n, --lines`：显示尾部行数（默认 `100`）。
- `-F, --follow`：实时跟随日志。

## kill

任务卡住或不再需要时，用它快速终止，既可杀单进程，也可按进程组结束整批子进程。

```bash
jsrc job kill 12 -s TERM -g
```

- `target`（位置参数）：任务 ID 或 PID。
- `-s, --signal`：信号 `TERM|KILL|INT`（默认 `TERM`）。
- `-g, --group`：按进程组终止。

## history

需要回溯执行历史、排查重复跑任务或整理记录时，这个命令能快速给你清晰的历史视图。

```bash
jsrc job history -l 100 -f tsv -q harmony
```

- `-l, --limit`：历史行数上限（默认 `50`）。
- `-f, --format`：输出格式 `table|tsv|json`（默认 `table`）。
- `-q, --query`：按命令/名称/日志路径过滤。

## gc

这个命令用于“做保洁”：控制历史条数上限、标记缺失日志、清理陈旧状态文件，让追踪系统长期保持干净。

```bash
jsrc job gc -k 1000 --prune-missing-log --remove-dead-state
```

- `-k, --keep-history`：保留最近 N 条历史（默认 `1000`）。
- `--prune-missing-log`：标记日志文件丢失的记录。
- `--remove-dead-state`：清理陈旧状态文件。
