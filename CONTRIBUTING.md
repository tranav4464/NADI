# Contributing to NADI

Thank you for helping improve NADI. Contributions should preserve the project's
evidence boundaries and reproducibility guarantees.

## Development setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
```

## Contribution rules

1. Do not commit credentials, local environments or unlicensed raw datasets.
2. Do not tune models, thresholds or policies using locked-test labels.
3. Label evidence as observed, laboratory-confirmed, model-estimated,
   reconstructed, simulated or assumed.
4. Add semantic tests for new mathematical or data-processing behaviour.
5. Record configurations, seeds, data hashes and output provenance.
6. Do not overwrite canonical or frozen results; create a new run ID.
7. Update the claim matrix when a change affects a scientific claim.

## Pull requests

Describe the research question, affected evidence track, commands run, tests,
new artifacts and claim-boundary impact. Negative and tie results must not be
removed merely because they are inconvenient.
