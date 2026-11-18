from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ingestion.wqp_weather import prepare
from .microbial_risk.weather_model import train
from .paths import CONFIG_ROOT
from .pipeline.demo import run_demo
from .provenance import audit_manifest, freeze_manifest
from .evaluation.benchmark import run_locked
from .hydraulics.generate import generate as generate_hydraulics
from .reporting.evidence import build as build_evidence


def load_config(path: str | None = None) -> dict:
    target = Path(path) if path else CONFIG_ROOT / "default.json"
    return json.loads(target.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nadi", description="NADI reproducible decision pipeline")
    parser.add_argument("--config")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("freeze-resources")
    commands.add_parser("audit-resources")
    commands.add_parser("prepare")
    commands.add_parser("train-risk")
    commands.add_parser("generate-hydraulics")
    commands.add_parser("build-evidence")
    demo = commands.add_parser("run-demo")
    demo.add_argument("--seed", type=int, default=20261117)
    demo.add_argument("--budget", type=int, default=3)
    demo.add_argument("--domain", default="SIMULATED_NETWORK_EVENT")
    benchmark = commands.add_parser("benchmark")
    benchmark.add_argument("--benchmark-config", default=str(CONFIG_ROOT / "locked_benchmark.json"))
    benchmark.add_argument("--output-name", default="locked_benchmark_v1")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.command == "freeze-resources":
        result = freeze_manifest()
    elif args.command == "audit-resources":
        result = audit_manifest()
    elif args.command == "prepare":
        result = prepare(config["risk_model"]["threshold"])
    elif args.command == "train-risk":
        result = train(config)
    elif args.command == "generate-hydraulics":
        result = generate_hydraulics()
    elif args.command == "build-evidence":
        result = build_evidence()
    elif args.command == "run-demo":
        result = run_demo(config, args.seed, args.budget, args.domain)
    elif args.command == "benchmark":
        benchmark_config = json.loads(Path(args.benchmark_config).read_text(encoding="utf-8"))
        result = run_locked(config, benchmark_config, args.output_name)
    else:
        parser.error("Unknown command")
    print(json.dumps(result, indent=2, default=str))
    return 0 if not isinstance(result, dict) or result.get("passed", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())

