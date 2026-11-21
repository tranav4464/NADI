"""Audit the Lira piped-water workbook without turning it into a network event.

The source workbook is an .xlsx file with a title row, a header row and a
units row.  This standard-library reader deliberately preserves that distinction
and treats ``<1`` CFU/100 ml as a non-detect for a *binary presence* endpoint.
It is an endpoint/transfer asset only: it has no sampling time-series, pipe
topology, operational state or downstream response observation.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def ecoli_presence(raw: object) -> int | None:
    """Return presence for a valid Lira E. coli result, otherwise ``None``."""
    if raw is None:
        return None
    value = str(raw).strip()
    if not value or value.lower() in {"nan", "none", "cfu/100ml"}:
        return None
    if value.startswith("<"):
        # The workbook's observed censoring notation means below the 1 CFU/100
        # ml reporting threshold.  It is not a measured zero concentration.
        return 0
    try:
        return int(float(value) > 0.0)
    except ValueError:
        return None


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return ["".join(node.itertext()) for node in root.findall(f"{NS}si")]


def _rows(archive: zipfile.ZipFile, worksheet: str = "xl/worksheets/sheet1.xml") -> list[list[str]]:
    shared = _shared_strings(archive)
    root = ET.fromstring(archive.read(worksheet))
    rows: list[list[str]] = []
    for row in root.findall(f".//{NS}sheetData/{NS}row"):
        values: list[str] = []
        for cell in row.findall(f"{NS}c"):
            v = cell.find(f"{NS}v")
            if v is None:
                values.append("")
            elif cell.get("t") == "s":
                values.append(shared[int(v.text or "0")])
            else:
                values.append(v.text or "")
        rows.append(values)
    return rows


def audit_workbook(path: Path) -> dict:
    """Create a compact, provenance-rich audit of the piped-water sheet."""
    with zipfile.ZipFile(path) as archive:
        rows = _rows(archive)
    if len(rows) < 5:
        raise ValueError("Lira workbook has fewer than five expected rows")
    headers = rows[2]
    if "E Coli" not in headers:
        raise ValueError("Expected E Coli column is missing from Lira piped-water sheet")
    index = {name: i for i, name in enumerate(headers)}

    def field(row: list[str], name: str) -> str:
        position = index[name]
        return row[position] if position < len(row) else ""

    records = rows[4:]  # skip title rows, headers and units
    outcomes = [ecoli_presence(field(row, "E Coli")) for row in records]
    valid = [value for value in outcomes if value is not None]
    system_types = Counter(
        field(row, "Type of Water System Sample").strip() or "UNSPECIFIED"
        for row in records
    )
    return {
        "source_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper(),
        "data_origin": "AUTHENTIC_OBSERVED",
        "endpoint": {
            "name": "E. coli presence",
            "source_column": "E Coli",
            "unit": "CFU/100 ml",
            "binary_rule": "numeric value > 0 is presence; '<1' is below reporting threshold and treated as non-detect",
            "valid_rows": len(valid),
            "positive_rows": int(sum(valid)),
            "negative_rows": int(len(valid) - sum(valid)),
            "invalid_or_missing_rows": int(len(outcomes) - len(valid)),
        },
        "rows_in_piped_water_sheet": len(records),
        "available_context_columns": [
            name for name in (
                "Water System ID", "Name of Sample Site", "Latitude of Sample GPS",
                "Longitude of Sample GPS", "Type of Water System Sample",
                "Free Chlorine residue", "Total Chlorine residue", "Turbidity", "pH",
                "Temperature", "Conductivity",
            ) if name in index
        ],
        "system_type_counts": dict(sorted(system_types.items())),
        "claim_boundary": (
            "Cross-sectional piped-water endpoint/chemistry/GPS data only. No timestamped "
            "operations, pipe graph, contamination-source event, downstream samples or response "
            "outcome; it cannot validate NADI pipeline localisation or forecasting."
        ),
    }


def write_audit(path: Path, output: Path) -> dict:
    audit = audit_workbook(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    return audit
