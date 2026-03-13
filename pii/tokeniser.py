"""Assign tokens to findings. Same value always gets the same token."""

from pii.detector import Finding


def tokenise(findings: list[Finding], opaque: bool = False) -> list[Finding]:
    """Assign a token to each finding in-place. Returns the same list.

    Same original value always maps to the same token (deduplication).
    In typed mode: [NAME_1], [AHV_1], [IBAN_1], ...
    In opaque mode: [REDACTED_001], [REDACTED_002], ...
    """
    value_to_token: dict[str, str] = {}
    type_counters: dict[str, int] = {}
    opaque_counter = 0

    for finding in findings:
        if finding.value in value_to_token:
            finding.token = value_to_token[finding.value]
            continue

        if opaque:
            opaque_counter += 1
            token = f"[REDACTED_{opaque_counter:03d}]"
        else:
            token_type = finding.type.upper().replace(" ", "_")
            count = type_counters.get(token_type, 0) + 1
            type_counters[token_type] = count
            token = f"[{token_type}_{count}]"

        finding.token = token
        value_to_token[finding.value] = token

    return findings
