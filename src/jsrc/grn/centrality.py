from __future__ import annotations

from argparse import Namespace
from collections import defaultdict
from typing import Any


def cmd(args: Namespace) -> None:
    out_degree: dict[str, float] = defaultdict(float)
    in_degree: dict[str, float] = defaultdict(float)
    nodes = set()
    edge_count = 0

    with open(args.input, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(args.sep) if args.sep else line.split()
            if len(parts) < 2:
                continue
            src, dst = parts[0], parts[1]
            w = float(parts[2]) if len(parts) >= 3 else 1.0
            out_degree[src] += w
            in_degree[dst] += w
            nodes.add(src)
            nodes.add(dst)
            edge_count += 1

    ranked = []
    for n in nodes:
        inn = in_degree.get(n, 0.0)
        outn = out_degree.get(n, 0.0)
        ranked.append((n, inn, outn, inn + outn))
    ranked.sort(key=lambda x: x[3], reverse=True)

    print(f"nodes\t{len(nodes):,}")
    print(f"edges\t{edge_count:,}")
    print("node\tin_degree\tout_degree\ttotal_degree")
    for node, inn, outn, total in ranked[: args.top]:
        print(f"{node}\t{inn:.4f}\t{outn:.4f}\t{total:.4f}")


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("centrality", help="Compute GRN node centrality summary")
    p.add_argument(
        "-i", "--input", required=True, help="Edge table (source target [weight])"
    )
    p.add_argument(
        "--sep", default=None, help="Column separator (default: auto whitespace/tab)"
    )
    p.add_argument("--top", type=int, default=20, help="Top N nodes to print")
    p.set_defaults(func=cmd)
