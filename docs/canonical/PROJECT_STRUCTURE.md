# Canonical project structure and compatibility boundary

NADI now exposes the following current-facing structure:

```text
src/nadi/
  core/ authentic/ microbial_risk/ decision/ hydraulics/ simulation/
  transfer/ telemetry/ reporting/ dashboard/
configs/
  canonical/ historical/ simulation/ transfer/
scripts/
  canonical/ audit/ historical/ acquisition/
data/
  raw/ processed/ manifests/ external/ simulated/
results/
  canonical/ historical/ simulation/ transfer/ audit/
docs/
  canonical/ evidence/ historical/ competition/
archive/
```

## Compatibility rules

The legacy data directories (`data_raw/`, `data_processed/`, and
`data_interim/`) and historical result paths remain the byte-preserved sources
for audited runs. The canonical configurations pin their hashes and refer to
those sources explicitly. The new `data/` and `results/` subdirectories are
the forward-facing layout for new outputs; they must not receive copied data
that would make a duplicate look like an independent dataset.

`src/nadi/provenance.py` remains a module, rather than a `provenance/` package,
to avoid changing import resolution for existing reproducibility code. It is
the provenance component required by the logical architecture.

The `simulation/`, `transfer/`, `historical/`, and `acquisition/` directories
are intentionally empty until a component is migrated with the procedure
below. Their existence makes the intended ownership layout visible without
silently relocating evidence.

## Safe migration procedure

1. Add the original path, SHA-256, proposed destination, consumers and evidence
   class to `reports/migration_manifest.csv`.
2. Update every canonical configuration and provenance record that refers to
   the artifact.
3. Copy or move one bounded group only after its consumers are tested.
4. Record old and new hashes, run the relevant canonical workflow, and retain
   the historical path or a compatibility redirect when necessary.
5. Update `archive/historical_index.csv` if the artifact is historical or
   superseded.

No current NADI claim depends on a file being physically relocated. The
canonical CLI and dashboard use only the guarded current path.
