from collections import defaultdict


def cmd(args):
    out_degree = defaultdict(float)
    in_degree = defaultdict(float)
    nodes = set()
    edge_count = 0

    with open(args.input, "r", encoding="utf-8") as f:
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
