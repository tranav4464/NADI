# Clean-environment reproduction

## Current isolated verification — 20 November 2026

NADI was installed into a newly created Python 3.10 virtual environment outside
the repository. The environment did **not** use `--system-site-packages`.
Dependencies came from `requirements-lock.txt` plus the editable local package.

```powershell
python -m venv <fresh-environment>
<fresh-environment>\Scripts\python.exe -m pip install --upgrade pip
<fresh-environment>\Scripts\python.exe -m pip install -r requirements-lock.txt -e .
<fresh-environment>\Scripts\python.exe -m pytest
<fresh-environment>\Scripts\nadi.exe run-tests `
  --config configs\canonical\run_tests.json `
  --run-id audit_20261120_isolated_04
```

Result: **88 tests passed in 21.69 seconds** through the installed canonical
CLI. The retained log and manifest are under
`results/canonical/tests/audit_20261120_isolated_04/`.

The first isolated attempt correctly revealed that `openpyxl` was undeclared
even though the EPA workbook audit uses it. It is now pinned as
`openpyxl==3.1.5` in both dependency declarations, and a regression test guards
that requirement.

This verifies package installation and software reproducibility, not utility,
laboratory, biological or field validation.

## Earlier shared-environment record (superseded)

A fresh Python 3.10 virtual environment, `.venv_clean`, was created after the
local development environment and installed from the repository with the
declared project dependencies. The complete pytest suite was run from that
environment and exited with code 0. The claim-boundary audit and performance
matrix generation also exited with code 0.

The fresh-environment check was rerun on 19 November 2026 after the authentic
SDAIF replay, Lira endpoint audit and Xylem submission audit were added.

Commands used:

```powershell
C:\Users\TRANAV\AppData\Local\Programs\Python\Python310\python.exe -m venv .venv_clean --system-site-packages
.venv_clean\Scripts\python.exe -m pip install -e ".[dev]"
.venv_clean\Scripts\python.exe -m pytest -q
.venv_clean\Scripts\python.exe scripts\audit_claim_boundaries.py
.venv_clean\Scripts\python.exe scripts\audit_authentic_submission.py
.venv_clean\Scripts\python.exe scripts\audit_xylem_submission_pack.py
```

Result: **66 tests passed**, the evidence-boundary audit passed, the
authentic-only submission audit passed, and the Xylem narrative audit confirmed
the frozen 114 / 80 / 84 comparison.

This is an independent package/environment reproduction, not an independent
utility or laboratory validation. The clean environment used the same frozen
resources and therefore cannot establish field transfer or biological truth.
