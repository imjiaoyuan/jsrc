let allLinks = [];
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

    let content = "GeneID\tPotriID\tAnnotation\tRelation\tWeight\n";

    const centerInfo = annotations[currentCenterId] || { p: "", d: "" };
    content += `${currentCenterId}\t${centerInfo.p}\t${centerInfo.d.replace(/[\n\r]/g, " ")}\tCenter\t-\n`;

    currentNeighbors.forEach(n => {
        const info = annotations[n.id] || { p: "", d: "" };
        content += `${n.id}\t${info.p}\t${info.d.replace(/[\n\r]/g, " ")}\tNeighbor\t${n.val}\n`;
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
