# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
from __future__ import annotations

# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Pedro Sordo Martínez

"""GraphNexus pipeline: export GraphOutput to web-consumable JSON."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from graphnexus.engine import GraphOutput


def export_graph_to_web(
    graph_output: GraphOutput,
    output_dir: str = "web/data",
    theme: str | None = None,
    source_path: str | None = None,
    critical_path: dict | None = None,
) -> str:
    time_range = None  # inicializar para evitar UnboundLocalError
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    metadata = {
        "generated_at": datetime.now(UTC).isoformat(),
        "node_count": len(graph_output.nodes),
        "edge_count": len(graph_output.edges),
    }
    if source_path is not None:
        src_path = Path(source_path)
        metadata["filename"] = src_path.name
        try:
            if src_path.suffix == ".json":
                df_src = pd.read_json(str(src_path))
            else:
                df_src = pd.read_csv(str(src_path))
            metadata["total_rows"] = len(df_src)
            metadata["total_columns"] = len(df_src.columns)
            metadata["columns"] = list(df_src.columns)
        except Exception:
            metadata["filename"] = src_path.name
            metadata["total_rows"] = None
            metadata["total_columns"] = None
            metadata["columns"] = None
    else:
        metadata["filename"] = None
    if theme:
        metadata["theme"] = theme
    # Calcular rango temporal real antes de inyectar en metadata
    ts_vals = [n.attributes.get("timestamp") for n in graph_output.nodes if n.attributes.get("timestamp") is not None]
    if ts_vals:
        time_range = [min(ts_vals), max(ts_vals)]
    if time_range is not None:
        metadata["time_range"] = time_range
    payload = {
        "metadata": metadata,
        "nodes": [
            {"id": n.id, "group": n.group, "attributes": n.attributes}
            for n in graph_output.nodes
        ],
        "links": [
            {"source": e.source, "target": e.target, "weight": e.weight}
            for e in graph_output.edges
        ],
    }
    if critical_path is not None:
        payload["critical_path"] = critical_path
    target = out_path / "graph.json"
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return str(target)
