# Canonical NADI track

The primary empirical workflow ranks confirmatory tests in recorded UK EA environmental-water monitoring rounds. The EA source mixes sea, river, estuarine, drainage and other materials. The current experiment is retrospective and is not a drinking-water pipe detector.

The canonical configuration is `configs/canonical/authentic_xylem.json`. New
runs must write to a unique directory beneath `results/canonical`; historical
`results/authentic_locked` files remain untouched. The installed `nadi` command
is the guarded canonical command; `nadi-legacy` and `python -m nadi.cli` are
historical entry points only. See `reports/canonical_architecture.md`,
`reports/canonical_entry_points.md`, and
`NADI_Evidence_Corrected_Manuscript.md` for the current evidence boundary.
