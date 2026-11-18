from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nadi.cli import load_config  # noqa: E402
from nadi.pipeline.demo import run_demo  # noqa: E402

app = Flask(
    __name__,
    template_folder=str(ROOT / "app" / "templates"),
    static_folder=str(ROOT / "app" / "static"),
)


def _latest_demo() -> dict:
    paths = sorted((ROOT / "results" / "runs").glob("demo_*.json"), key=lambda p: p.stat().st_mtime)
    if not paths:
        return run_demo(load_config(), 20261118, 3)
    return json.loads(paths[-1].read_text(encoding="utf-8"))


def _benchmark() -> dict:
    path = ROOT / "results" / "locked" / "locked_benchmark_v3_summary.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"gate": "NOT_RUN"}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/latest")
def latest():
    return jsonify(_latest_demo())


@app.get("/api/benchmark")
def benchmark():
    return jsonify(_benchmark())


@app.post("/api/demo")
def demo():
    body = request.get_json(silent=True) or {}
    seed = int(body.get("seed", 20261118))
    budget = max(1, min(10, int(body.get("budget", 3))))
    domain = str(body.get("domain", "SIMULATED_NETWORK_EVENT"))
    return jsonify(run_demo(load_config(), seed, budget, domain))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("NADI_PORT", "5050")), debug=False)

