# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
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

import json
from pathlib import Path

import pandas as pd

from src.engine import UniversalGraphEngine
from src.pipeline import export_graph_to_web


def test_pipeline_export(tmp_path):
    df = pd.DataFrame(
        {
            "entity_id": ["A", "B", "C", "D", "E"],
            "cluster_key": ["C1", "C1", "C2", "C2", "C2"],
            "label": ["alpha", "beta", "gamma", "delta", "epsilon"],
        }
    )
    csv_path = tmp_path / "test_pipeline.csv"
    df.to_csv(csv_path, index=False)
    engine = UniversalGraphEngine(
        source_path=str(csv_path),
        node_col="entity_id",
        business_rule_col="cluster_key",
        attr_cols=["label"],
    )
    out = engine.build()
    out_dir = tmp_path / "data"
    file_path = export_graph_to_web(out, output_dir=str(out_dir))
    path = Path(file_path)
    assert path.exists()
    payload = json.loads(path.read_text())
    assert "metadata" in payload
    assert "generated_at" in payload["metadata"]
    assert payload["metadata"]["node_count"] == 5
    assert payload["metadata"]["edge_count"] > 0
    assert "nodes" in payload
    assert "links" in payload
