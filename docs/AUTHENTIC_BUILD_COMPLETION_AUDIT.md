# Authentic-data build completion audit

This audit maps the active build objective to evidence in the current
workspace. A `PASS` means the requirement is demonstrated; `BOUNDED` means
the available authentic source was used but its domain is narrower than NADI's
future drinking-network claim; `EXTERNAL` means the remaining evidence cannot
be manufactured from public files.

| Requirement | Status | Evidence |
|---|---|---|
| Download and checksum official authentic laboratory observations | PASS | `provenance/resource_manifest.json`; EA 2024 CSV and sidecar metadata |
| Train on real E. coli observations with leakage-safe splits | PASS | `results/ea_ecoli_authentic_baseline_v1.json`; temporal split |
| Sample-matched physicochemical features | PASS | `results/ea_ecoli_physchem_panel_v1.json`; official sample-URI joins |
| Prior-art XGBoost family adaptation | PASS | `results/open_ecoli_prior_art_adaptation_v1.json` |
| Unseen-location transfer test | PASS | `results/ea_ecoli_physchem_geographic_holdout_v1.json` |
| Open-Meteo prior-art weather enrichment | PASS | `results/ea_weather_enriched_holdout_v1.json`; 100% weather join |
| GECCO operational event workflow | PASS | `results/gecco_event_v1.json` |
| Bristol operational telemetry audit | PASS | `results/bristol_telemetry_audit_v1.json` |
| WDSEventDB event-file holdout | PASS | `results/wdseventdb_event_holdout_v1.json` |
| BattLeDIM/L-TOWN network smoke reproduction | PASS | `results/authentic_prior_art_replication_v1.json` |
| EPANET/WNTR acquisition and use | PASS | repository commits and hydraulic results in `results/` |
| Controlled physical-pipe pressure audit | PASS | `results/texas_physical_pressure_v1.json`; whole-run grouped physical holdout |
| Indian/global transfer workflows | BOUNDED | Bangladesh, Marion/NOAA and other tracks are evaluated separately; no false pooling |
| Dashboard exposes authentic and simulated tracks separately | PASS | `/api/authentic`, `/api/authentic-xylem`, `app/templates/authentic.html`, `app/static/authentic.js` |
| Prospective ranking/laboratory provenance gate | PASS | `src/nadi/pilot/schema.py`; `/api/pilot-preflight`; `docs/PROSPECTIVE_AUTHENTIC_PILOT_PROTOCOL.md` |
| Performance matrix updated | PASS | `results/performance_matrix_v1.json`, `docs/PERFORMANCE_MATRIX.md` |
| Claim matrix and Xylem evidence pack updated | PASS | `docs/CLAIM_MATRIX.md`, `docs/XYLEM_EVIDENCE_PACK.md` |
| Provenance and reproducibility artifacts | PASS | 15 provenance resources, 37 hashed artifacts, green manifest |
| Full Open E. coli multi-agency bit-for-bit reproduction | BOUNDED | Repository acquired; controlled authentic EA subset adaptation completed. Full EA/NRW/SEPA/CORINE/MODIS source tables are not bundled |
| Paired intermittent drinking-network sensor + E. coli labels | EXTERNAL | No public row-level source identified; requires field/utility collection |
| Delhi-NCR biological validation | EXTERNAL | No public paired Delhi-NCR dataset identified |

## Current verified state

- 71 automated tests pass.
- Claim-boundary audit passes.
- Reproducibility manifest has exit code 0 and no missing expected files.
- Authentic scores are never presented as Delhi-NCR or drinking-network
  validation.

The build is therefore complete for all legally and technically available
public tracks, with the two external validation requirements explicitly
remaining outside the public-data-only build.
