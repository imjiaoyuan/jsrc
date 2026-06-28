from __future__ import annotations

import csv
import logging
from argparse import Namespace
from typing import Any

from jsrc.core import open_text
from jsrc.grn.core import write_json

logger = logging.getLogger(__name__)


def network_to_json(
    input_path: str, output_path: str
) -> tuple[list[dict[str, Any]], int]:
    links = []
    with open_text(input_path) as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) < 3:
                continue
            source_id = str(row[0])
            target_id = str(row[1])
            try:
                weight = float(row[2])
            except ValueError:
                continue
            links.append({"source": source_id, "target": target_id, "val": weight})
    write_json(output_path, links)
    nodes = set()
    for item in links:
        nodes.add(item["source"])
        nodes.add(item["target"])
    logger.info("Network JSON written: %s", output_path)
    logger.info("Genes: %d | Edges: %d", len(nodes), len(links))
    return links, len(nodes)


def cmd(args: Namespace) -> None:
    network_to_json(args.input, args.output)


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("net2json", help="Convert GRN edge table to grn.json")
    p.add_argument("-i", "--input", required=True, help="Input edge table (TSV)")
    p.add_argument("-o", dest="output", required=True, help="Output JSON path")
    p.set_defaults(func=cmd)
