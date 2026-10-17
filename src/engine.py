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

"""GraphNexus engine - local graph abstraction from tabular data."""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import pandas as pd
from networkx.algorithms import community
from pydantic import BaseModel, Field


class Node(BaseModel):
    id: str
    group: str | int
    attributes: dict = Field(default_factory=dict)


class Edge(BaseModel):
    source: str
    target: str
    weight: float = 1.0


class GraphOutput(BaseModel):
    nodes: list[Node]
    edges: list[Edge]


class UniversalGraphEngine:
    def __init__(
        self,
        source_path: str | Path,
        node_col: str,
        target_col: str | None = None,
        attr_cols: list[str] | None = None,
        business_rule_col: str | None = None,
    ):
        self.source_path = Path(source_path)
        self.node_col = node_col
        self.target_col = target_col
        self.attr_cols = attr_cols or []
        self.business_rule_col = business_rule_col

    def load_data(self) -> pd.DataFrame:
        path = self.source_path
        if path.suffix == ".json":
            return pd.read_json(path)
        return pd.read_csv(path)

    def build(self) -> GraphOutput:
        df = self.load_data()
        G = nx.Graph()

        # Nodes
        nodes = {}
        for row in df.itertuples(index=False):
            nid = str(getattr(row, self.node_col))
            attrs = {
                col: getattr(row, col, None)
                for col in self.attr_cols
                if hasattr(row, col)
            }
            nodes[nid] = attrs
            G.add_node(nid)

        # Edges
        if self.target_col is not None and self.target_col in df.columns:
            for row in df.itertuples(index=False):
                s = str(getattr(row, self.node_col))
                t = str(getattr(row, self.target_col))
                if s != t and G.has_node(s) and G.has_node(t):
                    weight_col = getattr(row, "weight", None)
                    weight = float(weight_col) if weight_col is not None else 1.0
                    if G.has_edge(s, t):
                        G[s][t]["weight"] += weight
                    else:
                        G.add_edge(s, t, weight=weight)
        elif self.business_rule_col is not None and self.business_rule_col in df.columns:
            # ADVERTENCIA: Complejidad O(n^2) por grupo. Para grupos >1000 nodos,
            # considerar muestreo o estrategia de conexión alternativa para evitar
            # explosión de memoria (clique completo dentro de cada comunidad).
            groups = df.groupby(self.business_rule_col)
            for _, group_df in groups:
                ids = group_df[self.node_col].astype(str).tolist()
                for i in range(len(ids)):
                    for j in range(i + 1, len(ids)):
                        s, t = ids[i], ids[j]
                        G.add_edge(s, t, weight=1.0)

        # Louvain communities
        communities = community.louvain_communities(G, seed=42)
        group_map = {}
        for idx, comm in enumerate(communities):
            for nid in comm:
                group_map[str(nid)] = idx

        # Build output
        out_nodes = [
            Node(
                id=str(nid),
                group=group_map.get(str(nid), -1),
                attributes=nodes.get(str(nid), {}),
            )
            for nid in G.nodes()
        ]
        out_edges = [
            Edge(source=str(u), target=str(v), weight=float(G[u][v].get("weight", 1.0)))
            for u, v in G.edges()
        ]
        return GraphOutput(nodes=out_nodes, edges=out_edges)
