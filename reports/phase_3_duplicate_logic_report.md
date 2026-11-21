# Phase 3 duplicate and conflicting logic audit

## Distinct implementations that must not be merged blindly

1. `src/nadi/authentic/policy.py` defines a posterior-weighted robust MILP for calibrated model probabilities and selected authentic laboratory outcomes. `src/nadi/sdaif/engine.py` defines enumerated-scenario minimax regret for simulated affected-node sets. They share mathematical vocabulary, but their uncertainty vertices, loss semantics, solver and evidence classes differ. A future common interface may wrap them; copying one into the other would change historical results.
2. `src/nadi/authentic/benchmark.py` computes positives-found and oracle-positive-discovery regret on authentic monitoring candidates. `src/nadi/evaluation/metrics.py` computes coverage and population-weighted coverage on simulated affected sets. The denominator is fundamentally different. The same term “positive” can mean a real high E. coli result in one path and a simulated tracer-reached node in another.
3. `src/nadi/authentic/models.py` and `src/nadi/microbial_risk/weather_model.py` each implement calibration error, calibrated model wrappers and classification metrics. The former uses EA environmental-water site history; the latter uses Marion/WQP weather data and older risk heads. They are alternate domain pipelines, not duplicate evidence for one model.
4. `scripts/build_authentic_site_rounds.py`, `scripts/run_authentic_xylem_experiment.py`, `scripts/train_ea_ecoli_authentic.py`, `scripts/train_ea_physchem_panel.py` and weather reconstruction scripts all write EA-related artifacts. Their different sample windows, feature sets and split definitions must remain named explicitly. The authentic Xylem headline uses only the first two.
5. `results/locked/locked_benchmark_v1..v4`, V5 no-placeholder files and regression outputs retain multiple simulated generations. `logs/protocol_deviations.md` identifies comparator fairness, configuration hash, budget accounting and empty-event repairs. V3 is historical and must not be promoted as a repaired-engine result.

## Hidden and unsafe fallbacks

`app/server.py` chooses a requested round or silently falls back to the last eligible round if the request is invalid. It reads hard-coded `results/authentic_locked` files directly, and `/api/authentic-xylem` returns every candidate's `laboratory_high_500` truth in one JSON payload. It verifies the SDAIF selected order but not result hashes or release timing. `src/nadi/cli.py` uses `configs/default.json` if no config is passed, while the authentic scripts embed their own defaults. Several generators call `write_text`/`to_csv` on fixed output paths, including those named locked. These are ownership and release-control defects for Phase 4–5.

## Audit status

Source signatures, imports and principal write paths were inspected. The report does not yet certify all notebook-only behavior, dynamic file references, test semantics, or every benchmark runner. Existing artifacts remain untouched. The next change should record a migration manifest, then introduce guarded canonical entry points without rewriting historical mathematics.
