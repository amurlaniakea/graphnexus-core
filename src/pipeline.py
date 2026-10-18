# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
from __future__ import annotations
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Pedro Sordo Martínez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

"""GraphNexus pipeline: export GraphOutput to web-consumable JSON."""


import json
from datetime import UTC, datetime
from pathlib import Path

from src.engine import GraphOutput


def export_graph_to_web(graph_output: GraphOutput, output_dir: str = "web/data") -> str:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "generated_at": datetime.now(UTC).isoformat(),
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
