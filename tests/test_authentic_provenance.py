import json
from pathlib import Path


def test_authentic_resources_have_checksums():
    path = Path(__file__).resolve().parents[1] / "provenance" / "resource_manifest.json"
    rows = {r["resource_id"]: r for r in json.loads(path.read_text(encoding="utf-8"))["records"]}
    for resource_id in ("EA_ECOLI_2024", "EA_ECOLI_PHYSCHEM_PANEL_Q1_2024", "BRISTOL_POU_TELEMETRY"):
        assert rows[resource_id]["sha256"]
        assert rows[resource_id]["bytes"] > 0
    for resource_id in ("OPEN_ECOLI_MODELS", "WNTR", "EPANET"):
        assert rows[resource_id]["version"]
