"""Tests for token assignment and deduplication."""

from pii.detector import Finding
from pii.tokeniser import tokenise


def _finding(type_: str, value: str) -> Finding:
    return Finding(type=type_, value=value, page=0, bbox=(0, 0, 10, 10), confidence=0.9)


def test_typed_tokens_have_correct_format():
    findings = [_finding("NAME", "Lara Meier"), _finding("IBAN", "CH44 3199")]
    tokenise(findings)
    assert findings[0].token == "[NAME_1]"
    assert findings[1].token == "[IBAN_1]"


def test_typed_token_counter_per_type():
    findings = [
        _finding("NAME", "Lara Meier"),
        _finding("NAME", "Marco Bianchi"),
        _finding("IBAN", "CH44 3199"),
    ]
    tokenise(findings)
    assert findings[0].token == "[NAME_1]"
    assert findings[1].token == "[NAME_2]"
    assert findings[2].token == "[IBAN_1]"


def test_same_value_gets_same_token():
    findings = [
        _finding("NAME", "Lara Meier"),
        _finding("NAME", "Lara Meier"),  # duplicate value
    ]
    tokenise(findings)
    assert findings[0].token == findings[1].token == "[NAME_1]"


def test_opaque_tokens_format():
    findings = [_finding("NAME", "Lara Meier"), _finding("AHV", "756.1234")]
    tokenise(findings, opaque=True)
    assert findings[0].token == "[REDACTED_001]"
    assert findings[1].token == "[REDACTED_002]"


def test_opaque_deduplication():
    findings = [
        _finding("NAME", "Lara Meier"),
        _finding("NAME", "Lara Meier"),  # same value
    ]
    tokenise(findings, opaque=True)
    # Same value must get same opaque token
    assert findings[0].token == findings[1].token


def test_empty_findings_returns_empty():
    result = tokenise([])
    assert result == []
