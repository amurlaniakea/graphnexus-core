#!/usr/bin/env python3
"""GraphNexus CLI entrypoint."""

import argparse
import sys
from pathlib import Path
from src.engine import UniversalGraphEngine
from src.pipeline import export_graph_to_web


def parse_args():
    parser = argparse.ArgumentParser(
        description="GraphNexus: tabular to interactive 3D graph."
    )
    parser.add_argument("--input", required=True, help="Path to CSV/JSON dataset")
    parser.add_argument(
        "--node-id", required=True, help="Column name for node identity"
    )
    parser.add_argument(
        "--target", default=None, help="Column name for direct connection (optional)"
    )
    parser.add_argument(
        "--attributes", default="", help="Comma-separated metadata columns"
    )
    return parser.parse_args()


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
        )
        output = engine.build()
        file_path = export_graph_to_web(output, output_dir="web/data")
        print(f"Graph exported: {file_path}")
        print(f"Nodes: {len(output.nodes)} | Edges: {len(output.edges)}")
    except Exception as exc:
        print(f"Error processing dataset: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
