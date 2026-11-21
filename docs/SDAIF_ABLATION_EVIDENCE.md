# SDAIF component ablation evidence

`scripts/run_sdaif_ablations.py` holds the 120-event Net3 decision protocol,
seeds and three-test budget fixed, then changes one mathematical ingredient at
a time. Outcomes are simulated tracer reach, not E. coli observations.

| Variant | Nonempty events | Mean Coverage@3 | Mean worst-case regret | Certificate rate |
|---|---:|---:|---:|---:|
| Full SDAIF | 76 | 0.504 | 0.105 | 100% |
| Point risk (no risk interval) | 76 | 0.504 | 0.060 | 100% |
| Wide risk interval [0,1] | 76 | 0.504 | 0.292 | 0% |
| Uniform consequence weights | 76 | 0.504 | 0.060 | 100% |
| Single network scenario | 76 | 0.149 | 0.000 | 100% |
| Static robust plan | 76 | 0.294 | 0.383 | 0% |

The ablation gives two important findings. First, the present common scalar
risk does not change which nodes are selected; this confirms the core-coupling
limitation and motivates node-specific evidence. Second, network uncertainty
and adaptive sequential selection materially affect the decision: collapsing the
network to one scenario or removing adaptation reduces coverage and increases
regret. A wide unsupported risk interval destroys certification, which validates
the need for transfer gating and abstention.

These are mathematical decision findings, not biological-performance claims.
