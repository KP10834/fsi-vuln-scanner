from __future__ import annotations

from dataclasses import dataclass

SEVERITY_ORDER = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


def severity_rank(severity: str) -> int:
    if severity not in SEVERITY_ORDER:
        raise ValueError(f"unknown severity: {severity!r}")
    return SEVERITY_ORDER[severity]


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    target: str
    path: str
    line: int
    message: str
    evidence: str
    recommendation: str
