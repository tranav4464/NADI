# NADI: Network-Adaptive Decision Intelligence for Water Safety

NADI is a software-first applied-mathematics prototype for deciding **where limited confirmatory water tests should begin** when E. coli-referenced risk evidence and water-network movement are uncertain.

The executable chain is:

```text
frozen evidence -> calibrated risk interval -> uncertain network reach
-> candidate consequences -> adaptive SDAIF test plan -> decision card
```

The project keeps four evidence types separate:

- `LAB_CONFIRMED`: an accepted microbiological result in its original dataset;
- `OBSERVED`: weather, telemetry, or network input actually recorded in its source;
- `MODEL_ESTIMATE`: calibrated or simulated model output;
- `SIMULATED`: constructed network event or hidden benchmark truth.

NADI does **not** claim that ordinary sensors directly detect E. coli, that the benchmark is Delhi's real pipe network, or that the software has already prevented illness.

## Reproduce

```powershell
py -3.10 -m venv .venv --system-site-packages
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m nadi.cli audit-resources
.\.venv\Scripts\python -m nadi.cli prepare
.\.venv\Scripts\python -m nadi.cli train-risk
.\.venv\Scripts\python -m nadi.cli generate-hydraulics
.\.venv\Scripts\python -m nadi.cli run-demo --seed 20261118 --budget 3
.\.venv\Scripts\python -m nadi.cli build-evidence
.\.venv\Scripts\python -m pytest
```

The headline locked result is V3. It is preserved in `results/locked` and is
not rerun by the ordinary reproduction script, preventing accidental
replacement of the frozen evaluation. Run `scripts/reproduce.ps1` to rebuild
the ordinary pipeline, tests, demonstration, and evidence report.

Raw resources remain in the sibling `nadi_resources` directory. `provenance/resource_manifest.json` freezes their paths and checksums.

