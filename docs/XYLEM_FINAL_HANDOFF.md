# NADI Xylem final handoff

## The exact project to submit

**NADI: Mathematical Prioritisation of Limited E. coli Testing**

NADI is a software-first applied-mathematical decision system. It uses only
information available before a monitoring round to rank which limited locations
should receive confirmatory E. coli tests first. Its authenticated demonstration
uses UK Environment Agency surface-water observations; it does not claim a
Delhi drinking-water digital twin or direct sensor detection.

## Judge-facing one-line evidence

On 41 untouched authentic multi-site rounds with the same three-test budget,
SDAIF found 114 high E. coli results, compared with 80 for the declared
deterministic-random policy and 84 for routine-frequency priority. It tied its
strongest fair single-model and Bayesian comparators. See
`results/authentic_locked/authentic_test_summary.csv` and
`docs/XYLEM_APPLICATION_DRAFT.md`.

## Required actions before publishing

These are user-controlled actions; they cannot be completed by source code.

- [ ] Register each team member and add every member to the platform's **Our
  Team** section.
- [ ] Add the actual teacher, mentor, laboratory and AI disclosures.
- [ ] Record the 3–4 minute video using `docs/XYLEM_3_TO_4_MINUTE_VIDEO_SCRIPT.md`.
- [ ] Upload the video publicly; test it while signed out.
- [ ] Upload/publicly share the slide deck or PDF; test it while signed out.
- [ ] Paste `docs/XYLEM_PROJECT_PAGE_COPY.md` into the project page, replacing
  every bracketed placeholder.
- [ ] Attach or link the reproducibility bundle, not private source paths.
- [ ] Publish before **1:00 PM ET, 20 November 2026**.
- [ ] Capture the published-page and upload confirmations.

## Approved claim

> NADI retrospectively prioritised authentic surface-water monitoring locations
> using only pre-round information and found more laboratory-confirmed high
> E. coli observations with the same three-test budget than its declared
> random and routine-frequency comparators on a locked period.

## Claims that must not appear

- “NADI directly detects E. coli.”
- “NADI proved a drinking-water pipe or branch was contaminated.”
- “NADI was validated in Delhi-NCR.”
- “NADI prevents illness” or “NADI already reduced exposure.”
- “SDAIF is a globally novel theorem” or “SDAIF beat every baseline.”

## Fast demo path

1. Run the dashboard.
2. Load an authentic locked round.
3. Explain that all displayed risks use pre-round evidence only.
4. Show the three frozen SDAIF selections.
5. Reveal each historical laboratory result only after explaining its selection.
6. Show the adaptive replay: model disagreement and regret guide the next
   test, while the mathematics remains within the same budget.
7. End with the transfer boundary and prospective-pilot path.

## Evidence bundle

The current portable review archive is
`dist/NADI_XYLEM_EVIDENCE_2026-11-19_v8.zip`. It intentionally excludes raw
source datasets, which retain their own licences and access conditions. Verify
the archive locally with `Get-FileHash -Algorithm SHA256` before uploading.
Earlier archives are retained only as historical snapshots; submit `v8`.

- `docs/XYLEM_APPLICATION_DRAFT.md`
- `docs/XYLEM_2MIN_PITCH.md`
- `docs/XYLEM_3_TO_4_MINUTE_VIDEO_SCRIPT.md`
- `docs/MATHEMATICAL_ASSURANCE_CASE.md`
- `docs/PROSPECTIVE_AUTHENTIC_PILOT_PROTOCOL.md`
- `docs/TEXAS_PHYSICAL_NETWORK_EVIDENCE.md`
- `docs/FINAL_GOAL_REQUIREMENTS_AUDIT.md`
- `docs/PARTNER_DATA_REQUEST.md`
- `results/authentic_locked/authentic_experiment_report.json`
- `results/authentic_locked/authentic_test_summary.csv`
- `results/authentic_locked/authentic_test_events.csv`
- `results/reproducibility_manifest_v1.json`
- `results/texas_physical_pressure_v1.json`

The data acquisition and mathematical software are reproducible. The remaining
publish, identity, consent and public-link steps require the team.
