from __future__ import annotations

import csv
import json
import os
import shlex
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

FIELDS = [
    "job_id",
    "name",
    "submit_time",
    "start_time",
    "end_time",
    "status",
    "pid",
    "exit_code",
    "cwd",
    "log_path",
    "rss_kb_last",
    "rss_kb_min",
    "rss_kb_peak",
    "rss_kb_sum",
    "rss_samples",
    "runtime_sec",
    "command",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _to_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _data_home() -> Path:
    xdg = os.getenv("XDG_DATA_HOME")
    if xdg:
        return Path(xdg).expanduser() / "jsrc"
    return Path.home() / ".local" / "share" / "jsrc"


def _history_path() -> Path:
    override = os.getenv("JSRC_JOBS_FILE", "")
    if override:
        return Path(override).expanduser()
    return _data_home() / "jobs"


def _default_log_dir() -> Path:
    return _data_home() / "job-logs"


def _state_dir() -> Path:
    return _data_home() / "job-state"


def _ensure_dirs() -> None:
    _history_path().parent.mkdir(parents=True, exist_ok=True)
    _default_log_dir().mkdir(parents=True, exist_ok=True)
    _state_dir().mkdir(parents=True, exist_ok=True)


def _load_jobs() -> list[dict[str, str]]:
    path = _history_path()
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        rows = []
        for row in reader:
            rows.append({k: row.get(k, "") for k in FIELDS})
        return rows


def _write_jobs(rows: list[dict[str, str]], keep: int | None = None) -> None:
    if keep is not None and keep > 0 and len(rows) > keep:
        rows = rows[-keep:]
    path = _history_path()
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in FIELDS})


def _next_job_id(rows: list[dict[str, str]]) -> int:
    if not rows:
        return 1
    return max(_to_int(r.get("job_id", "0")) for r in rows) + 1


def _state_file(job_id: str) -> Path:
    return _state_dir() / f"{job_id}.exit"


def _read_exit_code(job_id: str) -> str:
    path = _state_file(job_id)
    if not path.exists():
        return ""
    value = path.read_text(encoding="utf-8").strip()
    return value


def _get_rss_kb_from_status(pid: int) -> int:
    status = Path(f"/proc/{pid}/status")
    if not status.exists():
        return 0
    for line in status.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("VmRSS:"):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                return int(parts[1])
    return 0


def _process_alive(pid: int) -> bool:
    return Path(f"/proc/{pid}").exists()


