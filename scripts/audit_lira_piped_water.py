"""Write the provenance and endpoint audit for the downloaded Lira workbook."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from nadi.microbial_risk.lira import write_audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/lira_piped_water_audit.json"))
    args = parser.parse_args()
    print(json.dumps(write_audit(args.input, args.output), indent=2))


if __name__ == "__main__":
    main()
