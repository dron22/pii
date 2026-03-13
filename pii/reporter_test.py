"""Tests for audit report output."""

import tempfile
from pathlib import Path

from pii.detector import Finding
from pii.reporter import report


def _finding(type_: str, token: str, confidence: float = 0.9) -> Finding:
    f = Finding(type=type_, value="x", page=0, bbox=(0, 0, 1, 1), confidence=confidence)
    f.token = token
    return f


def test_report_stdout(capsys):
    redacted = [_finding("NAME", "[NAME_1]", 0.95), _finding("IBAN", "[IBAN_1]", 0.9)]
    report(redacted, redacted)
    out = capsys.readouterr().out
    assert "NAME" in out
    assert "IBAN" in out
    assert "2" in out  # total detected


def test_report_shows_excluded_count(capsys):
    all_findings = [_finding("NAME", "[NAME_1]"), _finding("IBAN", "[IBAN_1]")]
    redacted = all_findings[:1]  # only NAME redacted
    report(redacted, all_findings)
    out = capsys.readouterr().out
    assert "Excluded" in out


def test_report_writes_to_file():
    findings = [_finding("AHV", "[AHV_1]", 0.95)]
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        path = f.name
    report(findings, findings, report_file=path)
    content = Path(path).read_text()
    assert "AHV" in content
    assert "[AHV_1]" in content
