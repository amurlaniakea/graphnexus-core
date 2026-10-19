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

"""GraphNexus engine - local graph abstraction from tabular data."""

import logging
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
        time_col: str | None = None,
        community_algo: str = "louvain",
    ):
        self.source_path = Path(source_path)
        self.G = nx.Graph()
        self.node_col = node_col
        self.target_col = target_col
        self.attr_cols = attr_cols or []
        self.business_rule_col = business_rule_col
        self.time_col = time_col
        self.community_algo = community_algo

    def load_data(self) -> pd.DataFrame:
        path = self.source_path
        if path.suffix == ".json":
            return pd.read_json(path)
        return pd.read_csv(path)

    def find_critical_path(self, source: str, target: str) -> dict:
        if source not in self.G or target not in self.G:
            return {"found": False, "error": "Node not found"}
        try:
            path = nx.shortest_path(self.G, source=source, target=target, weight="weight")
            total_weight = sum(
                self.G[path[i]][path[i + 1]].get("weight", 1.0)
                for i in range(len(path) - 1)
            )
            edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            return {
                "found": True,
                "path": path,
                "edges": edges,
                "length": len(path) - 1,
                "total_weight": float(total_weight),
            }
        except nx.NetworkXNoPath:
            return {"found": False, "error": "No path exists between nodes"}

    def build(self) -> GraphOutput:
        df = self.load_data()
        self.G = nx.Graph()  # rebuild graph for pathfinding
        G = self.G

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
            max_nodes = 100
            max_edges_per_node = 5
            groups = df.groupby(self.business_rule_col)
            for _, group_df in groups:
                ids = group_df[self.node_col].astype(str).tolist()
                if len(ids) > max_nodes:
                    logging.warning(
                        f"Business rule group exceeds {max_nodes} nodes ({len(ids)}); "
                        f"limiting edges per node to {max_edges_per_node} to prevent O(n^2) explosion."
                    )
                # MITIGACIÓN O(N²): Topología en estrella (no clique completo)
                # Reduce complejidad a O(N) y evita explosión con grupos grandes.
                if len(ids) > 1:
                    center = ids[0]
                    for node in ids[1:]:
                        if G.has_edge(center, node):
                            G[center][node]["weight"] += 1.0
                        else:
                            G.add_edge(center, node, weight=1.0)

        # Temporal parsing (Unix timestamp for frontend)
        time_range = None
        if self.time_col and self.time_col in df.columns:
            df['_ts_raw'] = pd.to_datetime(df[self.time_col], errors='coerce')
            df['_unix_time'] = df['_ts_raw'].astype('int64') // 10**9
            valid = df['_unix_time'].notna()
            if valid.any():
                time_range = [int(df.loc[valid, '_unix_time'].min()), int(df.loc[valid, '_unix_time'].max())]

        # Structural centrality metrics (sampled for performance)
        k_sample = min(500, len(G)) if len(G) > 0 else 1
        betweenness_map = nx.betweenness_centrality(G, k=k_sample)
        closeness_map = nx.closeness_centrality(G)

        # Role classification heuristic
        roles = {}
        degrees = dict(G.degree())
        for nid in G.nodes():
            deg = degrees.get(nid, 0)
            bet = betweenness_map.get(nid, 0.0)
            close = closeness_map.get(nid, 0.0)
            if bet > 0.05 and deg <= 3:
                roles[nid] = "Global Broker"
            elif deg >= 5 and bet < 0.02:
                roles[nid] = "Local Hub"
            elif close > 0.3:
                roles[nid] = "Super-Spreader"
            else:
                roles[nid] = "Peripheral"

        # Degree centrality for web visualization
        centrality_map = nx.degree_centrality(G)

        # Community detection (Leiden or Louvain)
        if self.community_algo == "leiden":
            communities = community.leiden_communities(G, seed=42)
        else:
            communities = community.louvain_communities(G, seed=42)
        group_map = {}
        for idx, comm in enumerate(communities):
            for nid in comm:
                group_map[str(nid)] = idx

        # Timestamp temporal injection (Fase 4 backend)
        time_range = None
        if self.time_col and self.time_col in df.columns:
            df['_ts_raw'] = pd.to_datetime(df[self.time_col], errors='coerce')
            df['_unix_time'] = df['_ts_raw'].astype('int64') // 10**9
            valid = df['_unix_time'].notna()
            if valid.any():
                time_range = [int(df.loc[valid, '_unix_time'].min()), int(df.loc[valid, '_unix_time'].max())]

        # Build output
        out_nodes = []
        for nid in G.nodes():
            node_attrs = {**nodes.get(str(nid), {})}
            if self.time_col and self.time_col in df.columns and '_unix_time' in df.columns:
                nid_str = str(nid)
                matches = df[df[self.node_col].astype(str) == nid_str]
                if not matches.empty:
                    ts_series = matches.iloc[:1]['_unix_time']
                    ts_val = ts_series.iloc[0] if len(ts_series) > 0 else float('nan')
                    if not pd.isna(ts_val):
                        node_attrs['timestamp'] = int(ts_val)
            out_nodes.append(Node(
                id=str(nid),
                group=group_map.get(str(nid), -1),
                attributes={
                    **node_attrs,
                    'centrality': float(centrality_map.get(str(nid), 0.0)),
                    'betweenness': float(betweenness_map.get(str(nid), 0.0)),
                    'closeness': float(closeness_map.get(str(nid), 0.0)),
                    'role': roles.get(str(nid), 'Peripheral'),
                },
            ))
        out_edges = [
            Edge(source=str(u), target=str(v), weight=float(G[u][v].get('weight', 1.0)))
            for u, v in G.edges()
        ]

        return GraphOutput(nodes=out_nodes, edges=out_edges)

    def export(self, G: nx.Graph, output_path: str, fmt: str = "json") -> str:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if fmt in ("gexf", "graphml"):
            out_file = p.with_suffix("." + fmt)
            if fmt == "gexf":
                nx.write_gexf(G, str(out_file))
            else:
                nx.write_graphml(G, str(out_file))
            return str(out_file)
        return str(p)