def _ps_row(pid: int) -> tuple[bool, str, float, str]:
    proc = subprocess.run(
        ["ps", "-o", "etime=,pcpu=,stat=", "-p", str(pid)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return False, "", 0.0, ""
    line = proc.stdout.strip()
    if not line:
        return False, "", 0.0, ""
    parts = line.split(None, 2)
    if len(parts) < 3:
        return False, "", 0.0, ""
    etime, pcpu, stat = parts
    return True, etime, _to_float(pcpu, 0.0), stat


def _etime_to_seconds(etime: str) -> int:
    if not etime:
        return 0
    days = 0
    if "-" in etime:
        d, rest = etime.split("-", 1)
        days = _to_int(d, 0)
        etime = rest
    parts = etime.split(":")
    if len(parts) == 3:
        h, m, s = (_to_int(x, 0) for x in parts)
    elif len(parts) == 2:
        h = 0
        m, s = (_to_int(x, 0) for x in parts)
    else:
        h = 0
        m = 0
        s = _to_int(parts[0], 0)
    return days * 86400 + h * 3600 + m * 60 + s


def _parse_iso(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def _runtime_seconds(row: dict[str, str], live: dict[str, str]) -> int:
    if row.get("status", "") == "running":
        return _etime_to_seconds(live.get("etime", ""))
    stored = _to_int(row.get("runtime_sec", "0"), 0)
    if stored > 0:
        return stored
    start = _parse_iso(row.get("start_time", ""))
    end = _parse_iso(row.get("end_time", ""))
    if start and end:
        return max(0, int((end - start).total_seconds()))
    return 0


def _format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "0s"
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    if days > 0:
        return f"{days}d{hours:02d}h{minutes:02d}m{secs:02d}s"
    if hours > 0:
        return f"{hours}h{minutes:02d}m{secs:02d}s"
    if minutes > 0:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


def _to_row_view(row: dict[str, str], live: dict[str, str]) -> dict[str, str]:
    rss_kb = _to_int(row.get("rss_kb_last", "0"), 0)
    min_kb = _to_int(row.get("rss_kb_min", "0"), 0)
    if min_kb <= 0 and rss_kb > 0:
        min_kb = rss_kb
    peak_kb = _to_int(row.get("rss_kb_peak", "0"), 0)
    sum_kb = _to_int(row.get("rss_kb_sum", "0"), 0)
    samples = _to_int(row.get("rss_samples", "0"), 0)
    avg_kb = int(sum_kb / samples) if samples > 0 else rss_kb
    runtime_sec = _runtime_seconds(row, live)
    out = dict(row)
    out["rss_mb"] = f"{rss_kb / 1024:.1f}"
    out["rss_min_mb"] = f"{min_kb / 1024:.1f}"
    out["rss_avg_mb"] = f"{avg_kb / 1024:.1f}"
    out["rss_peak_mb"] = f"{peak_kb / 1024:.1f}"
    out["elapsed"] = live.get("etime", "")
    out["elapsed_sec"] = str(_etime_to_seconds(live.get("etime", "")))
    out["runtime_sec"] = str(runtime_sec)
    out["runtime"] = _format_duration(runtime_sec)
    out["cpu_pct"] = f"{_to_float(live.get('pcpu', '0'), 0.0):.1f}"
    out["state"] = live.get("stat", "")
    return out


def _refresh_jobs(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], bool]:
    changed = False
    now = _now_iso()
    for row in rows:
        pid = _to_int(row.get("pid", "0"), 0)
        if pid <= 0:
            continue
        running = row.get("status", "") == "running"
        alive = _process_alive(pid)
        if alive and running:
            rss_kb = _get_rss_kb_from_status(pid)
            old_last = _to_int(row.get("rss_kb_last", "0"), 0)
            old_peak = _to_int(row.get("rss_kb_peak", "0"), 0)
            old_min = _to_int(row.get("rss_kb_min", "0"), 0)
            old_sum = _to_int(row.get("rss_kb_sum", "0"), 0)
            old_samples = _to_int(row.get("rss_samples", "0"), 0)
            if old_samples <= 0:
                seed = old_last if old_last > 0 else rss_kb
                old_samples = 1 if seed >= 0 else 0
                old_sum = max(seed, 0)
                if old_min <= 0:
                    old_min = max(seed, 0)
            new_peak = max(old_peak, rss_kb)
            new_min = min(old_min, rss_kb) if old_min > 0 else rss_kb
            new_sum = old_sum + max(rss_kb, 0)
            new_samples = old_samples + 1
            if (
                rss_kb != old_last
                or new_peak != old_peak
                or new_min != old_min
                or new_sum != old_sum
                or new_samples != old_samples
            ):
                row["rss_kb_last"] = str(rss_kb)
                row["rss_kb_min"] = str(new_min)
                row["rss_kb_peak"] = str(new_peak)
                row["rss_kb_sum"] = str(new_sum)
                row["rss_samples"] = str(new_samples)
                changed = True
            continue
        if running and not alive:
            exit_code = _read_exit_code(row.get("job_id", ""))
            if exit_code == "":
                row["status"] = "lost"
            elif _to_int(exit_code, 1) == 0:
                row["status"] = "exited"
            else:
                row["status"] = "failed"
            row["exit_code"] = exit_code
            row["end_time"] = now
            row["runtime_sec"] = str(_runtime_seconds(row, {}))
            changed = True
    return rows, changed


def _filter_rows(rows: list[dict[str, str]], query: str) -> list[dict[str, str]]:
    if not query:
        return rows
    q = query.lower()
    out = []
    for r in rows:
        text = " ".join([r.get("command", ""), r.get("name", ""), r.get("log_path", "")]).lower()
        if q in text:
            out.append(r)
    return out


def _sort_rows(rows: list[dict[str, str]], key: str, reverse: bool) -> list[dict[str, str]]:
    if key == "submit_time":
        return sorted(rows, key=lambda r: r.get("submit_time", ""), reverse=reverse)
    if key == "pid":
        return sorted(rows, key=lambda r: _to_int(r.get("pid", "0")), reverse=reverse)
    if key == "job_id":
        return sorted(rows, key=lambda r: _to_int(r.get("job_id", "0")), reverse=reverse)
    if key == "status":
        return sorted(rows, key=lambda r: r.get("status", ""), reverse=reverse)
    if key == "rss_mb":
        return sorted(rows, key=lambda r: _to_float(r.get("rss_mb", "0"), 0.0), reverse=reverse)
    if key == "rss_min_mb":
        return sorted(rows, key=lambda r: _to_float(r.get("rss_min_mb", "0"), 0.0), reverse=reverse)
    if key == "rss_avg_mb":
        return sorted(rows, key=lambda r: _to_float(r.get("rss_avg_mb", "0"), 0.0), reverse=reverse)
    if key == "rss_peak_mb":
        return sorted(rows, key=lambda r: _to_float(r.get("rss_peak_mb", "0"), 0.0), reverse=reverse)
    if key in {"elapsed", "runtime", "runtime_sec"}:
        return sorted(rows, key=lambda r: _to_int(r.get("runtime_sec", "0"), 0), reverse=reverse)
    return rows


def _print_table(rows: list[dict[str, str]], columns: list[str]) -> None:
    if not rows:
        print("(no records)")
        return
    widths = {c: len(c) for c in columns}
    for row in rows:
        for c in columns:
            widths[c] = max(widths[c], len(str(row.get(c, ""))))
    header = "  ".join(c.ljust(widths[c]) for c in columns)
    print(header)
    print("  ".join("-" * widths[c] for c in columns))
    for row in rows:
        print("  ".join(str(row.get(c, "")).ljust(widths[c]) for c in columns))


def _print_rows(rows: list[dict[str, str]], columns: list[str], fmt: str) -> None:
    if fmt == "json":
        print(json.dumps([{c: r.get(c, "") for c in columns} for r in rows], ensure_ascii=False, indent=2))
        return
    if fmt == "tsv":
        print("\t".join(columns))
        for row in rows:
            print("\t".join(str(row.get(c, "")) for c in columns))
        return
    _print_table(rows, columns)


def _build_live(pid: int) -> dict[str, str]:
    ok, etime, pcpu, stat = _ps_row(pid)
    if not ok:
        return {"etime": "", "pcpu": "0", "stat": ""}
    return {"etime": etime, "pcpu": str(pcpu), "stat": stat}


def _find_row(rows: list[dict[str, str]], target: str) -> dict[str, str] | None:
    if target.isdigit():
        for row in reversed(rows):
            if row.get("job_id", "") == target:
                return row
        for row in reversed(rows):
            if row.get("pid", "") == target:
                return row
        return None
    for row in reversed(rows):
        if row.get("name", "") == target:
            return row
    return None


def _parse_env(items: list[str]) -> dict[str, str]:
    extra = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"invalid --env value: {item!r}, expected KEY=VAL")
        k, v = item.split("=", 1)
        if not k:
            raise ValueError(f"invalid --env key in {item!r}")
        extra[k] = v
    return extra


def cmd_submit(args) -> None:
    _ensure_dirs()
    rows = _load_jobs()
    job_id = str(_next_job_id(rows))
    cwd = str(Path(args.cwd).expanduser().resolve())
    log_path = args.log
    if not log_path:
        log_path = str((_default_log_dir() / f"{job_id}.log").resolve())
    else:
        log_path = str(Path(log_path).expanduser().resolve())
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.update(_parse_env(args.env))

    mode = "a" if args.append else "w"
    state_path = _state_file(job_id).resolve()
    wrapped = (
        f"{args.command}\n"
        f"__jsrc_ec=$?\n"
        f'printf "%s\\n" "$__jsrc_ec" > {shlex.quote(str(state_path))}\n'
        'exit "$__jsrc_ec"\n'
    )
    with open(log_path, mode, encoding="utf-8") as logfh:
        proc = subprocess.Popen(
            ["nohup", args.shell, "-lc", wrapped],
            stdin=subprocess.DEVNULL,
            stdout=logfh,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            env=env,
            start_new_session=True,
            text=True,
        )

    rss_kb = _get_rss_kb_from_status(proc.pid)
    now = _now_iso()
    row = {
        "job_id": job_id,
        "name": args.name,
        "submit_time": now,
        "start_time": now,
        "end_time": "",
        "status": "running",
        "pid": str(proc.pid),
        "exit_code": "",
        "cwd": cwd,
        "log_path": log_path,
        "rss_kb_last": str(rss_kb),
        "rss_kb_min": str(rss_kb),
        "rss_kb_peak": str(rss_kb),
        "rss_kb_sum": str(max(rss_kb, 0)),
        "rss_samples": "1",
        "runtime_sec": "0",
        "command": args.command,
    }
    rows.append(row)
    _write_jobs(rows, keep=1000)
    print(f"job_id\t{job_id}")
    print(f"pid\t{proc.pid}")
    print(f"log\t{log_path}")
    print("status\trunning")


def _collect_render_rows(args, refresh: bool) -> list[dict[str, str]]:
    rows = _load_jobs()
    changed = False
    if refresh:
        rows, changed = _refresh_jobs(rows)
    if changed:
        _write_jobs(rows, keep=1000)
    rows = _filter_rows(rows, args.query)
    rendered = []
    for row in rows:
        live = _build_live(_to_int(row.get("pid", "0"), 0)) if row.get("status", "") == "running" else {}
        view = _to_row_view(row, live)
        view["_etime"] = live.get("etime", "")
        rendered.append(view)
    rendered = _sort_rows(rendered, args.sort, args.reverse)
    if not args.all and args.limit > 0:
        rendered = rendered[-args.limit :]
    return rendered


def cmd_ls(args) -> None:
    columns = [c.strip() for c in args.cols.split(",") if c.strip()]
    if not columns:
        columns = ["job_id", "status", "pid", "runtime", "rss_mb", "rss_min_mb", "rss_avg_mb", "rss_peak_mb", "command"]

    if args.watch:
        try:
            while True:
                rows = _collect_render_rows(args, refresh=True)
                sys.stdout.write("\033[2J\033[H")
                print(f"# jsrc job ls --watch  interval={args.interval}s  time={_now_iso()}")
                _print_rows(rows, columns, args.format)
                sys.stdout.flush()
                time.sleep(max(args.interval, 0.2))
        except KeyboardInterrupt:
            return
    rows = _collect_render_rows(args, refresh=True)
    _print_rows(rows, columns, args.format)


def cmd_show(args) -> None:
    rows = _load_jobs()
    rows, changed = _refresh_jobs(rows)
    if changed:
        _write_jobs(rows, keep=1000)
    row = _find_row(rows, str(args.target))
    if row is None:
        raise SystemExit(f"job not found: {args.target}")
    live = _build_live(_to_int(row.get("pid", "0"), 0)) if row.get("status", "") == "running" else {}
    view = _to_row_view(row, live)
    columns = [c.strip() for c in args.cols.split(",") if c.strip()] if args.cols else list(view.keys())
    _print_rows([view], columns, args.format)


def _tail_lines(path: Path, n: int) -> list[str]:
    if n <= 0:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    return [x.rstrip("\n") for x in lines[-n:]]


def cmd_logs(args) -> None:
    rows = _load_jobs()
    row = _find_row(rows, str(args.target))
    if row is None:
        raise SystemExit(f"job not found: {args.target}")
    path = Path(row.get("log_path", "")).expanduser()
    if not path.exists():
        raise SystemExit(f"log file not found: {path}")
    if args.follow:
        subprocess.run(["tail", "-n", str(args.lines), "-f", str(path)], check=False)
        return
    for line in _tail_lines(path, args.lines):
        print(line)


def cmd_kill(args) -> None:
    rows = _load_jobs()
    row = _find_row(rows, str(args.target))
    if row is None:
        raise SystemExit(f"job not found: {args.target}")
    pid = _to_int(row.get("pid", "0"), 0)
    if pid <= 0:
        raise SystemExit("invalid pid")
    sig = {"TERM": signal.SIGTERM, "KILL": signal.SIGKILL, "INT": signal.SIGINT}[args.signal]
    try:
        if args.group:
            pgid = os.getpgid(pid)
            os.killpg(pgid, sig)
        else:
            os.kill(pid, sig)
    except ProcessLookupError:
        pass
    row["status"] = "killed"
    row["end_time"] = _now_iso()
    row["runtime_sec"] = str(_runtime_seconds(row, {}))
    _write_jobs(rows, keep=1000)
    print(f"killed\t{pid}")
    print(f"signal\t{args.signal}")


def cmd_history(args) -> None:
    rows = _load_jobs()
    rows = _filter_rows(rows, args.query)
    if args.limit > 0:
        rows = rows[-args.limit :]
    rendered = []
    for row in rows:
        view = _to_row_view(row, {})
        rendered.append(view)
    cols = [
        "job_id",
        "status",
        "pid",
        "submit_time",
        "end_time",
        "runtime",
        "runtime_sec",
        "rss_mb",
        "rss_min_mb",
        "rss_avg_mb",
        "rss_peak_mb",
        "log_path",
        "command",
    ]
    _print_rows(rendered, cols, args.format)


def cmd_gc(args) -> None:
    rows = _load_jobs()
    if args.prune_missing_log:
        for row in rows:
            log_path = row.get("log_path", "")
            if log_path and not Path(log_path).expanduser().exists() and row.get("status", "") == "running":
                row["status"] = "lost"
                row["end_time"] = _now_iso()
                row["runtime_sec"] = str(_runtime_seconds(row, {}))
    _write_jobs(rows, keep=max(1, args.keep_history))
    removed = 0
    if args.remove_dead_state:
        active = {r.get("job_id", "") for r in rows}
        for item in _state_dir().glob("*.exit"):
            jid = item.stem
            if jid not in active:
                item.unlink(missing_ok=True)
                removed += 1
    print(f"kept_history\t{max(1, args.keep_history)}")
    print(f"state_files_removed\t{removed}")
