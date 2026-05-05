from typing import Any

from jsrc.gs import build, split, train


def register_subparser(subparsers: Any) -> None:
    gs_parser = subparsers.add_parser(
        "gs", help="Genomic selection dataset and model workflows"
    )
    gs_sub = gs_parser.add_subparsers(dest="gs_cmd")
    gs_parser.set_defaults(_group_parser=gs_parser)

    build.register(gs_sub)
    split.register(gs_sub)
    train.register(gs_sub)
