# NADI mathematical assurance case

## What the mathematics decides

For a fixed event, NADI receives a finite set of candidate monitoring sites
`V`, an allowed test budget `k`, a declared set of compatible risk/network
states `Q`, and a consequence weight `w_i` for each site. A plan is a set
`A ⊆ V` with `|A| ≤ k`.

For state `q`, the missed-consequence loss is:

```text
L(A, q) = sum(i in affected(q) and i not in A) risk(q) * w_i + c * |A|
```

The state-wise oracle knows `q` and selects the least-loss valid plan. Its loss
is `L*(q)`. NADI's regret is therefore:

```text
R(A, q) = L(A, q) - L*(q)
```

SDAIF selects a feasible plan by minimising a declared blend of posterior
average regret and worst-case regret. It does **not** know the future lab
result. After an already-selected site is tested and its result becomes
available, incompatible states are removed and the plan is recomputed.

## Claims that are mathematically established in code

| Assurance claim | Why it matters | Executable evidence |
|---|---|---|
| A returned test plan never exceeds budget and retains committed tests. | A decision rule that silently exceeds field capacity is unusable. | `tests/test_sdaif.py::test_conditional_plans_keep_prior_tests_and_total_budget` |
| Regret is evaluated against a scenario-specific oracle. | The comparison is against the best feasible plan for the same assumed state, not an arbitrary score. | `src/nadi/sdaif/engine.py::plan_regrets`, `robust_plan` |
| Broadening an enumerated uncertainty set cannot lower the static worst-case regret for a fixed decision problem. | More uncertainty must not create unjustified confidence. | `tests/test_sdaif.py::test_more_compatible_uncertainty_cannot_reduce_static_regret` |
| A pending lab test consumes capacity but does not reveal its result. | Prevents an impossible “instant laboratory result” advantage. | `tests/test_sdaif.py::test_pending_lab_test_consumes_budget_without_revealing_result` |
| If feedback is unavailable by the decision deadline, SDAIF uses the static plan rather than pretending it can adapt. | Makes delay an operational constraint rather than a cosmetic field. | `tests/test_sdaif.py::test_result_beyond_deadline_uses_static_plan_without_contingency` |
| Incompatible observations cause abstention rather than a false recommendation. | The framework fails safely when its finite state set cannot explain evidence. | `tests/test_sdaif.py::test_inconsistent_evidence_abstains` |
| The authentic replay's first choice is invariant to hidden future labels. | Prevents retrospective outcome leakage in the real-record replay. | `tests/test_authentic_policy.py::test_first_authentic_decision_is_invariant_to_hidden_future_outcomes` |
| Every replayed SDAIF choice is reproducible from saved predictions, weights and prior observations. | A judge can reconstruct the stated decision from frozen files. | `app/server.py` checks replay order against `authentic_test_events.csv`; `tests/test_dashboard.py` verifies it. |

## What is not a theorem

The following claims are deliberately **not** made:

- no universal guarantee that the real utility state belongs to NADI's finite
  uncertainty set;
- no theorem that SDAIF is globally novel or superior to all robust or Bayesian
  methods;
- no proof that the historical Environment Agency test order will improve a
  drinking-water utility's future response;
- no causal claim of reduced illness or exposure.

The regret certificate is conditional: it means “near-best among the feasible
actions for the explicitly enumerated states and costs.” It is not a water
safety certificate.

## Evidence types must remain separate

The authentic Xylem evaluation tests retrospective prioritisation on observed
UK surface-water laboratory records. The hydraulic ensemble and its
affected-region results are separate, simulated/digital-twin evidence. The
physical pipe testbed is observed pressure/leak evidence but has no E. coli
endpoint. Combining those sources into an apparently observed contaminated
pipe event would invalidate this assurance case.

## Reproduction command

```powershell
./.venv/Scripts/python.exe -m pytest tests -q
./.venv/Scripts/python.exe scripts/audit_authentic_submission.py
./.venv/Scripts/python.exe scripts/audit_claim_boundaries.py
```

The test suite must pass before any reported mathematical claim is used in a
pitch, dashboard, poster or application.
