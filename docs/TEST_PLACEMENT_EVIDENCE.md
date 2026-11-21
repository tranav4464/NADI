# Test-placement mathematics and negative results

The current L-TOWN reference contains eight simulated tracer scenarios from
two reservoir sources under four operating conditions. The original candidate
rule round-robins across distinct reach signatures. Two additional placement
rules were tested using standard greedy set-cover ideas:

1. **Source-pair cover:** select nodes that distinguish the most source pairs.
2. **Balanced cover:** after source discrimination, raise the minimum number of
   monitoring nodes reached in any reference operating scenario and prefer
   distinct reach signatures.

These are modifications to candidate placement, while the SDAIF test-selection
engine and three-test budget remain the same. V1 revealed that pure source-pair
cover filled spare slots with redundant nodes. V2 was designed after seeing
that failure and reused its cases, so V2 is development evidence. V3 froze
eight new operating conditions before simulation.

| Placement on V3 new holdout | Cases with affected candidates | Mean Coverage@3 on those cases | Source top rank correct | Model mismatch |
|---|---:|---:|---:|---:|
| Original reach-signature round-robin | 8/8 | 0.291 | 4/8 | 1/8 |
| Pure source-pair cover | 4/8 | 0.250 | 8/8 | 0/8 |
| Balanced cover | 8/8 | 0.273 | 4/8 | 0/8 |

All three placements distinguished all 16 cross-source pairs in the eight
*reference* scenarios. That training-set objective did not predict held-out
affected-node coverage. Pure pair cover looked best for source ranking but
failed to place a reachable candidate in half of the new cases. Balanced cover
removed that blind spot but did not beat the original placement on mean
Coverage@3. This is a negative result for the attempted modification, not a
new source-localisation theorem or a performance win.

The exact protocols and full case-level outputs are
`configs/ltown_placement_comparison_v1.json`,
`configs/ltown_placement_comparison_v2.json`,
`configs/ltown_placement_holdout_v3.json`, and
`results/ltown_placement_holdout_v3.json`. All outcomes are simulated tracer
reach, not E. coli or public-health outcomes. A real deployment would also
need sampling access, cost, pressure, demand and topology constraints.
