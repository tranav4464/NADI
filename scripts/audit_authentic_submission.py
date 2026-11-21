from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIMARY = [
    ROOT / "docs" / "XYLEM_APPLICATION_DRAFT.md",
    ROOT / "docs" / "XYLEM_2MIN_PITCH.md",
    ROOT / "docs" / "AUTHENTIC_XYLEM_METHOD_AND_RESULTS.md",
    ROOT / "docs" / "XYLEM_3_TO_4_MINUTE_VIDEO_SCRIPT.md",
    ROOT / "docs" / "XYLEM_PROJECT_PAGE_COPY.md",
]
FORBIDDEN_AS_EVIDENCE = [
    "120 simulated network events",
    "simulated affected-node",
    "Delhi digital twin",
    "directly detects E. coli",
]


def audit() -> dict:
    violations = []
    for path in PRIMARY:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_AS_EVIDENCE:
            if phrase.lower() in text:
                violations.append({"file": str(path), "phrase": phrase})
    report_path = ROOT / "results" / "authentic_locked" / "authentic_experiment_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    policy = report["data_policy"]
    if policy["synthetic_records_used"] or policy["simulated_records_used"]:
        violations.append({"file": str(report_path), "phrase": "non-authentic record flag"})
    script_path = ROOT / "docs" / "XYLEM_3_TO_4_MINUTE_VIDEO_SCRIPT.md"
    spoken = "\n".join(
        line for line in script_path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    )
    word_count = len(spoken.split())
    if not 420 <= word_count <= 650:
        violations.append({"file": str(script_path), "phrase": f"video script word count {word_count} outside 420–650"})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations}


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
