# Historical configurations

Versioned benchmark and auxiliary configurations remain at their original
`configs/*.json` paths while old consumers still depend on those paths. The
migration plan is in `reports/migration_manifest.csv`. The only added canonical
configuration currently lives in `configs/canonical/authentic_xylem.json`.
Do not treat a versioned simulation configuration as a configuration for the
authentic EA biological experiment.
