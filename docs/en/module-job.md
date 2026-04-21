# jsrc job

> Compatibility note: currently tested on **Arch Linux**.

## submit

Use this to launch and register long-running tasks in one step. It captures command metadata, runtime status, and memory statistics so you can trace work later without guessing.

```bash
jsrc job submit "Rscript 02.harmony2.R" "logs/02.harmony2.log" -N harmony -C . -S bash -A -E KEY=VAL
```

- `command` (positional): command string to run under nohup.
- `log` (positional, optional): log file path.
- `-N, --name`: optional job name.
- `-C, --cwd`: working directory (default: current directory).
- `-S, --shell`: shell binary used with `-lc` (default: `bash`).
- `-A, --append`: append log instead of overwrite.
- `-E, --env`: extra environment variable `KEY=VAL` (repeatable).

## ls

This is your real-time dashboard. It can stream updates, sort by runtime or memory, and filter by keywords so you can focus on the jobs that matter now.

```bash
jsrc job ls -w -n 2 -c job_id,status,pid,runtime,rss_mb,rss_min_mb,rss_avg_mb,rss_peak_mb -f table -s runtime -r -a -l 50 -q harmony
```

- `-w, --watch`: refresh continuously.
- `-n, --interval`: refresh interval in seconds (default: `2.0`).
- `-c, --cols`: comma-separated columns to display.
- `-f, --format`: output format `table|tsv|json` (default: `table`).
- `-s, --sort`: sort key (`submit_time|elapsed|runtime|runtime_sec|rss_mb|rss_min_mb|rss_avg_mb|rss_peak_mb|pid|job_id|status`).
- `-r, --reverse`: reverse sort order.
- `-a, --all`: show all records.
- `-l, --limit`: max rows when not using `--all` (default: `20`).
- `-q, --query`: filter text on command/name/log path.

## show

Need full details for one specific task? This command gives a focused single-job view by job ID or PID.

```bash
jsrc job show 12 -f json -c job_id,status,pid,runtime,rss_mb,rss_avg_mb,command
```

- `target` (positional): job ID or PID.
- `-f, --format`: output format `table|json` (default: `table`).
- `-c, --cols`: comma-separated columns to display.

## logs

When you need to read execution output, this command tails or follows the saved log file without manual path lookup.

```bash
jsrc job logs 12 -n 200 -F
```

- `target` (positional): job ID or PID.
- `-n, --lines`: tail line count (default: `100`).
- `-F, --follow`: follow log output in real time.

## kill

If a task is stuck or no longer needed, use this to stop it cleanly, either by PID or by process group.

```bash
jsrc job kill 12 -s TERM -g
```

- `target` (positional): job ID or PID.
- `-s, --signal`: signal `TERM|KILL|INT` (default: `TERM`).
- `-g, --group`: kill process group instead of single PID.

## history

For audit and reproducibility, this shows your recorded execution history with filtering and multiple output formats.

```bash
jsrc job history -l 100 -f tsv -q harmony
```

- `-l, --limit`: max history rows (default: `50`).
- `-f, --format`: output format `table|tsv|json` (default: `table`).
- `-q, --query`: filter text on command/name/log path.

## gc

Use this to keep the tracker tidy by capping history size and cleaning stale bookkeeping artifacts.

```bash
jsrc job gc -k 1000 --prune-missing-log --remove-dead-state
```

- `-k, --keep-history`: keep last N history records (default: `1000`).
- `--prune-missing-log`: mark records with missing log files.
- `--remove-dead-state`: remove stale state files.
