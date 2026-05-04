import os

from jsrc.grn.core import ensure_dir, write_json, write_text

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

SCRIPT_JS = """let allLinks = [];
let annotations = {};
let isLoaded = false;
let historyStack = [];
let historyIndex = -1;
let expandColorIndex = 0;
let currentCenterId = null;
let highlightedNodeId = null;
let expandedSet = new Set();
let currentNeighbors = [];
let _fullViewZoomed = false;
const VIEW_MODE = "__JSRC_VIEW_MODE__";
const FULL_VIEW_THRESHOLD = __JSRC_FULL_THRESHOLD__;
const MAX_DISPLAY_NODES = __JSRC_MAX_DISPLAY_NODES__;

const expandPalette = [
    '0, 123, 255', '255, 71, 87', '46, 213, 115',
    '255, 165, 2', '162, 155, 254', '255, 107, 129',
    '87, 75, 144', '61, 193, 211', '24, 220, 255',
    '255, 159, 26', '50, 255, 126', '126, 255, 245'
];

const Graph = ForceGraph()
    (document.getElementById('graph'))
    .backgroundColor('#ffffff')
    .nodeId('id')
    .linkWidth(link => link.val * 1.5)
    .linkColor(link => `rgba(${link.baseColor || '0, 123, 255'}, 0.5)`)
    .linkDirectionalArrowLength(12)
    .linkDirectionalArrowRelPos(0.5)
    .linkDirectionalArrowColor(() => '#333333')
    .d3AlphaDecay(0.08)
    .d3VelocityDecay(0.6)
    .d3Force('charge', d3.forceManyBody().strength(-500))
    .d3Force('link', d3.forceLink().distance(120).strength(0.7))
    .nodeCanvasObject((node, ctx, globalScale) => {
        const label = node.id;
        const fontSize = 14 / globalScale;
        const isHighlighted = node.id === highlightedNodeId;
        const radius = isHighlighted ? 22 : 15;

        ctx.beginPath();
        ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
        ctx.fillStyle = isHighlighted ? '#ffff00' : (node.color || '#007bff');
        ctx.fill();

        ctx.strokeStyle = isHighlighted ? '#ff4757' : '#ffffff';
        ctx.lineWidth = (isHighlighted ? 4 : 2) / globalScale;
        ctx.stroke();

        ctx.font = `bold ${fontSize}px Sans-Serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillStyle = '#1e272e';
        ctx.fillText(label, node.x, node.y + radius + 4);
    })
    .onNodeDragEnd(node => {
        node.fx = node.x;
        node.fy = node.y;
    })
    .onNodeClick(node => {
        expandNode(node.id);
    })
    .onEngineStop(() => {
        if (!_fullViewZoomed && Graph.graphData().nodes.length > 0) {
            _fullViewZoomed = true;
            Graph.zoomToFit(600, 200);
        }
    });

Promise.all([
    fetch('json/grn.json').then(res => {
        if (!res.ok) throw new Error(`Failed to load grn.json: ${res.status}`);
        return res.json();
    }),
    fetch('json/annotation.json')
        .then(res => res.ok ? res.json() : {})
        .catch(() => ({}))
]).then(([linkData, annoData]) => {
    allLinks = linkData;
    annotations = annoData;
    isLoaded = true;
    document.getElementById('nodeCount').innerText = `Data Ready`;

    const uniqueGeneCount = countUniqueGenes();
    const useFullView = (
        VIEW_MODE === 'full' ||
        (VIEW_MODE === 'auto' && FULL_VIEW_THRESHOLD > 0 && uniqueGeneCount <= FULL_VIEW_THRESHOLD)
    );
    if (useFullView) {
        startFullView();
        return;
    }

    const allGeneIds = new Set();
    allLinks.forEach(l => { allGeneIds.add(l.source); allGeneIds.add(l.target); });
    const geneArray = Array.from(allGeneIds);
    if (geneArray.length > 0) {
        const startId = geneArray[Math.floor(Math.random() * geneArray.length)];
        document.getElementById('geneInput').value = startId;
        startNewSearch();
    } else {
        document.getElementById('nodeCount').innerText = "Data Loaded. Enter ID.";
    }
}).catch(err => {
    console.error("Error loading data:", err);
    document.getElementById('nodeCount').innerText = "Load Error";
});

function sanitizeGraphData(graphData) {
    return {
        nodes: graphData.nodes.map(n => ({
            id: n.id,
            color: n.color,
            x: n.x, y: n.y, vx: n.vx, vy: n.vy, fx: n.fx, fy: n.fy
        })),
        links: graphData.links.map(l => ({
            source: l.source.id || l.source,
            target: l.target.id || l.target,
            val: l.val,
            baseColor: l.baseColor
        }))
    };
}

function updateHistory(nodes, links, centerId) {
    if (historyIndex < historyStack.length - 1) {
        historyStack = historyStack.slice(0, historyIndex + 1);
    }
    const snapshot = sanitizeGraphData({ nodes, links });
    historyStack.push({
        nodes: snapshot.nodes,
        links: snapshot.links,
        colorIndex: expandColorIndex,
        centerId: centerId,
        expandedNodes: new Set(expandedSet)
    });
    historyIndex++;
    updateButtons();
}

function renderState(state) {
    expandColorIndex = state.colorIndex;
    currentCenterId = state.centerId;
    expandedSet = new Set(state.expandedNodes || []);
    const cleanState = sanitizeGraphData(state);

    Graph.graphData({ nodes: cleanState.nodes, links: cleanState.links });
    document.getElementById('emptyState').style.display = cleanState.nodes.length > 0 ? 'none' : 'block';

    updateButtons();
    updateInfoPanel();

    const centerNode = cleanState.nodes.find(n => n.id === currentCenterId);
    if (centerNode && centerNode.x !== undefined) {
        Graph.centerAt(centerNode.x, centerNode.y, 800);
    }
}

function updateButtons() {
    document.getElementById('btnBack').disabled = historyIndex <= 0;
    document.getElementById('btnFwd').disabled = historyIndex >= historyStack.length - 1;
}

function goBack() {
    if (historyIndex > 0) {
        historyIndex--;
        renderState(historyStack[historyIndex]);
    }
}

function goForward() {
    if (historyIndex < historyStack.length - 1) {
        historyIndex++;
        renderState(historyStack[historyIndex]);
    }
}

function resetView() {
    Graph.graphData({ nodes: [], links: [] });
    document.getElementById('geneInput').value = '';
    document.getElementById('neighborList').innerHTML = '';
    document.getElementById('nodeCount').innerText = 'Nodes: 0';
    document.getElementById('emptyState').style.display = 'block';
    historyStack = [];
    historyIndex = -1;
    expandColorIndex = 0;
    currentCenterId = null;
    highlightedNodeId = null;
    expandedSet.clear();
    currentNeighbors = [];
    updateButtons();
}

function handleListClick(id) {
    if (highlightedNodeId === id) {
        highlightedNodeId = null;
        updateInfoPanelState();
    } else {
        highlightNode(id);
    }
}

function updateInfoPanelState() {
    const listItems = document.querySelectorAll('.list-item');
    listItems.forEach(item => {
        if (item.dataset.id === highlightedNodeId) {
            item.classList.add('highlighted');
            item.classList.add('expanded');
            item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            item.classList.remove('highlighted');
            item.classList.remove('expanded');
        }
    });
}

function highlightNode(id) {
    highlightedNodeId = id;
    const nodes = Graph.graphData().nodes;
    const target = nodes.find(n => n.id === id);
    if (target) {
        Graph.centerAt(target.x, target.y, 600);
    }
    updateInfoPanelState();
    Graph.d3ReheatSimulation();
}

function downloadListInfo() {
    if (!currentCenterId) return;

    let content = "GeneID\\tPotriID\\tAnnotation\\tRelation\\tWeight\\n";

    const centerInfo = annotations[currentCenterId] || { p: "", d: "" };
    content += `${currentCenterId}\\t${centerInfo.p}\\t${centerInfo.d.replace(/[\\n\\r]/g, " ")}\\tCenter\\t-\\n`;

    currentNeighbors.forEach(n => {
        const info = annotations[n.id] || { p: "", d: "" };
        content += `${n.id}\\t${info.p}\\t${info.d.replace(/[\\n\\r]/g, " ")}\\tNeighbor\\t${n.val}\\n`;
    });

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${currentCenterId}_neighbors_info.txt`;
    link.style.display = "none";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function updateInfoPanel() {
    const data = Graph.graphData();
    document.getElementById('nodeCount').innerText = `View Nodes: ${data.nodes.length} | Expanded: ${expandedSet.size}`;
    const listContainer = document.getElementById('neighborList');
    listContainer.innerHTML = '';

    if (!currentCenterId) return;

    const allPossibleLinks = allLinks.filter(l => l.source === currentCenterId || l.target === currentCenterId);
    const totalCount = allPossibleLinks.length;

    currentNeighbors = [];
    data.links.forEach(l => {
        const s = l.source.id || l.source;
        const t = l.target.id || l.target;
        if (s === currentCenterId) currentNeighbors.push({ id: t, val: l.val });
        else if (t === currentCenterId) currentNeighbors.push({ id: s, val: l.val });
    });

    currentNeighbors.sort((a, b) => b.val - a.val);
    const info = annotations[currentCenterId] || { p: 'N/A', d: 'No annotation found' };

    const header = document.createElement('div');
    header.className = 'panel-header';
    header.innerHTML = `
        <div class="panel-title">${currentCenterId}</div>
        <div class="panel-desc">
            <b>Ptr:</b> ${info.p || '-'}<br>
            ${info.d || '-'}
        </div>
        <div class="panel-stats">
            Neighbors: ${currentNeighbors.length} / ${totalCount}
        </div>
        <button onclick="downloadListInfo()" class="btn-download-list">Download List Info (.txt)</button>
    `;
    listContainer.appendChild(header);

    currentNeighbors.forEach(n => {
        const nInfo = annotations[n.id] || { p: 'N/A', d: 'No annotation' };

        const div = document.createElement('div');
        div.className = 'list-item';
        div.dataset.id = n.id;
        if (n.id === highlightedNodeId) {
            div.classList.add('highlighted');
            div.classList.add('expanded');
        }

        div.onclick = () => handleListClick(n.id);
        div.ondblclick = () => expandNode(n.id);

        div.innerHTML = `
            <div class="item-row">
                <span class="gene-id-text">${n.id}</span>
                <span class="item-val">w:${n.val}</span>
            </div>
            <div class="item-details" onclick="event.stopPropagation()">
                <div class="detail-line"><span class="detail-label">Potri:</span> ${nInfo.p || '-'}</div>
                <div class="detail-line"><span class="detail-label">Desc:</span> ${nInfo.d || '-'}</div>
            </div>
        `;

        listContainer.appendChild(div);
    });
}

function countUniqueGenes() {
    const set = new Set();
    allLinks.forEach(l => {
        set.add(l.source);
        set.add(l.target);
    });
    return set.size;
}

function startFullView() {
    if (!isLoaded || allLinks.length === 0) {
        document.getElementById('nodeCount').innerText = "No data";
        return;
    }

    const degree = new Map();
    const nodeSet = new Map();
    allLinks.forEach(l => {
        const s = l.source;
        const t = l.target;
        nodeSet.set(s, { id: s, color: '#007bff' });
        nodeSet.set(t, { id: t, color: '#007bff' });
        degree.set(s, (degree.get(s) || 0) + 1);
        degree.set(t, (degree.get(t) || 0) + 1);
    });

    let keepIds = null;
    if (MAX_DISPLAY_NODES > 0 && nodeSet.size > MAX_DISPLAY_NODES) {
        const ranked = Array.from(degree.entries()).sort((a, b) => b[1] - a[1]);
        keepIds = new Set(ranked.slice(0, MAX_DISPLAY_NODES).map(e => e[0]));
        for (const id of nodeSet.keys()) {
            if (!keepIds.has(id)) nodeSet.delete(id);
        }
    }

    let centerId = '';
    degree.forEach((d, id) => {
        if (keepIds && !keepIds.has(id)) return;
        if (!centerId || d > (degree.get(centerId) || -1)) centerId = id;
    });
    if (!centerId) centerId = Array.from(nodeSet.keys())[0];

    currentCenterId = centerId;
    highlightedNodeId = null;
    expandColorIndex = 0;
    expandedSet = new Set(nodeSet.keys());
    const baseRgb = expandPalette[0];

    const links = allLinks.filter(l => {
        if (!keepIds) return true;
        return keepIds.has(l.source) && keepIds.has(l.target);
    }).map(l => ({
        source: l.source, target: l.target, val: l.val, baseColor: baseRgb
    }));
    if (nodeSet.has(centerId)) {
        nodeSet.set(centerId, { ...nodeSet.get(centerId), color: '#ff4757' });
    }
    const nodes = Array.from(nodeSet.values());

    historyStack = [];
    historyIndex = -1;
    _fullViewZoomed = false;
    updateHistory(nodes, links, centerId);
    renderState(historyStack[0]);
    Graph.d3ReheatSimulation();
}

function getTopNeighbors(centerId, limit = 100) {
    const related = allLinks.filter(l => l.source === centerId || l.target === centerId);
    related.sort((a, b) => b.val - a.val);
    return related.slice(0, limit);
}

function startNewSearch() {
    if (!isLoaded) return;
    const id = document.getElementById('geneInput').value.trim();
    if (!id) return;

    const linksRaw = getTopNeighbors(id, 100);
    if (linksRaw.length === 0) {
        alert("No data found for: " + id);
        return;
    }

    expandColorIndex = 0;
    currentCenterId = id;
    highlightedNodeId = null;
    expandedSet.clear();
    const baseRgb = expandPalette[0];

    const links = linksRaw.map(l => ({
        source: l.source, target: l.target, val: l.val, baseColor: baseRgb
    }));

    const nodeSet = new Map();
    nodeSet.set(id, { id: id, color: '#ff4757', fx: 0, fy: 0 });

    links.forEach(l => {
        const n = l.source === id ? l.target : l.source;
        if (!nodeSet.has(n)) nodeSet.set(n, { id: n, color: '#007bff' });
    });

    const nodes = Array.from(nodeSet.values());
    historyStack = [];
    historyIndex = -1;
    updateHistory(nodes, links, id);
    renderState(historyStack[0]);
}

function expandNode(id) {
    const currentData = Graph.graphData();
    const safeCurrent = sanitizeGraphData(currentData);

    if (currentCenterId !== id) {
        updateHistory(safeCurrent.nodes, safeCurrent.links, currentCenterId);
    }

    currentCenterId = id;
    highlightedNodeId = null;
    expandedSet.add(id);

    const existingLinks = new Set(safeCurrent.links.map(l => l.source + '-' + l.target));
    const existingNodes = new Map(safeCurrent.nodes.map(n => [n.id, n]));

    const newLinksRaw = getTopNeighbors(id, 100);
    let addedCount = 0;

    expandColorIndex++;
    const paletteIndex = 1 + ((expandColorIndex - 1) % (expandPalette.length - 1));
    const newRgb = expandPalette[paletteIndex];
    const nextLinks = [...safeCurrent.links];

    const sourceNode = existingNodes.get(id);
    const startX = sourceNode ? sourceNode.x : 0;
    const startY = sourceNode ? sourceNode.y : 0;

    newLinksRaw.forEach(l => {
        const key = l.source + '-' + l.target;
        if (!existingLinks.has(key)) {
            nextLinks.push({ source: l.source, target: l.target, val: l.val, baseColor: newRgb });
            existingLinks.add(key);
            addedCount++;
        }
        const nId = l.source === id ? l.target : l.source;
        if (!existingNodes.has(nId)) {
            existingNodes.set(nId, {
                id: nId,
                color: '#007bff',
                x: startX + (Math.random() - 0.5) * 40,
                y: startY + (Math.random() - 0.5) * 40
            });
        }
    });

    if (existingNodes.has(id)) {
        const node = existingNodes.get(id);
        existingNodes.set(id, { ...node, color: '#ff4757' });
    }

    const nextNodes = Array.from(existingNodes.values());
    if (addedCount > 0) {
        updateHistory(nextNodes, nextLinks, id);
        renderState(historyStack[historyIndex]);
        Graph.d3ReheatSimulation();
    } else {
        updateInfoPanel();
        const targetNode = nextNodes.find(n => n.id === id);
        if (targetNode) Graph.centerAt(targetNode.x, targetNode.y, 800);
    }
}

function exportImage(type) {
    const canvasElement = document.querySelector('canvas');
    if (!canvasElement) return;
    const width = canvasElement.width;
    const height = canvasElement.height;
    const watermarkText = document.getElementById('watermark').innerText;
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = width;
    tempCanvas.height = height;
    const ctx = tempCanvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);
    ctx.drawImage(canvasElement, 0, 0);
    ctx.font = 'bold 96px sans-serif';
    ctx.fillStyle = 'rgba(0,0,0,0.1)';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'top';
    ctx.fillText(watermarkText, width - 40, 40);
    const imgData = tempCanvas.toDataURL('image/png');
    if (type === 'pdf') {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({ orientation: 'landscape', unit: 'px', format: [width, height] });
        doc.addImage(imgData, 'PNG', 0, 0, width, height);
        const filename = currentCenterId ? `${currentCenterId}-network.pdf` : 'network.pdf';
        doc.save(filename);
    }
}

document.getElementById('geneInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') startNewSearch();
});

"""


def sync_viewer_assets(
    base: str,
    init_empty_json: bool,
    view_mode: str = "auto",
    full_view_threshold: int = 300,
    max_display_nodes: int = 0,
):
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
        SCRIPT_JS.replace("__JSRC_VIEW_MODE__", mode)
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


def cmd_init(args):
    sync_viewer_assets(args.outdir, init_empty_json=True, view_mode="auto", full_view_threshold=300, max_display_nodes=0)
    print(f"Viewer scaffold created in {args.outdir}")
