import os

from jsrc.grn.core import ensure_dir, write_json, write_text

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GRN Viewer</title>
  <link rel="stylesheet" href="css/style.css">
  <script src="https://unpkg.com/d3@7"></script>
</head>
<body>
  <div id="controls">
    <input id="geneInput" placeholder="Gene ID">
    <button id="searchBtn">Search</button>
    <div id="status">Load data and search.</div>
  </div>
  <svg id="graph"></svg>
  <script src="js/app.js"></script>
</body>
</html>
"""

STYLE_CSS = """body { margin: 0; font-family: sans-serif; }
#controls { position: absolute; top: 12px; left: 12px; z-index: 10; background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 6px; }
#graph { width: 100vw; height: 100vh; display: block; }
"""

APP_JS = """let allLinks = [];
let annotations = {};

Promise.all([
  fetch('json/grn.json').then(r => r.json()),
  fetch('json/annotation.json').then(r => r.json())
]).then(([links, anno]) => {
  allLinks = links;
  annotations = anno;
  document.getElementById('status').innerText = 'Data loaded.';
}).catch(() => {
  document.getElementById('status').innerText = 'Failed to load json/grn.json or annotation.json';
});

function draw(center) {
  const links = allLinks.filter(l => l.source === center || l.target === center).slice(0, 100);
  const nodesMap = new Map();
  nodesMap.set(center, {id: center});
  links.forEach(l => {
    nodesMap.set(l.source, {id: l.source});
    nodesMap.set(l.target, {id: l.target});
  });
  const nodes = Array.from(nodesMap.values());
  const svg = d3.select('#graph');
  svg.selectAll('*').remove();
  const width = window.innerWidth;
  const height = window.innerHeight;
  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(120))
    .force('charge', d3.forceManyBody().strength(-250))
    .force('center', d3.forceCenter(width / 2, height / 2));

  const link = svg.append('g').selectAll('line').data(links).enter().append('line')
    .attr('stroke', '#999').attr('stroke-opacity', 0.6)
    .attr('stroke-width', d => Math.max(1, d.val || 1));
  const node = svg.append('g').selectAll('circle').data(nodes).enter().append('circle')
    .attr('r', d => d.id === center ? 8 : 6).attr('fill', d => d.id === center ? '#e74c3c' : '#3498db');
  const label = svg.append('g').selectAll('text').data(nodes).enter().append('text')
    .text(d => d.id).attr('font-size', 11).attr('dx', 8).attr('dy', 4);

  node.append('title').text(d => {
    const a = annotations[d.id] || {};
    return `${d.id}\\n${a.p || ''}\\n${a.d || ''}`;
  });

  sim.on('tick', () => {
    link.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
    node.attr('cx', d => d.x).attr('cy', d => d.y);
    label.attr('x', d => d.x).attr('y', d => d.y);
  });
}

document.getElementById('searchBtn').addEventListener('click', () => {
  const center = document.getElementById('geneInput').value.trim();
  if (!center) return;
  draw(center);
  document.getElementById('status').innerText = `Center: ${center}`;
});
"""


def cmd_init(args):
    base = args.outdir
    ensure_dir(base)
    ensure_dir(os.path.join(base, "css"))
    ensure_dir(os.path.join(base, "js"))
    ensure_dir(os.path.join(base, "json"))
    write_text(os.path.join(base, "index.html"), INDEX_HTML)
    write_text(os.path.join(base, "css/style.css"), STYLE_CSS)
    write_text(os.path.join(base, "js/app.js"), APP_JS)
    write_json(os.path.join(base, "json/grn.json"), [])
    write_json(os.path.join(base, "json/annotation.json"), {})
    print(f"Viewer scaffold created in {base}")

