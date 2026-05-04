import re


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

