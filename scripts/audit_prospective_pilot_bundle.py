"""Audit a partner-provided NADI prospective-pilot bundle without altering it."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nadi.pilot import audit_pilot_bundle  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=Path, required=True, help="Pseudonymous observed laboratory-sample CSV")
    parser.add_argument("--rankings", type=Path, required=True, help="Frozen pre-laboratory ranking CSV")
    parser.add_argument("--endpoint-json", type=Path, help="Optional preregistered endpoint-rule JSON")
    parser.add_argument("--out", type=Path, help="Optional JSON report path")
    args = parser.parse_args()
    endpoint = json.loads(args.endpoint_json.read_text(encoding="utf-8")) if args.endpoint_json else None
    report = audit_pilot_bundle(pd.read_csv(args.samples), pd.read_csv(args.rankings), endpoint_rule=endpoint).as_dict()
    print(json.dumps(report, indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
