# Phase 10 — research-quality notebook

Created `notebooks/NADI_Canonical_Evidence_Notebook.ipynb` as a clean,
evidence-corrected research notebook. It contains the requested 18 sections:
scope, evidence map, dataset inventory, causal features, model comparison,
calibration, SDAIF, policy comparison, sequential replay, regret explanation,
authentic results, hydraulic track, simulation track, transfer results,
abstention, provenance, traceability, and limitations.

The notebook deliberately includes no unlabeled visualization. Its code cells
load canonical run artifacts and assert essential boundaries: locked sample
count, low specificity, decision-policy tie, and simulation label. The
notebook does not download data, retrain models, or write results.

Because the clean environment does not include Jupyter packages, the notebook
is executed in tests by parsing its standard nbformat 4 JSON and executing each
code cell from repository root. `tests/test_canonical_notebook.py` passed,
which proves the displayed code cells execute against canonical artifacts.

Remaining limitation: execution from a Jupyter UI is not separately tested;
the notebook uses only Python standard library, pandas, and existing artifacts,
so no notebook-specific dependency is required for its cells.
