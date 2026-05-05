from typing import Any

from jsrc.job import gc, history, kill, logs, ls, show, submit


def register_subparser(subparsers: Any) -> None:
    job_parser = subparsers.add_parser("job", help="Track and manage background jobs")
    job_sub = job_parser.add_subparsers(dest="job_cmd")
    job_parser.set_defaults(_group_parser=job_parser)

    submit.register(job_sub)
    ls.register(job_sub)
    show.register(job_sub)
    logs.register(job_sub)
    kill.register(job_sub)
    history.register(job_sub)
    gc.register(job_sub)
