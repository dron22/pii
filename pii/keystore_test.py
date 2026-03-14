"""Tests for key file encryption and decryption."""

import tempfile
from pathlib import Path

import pytest

from pii.detector import Finding
from pii.keystore import decrypt_keyfile, encrypt_keyfile


def _findings() -> list[Finding]:
    f1 = Finding(type="NAME", value="Lara Meier", page=0, bbox=(10, 10, 100, 20), confidence=0.95, token="[NAME_1]")
    f2 = Finding(type="AHV", value="756.9217.4821.09", page=0, bbox=(10, 30, 150, 40), confidence=0.95, token="[AHV_1]")
    f3 = Finding(
        type="IBAN",
        value="CH44 3199 9123 0000 5512 8",
        page=1,
        bbox=(10, 50, 200, 60),
        confidence=0.9,
        token="[IBAN_1]",
    )
    return [f1, f2, f3]


def test_roundtrip():
    with tempfile.NamedTemporaryFile(suffix=".key.enc", delete=False) as f:
        path = f.name
    encrypt_keyfile(_findings(), "pw123", path)
    key_map = decrypt_keyfile(path, "pw123")
    tokens = key_map["tokens"]
    assert tokens["[NAME_1]"]["value"] == "Lara Meier"
    assert tokens["[AHV_1]"]["value"] == "756.9217.4821.09"
    assert tokens["[IBAN_1]"]["value"] == "CH44 3199 9123 0000 5512 8"


def test_wrong_password_raises():
    with tempfile.NamedTemporaryFile(suffix=".key.enc", delete=False) as f:
        path = f.name
    encrypt_keyfile(_findings(), "correct", path)
    with pytest.raises(ValueError, match="[Ii]ncorrect|corrupted"):
        decrypt_keyfile(path, "wrong")


def test_file_is_not_plaintext():
    with tempfile.NamedTemporaryFile(suffix=".key.enc", delete=False) as f:
        path = f.name
    encrypt_keyfile(_findings(), "any", path)
    raw = Path(path).read_bytes()
    assert b"Lara Meier" not in raw
    assert b"756.9217" not in raw


def test_key_map_has_font_info():
    with tempfile.NamedTemporaryFile(suffix=".key.enc", delete=False) as f:
        path = f.name
    encrypt_keyfile(_findings(), "pw", path)
    key_map = decrypt_keyfile(path, "pw")
    tokens = key_map["tokens"]
    assert "font_name" in tokens["[NAME_1]"]
    assert "font_size" in tokens["[NAME_1]"]
