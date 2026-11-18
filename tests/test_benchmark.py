from __future__ import annotations

import json

from nadi.cli import load_config
from nadi.evaluation.benchmark import run_locked
from nadi.paths import CONFIG_ROOT


def test_small_benchmark_enforces_equal_event_counts(tmp_path):
    config = load_config()
    benchmark = json.loads((CONFIG_ROOT / "locked_benchmark.json").read_text())
    benchmark.update({"event_count_per_seed": 2, "seeds": [20261117], "budgets": [1, 3], "bootstrap_repetitions": 50})
    summary = run_locked(config, benchmark, "test_benchmark")
    assert summary["events_evaluated"] == 2
    assert summary["primary_budget"] == 3
    assert summary["strongest_fair_baseline"] != "adaptive_sdaif"
    assert len(summary["config_sha256"]) == 64

