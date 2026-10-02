from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from engine.model import Finding
from engine.scanner import DOC_EXTS, masked, rulesets_for


@dataclass(frozen=True)
class Rule:
    rule_id: str
    severity: str
    pattern: str
    message: str
    recommendation: str
    rulesets: tuple[str, ...]
    documentation_safe: bool  # True면 문서 파일에서도 적용(개인키 등)


def scan_file(
    path: Path,
    root: Path,
    target: str,
    rules: list[Rule],
    findings: list[Finding],
) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    active = set(rulesets_for(path))
    is_doc = path.suffix.lower() in DOC_EXTS
    applicable = [
        r for r in rules
        if active.intersection(r.rulesets) and (r.documentation_safe or not is_doc)
    ]
    if not applicable:
        return
    rel = str(path.relative_to(root))
    compiled = [(re.compile(rule.pattern), rule) for rule in applicable]
    for line_no, line in enumerate(text.splitlines(), 1):
        for rx, rule in compiled:
            if rx.search(line):
                findings.append(Finding(
                    rule.severity, rule.rule_id, target, rel, line_no,
                    rule.message, masked(line), rule.recommendation,
                ))
