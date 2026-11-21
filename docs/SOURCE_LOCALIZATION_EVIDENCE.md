# Source-localisation identifiability audit

The localisation routine filters simulated hydraulic scenarios using only
revealed binary tracer-reach results. It ranks the **enumerated** source nodes
by how many compatible scenarios each has, assuming those scenarios were
listed with equal weight. This fraction is not a calibrated probability that a
real contaminant entered at that source. Every output records that an
unmodelled source remains possible.

The evaluation used test locations chosen by the frozen decision policies and
then revealed each location's held-out simulated reach result. No biological
assay or field source investigation was involved.

| Evaluation | SDAIF result after up to three tests | Comparator context |
|---|---|---|
| L-TOWN: four cases with a source in the enumerated set | Top-ranked source correct in 3/4; one case produced an out-of-model result | Adaptive Bayesian 2/4; random 3/4 on this tiny set |
| Net3: 12 cases with sources absent from the enumerated set | All 12 matched a known-source pattern and would be falsely attributed if the top rank were called the true source | Every tested policy had the same 12/12 false-attribution issue |

Details are in `results/ltown_source_localization_v1.json` and
`results/net3_unseen_source_localization_v1.json`.

The mathematical limit is straightforward: if two possible source states
produce identical test outcomes at all observed nodes, no method using only
those outcomes can distinguish them. Adding probability scores or ML cannot
recover information the test placement did not collect. To improve the result,
NADI needs more diverse test locations and a wider set of possible entry
points, then an independent held-out source test. Until that happens, the
product output must say “consistent with these modelled sources,” not “source
identified.”
