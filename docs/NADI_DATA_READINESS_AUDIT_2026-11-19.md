# NADI Data Readiness Audit — 19 November 2026

## Purpose

This is a pre-training inventory for NADI. It distinguishes data that are
downloadable now from data that require an owner request, and it prevents
separate evidence tracks from being silently joined as though they were one
real contamination event.

The intended end-to-end evidence key is:

```text
network_id + node_id + event_id + timestamp
  + operational state + independent microbiological result
  + downstream observation / response outcome
```

No public data source verified during this audit contains every element above.

## Evidence standard for a full, observed contamination-to-response validation

| Required field group | Minimum content |
|---|---|
| Network identity | Verified node/pipe topology; tanks, pumps, valves, source and demand nodes |
| Operations | Timestamped pressure, flow, tank level, pump/valve/supply state and interruption/restart information |
| Biological truth | Independently measured E. coli presence/count, method, detection limit and QC |
| Spatial linkage | Exact sample node/location and link to the hydraulic network |
| Event truth | Intrusion/leak/break/contamination investigation with time and source hypothesis |
| Outcome | Downstream samples, confirmed affected locations, laboratory turnaround and response/action log |

## A. Microbiology and drinking-water-quality data

| Source | Access | What is real and usable | Missing for NADI | Correct use |
|---|---|---|---|---|
| England Environment Agency, confirmed membrane-filtration E. coli, 2024 | Downloaded locally | 14,069 observed surface-water laboratory records with date/site coordinates | Drinking-water domain, pipe topology, operations, downstream route outcomes | Authentic microbial-risk and testing-prioritisation track only |
| U.S. EPA Distribution Water Data 2023–2024 | Downloaded locally | 144 authentic distribution-water records: microbial, chlorine, pH, temperature and other chemistry | No positive E. coli record; no topology/operations | Domain audit; not classifier training |
| Lira, Uganda piped-water/groundwater study, Mendeley `jv6drgtvzc.1` | Open CC BY 4.0 | 306 records; 56 piped-water samples including E. coli, chlorine, turbidity, pH, temperature, conductivity and GPS | No pipe graph, time-series operations or downstream event outcomes | External drinking-water microbial transfer/endpoint stress track |
| Delhi Jal Board daily quality reports | Public reports | City-specific surveillance counts and source/treatment context | Not a downloaded sample-level, ML-ready E. coli + node + time table; no topology/operations join | Delhi background/context and data-owner pathway only |
| JJM-WQMIS / Citizen Corner | Public portal and reports | India-wide laboratory and field-testing coverage; possible village-level reporting | Raw sample-level export, linked hydraulic information and consistent timing not verified | India context and potential request pathway |
| Chennai People's Water Data | Paper/preprint reported | Indian household point-of-use E. coli prediction setting | Raw table, QC table and code not verified open | Author-request candidate; never assume acquisition |
| Hubli–Dharwad intermittent-supply studies | Publications/thesis open; underlying data not verified open | Historic paired pressure/physicochemical/grab-sample indicator-bacteria study in India | Raw records, exact node topology and complete operational log are unavailable publicly | Highest-priority author/utility request candidate |
| Ålesund, Norway distribution study | Publication open; data restricted | Weekly network water-quality records, E. coli/coliform context, pipe-zone characteristics and calibrated hydraulic quantities | Authors state records cannot be made public because of security | Highest-priority author/municipality request candidate |

## B. Authentic operations, pressure, flow and leak data

