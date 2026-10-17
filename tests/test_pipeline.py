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
