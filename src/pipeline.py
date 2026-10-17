"""GraphNexus pipeline: export GraphOutput to web-consumable JSON."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.engine import GraphOutput


def export_graph_to_web(graph_output: GraphOutput, output_dir: str = "web/data") -> str:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "node_count": len(graph_output.nodes),
            "edge_count": len(graph_output.edges),
        },
        "nodes": [
            {"id": n.id, "group": n.group, "attributes": n.attributes}
            for n in graph_output.nodes
        ],
        "links": [
            {"source": e.source, "target": e.target, "weight": e.weight}
            for e in graph_output.edges
        ],
    }
    target = out_path / "graph.json"
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return str(target)
