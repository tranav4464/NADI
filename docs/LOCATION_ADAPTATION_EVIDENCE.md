# Location-adaptive normalisation evidence

NADI does not apply one universal pressure, chlorine, turbidity or conductivity
cutoff to every city or monitoring point. The `fit_local_normals` component
fits robust medians and median absolute deviations on a **training window only**.
When a location (or operating regime) has enough observations, its own baseline
is used; otherwise the model falls back to the global training baseline.

For a feature \(x_{i,t}\) at group \(g\), the score is

\[
z_{i,t}=\frac{x_{i,t}-\operatorname{median}(x_g)}
{1.4826\,\operatorname{MAD}(x_g)\vee\epsilon}.
\]

The baseline is frozen before calibration and test periods. Unknown or sparse
groups use global training statistics, avoiding artificially precise thresholds.
Missing values remain missing. Unit tests verify group selection, fallback and
future-data-free fitting. This is a mathematical evidence-normalisation layer,
not a biological label and not a direct E. coli detector.

It supports the complete NADI architecture by supplying comparable,
location-aware evidence to risk, intrusion, fusion and decision modules while
leaving biological confirmation to an independent endpoint. The Bristol audit
therefore remains operational telemetry evidence only; it must not be reported
as microbial accuracy.

Evidence: `src/nadi/telemetry/normal.py` and
`tests/test_local_normals.py`.

The intrusion layer accepts these local z-scores (`pressure_low_z`,
`pressure_drop_z`, `chlorine_drop_z`, and `turbidity_spike_z`) and maps them
through bounded monotone functions before evidence fusion. This links local
normalisation to the non-biological hazard pathway without silently treating a
raw value as a universal safety threshold.
