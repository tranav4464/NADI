# NADI core coupling audit

## What is implemented

The current computational chain loads a weather-based surface-water E. coli
model, converts its forecast to a risk interval, combines that interval with
24 simulated Net3 tracer-reach scenarios, and asks adaptive SDAIF to choose
test nodes under a fixed budget. The test outcomes in the locked V4 benchmark
are simulated tracer reach (`node in hidden.affected`), not biological E. coli
results. The weather and network records are from separate domains and have no
shared sample, location, or event identifiers.

## What the locked benchmark actually shows

Across 120 simulated events the forecast risk took 95 distinct values. At a
one-test budget, SDAIF nevertheless chose the same node in every event. At the
primary three-test budget it produced only two test sequences. This is
consistent with the current loss function: for a fixed number of tests, the
same scalar E. coli risk multiplies missed reach at *every* candidate node.
Changing that scalar generally changes the magnitude of regret and whether a
certificate meets its threshold, but cannot supply spatial information about
which branch contains E. coli. The V4 primary Coverage@3 result is 0.504 for
SDAIF and 0.504 for adaptive Bayesian on the 76 events with nonempty simulated
reach. It demonstrates sequential decision mechanics over hydraulic scenarios;
it does not validate E. coli test prioritisation.

## Mathematical reason

For a fixed cardinality plan `S` and simulated affected set `A`, the present
loss is `L(S; p,A) = p * sum_{i in A\S} w_i + c|S|`. If `p > 0` is common to all
nodes and every candidate plan has the same `|S|`, minimizing loss for known
`A` is equivalent to maximizing `sum_{i in A∩S} w_i`, independent of `p`.
The minimax-regret and adaptive policies can still change when uncertainty-set
structure or revealed reach results change. That does not turn the surface-water
forecast into location-specific biological evidence.

## Required integration test before a stronger claim

Use a common drinking-water sampling event with independently measured E. coli
at named network nodes and forecast-time observations. Freeze the model before
revealing those results. Then compare SDAIF's first `k` tests with routine,
hydraulic-only, weather-only, and adaptive Bayesian rankings on the same
events. A separate simulation can exercise a coherent biological state model,
but must remain labelled simulated. Until such paired evidence exists, the
defensible claim is a working mathematical decision prototype with separate
surface-water and hydraulic evidence tracks.
