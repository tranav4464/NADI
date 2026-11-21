import json
from pathlib import Path


def test_reproducibility_manifest_is_complete_and_green():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "results" / "reproducibility_manifest_v1.json").read_text(encoding="utf-8"))
    assert manifest["test_exit_code"] == 0
    assert not manifest["missing_expected_files"]
    assert len(manifest["files"]) >= 10
    for item in manifest["files"].values():
        assert len(item["sha256"]) == 64
