"""Run notebook code cells without requiring Jupyter in the clean environment."""
from __future__ import annotations

import json
from pathlib import Path


def test_canonical_evidence_notebook_executes_from_repository_root(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    notebook = json.loads((root / "notebooks/NADI_Canonical_Evidence_Notebook.ipynb").read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    required = [f"## {number}." for number in range(1, 19)]
    markdown = "\n".join("".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "markdown")
    assert all(label in markdown for label in required)
    monkeypatch.chdir(root)
    namespace = {"__name__": "__main__"}
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            exec("".join(cell["source"]), namespace)
