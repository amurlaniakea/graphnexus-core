#!/usr/bin/env python3
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

"""GraphNexus CLI entrypoint."""

import argparse
import sys
from pathlib import Path

from graphnexus.engine import UniversalGraphEngine
from graphnexus.pipeline import export_graph_to_web


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
