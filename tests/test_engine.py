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

import pandas as pd

from src.engine import Edge, GraphOutput, Node, UniversalGraphEngine


def test_engine_louvain_communities(tmp_path):
    data = {
        "entity_id": ["A", "B", "C", "D", "E"],
        "cluster_key": ["C1", "C1", "C2", "C2", "C2"],
        "label": ["alpha", "beta", "gamma", "delta", "epsilon"],
    }
    df = pd.DataFrame(data)
    csv_path = tmp_path / "test_data.csv"
    df.to_csv(csv_path, index=False)

    engine = UniversalGraphEngine(
        source_path=str(csv_path),
        node_col="entity_id",
        business_rule_col="cluster_key",
        attr_cols=["label"],
    )
    result = engine.build()

    assert isinstance(result, GraphOutput)
    assert len(result.nodes) >= 5
    groups = {str(n.group) for n in result.nodes}
    assert len(groups) >= 2
    for n in result.nodes:
        assert isinstance(n, Node)
        assert n.id in ["A", "B", "C", "D", "E"]
        assert "label" in n.attributes
    for e in result.edges:
        assert isinstance(e, Edge)
        assert isinstance(e.weight, float)
