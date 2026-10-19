(async () => {
  const res = await fetch('./data/graph.json');
  const payload = await res.json();
  window.graphData = payload;

  document.getElementById('m-nodes').textContent = payload.metadata.node_count;
  document.getElementById('m-edges').textContent = payload.metadata.edge_count;
  document.getElementById('meta-file').textContent = payload.metadata.filename || '-';
  document.getElementById('meta-theme').textContent = payload.metadata.theme || 'Desconocido';
  document.getElementById('meta-rows').textContent = payload.metadata.total_rows != null ? payload.metadata.total_rows : '-';
  document.getElementById('meta-cols').textContent = payload.metadata.total_columns != null ? payload.metadata.total_columns : '-';
  const cols = payload.metadata.columns || [];
  const maxVisible = 5;
  const visibleCols = cols.slice(0, maxVisible).join(', ');
  const hiddenCount = Math.max(0, cols.length - maxVisible);
  let colText = visibleCols;
  if (hiddenCount > 0) {
    colText = visibleCols + ` <button id="show-cols-btn" style="font-size:9px;background:#00ffc8;color:#0b0b12;border:none;padding:2px 4px;border-radius:3px;cursor:pointer;">Ver +${hiddenCount}</button>`;
  }
  document.getElementById('meta-col-list').innerHTML = colText;
  document.getElementById('meta-col-list').addEventListener('click', (e) => {
    if (e.target.id === 'show-cols-btn') {
      const container = document.getElementById('meta-col-list');
      if (container.dataset.expanded === 'true') {
        container.innerHTML = visibleCols + ` <button id="show-cols-btn" style="font-size:9px;background:#00ffc8;color:#0b0b12;border:none;padding:2px 4px;border-radius:3px;cursor:pointer;">Ver +${hiddenCount}</button>`;
        container.dataset.expanded = 'false';
      } else {
        container.innerHTML = cols.join(', ') + ` <button id="hide-cols-btn" style="font-size:9px;background:#ff2a6a;color:#fff;border:none;padding:2px 4px;border-radius:3px;cursor:pointer;">Ver -</button>`;
        container.dataset.expanded = 'true';
      }
    } else if (e.target.id === 'hide-cols-btn') {
      const container = document.getElementById('meta-col-list');
      container.innerHTML = visibleCols + ` <button id="show-cols-btn" style="font-size:9px;background:#00ffc8;color:#0b0b12;border:none;padding:2px 4px;border-radius:3px;cursor:pointer;">Ver +${hiddenCount}</button>`;
      container.dataset.expanded = 'false';
    }
  });
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

  const criticalPath = payload.critical_path || null;
  const pathNodes = new Set(criticalPath?.path || []);
  const pathEdges = new Set(
    (criticalPath?.edges || []).map(e => `${e[0]}-${e[1]}`)
  );

  const graphInstance = ForceGraph3D()
    (document.getElementById('3d-graph'))
    .graphData({ nodes: payload.nodes, links: payload.links })
    .nodeLabel(node => {
      const role = node.attributes?.role || 'Peripheral';
      const bet = (node.attributes?.betweenness || 0).toFixed(4);
      return `${node.id}\nRol: ${role}\nBetweenness: ${bet}`;
    })
    .nodeColor(node => {
      const role = node.attributes?.role || 'Peripheral';
      if (pathNodes.has(node.id)) return '#ffffff';
      if (role === 'Global Broker') return '#ff2a6a';
      if (role === 'Local Hub') return '#00ffc8';
      if (role === 'Super-Spreader') return '#ffe600';
      return '#6a3cff';
    })
    .nodeVal(node => pathNodes.has(node.id) ? 15 : 5)
    .cooldownTicks(150)
    .linkColor(link => {
      const k = `${link.source}-${link.target}`;
      const rev = `${link.target}-${link.source}`;
      if (pathEdges.has(k) || pathEdges.has(rev)) return '#ffff00';
      return 'rgba(255,255,255,0.15)';
    })
    .linkWidth(link => {
      const k = `${link.source}-${link.target}`;
      const rev = `${link.target}-${link.source}`;
      if (pathEdges.has(k) || pathEdges.has(rev)) return 3.5;
      return Math.min(1.5, (link.weight || 1) * 0.5);
    })
    .linkOpacity(0.3)

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

    const visibleNodes = processedNodes.filter(n => n.opacity > 0.5);
    const visibleLinks = processedLinks.filter(l => l.opacity > 0.5);
    document.getElementById('m-nodes').textContent = visibleNodes.length;
    document.getElementById('m-edges').textContent = visibleLinks.length;
    const vn = visibleNodes.length;
    const ve = visibleLinks.length;
    document.getElementById('m-density').textContent = vn > 1 ? (ve / (vn*(vn-1))).toFixed(4) : '0';

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

  graphInstance.onNodeClick(node => {
    const panel = document.getElementById('node-analysis-panel');
    const role = node.attributes?.role || 'Peripheral';
    const bet = (node.attributes?.betweenness || 0).toFixed(4);
    const close = (node.attributes?.closeness || 0).toFixed(4);
    const deg = (node.attributes?.centrality || 0).toFixed(4);
    panel.innerHTML = `
      <h3 style="margin:0 0 12px 0; color:#00ffc8;">🔍 ${node.id}</h3>
      <p><strong>Rol:</strong> <span style="color:#ffe600;">${role}</span></p>
      <p><strong>Grupo:</strong> ${node.group}</p>
      <hr style="border-color:#2a2a40; margin:10px 0;">
      <h4 style="margin:0 0 8px 0; font-size:12px; color:#888;">📊 Métricas</h4>
      <p style="font-size:12px; margin:2px 0;"><strong>Betweenness:</strong> ${bet}</p>
      <p style="font-size:12px; margin:2px 0;"><strong>Closeness:</strong> ${close}</p>
      <p style="font-size:12px; margin:2px 0;"><strong>Degree:</strong> ${deg}</p>
      <p style="font-size:10px; color:#666; margin-top:4px;">Betweenness: puente / Closeness: alcance rápido</p>
    `;
    panel.style.display = 'block';
  });

  window.exportMetrics = () => {
    const nodes = window.graphData.nodes;
    let csv = 'id,role,group,betweenness,closeness,degree\n';
    nodes.forEach(n => {
      csv += `"${n.id}","${n.attributes?.role || 'Peripheral'}",${n.group},${(n.attributes?.betweenness || 0).toFixed(4)},${(n.attributes?.closeness || 0).toFixed(4)},${(n.attributes?.centrality || 0).toFixed(4)}\n`;
    });
    const blob = new Blob([csv], {type:'text/csv'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'graphnexus_metrics.csv'; a.click();
  };

  document.getElementById('reset-cam').addEventListener('click', () => {
    if (graphInstance) {
      graphInstance.cameraPosition({ x: 0, y: 0, z: 250 }, { x: 0, y: 0, z: 0 }, 800);
    }
  });
})();
