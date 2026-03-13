"""Audit summary report."""

from typing import Optional

from pii.detector import Finding


def report(
    redacted: list[Finding],
    all_findings: list[Finding],
    report_file: Optional[str] = None,
) -> None:
    """Write an audit summary to stdout or a file."""
    excluded = len(all_findings) - len(redacted)
    lines = [
        "--- Audit Report ---",
        f"Total detected:  {len(all_findings)}",
        f"Redacted:        {len(redacted)}",
        f"Excluded:        {excluded}",
        "",
        f"  {'Type':<14} {'Token':<18} {'Confidence':>10}",
        f"  {'-' * 14} {'-' * 18} {'-' * 10}",
    ]
    for f in redacted:
        lines.append(f"  {f.type:<14} {f.token or '—':<18} {f.confidence:>9.0%}")

    output = "\n".join(lines) + "\n"

    if report_file:
        with open(report_file, "w", encoding="utf-8") as fh:
            fh.write(output)
    else:
        print(output)