| Source | Access | What is real and usable | Missing for NADI | Correct use |
|---|---|---|---|---|
| Slovak utility multi-source dataset, Zenodo `15096167` | Open CC BY 4.0 | One year of hourly flow, pressure, energy, weather/groundwater variables and confirmed leak information in an isolated utility zone | Full pipe topology and microbiological labels | Authentic intrusion/operational anomaly model; cannot be called E. coli data |
| City D field leak repair records | Open leak-record release; model may require author/utility permission | 256 municipal leak work orders, 230 linked to anonymised City D nodes | Publicly reliable topology availability must be rechecked; no microbiology | Authentic pipe-failure prior and source-hypothesis analysis |
| Texas laboratory pipe-network leak benchmark | Open Mendeley/primary paper | Real physical branched and looped 47 m PVC network; pressure/acoustic/accelerometer measurements for controlled leaks | E. coli and drinking-water field outcomes | Physical hydraulic validation, not biological validation |
| WDSEventDB | Open Zenodo | Sensor-instrumented physical testbed with leakage, cyberattack and sensor-failure events | E. coli, municipal topology/field outcome | Hardware/testbed anomaly robustness only |
| UT Austin multi-parameter distribution monitoring, Mendeley `wwy39n8p7z.1` | Open CC BY 4.0 | 5-minute temperature, conductivity, turbidity, fDOM, pH, ORP and combined chlorine at four distribution locations plus maintenance logs | E. coli labels and pipe topology | Authentic sensor normalisation/fouling/missingness track |
| Bristol POU telemetry | Downloaded locally | 5-minute flow, pressure, chlorine, ORP and filtration operation for 34 months | Network topology and microbiology | Authentic device/telemetry reliability track |
| Sectorised utility pressure/flow study | Paper identifies confidential data | About 200k five-minute records over eight real sectors, including restart peaks | Raw data and topology are confidential | Prior-art comparison only unless author grants access |

## C. Network topology and hydraulic-model data

| Source | Access | Legitimate value | Status under no-synthetic-scored-evidence rule |
|---|---|---|---|
| University of Kentucky WDS Research Database | Open / some systems via request | More than 40 EPANET-compatible systems; Kentucky set includes 18 real pipe systems and real demand/water-loss/cost context | Real-system-derived topology is usable for structural and transfer analysis; any generated contamination transport remains simulated |
| WaterBenchmarkHub / EPA WNTR networks | Downloaded locally | Standard reproducible hydraulic topologies and modelling utilities | Development only when transport events are generated |
| L-TOWN / BattLeDIM | Downloaded locally | 782-node network, five-minute SCADA benchmark and leak-event rules | A benchmark/digital twin; do not use generated tracer truth as authentic outcome evidence |
| IIT Bombay India flow-starved WaterGEMS models, Zenodo `7162154` | Open | India-relevant intermittent/flow-starved transmission topology and pressure-driven analysis model | Hydraulic model, not field microbiological validation |
| Delhi/Ghaziabad public drawings/GIS viewers | Partial public visibility | Local scoping, DMA/tank/pipe context and possible pilot selection | Not verified current, calibrated, machine-readable or security-cleared for route claims |
| Hubli–Dharwad public project documents | Public summaries | Recent network lengths, pipe sizes, tanks, zones and supply context | Not an executable as-built topology or paired laboratory record |

## D. Explicitly unsuitable for authentic-only scoring

These are useful for code verification or future digital-twin analysis but must
not be used as observed contamination validation:

- LeakDB, C-Town/DHALSIM, BATADAL and generated WDN state snapshots;
- Net3/L-TOWN tracer-injection or contaminant-release scenarios;
- simulated contamination Zenodo datasets;
- any row created by joining E. coli from one geography to a network from
  another geography;
- sensor proxies relabelled as E. coli.

## Acquisition priority

### Priority 1 — immediately downloadable and auditable

1. Slovak utility operational/leak dataset.
2. Lira, Uganda piped-water microbiology/chemistry dataset.
3. City D open leak work orders and metadata.
4. Texas physical pipe-testbed leak records.
5. Kentucky real-system-derived topology set.
6. IIT Bombay intermittent WaterGEMS model.

These will strengthen individual NADI interfaces but do **not** by themselves
create an end-to-end observed E. coli-to-pipeline dataset.

### Priority 2 — request, because these can close the actual gap

1. Hubli–Dharwad study authors / utility: de-identified sample-level
   pressure, physicochemical, microbiological, timing and ward/node data.
