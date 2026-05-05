import os
import pathlib

from jsrc.grn.core import ensure_dir, write_json, write_text

_SCRIPT_TEMPLATE = (
    pathlib.Path(__file__).parent / "sources" / "script.js"
).read_text(encoding="utf-8")

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GRN</title>
    <link rel="stylesheet" href="css/style.css">
    <script src="//unpkg.com/d3"></script>
    <script src="//unpkg.com/force-graph"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
</head>
<body>
    <div id="controls">
        <div class="row">
            <button onclick="goBack()" id="btnBack" disabled>&lt;</button>
            <button onclick="goForward()" id="btnFwd" disabled>&gt;</button>
            <button onclick="exportImage('pdf')" class="btn-export">PDF</button>
            <button onclick="resetView()" class="btn-reset">Reset</button>
        </div>

        <div class="row search-row">
            <input type="text" id="geneInput" placeholder="Enter Gene ID">
            <button onclick="startNewSearch()" class="btn-search">Search</button>
        </div>

        <div id="legend">Line thickness indicates weight</div>
        <div id="nodeCount">Nodes: 0</div>
        <div id="neighborList"></div>
    </div>

    <div id="watermark">GRN</div>
    <div id="emptyState">No Nodes</div>
    <div id="graph"></div>

    <script src="js/script.js"></script>
</body>
</html>
"""

STYLE_CSS = """body {
    margin: 0;
    background: #ffffff;
    color: #000;
    font-family: sans-serif;
    overflow: hidden;
    width: 100vw;
    height: 100vh;
}

#graph {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
}

#controls {
    position: absolute;
    top: 20px;
    left: 20px;
    z-index: 999;
    background: rgba(255, 255, 255, 0.96);
    padding: 12px;
    border-radius: 6px;
    border: 1px solid #ccc;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 90vh;
    width: 350px;
}

.row {
    display: flex;
    gap: 6px;
    align-items: center;
}

.search-row {
    display: flex;
    gap: 4px;
}

input {
    padding: 8px 10px;
    border-radius: 4px;
    border: 1px solid #ccc;
    background: #fff;
    color: #000;
    flex: 1;
    outline: none;
    font-size: 15px;
    min-width: 0;
}

button {
    padding: 6px 10px;
    cursor: pointer;
    background: #eee;
    color: #333;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-weight: bold;
    font-size: 13px;
    flex-grow: 1;
}

.btn-search {
    flex: 0 0 65px;
    background: #e9ecef;
}

button:hover {
    background: #ddd;
}

button:disabled {
    color: #aaa;
    cursor: default;
}

.btn-export {
    background: #007bff;
    color: white;
    border: none;
}

.btn-export:hover {
    background: #0056b3;
}

.btn-reset {
    background: #dc3545;
    color: white;
    border: none;
}

.btn-reset:hover {
    background: #bb2d3b;
}

#legend {
    font-size: 13px;
    color: #666;
    font-style: italic;
    border-bottom: 1px solid #eee;
    padding-bottom: 4px;
}

#nodeCount {
    font-weight: bold;
    color: #333;
    margin-top: 4px;
    border-bottom: 1px solid #eee;
    padding-bottom: 6px;
    font-size: 14px;
}

#neighborList {
    overflow-y: auto;
    flex: 1;
    margin-top: 4px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 0;
    background: #fafafa;
}

.panel-header {
    padding: 10px 10px;
    background: #fff;
    border-bottom: 1px solid #ccc;
    margin-bottom: 0;
}

.panel-title {
    font-weight: bold;
    font-size: 18px;
    color: #007bff;
    margin-bottom: 6px;
}

.panel-stats {
    font-size: 13px;
    font-weight: bold;
    color: #333;
    margin-bottom: 6px;
}

.panel-desc {
    font-size: 14px;
    color: #333;
    margin-bottom: 8px;
    line-height: 1.4;
}

.btn-download-list {
    width: 100%;
    background: #20c997;
    color: white;
    border: none;
    font-size: 13px;
    padding: 8px;
    border-radius: 4px;
    margin-top: 6px;
    cursor: pointer;
}

.btn-download-list:hover {
    background: #1aa179;
}

.list-item {
    border-bottom: 1px solid #eee;
    display: flex;
    flex-direction: column;
    background: #fff;
    transition: background 0.1s;
}

.item-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 8px;
    cursor: pointer;
}

.item-row:hover {
    background: #f0f4f8;
}

.gene-id-text {
    font-weight: bold;
    font-size: 15px;
    color: #333;
}

.item-val {
    color: #888;
    font-size: 12px;
    margin-left: 8px;
}

.list-item.highlighted .item-row {
    background: #fff3cd;
    border-left: 4px solid #ffc107;
}

.list-item.highlighted .gene-id-text {
    color: #0056b3;
}

.item-details {
    display: none;
    padding: 8px;
    background: #f8f9fa;
    border-top: 1px dashed #e9ecef;
    font-size: 13px;
    color: #333;
    line-height: 1.5;
}

.list-item.expanded .item-details {
    display: block;
}

.detail-line {
    margin-bottom: 3px;
}

.detail-label {
    font-weight: bold;
    color: #555;
    display: inline-block;
    min-width: 45px;
}

#watermark {
    position: absolute;
    top: 20px;
    right: 30px;
    z-index: 998;
    font-size: 48px;
    font-weight: bold;
    color: rgba(0, 0, 0, 0.15);
    pointer-events: none;
    user-select: none;
}

#emptyState {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 24px;
    color: #ccc;
    z-index: 0;
    display: block;
}

::-webkit-scrollbar {
    width: 5px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 3px;
}
"""


def sync_viewer_assets(
    base: str,
    init_empty_json: bool,
    view_mode: str = "auto",
    full_view_threshold: int = 300,
    max_display_nodes: int = 0,
) -> None:
    mode = view_mode if view_mode in {"expand", "full", "auto"} else "auto"
    threshold = max(0, int(full_view_threshold))
    max_nodes = max(0, int(max_display_nodes))
    ensure_dir(base)
    ensure_dir(os.path.join(base, "css"))
    ensure_dir(os.path.join(base, "js"))
    ensure_dir(os.path.join(base, "json"))
    write_text(os.path.join(base, "index.html"), INDEX_HTML)
    write_text(os.path.join(base, "css/style.css"), STYLE_CSS)
    script = (
        _SCRIPT_TEMPLATE.replace("__JSRC_VIEW_MODE__", mode)
        .replace("__JSRC_FULL_THRESHOLD__", str(threshold))
        .replace("__JSRC_MAX_DISPLAY_NODES__", str(max_nodes))
    )
    write_text(os.path.join(base, "js/script.js"), script)
    if init_empty_json:
        write_json(os.path.join(base, "json/grn.json"), [])
        write_json(os.path.join(base, "json/annotation.json"), {})
        return
    anno_path = os.path.join(base, "json/annotation.json")
    if not os.path.exists(anno_path):
        write_json(anno_path, {})
