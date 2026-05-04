import csv
from jsrc.common.gff import parse_gff_attributes


def _load_csv_mapping(path: str) -> dict[str, str]:
    mapping = {}
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) >= 2:
                mapping[row[0].strip()] = row[1].strip()
    return mapping


def _load_gff_mapping(gff_path: str, parent_field: str) -> dict[str, str]:
    mapping = {}
    with open(gff_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) < 9 or parts[2] != "mRNA":
                continue
            attr = parse_gff_attributes(parts[8])
            tid = attr.get("ID")
            pid = attr.get(parent_field)
            if tid and pid:
                mapping[tid] = pid
    return mapping


def _apply_mapping(fasta_path: str, output_path: str, mapping: dict[str, str]):
    with open(fasta_path, "r", encoding="utf-8") as fin, open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            if line.startswith(">"):
                old_id = line[1:].split()[0]
                fout.write(f">{mapping[old_id]}\n" if old_id in mapping else line)
            else:
                fout.write(line)


def cmd(args):
    mode = args.mode
    if mode == "csv":
        if not args.map:
            raise SystemExit("Error: mode=csv requires -map")
        mapping = _load_csv_mapping(args.map)
    else:
        if not args.gff or not args.parent:
            raise SystemExit("Error: mode=gff requires -gff and -parent")
        mapping = _load_gff_mapping(args.gff, args.parent)

    _apply_mapping(args.fa, args.o, mapping)
    print(f"Renamed {len(mapping)} IDs to {args.o}")
