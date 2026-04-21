# Job Module

```bash
jsrc job submit "Rscript 02.harmony2.R" "logs/02.harmony2.log"
jsrc job submit "python train.py --epochs 100"
```

Use this to submit and track long-running background jobs via `nohup`. Every submitted job is recorded in a plain-text history file at `~/.local/share/jsrc/jobs`, and default logs are written to `~/.local/share/jsrc/job-logs/`.

---

```bash
jsrc job ls
jsrc job ls -w -n 2
jsrc job ls -c job_id,status,pid,runtime,rss_mb,rss_min_mb,rss_avg_mb,rss_peak_mb,cpu_pct,command
```

Use this to inspect running and historical jobs. With `-w/--watch`, process state is refreshed in real time, including RSS current/min/avg/peak memory and runtime metrics, and updated values are written back to history.

---

```bash
jsrc job show 12
jsrc job show 24831 -f json
```

Use this to view one job in detail by job ID or PID.

---

```bash
jsrc job logs 12 -n 200
jsrc job logs 12 -F
```

Use this to read the saved log for a job (`-F/--follow` for streaming output).

---

```bash
jsrc job kill 12
jsrc job kill 24831 -s KILL -g
```

Use this to stop one job by ID or PID, optionally by process group.

---

```bash
jsrc job history -l 100
jsrc job gc -k 1000 --remove-dead-state
```

Use `history` to review recent command records and `gc` to enforce retention limits (default keep: 1000 records).
