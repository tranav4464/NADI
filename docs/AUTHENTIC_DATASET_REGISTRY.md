# Authentic-data registry

This registry distinguishes real observations from simulations and from prior-
art source code. It is the authoritative data plan for the authentic-data build.

| Resource | Real content | Current status | Legitimate use |
|---|---|---|---|
| Marion County/WQP | laboratory E. coli surface-water samples | downloaded and used | weather nowcast/forecast context |
| NOAA GHCN-D | observed temperature/precipitation | downloaded and used | past-only weather features |
| Bangladesh MICS/WQ endpoints | household/source-water survey and test fields | downloaded and audited | cross-sectional drinking-water transfer stress |
| GECCO 2019 | real drinking-water operational quality telemetry with event labels | downloaded and evaluated | operational anomaly benchmark only |
| Bristol POU telemetry | real operational telemetry, no microbial labels | downloaded and audited | anomaly and location-normalisation evidence |
| BattLeDIM L-TOWN | real SCADA measurements plus benchmark leak records and network model | downloaded and evaluated | leak/network localisation; not fecal contamination |
| WDSEventDB | water-distribution event testbed data | downloaded and audited | event/anomaly methods only |
| Open E. coli Models | prior-art code/notebooks; external EA/NRW/SEPA data dependencies | repository downloaded; core XGBoost adapted on authentic EA subset; full workflow not bit-for-bit reproduced | method replication source |
| EPA WNTR | open-source network modelling code/examples | repository downloaded; package tested | hydraulic computation |
| EPA EPANET 2.2 | open-source hydraulic/water-quality engine | repository downloaded; engine used through WNTR | network computation |
| EA Water Quality Archive | real UK laboratory/field water-quality observations | authentic E. coli subset downloaded (14,069 confirmed MF observations, 2024) | authentic surface-water E. coli replication; not drinking-network validation |
| Lira Uganda water-quality study | 56 piped-water observations with E. coli, chlorine, turbidity, pH, temperature, conductivity and GPS | downloaded and schema-inspected | drinking-water endpoint/transfer analysis; no network or time-series claim |
| Slovak utility operations/leaks | 8,737 observed hourly utility-state records with documented fault label | downloaded and schema-inspected | operational anomaly/intrusion-evidence track; not microbiology |
| City D municipal leak records | 256 field repair records with mapped-node and pipe/leak metadata | downloaded and schema-inspected | pipe-failure prior/source hypothesis; no microbial outcome |
| Texas physical pipe testbed | controlled real pressure measurements from branched and looped PVC physical network | downloaded; pressure subarchive extracted | physical hydraulic/anomaly validation; no microbial outcome |
| IIT Bombay flow-starved WaterGEMS model | India-relevant intermittent/flow-starved hydraulic model | downloaded as supplied archive | structural/hydraulic analysis only; transport outputs are simulated |

WDSEventDB is also evaluated with an event-file holdout in
`results/wdseventdb_event_holdout_v1.json` (15,422 observed testbed rows across
eight event files). Its labels represent leakage, cyberattack and sensor
failure, not E. coli; the macro F1 is reported to expose event-distribution
shift rather than being used as a pathogen score.

The independent authentic prior-art smoke result is in
`results/authentic_prior_art_replication_v1.json`: the real L-TOWN network
successfully runs through WNTR/EPANET (782 junctions, 905 pipes, 2,017 time
steps). Open E. coli notebooks remain blocked on their external EA/NRW/SEPA,
weather and satellite input files, so no performance result is claimed for
that workflow yet.

`scripts/evaluate_texas_physical_pressure.py` now performs a grouped,
measurement-only hydraulic audit on 40 P1 physical runs. It uses whole-run
condition groups, reports the always-leak baseline and writes
`results/texas_physical_pressure_v1.json`. Its 0.826 out-of-fold ROC-AUC is
evidence that observed pressure spectra contain controlled leak information,
but its thresholded F1 does not beat the always-leak baseline due to the 80%
leak prevalence. The correct use is a bounded hydraulic-evidence input, not a
microbial detection or pipeline-contamination claim.

The EA extraction is reproducible with
`scripts/download_ea_ecoli_authentic.py`. The immutable raw CSV and its
sidecar provenance record are stored under
`../nadi_resources/datasets/EA_ECOLI_AUTHENTIC/`; the query uses the official
API, determinand `2348` (confirmed membrane-filtration E. coli), a bounded
England polygon and a 2024 date range. The API data are observed surface-water
laboratory records and are intentionally kept separate from the Marion
drinking-water proxy track.

`scripts/train_ea_ecoli_authentic.py` provides a leakage-safe temporal baseline
on this authentic file. It defines the endpoint from the laboratory qualifier
(`result` beginning with `<` is a non-detect) and reports the full metric set in
`results/ea_ecoli_authentic_baseline_v1.json`. The best current baseline is
histogram gradient boosting (F1 0.864, recall 0.865, ROC-AUC 0.838 on the
held-out final 20%); these numbers describe English surface-water observations
only and must not be presented as Delhi drinking-water performance.

For a stronger authentic feature test, `scripts/download_ea_ecoli_feature_panel.py`
joins E. coli to the sample-matched pH, water-temperature and conductivity
observations available in the bounded period, using the official sample URI
(not nearest-time matching). Ammoniacal nitrogen was requested but had no
sample-matched observations in this extraction and is recorded as unavailable,
not imputed. The bounded Q1-2024 panel contains 648 E. coli samples;
physicochemical completeness is uneven and is reported explicitly. The
resulting metrics are in
`results/ea_ecoli_physchem_panel_v1.json` and remain an England surface-water
track, not a drinking-network or Delhi-NCR claim. The evidence pack reports the
physicochemical-only result; context-only and combined models are retained as
diagnostics because location/time can dominate environmental datasets.
An additional deterministic site-hash holdout is in
`results/ea_ecoli_physchem_geographic_holdout_v1.json` (38 unseen locations;
XGBoost F1 0.737), providing a stricter transfer check than the temporal split.
The same unseen-site split is also evaluated after joining observed historical
Open-Meteo weather by site and UTC date in
`results/ea_weather_enriched_holdout_v1.json` (weather match rate 1.0; XGBoost
F1 0.733, ROC-AUC 0.750). This is a prior-art-style weather adaptation, not a
drinking-network model.

## Non-negotiable interpretation

No current public resource provides all four elements in one row-level table:
intermittent drinking-water operations, sensor telemetry, independent E. coli
truth and verified hydraulic node connectivity. Therefore the authentic-data
build must use separate domain tracks and cannot honestly train a single
paired drinking-network E. coli model until new field data are collected.

The prior-art repository acquisition log is
`results/prior_art_repository_audit_v1.json`. It deliberately records the
repositories as `ACQUIRED_NOT_REPRODUCED` until their workflows are executed
against their required source data.
