#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Pedro Sordo Martínez

"""GraphNexus CLI entrypoint."""

import argparse
import sys
from pathlib import Path

import yaml
import networkx as nx

from graphnexus.engine import UniversalGraphEngine
from graphnexus.pipeline import export_graph_to_web


def parse_args():
    parser = argparse.ArgumentParser(
        description="GraphNexus: tabular to interactive 3D graph."
    )
    parser.add_argument("--input", default=None, help="Path to CSV/JSON dataset")
    parser.add_argument("--node-id", default=None, help="Column name for node identity")
    parser.add_argument("--target", default=None, help="Column name for direct connection (optional)")
    parser.add_argument("--attributes", default="", help="Comma-separated metadata columns")
    parser.add_argument("--config", default=None, help="Path to YAML config file")
    parser.add_argument("--export-format", default="json", choices=["json", "gexf", "graphml"], help="Export format")
    parser.add_argument("--theme", default=None, help="Dataset theme/description")
    parser.add_argument(
        "--community-algo",
        choices=["louvain", "leiden"],
        default="leiden",
        help="Community detection algorithm (default: leiden)"
    )
    args = parser.parse_args()
    if args.config:
        with open(args.config) as f:
            cfg = yaml.safe_load(f) or {}
        if args.input is None:
            args.input = cfg.get("input")
        if args.node_id is None:
            args.node_id = cfg.get("node_id")
        if args.target is None:
            args.target = cfg.get("target")
        if args.attributes == "":
            args.attributes = cfg.get("attributes", "")
        if args.export_format == "json" and cfg.get("export_format"):
            args.export_format = cfg["export_format"]
    if not args.input or not args.node_id:
        parser.error("--input and --node-id are required (or set via --config)")
    return args


def main():
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    try:
        attr_cols = [a.strip() for a in args.attributes.split(",") if a.strip()]
        engine = UniversalGraphEngine(
            source_path=args.input,
            node_col=args.node_id,
            target_col=args.target,
            attr_cols=attr_cols,
            community_algo=args.community_algo,
        )
        output = engine.build()
        if args.export_format == "json":
            file_path = export_graph_to_web(output, output_dir="web/data", theme=args.theme, source_path=args.input)
        else:
            G_export = nx.Graph()
            for n in output.nodes:
                G_export.add_node(str(n.id), group=str(n.group), **n.attributes)
            for e in output.edges:
                G_export.add_edge(str(e.source), str(e.target), weight=e.weight)
            file_path = engine.export(G_export, "web/data/graph", fmt=args.export_format)
        print(f"Graph exported: {file_path}")
        print(f"Nodes: {len(output.nodes)} | Edges: {len(output.edges)}")
    except Exception as exc:
        print(f"Error processing dataset: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
