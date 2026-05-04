import importlib


def _dispatch(module_name: str, func_name: str):
    def _runner(args):
        module = importlib.import_module(module_name)
        getattr(module, func_name)(args)

    return _runner


def register_subparser(subparsers):
    job_parser = subparsers.add_parser("job", help="Track and manage background jobs")
    job_sub = job_parser.add_subparsers(dest="job_cmd")
    job_parser.set_defaults(_group_parser=job_parser)

    p = job_sub.add_parser("submit", help='Submit a job: jsrc job submit "cmd" "log"')
    p.add_argument("command", help='Command to run, wrapped by nohup (e.g. "Rscript 02.harmony2.R")')
    p.add_argument("log", nargs="?", help="Log file path (optional)")
    p.add_argument("-N", "--name", default="", help="Optional job name")
    p.add_argument("-C", "--cwd", default=".", help="Working directory")
    p.add_argument("-S", "--shell", default="bash", help="Shell binary used with -lc")
    p.add_argument("-A", "--append", action="store_true", help="Append to log file instead of overwrite")
    p.add_argument("-E", "--env", action="append", default=[], help="Extra env KEY=VAL (repeatable)")
    p.set_defaults(func=_dispatch("jsrc.job.commands", "cmd_submit"))

    p = job_sub.add_parser("ls", help="List tracked jobs")
    p.add_argument("-w", "--watch", action="store_true", help="Refresh continuously")
    p.add_argument("-n", "--interval", type=float, default=2.0, help="Refresh interval seconds")
    p.add_argument(
        "-c",
        "--cols",
        default="job_id,status,pid,runtime,rss_mb,rss_min_mb,rss_avg_mb,rss_peak_mb,submit_time,command",
        help="Columns to print, comma-separated",
    )
    p.add_argument("-f", "--format", choices=["table", "tsv", "json"], default="table", help="Output format")
    p.add_argument(
        "-s",
        "--sort",
        choices=[
            "submit_time",
            "elapsed",
            "runtime",
            "runtime_sec",
            "rss_mb",
            "rss_min_mb",
            "rss_avg_mb",
            "rss_peak_mb",
            "pid",
            "job_id",
            "status",
        ],
        default="submit_time",
        help="Sort field",
    )
    p.add_argument("-r", "--reverse", action="store_true", help="Reverse sort order")
    p.add_argument("-a", "--all", action="store_true", help="Show all records")
    p.add_argument("-l", "--limit", type=int, default=20, help="Max rows when --all is not set")
    p.add_argument("-q", "--query", default="", help="Filter by command/name/log path")
    p.set_defaults(func=_dispatch("jsrc.job.commands", "cmd_ls"))

    p = job_sub.add_parser("show", help="Show details of a job by job_id or pid")
    p.add_argument("target", help="Job ID or PID")
    p.add_argument("-f", "--format", choices=["table", "json"], default="table", help="Output format")
    p.add_argument("-c", "--cols", default="", help="Columns to print, comma-separated")
    p.set_defaults(func=_dispatch("jsrc.job.commands", "cmd_show"))

    p = job_sub.add_parser("logs", help="Show job log by job_id or pid")
    p.add_argument("target", help="Job ID or PID")
    p.add_argument("-F", "--follow", action="store_true", help="Follow log output")
    p.add_argument("-n", "--lines", type=int, default=100, help="Tail line count")
    p.set_defaults(func=_dispatch("jsrc.job.commands", "cmd_logs"))

    p = job_sub.add_parser("kill", help="Stop a running job by job_id or pid")
    p.add_argument("target", help="Job ID or PID")
    p.add_argument("-s", "--signal", default="TERM", choices=["TERM", "KILL", "INT"], help="Signal to send")
    p.add_argument("-g", "--group", action="store_true", help="Kill process group instead of single PID")
    p.set_defaults(func=_dispatch("jsrc.job.commands", "cmd_kill"))

    p = job_sub.add_parser("history", help="Print job history")
    p.add_argument("-l", "--limit", type=int, default=50, help="Limit rows")
    p.add_argument("-f", "--format", choices=["table", "tsv", "json"], default="table", help="Output format")
    p.add_argument("-q", "--query", default="", help="Filter by command/name/log path")
    p.set_defaults(func=_dispatch("jsrc.job.commands", "cmd_history"))

    p = job_sub.add_parser("gc", help="Trim history/log metadata")
    p.add_argument("-k", "--keep-history", type=int, default=1000, help="Keep last N history records")
    p.add_argument("--prune-missing-log", action="store_true", help="Mark records whose log file no longer exists")
    p.add_argument("--remove-dead-state", action="store_true", help="Remove stale job state files")
    p.set_defaults(func=_dispatch("jsrc.job.commands", "cmd_gc"))
