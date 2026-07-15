# jsrc job

Background job management for long-running tasks. Submit, monitor, tail logs, terminate, review history, and clean up — designed for nohup-style tasks on non-cluster environments (e.g., your own workstation).

> Compatibility note: currently tested on **Arch Linux**.

## submit

Launch a command in the background via nohup, while recording its command, log path, status, and memory usage. Supports working directory, shell selection, and environment variables. Logs can be appended or overwritten.

```bash
jsrc job submit "Rscript 02.harmony2.R" "logs/02.harmony2.log" \
  -N harmony -C . -S bash -A -E KEY=VAL
```

- `command` (positional): command string to run under nohup.
- `log` (positional, optional): log file path.
- `-N, --name`: optional job name.
- `-C, --cwd`: working directory (default: current directory).
- `-S, --shell`: execution shell (default: `bash`).
- `-A, --append`: append to log instead of overwrite.
- `-E, --env`: extra environment variable `KEY=VAL` (repeatable).

## ls

Real-time job dashboard. List all jobs with sorting by runtime or memory, and keyword filtering. Output in table/tsv/json. Customize displayed columns with `-c`.

```bash
jsrc job ls -c PID,S,mem,time,command -f table -s runtime -r -a -l 50 -q harmony
```

- `-c, --cols`: comma-separated columns to display (default: `pid,s,mem,time,command`).
- `-f, --format`: output format `table|tsv|json` (default: `table`).
- `-s, --sort`: sort key (`submit_time|time|elapsed|runtime|runtime_sec|rss_mb|rss|rss_min_mb|rss_avg_mb|rss_peak_mb|pid|job_id|status|s|mem`).
- `-r, --reverse`: reverse sort.
- `-a, --all`: show all records.
- `-l, --limit`: max rows without `--all` (default: `20`).
- `-q, --query`: filter by command/name/log path.

## top

Live monitoring dashboard (like `top`). Auto-refreshes at a configurable interval, showing running jobs (or all jobs with `-a`) with real-time process metrics. Press Ctrl+C to exit.

```bash
jsrc job top -n 2 -c pid,s,mem,time,command -s runtime -r
jsrc job top -a -n 1
```

- `-n, --interval`: refresh interval in seconds (default: `2.0`).
- `-c, --cols`: comma-separated columns to display (default: `pid,s,mem,time,command`).
- `-s, --sort`: sort field (`submit_time|time|elapsed|runtime|runtime_sec|rss_mb|rss|rss_min_mb|rss_avg_mb|rss_peak_mb|pid|job_id|status|s|mem`).
- `-r, --reverse`: reverse sort order.
- `-a, --all`: show all jobs (default: running only).

## logs

View job logs without manually hunting down the log file path. Look up by job ID or PID. Supports `-F` for real-time log following (tail -f style).

```bash
jsrc job logs 12 -n 200 -F
```

- `target` (positional): job ID or PID.
- `-n, --lines`: tail line count (default: `100`).
- `-F, --follow`: follow log output in real time.

## kill

Terminate a stuck or unwanted job. Sends TERM by default, also supports KILL and INT. `-g` kills the entire process group.

```bash
jsrc job kill 12 -s TERM -g
```

- `target` (positional): job ID or PID.
- `-s, --signal`: signal `TERM|KILL|INT` (default: `TERM`).
- `-g, --group`: kill process group instead of single PID.

## history

Review past job execution history. Useful for checking whether a task was already run or compiling a work log. Supports keyword filtering and table/tsv/json output.

```bash
jsrc job history -l 100 -f tsv -q harmony
```

- `-l, --limit`: max history rows (default: `50`).
- `-f, --format`: output format `table|tsv|json` (default: `table`).
- `-q, --query`: filter by command/name/log path.

## gc

Cleanup command. Caps history at a set limit (`-k`), marks records with missing log files, and removes stale state files — prevents the tracker from growing indefinitely over time.

```bash
jsrc job gc -k 1000 --prune-missing-log --remove-dead-state
```

- `-k, --keep-history`: keep last N history records (default: `1000`).
- `--prune-missing-log`: mark records with missing log files.
- `--remove-dead-state`: remove stale state files.
