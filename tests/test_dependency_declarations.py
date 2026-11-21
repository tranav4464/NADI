"""Regression checks for dependencies exercised by canonical/audit workflows."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_excel_reader_is_declared_in_project_and_lockfile() -> None:
    """The EPA workbook audit uses pandas.read_excel and therefore openpyxl."""
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    lockfile = (ROOT / "requirements-lock.txt").read_text(encoding="utf-8")
    assert '"openpyxl==3.1.5"' in project
    assert "openpyxl==3.1.5" in lockfile
