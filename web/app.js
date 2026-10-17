(async () => {
  const res = await fetch('./data/graph.json');
  const payload = await res.json();
  window.graphData = payload;

  document.getElementById('m-nodes').textContent = payload.metadata.node_count;
  document.getElementById('m-edges').textContent = payload.metadata.edge_count;
  const n = payload.metadata.node_count;
  const e = payload.metadata.edge_count;
  document.getElementById('m-density').textContent = (e / (n*(n-1))).toFixed(4);

  const groups = Array.from(new Set(payload.nodes.map(node => node.group))).sort((a,b)=>a-b);
  const select = document.getElementById('community-filter');
  groups.forEach(g => {
    const opt = document.createElement('option');
    opt.value = String(g);
    opt.textContent = 'Group ' + g;
    select.appendChild(opt);
  });

  const graphInstance = ForceGraph3D()
    (document.getElementById('3d-graph'))
    .graphData({ nodes: payload.nodes, links: payload.links })
    .nodeLabel(node => `${node.id}\n${JSON.stringify(node.attributes || {})}`)
    .nodeColor(node => ['#00ffc8','#ff2a6a','#ffe600','#6a3cff'][node.group % 4] || '#fff')
    .linkOpacity(0.3)
    .linkWidth(link => (link.weight || 1) * 1.5);

  let currentThreshold = 0;
  let currentGroup = 'all';

  function rebuild() {
    const originalNodes = window.graphData.nodes;
    const originalLinks = window.graphData.links;

    let filteredLinks = originalLinks.filter(l => (l.weight || 0) >= currentThreshold);

    const processedNodes = originalNodes.map(n => (
      { ...n, opacity: (currentGroup === 'all' || n.group === parseInt(currentGroup, 10)) ? 1 : 0.05 }
    ));

    const gVal = (currentGroup !== 'all') ? parseInt(currentGroup, 10) : null;
    const processedLinks = filteredLinks.map(l => {
      const sNode = originalNodes.find(n => n.id === l.source);
      const tNode = originalNodes.find(n => n.id === l.target);
      const sVal = sNode ? sNode.group : null;
      const tVal = tNode ? tNode.group : null;
      return { ...l, opacity: (gVal === null || (sVal === gVal && tVal === gVal)) ? 1 : 0.05 };
    });

    graphInstance.graphData({ nodes: processedNodes, links: processedLinks });
  }

  document.getElementById('community-filter').addEventListener('change', e => {
    currentGroup = e.target.value;
    rebuild();
  });

  document.getElementById('weight-slider').addEventListener('input', e => {
    currentThreshold = parseFloat(e.target.value);
    rebuild();
  });

  document.getElementById('node-search').addEventListener('change', e => {
    const targetId = e.target.value.trim();
    const node = window.graphData.nodes.find(n => n.id === targetId);
    if (node && graphInstance) {
      graphInstance.cameraPosition({ x: 0, y: 0, z: 0 }, node, 1000);
    }
  });

  document.getElementById('reset-cam').addEventListener('click', () => {
    if (graphInstance) {
      graphInstance.cameraPosition({ x: 0, y: 0, z: 250 }, { x: 0, y: 0, z: 0 }, 800);
    }
  });
})();
