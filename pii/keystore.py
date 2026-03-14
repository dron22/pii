"""AES-GCM encryption and decryption of the redaction key file."""

import base64
import json
import os
import struct
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from pii.detector import Finding

_PBKDF2_ITERATIONS = 600_000
_SALT_LEN = 16
_NONCE_LEN = 12
_KEY_LEN = 32  # AES-256


def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=_KEY_LEN,
        salt=salt,
        iterations=_PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_keyfile(
    findings: list[Finding],
    password: str,
    output_path: str,
    page_content: dict[int, bytes] | None = None,
) -> None:
    """Build a token→value mapping from findings and write an AES-GCM encrypted key file.

    page_content maps page number → original (decompressed) content stream bytes captured
    before redaction. When present, unredact_pdf can restore the PDF to byte-identical state.
    """
    # Group all occurrences of each token — the same PII value can appear multiple times.
    tokens: dict[str, dict[str, Any]] = {}
    for f in findings:
        if not f.token:
            continue
        if f.token not in tokens:
            tokens[f.token] = {
                "value": f.value,
                "type": f.type,
                "font_name": f.font_name,
                "font_size": f.font_size,
                "occurrences": [],
            }
        tokens[f.token]["occurrences"].append({"page": f.page, "bbox": list(f.bbox)})

    key_map: dict[str, Any] = {"tokens": tokens}

    if page_content:
        # Base64-encode binary content stream bytes for JSON serialisation.
        key_map["page_content"] = {
            str(page_num): base64.b64encode(content).decode("ascii") for page_num, content in page_content.items()
        }

    plaintext = json.dumps(key_map, ensure_ascii=False).encode("utf-8")

    salt = os.urandom(_SALT_LEN)
    nonce = os.urandom(_NONCE_LEN)
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    # File layout: [4-byte version][salt][nonce][ciphertext]
    version = struct.pack(">I", 2)  # version 2: nested format with page_content
    with open(output_path, "wb") as fh:
        fh.write(version + salt + nonce + ciphertext)


def decrypt_keyfile(key_path: str, password: str) -> dict[str, Any]:
    """Decrypt and return the key map from an encrypted key file.

    Raises ValueError on wrong password or corrupted file.
    """
    with open(key_path, "rb") as f:
        data = f.read()

    if len(data) < 4 + _SALT_LEN + _NONCE_LEN + 16:
        raise ValueError("Key file is too short or corrupted.")

    _version = data[:4]
    salt = data[4 : 4 + _SALT_LEN]
    nonce = data[4 + _SALT_LEN : 4 + _SALT_LEN + _NONCE_LEN]
    ciphertext = data[4 + _SALT_LEN + _NONCE_LEN :]

    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception:
        raise ValueError("Incorrect password or corrupted key file.")

    return dict(json.loads(plaintext.decode("utf-8")))
