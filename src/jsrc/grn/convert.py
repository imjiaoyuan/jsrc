import csv

from jsrc.grn.core import write_json


def _network_to_json(input_path: str, output_path: str):
    links = []
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) < 3:
                continue
            source_id = str(row[0]).replace("_", "-")
            target_id = str(row[1]).replace("_", "-")
            try:
                weight = float(row[2])
            except ValueError:
                continue
            links.append({"source": source_id, "target": target_id, "val": weight})
    write_json(output_path, links)
    print(f"Network JSON written: {output_path}")


def _annotation_to_json(input_path: str, output_path: str):
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


def cmd_network(args):
    _network_to_json(args.input, args.output)


def cmd_annotation(args):
    _annotation_to_json(args.input, args.output)


def cmd(args):
    if args.type == "network":
        cmd_network(args)
    else:
        cmd_annotation(args)
