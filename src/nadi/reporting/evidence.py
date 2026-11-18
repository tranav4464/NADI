from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ..paths import PROCESSED_ROOT, RESULTS_ROOT


def _bar_svg(rows: pd.DataFrame, target: Path) -> None:
    rows = rows.sort_values("mean_coverage", ascending=False)
    width, left, top, bar_h, gap = 900, 250, 50, 24, 12
    height = top + len(rows) * (bar_h + gap) + 45
    scale = 580
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f8fbfc"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#12343b}.label{font-size:14px}.value{font-size:13px;font-weight:bold}.title{font-size:20px;font-weight:bold}</style>',
        '<text x="20" y="28" class="title">Locked V3: Coverage@3 by policy</text>',
    ]
    for i, row in enumerate(rows.itertuples(index=False)):
        y = top + i * (bar_h + gap)
        value = float(row.mean_coverage)
        colour = "#007c91" if row.policy == "adaptive_sdaif" else ("#50a684" if row.policy == "adaptive_bayesian" else "#a8c7cf")
        parts.extend([
            f'<text x="20" y="{y + 17}" class="label">{row.policy}</text>',
            f'<rect x="{left}" y="{y}" width="{value * scale:.1f}" height="{bar_h}" rx="4" fill="{colour}"/>',
            f'<text x="{left + value * scale + 8:.1f}" y="{y + 17}" class="value">{value:.3f}</text>',
        ])
    parts.append('</svg>')
    target.write_text("\n".join(parts) + "\n", encoding="utf-8")


def build() -> dict:
    locked = RESULTS_ROOT / "locked"
    summary = json.loads((locked / "locked_benchmark_v3_summary.json").read_text(encoding="utf-8"))
    risk = json.loads((PROCESSED_ROOT / "risk_model_card.json").read_text(encoding="utf-8"))
    hydraulic = json.loads((PROCESSED_ROOT / "hydraulic_ensemble.json").read_text(encoding="utf-8"))
    aggregate = pd.read_csv(locked / "locked_benchmark_v3_aggregate.csv")
    primary = aggregate[aggregate.budget == summary["primary_budget"]].copy()
    figure_dir = RESULTS_ROOT / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    svg = figure_dir / "locked_v3_coverage_at_3.svg"
    _bar_svg(primary, svg)
    report = f"""# NADI Technical Evidence Summary

## Decision bottleneck

When confirmatory microbiological tests are limited, NADI decides which network locations should be tested first under uncertain E. coli-referenced risk and uncertain water movement.

## Executable mathematical chain

`calibrated risk interval -> 24-scenario reach set -> consequence loss -> adaptive minimax-regret testing -> certificate or abstention`

## Frozen evidence

- Surface-water endpoint: `{risk['forecast_24h']['claim_boundary']}`
- Forecast untouched test: n={risk['forecast_24h']['untouched_test']['n']}, ROC AUC={risk['forecast_24h']['untouched_test']['roc_auc']:.3f}, AP={risk['forecast_24h']['untouched_test']['average_precision']:.3f}, ECE={risk['forecast_24h']['untouched_test']['ece_10']:.3f}.
- Geographic audit: {risk['geographic_transfer_audit']['heldout_site_count']} unseen sites, n={risk['geographic_transfer_audit']['test_rows']}, ROC AUC={risk['geographic_transfer_audit']['metrics']['roc_auc']:.3f}, ECE={risk['geographic_transfer_audit']['metrics']['ece_10']:.3f}.
- Hydraulics: {hydraulic['scenario_count']} EPANET/WNTR TRACE scenarios with source, demand, tank and pipe-state uncertainty. These are simulated benchmark scenarios, not pathogen concentrations or a city twin.
- Locked V3: {summary['events_evaluated']} events; SDAIF Coverage@3={summary['adaptive_mean']:.3f}; strongest fair baseline `{summary['strongest_fair_baseline']}`={summary['strongest_baseline_mean']:.3f}.
- Result: `{summary['gate']}` for equivalence margin 0.02. Superiority supported: `{summary['superiority_supported']}`.

## Interpretation

SDAIF matches the strongest fair sequential comparator and adds a worst-case regret certificate, an adversarial witness, abstention, and the value of each next test. The frozen benchmark does **not** establish superiority, direct E. coli detection, Delhi-NCR performance, field validation, or prevented illness.

## Traceability

- Benchmark config SHA-256: `{summary['config_sha256']}`
- Event table SHA-256: `{summary['event_table_sha256']}`
- Aggregate SHA-256: `{summary['aggregate_sha256']}`
- Hydraulic network SHA-256: `{hydraulic['network_sha256']}`
"""
    docs = Path(__file__).resolve().parents[3] / "docs"
    docs.mkdir(exist_ok=True)
    report_path = docs / "TECHNICAL_EVIDENCE.md"
    report_path.write_text(report, encoding="utf-8")
    return {"report": str(report_path), "figure": str(svg), "benchmark_gate": summary["gate"]}
