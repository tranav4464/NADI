"""Explicit inputs and exclusive output ownership for canonical runs."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class RunLayout:
    config_path: Path
    input_path: Path
    output_root: Path
    evidence_class: str
    domain: str
    seed: int
    config_sha256: str
    input_sha256: str
    raw: dict[str, Any]

    def create_output(self, run_id: str) -> Path:
        if not run_id or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for character in run_id):
            raise ValueError("run_id must use letters, digits, underscore or hyphen")
        destination = self.output_root / run_id
        # An existing run is never reused, even when its contents seem empty.
        destination.mkdir(parents=True, exist_ok=False)
        return destination


def load_layout(config_path: Path) -> RunLayout:
    config_path = config_path.resolve(strict=True)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Configuration must be a JSON object")
    required = {"input", "output_root", "evidence_class", "domain", "seed"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"Missing configuration fields: {sorted(missing)}")
    input_path = (ROOT / payload["input"]).resolve(strict=True)
    output_root = (ROOT / payload["output_root"]).resolve()
    canonical_results = (ROOT / "results" / "canonical").resolve()
    if output_root != canonical_results and canonical_results not in output_root.parents:
        raise ValueError("Canonical outputs must remain under results/canonical")
    if not input_path.is_file():
        raise ValueError("Input must be an existing file")
    if payload["evidence_class"] not in {"LAB_CONFIRMED", "OBSERVED", "MODEL_ESTIMATE", "SIMULATED", "ASSUMED"}:
        raise ValueError("Unknown evidence class")
    return RunLayout(
        config_path=config_path,
        input_path=input_path,
        output_root=output_root,
        evidence_class=str(payload["evidence_class"]),
        domain=str(payload["domain"]),
        seed=int(payload["seed"]),
        config_sha256=sha256(config_path),
        input_sha256=sha256(input_path),
        raw=payload,
    )
