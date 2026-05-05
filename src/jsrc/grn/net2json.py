import csv
import logging
import zipfile
from argparse import Namespace
from pathlib import Path
from typing import Any

from jsrc.grn.anno2json import annotation_to_json

from jsrc.grn.core import write_json

from jsrc.grn.viewer import sync_viewer_assets

logger = logging.getLogger(__name__)

def network_to_json(input_path: str, output_path: str) -> tuple[list[dict[str, Any]], int]:
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
    logger.info("Network JSON written: %s", output_path)
    logger.info("Genes: %d | Edges: %d", len(nodes), len(links))
    return links, len(nodes)


def _infer_viewer_dir(output_json: str) -> Path:
    out = Path(output_json).expanduser().resolve()
    if out.parent.name == "json":
        return out.parent.parent
    return out.parent


def _zip_viewer(viewer_dir: Path, zip_output: str) -> None:
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
    logger.info("Viewer ZIP written: %s", zip_path)


def cmd(args: Namespace) -> None:
    links, _ = network_to_json(args.input, args.output)
    need_viewer = bool(args.zip_output or args.viewer_dir or args.annotation_input)
    if not need_viewer:
        return

    view_mode = "expand" if args.some else "auto"
    viewer_dir = (
        Path(args.viewer_dir).expanduser().resolve()
        if args.viewer_dir
        else _infer_viewer_dir(args.output)
    )
    sync_viewer_assets(
        str(viewer_dir),
        init_empty_json=False,
        view_mode=view_mode,
        full_view_threshold=args.threshold,
        max_display_nodes=args.max_nodes,
    )
    write_json(str(viewer_dir / "json" / "grn.json"), links)
    if args.annotation_input:
        annotation_to_json(
            args.annotation_input, str(viewer_dir / "json" / "annotation.json")
        )
    elif not (viewer_dir / "json" / "annotation.json").exists():
        write_json(str(viewer_dir / "json" / "annotation.json"), {})
    logger.info("Viewer assets written: %s", viewer_dir)
    if args.zip_output:
        _zip_viewer(viewer_dir, args.zip_output)


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("net2json", help="Convert GRN edge table to grn.json")
    p.add_argument("-i", "--input", required=True, help="Input file")
    p.add_argument("-o", dest="output", required=True, help="Output JSON")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Mode all: auto full-view when gene count <= threshold",
    )
    mode.add_argument(
        "-s",
        "--some",
        action="store_true",
        help="Mode some: manual click-to-expand only",
    )
    p.set_defaults(all=True, some=False)
    p.add_argument(
        "-t",
        "--threshold",
        type=int,
        default=300,
        help="In all mode, auto full-view when gene count <= this value",
    )
    p.add_argument(
        "-d",
        "--viewer-dir",
        help="Optional viewer output directory. If omitted, infer from -o (e.g. viewer/json/grn.json -> viewer)",
    )
    p.add_argument(
        "-n",
        "--annotation-input",
        help="Optional annotation TSV to generate json/annotation.json for package",
    )
    p.add_argument(
        "-z",
        "--zip-output",
        help="Optional ZIP output path containing html/css/js/json viewer package",
    )
    p.add_argument(
        "--max-nodes",
        type=int,
        default=0,
        help="Max nodes to display in full view mode (0 = all)",
    )
    p.set_defaults(func=cmd)