2. Ålesund study authors / municipality: anonymised weekly records, zone
   network features, calibrated hydraulic outputs and microbial endpoint schema.
3. Delhi Jal Board / Ghaziabad / Noida / GMDA: one bounded DMA's de-identified
   laboratory results, pseudonymised connectivity graph and coarse supply-state
   records.
4. Chennai People's Water Data authors: raw de-identified table, endpoint/QC
   dictionary and fixed split information.

### Priority 3 — required before the strongest final claim

Obtain one data asset where microbial labels, operational state and verified
network locations refer to the same system and time period. If it is not
obtainable, the final claim must remain: "authentic monitoring-site
prioritisation plus a separately labelled hydraulic digital twin," not
"validated contaminated-pipeline localisation."

## Score targets: evidence rule

No target score may be promised before a test is frozen.

- F1 >= 0.90 and ROC-AUC 0.91–0.92 need a fixed, endpoint-compatible,
  positive-rich held-out set.
- unseen-location F1 >= 0.80 requires a location-held-out test, not a random
  row split.
- Coverage@3 >= 0.40 needs real node-specific evidence or a clearly labelled
  digital-twin benchmark; it must not be achieved by tuning on the locked test.

## Verdict

The public-data package can support authentic microbial-risk, authentic
operational-anomaly, physical-testbed and real-system-derived topology tracks.
It cannot yet support an authentic, end-to-end E. coli pipeline-response claim.
The only credible paths to that claim are a controlled original pilot or a
de-identified release from a utility/research team.

## Acquisition record — completed 19 November 2026

The priority bundle was downloaded to:

```text
../nadi_resources/datasets/NADI_NETWORK_PRIORITY_2026_11_19/
```

`acquisition_manifest.json` records source URLs, SHA-256 hashes, byte counts,
claim boundaries and retrieval status. It includes these verified local assets:

| Asset | Local status | Inspection result | Permitted NADI role |
|---|---|---|---|
| Slovak utility operations/leak data | Downloaded | 8,737 hourly records; columns include utility state variables and `fault_d7` | Observed operational/anomaly evidence only |
| City D leak records | Downloaded | 256 repair records; fields include leak rate, mapped node, confidence, pipe material, type and repair timing | Observed pipe-failure prior only |
| Lira piped-water dataset | Downloaded and extracted | Workbook retained intact for independent endpoint/QC inspection | Observed drinking-water microbiology/chemistry transfer track only |
| Texas physical pipe testbed | Downloaded; dynamic-pressure subarchive extracted | 80 branched/looped physical-testbed pressure files; file paths encode leak/no-leak, leak type, flow and sensor position | Physical hydraulic/anomaly test only |
| IIT Bombay flow-starved WaterGEMS model | Downloaded as supplied archive | Archive retained; requires licensed/compatible model-reader inspection | India-relevant hydraulic structure only |
| Kentucky KY1 direct retrieval | Attempted and logged | Official direct endpoint returned HTTP 403 | Do not treat as downloaded; use official access/request route |

The Texas archive remains preserved in raw form. Only its dynamic-pressure
subarchive was extracted, deliberately avoiding unrelated acoustic data. This
is an evidence-management decision, not a deletion or alteration of source
data.

The Lira workbook's piped-water sheet confirms that it supplies a genuine
microbial endpoint (`E Coli`, CFU/100 ml) alongside free/total chlorine,
turbidity, pH, temperature, conductivity, TDS, sample-system identifiers,
sample-site labels and GPS coordinates. It has 56 observed piped-water rows.
This is valuable because the endpoint is real; it is still not a temporal
network-event dataset and must not be converted into one.

### Non-negotiable joining rule

None of the newly acquired rows may be joined to the England E. coli records
or to another network merely because timestamps or generic water variables look
compatible. Every modelling table must retain `dataset_id`, `data_origin`,
`endpoint_domain`, and `network_id`; cross-dataset work is transfer testing,
not an observed contamination event.
