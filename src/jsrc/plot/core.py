import re


from matplotlib.patches import Rectangle


def setup_matplotlib():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def parse_gff_attributes(attr_string: str) -> dict[str, str]:
    attrs = {}
    for item in attr_string.strip().strip(";").split(";"):
        if "=" in item:
            key, value = item.strip().split("=", 1)
            attrs[key] = value.strip('"')
        elif " " in item:
            parts = item.strip().split(None, 1)
            if len(parts) == 2:
                attrs[parts[0]] = parts[1].strip('"')
    return attrs


def natural_sort_key(value: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", value)]


def plot_gene_track(
    ax,
    coords: dict[str, list[tuple[int, int]]],
    gene_ids_sorted: list[str],
    *,
    rect_height: float = 0.3,
    color: str = "steelblue",
    title: str = "Gene Structure",
    xlabel: str = "Genomic Position",
):
    for i, gid in enumerate(gene_ids_sorted):
        y = len(gene_ids_sorted) - i - 1
        if gid not in coords or not coords[gid]:
            continue
        feature_list = sorted(coords[gid])
        gstart = min(c[0] for c in feature_list)
        gend = max(c[1] for c in feature_list)
        ax.plot([gstart, gend], [y, y], "k-", linewidth=1)
        for start, end in feature_list:
            ax.add_patch(
                Rectangle(
                    (start, y - rect_height / 2),
                    end - start,
                    rect_height,
                    facecolor=color,
                    edgecolor="black",
                )
            )
    ax.set_yticks(range(len(gene_ids_sorted)))
    ax.set_yticklabels(gene_ids_sorted[::-1])
    ax.set_xlabel(xlabel)
    ax.set_title(title)


def get_gene_structure(gff_file: str, gene_ids: list[str], feature_types: list[str]) -> dict[str, list[tuple[int, int]]]:
    target_set = set(gene_ids)
    valid_mrna = {}
    coords = {gid: [] for gid in gene_ids}
    with open(gff_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) < 9:
                continue
            ftype = parts[2]
            attr = parse_gff_attributes(parts[8])
            if ftype == "mRNA":
                pid = attr.get("Parent")
                mid = attr.get("ID")
                if pid in target_set and mid:
                    valid_mrna[mid] = pid
            elif ftype in feature_types:
                pid = attr.get("Parent")
                if not pid:
                    continue
                if pid in valid_mrna:
                    coords[valid_mrna[pid]].append((int(parts[3]), int(parts[4])))
                elif pid in target_set:
                    coords[pid].append((int(parts[3]), int(parts[4])))
    return coords

