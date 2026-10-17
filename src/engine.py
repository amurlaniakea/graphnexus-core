"""GraphNexus engine - local graph abstraction from tabular data."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Union

import pandas as pd
import networkx as nx
from pydantic import BaseModel, Field
from networkx.algorithms import community


class Node(BaseModel):
    id: str
    group: Union[str, int]
    attributes: dict = Field(default_factory=dict)


class Edge(BaseModel):
    source: str
    target: str
    weight: float = 1.0


class GraphOutput(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


class UniversalGraphEngine:
    def __init__(
        self,
        source_path: Union[str, Path],
        node_col: str,
        target_col: Optional[str] = None,
        attr_cols: Optional[List[str]] = None,
        business_rule_col: Optional[str] = None,
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
