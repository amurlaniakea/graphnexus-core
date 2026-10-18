# GraphNexus 🌌

[![CI](https://github.com/amurlaniakea/graphnexus-core/actions/workflows/deploy.yml/badge.svg)](https://github.com/amurlaniakea/graphnexus-core/actions/workflows/deploy.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/graphnexus-core.svg)](https://pypi.org/project/graphnexus-core/)

Agnostic framework that transforms any tabular dataset (CSV/JSON) into a formal graph structure (Nodes/Edges), ready for network analytics and interactive 3D visualization. Uses **Leiden** (`--community-algo leiden`, requires `leidenalg`) or **Louvain** (`--community-algo louvain`, default) for community detection.

## ✨ Features

- **Agnostic Ingestion**: Accepts any CSV or JSON file. You define the node, target, and attribute columns.
- **Strict Validation**: Powered by Pydantic to ensure data integrity between Python and the frontend.
- **Community Detection**: Automatic Louvain clustering to identify hidden groups and ecosystems.
- **Interactive 3D Visualization**: Zero-config WebGL dashboard (`3d-force-graph`) with real-time filtering.
- **Local-First & Secure**: No external API calls. All processing happens on your machine.

## 🚀 Quick Start

### Option 1: Install from PyPI (Recommended)

```bash
pip install graphnexus-core

# Run the CLI tool directly
graphnexus --input examples/web_stack.csv --node-id repo_name --target co_contributor --attributes "stars,language"

# Then open `web/index.html` in your browser
```

### Option 2: Install from Source

```bash
git clone https://github.com/amurlaniakea/graphnexus-core.git
cd graphnexus-core
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .

graphnexus --input examples/web_stack.csv --node-id repo_name --target co_contributor --attributes "stars,language"
```

## 🌍 Universal Use Cases

1. **Open-Source Web Stack Intelligence** — Map software ecosystems, cluster communities with Louvain, and identify strategic infrastructure nodes.
2. **Global Supply Chain Strangling** — Model logistics flows, detect chokepoints via community isolation, and expose sovereignty vulnerabilities.
3. **Financial Anti-Fraud Operations** — Build transaction entity graphs, highlight circular flows, and isolate suspicious clusters using real-time filters.

## 🛠️ Development

```bash
pip install -e ".[dev]"
pre-commit run --all-files
pytest tests/ -v
```

## 📄 License

AGPL-3.0-or-later — see [LICENSE](LICENSE).

*Author: Pedro Sordo Martínez — amurlaniakea@gmail.com*
