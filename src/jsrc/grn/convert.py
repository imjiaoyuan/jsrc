import csv
import zipfile
from pathlib import Path

from jsrc.grn.core import write_json
from jsrc.grn.viewer import sync_viewer_assets


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
    nodes = set()
    for item in links:
        nodes.add(item["source"])
        nodes.add(item["target"])
    print(f"Network JSON written: {output_path}")
    print(f"Genes: {len(nodes)} | Edges: {len(links)}")
    return links, len(nodes)


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
    return anno


def _infer_viewer_dir(output_json: str) -> Path:
    out = Path(output_json).expanduser().resolve()
    if out.parent.name == "json":
        return out.parent.parent
    return out.parent


def _zip_viewer(viewer_dir: Path, zip_output: str):
    zip_path = Path(zip_output).expanduser().resolve()
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    wanted = [
        viewer_dir / "index.html",
        viewer_dir / "css" / "style.css",
        viewer_dir / "js" / "script.js",
        viewer_dir / "json" / "grn.json",
        viewer_dir / "json" / "annotation.json",
    ]
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in wanted:
            if f.exists():
                zf.write(f, arcname=str(f.relative_to(viewer_dir)))
    print(f"Viewer ZIP written: {zip_path}")


def cmd_network(args):
    links, _ = _network_to_json(args.input, args.output)
    need_viewer = bool(args.zip_output or args.viewer_dir or args.annotation_input)
    if not need_viewer:
        return

    view_mode = "expand" if args.some else "auto"
    viewer_dir = Path(args.viewer_dir).expanduser().resolve() if args.viewer_dir else _infer_viewer_dir(args.output)
    sync_viewer_assets(
        str(viewer_dir),
        init_empty_json=False,
        view_mode=view_mode,
        full_view_threshold=args.threshold,
    )
    write_json(str(viewer_dir / "json" / "grn.json"), links)
    if args.annotation_input:
        _annotation_to_json(args.annotation_input, str(viewer_dir / "json" / "annotation.json"))
    elif not (viewer_dir / "json" / "annotation.json").exists():
        write_json(str(viewer_dir / "json" / "annotation.json"), {})
    print(f"Viewer assets written: {viewer_dir}")
    if args.zip_output:
        _zip_viewer(viewer_dir, args.zip_output)


def cmd_annotation(args):
    _annotation_to_json(args.input, args.output)


def cmd(args):
    if args.type == "network":
        cmd_network(args)
    else:
        cmd_annotation(args)
