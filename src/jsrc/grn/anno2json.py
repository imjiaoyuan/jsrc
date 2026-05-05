import csv
from argparse import Namespace
from typing import Any

from jsrc.grn.core import write_json


def annotation_to_json(input_path: str, output_path: str) -> dict[str, dict[str, str]]:
    anno = {}
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if not row:
                continue
            gid = str(row[0]).replace("_", "-")
            ptr = str(row[1]) if len(row) > 1 else ""
            desc = str(row[2]) if len(row) > 2 else ""
            anno[gid] = {"p": ptr, "d": desc}
    write_json(output_path, anno)
    print(f"Annotation JSON written: {output_path}")
    return anno


def cmd(args: Namespace) -> None:
    annotation_to_json(args.input, args.output)


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "anno2json", help="Convert annotation table to annotation.json"
    )
    p.add_argument("-i", "--input", required=True, help="Input file")
    p.add_argument("-o", dest="output", required=True, help="Output JSON")
    p.set_defaults(func=cmd)
