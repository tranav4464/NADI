# Texas physical-pipe pressure evidence

## What this track validates

The Texas dynamic-pressure archive is a controlled **physical** pipe-network
experiment with labelled leak and no-leak runs. NADI extracts pressure-wave and
Welch-spectrum features from the observed P1 recording of each run, then uses
whole-run grouped cross-validation. A condition run never appears on both
sides of a split.

Run:

```powershell
.\.venv\Scripts\python scripts\evaluate_texas_physical_pressure.py
```

Results are written to `results/texas_physical_pressure_v1.json`.

## Meaning and boundary

This is a real measurement-based check of the physical-hydraulic evidence layer
that can later enter NADI as a typed, uncertainty-bounded input. It does **not**
train the E. coli model, change the locked authentic biological result, or prove
that a leak caused faecal contamination. The always-leak baseline is reported
because leak-present conditions are common; F1 alone would otherwise be
misleading. The appropriate interpretation is ROC-AUC and balanced accuracy
under grouped holdout, alongside the complete boundary in the generated report.
