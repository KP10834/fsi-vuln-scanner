from __future__ import annotations

from pathlib import Path

from engine.model import Finding
from engine.scanner import files_to_scan
from engine.rule_engine import scan_file
from engine.rules.common import COMMON_RULES
from engine.rules.java_spring import JAVA_RULES
from engine.rules.go import GO_RULES

ALL_RULES = [*COMMON_RULES, *JAVA_RULES, *GO_RULES]


def scan_targets(targets: list[Path]) -> dict:
    findings: list[Finding] = []
    warnings: list[str] = []
    files_scanned = 0
    scanned_targets = 0
    for target in targets:
        if not target.exists() or not target.is_dir():
            warnings.append(f"대상 경로를 찾을 수 없어 건너뜀: {target}")
            continue
        scanned_targets += 1
        label = target.name
        paths = files_to_scan(target)
        files_scanned += len(paths)
        for p in paths:
            scan_file(p, target, label, ALL_RULES, findings)
    return {
        "findings": findings,
        "warnings": warnings,
        "filesScanned": files_scanned,
        "targetLabels": [t.name for t in targets if t.exists() and t.is_dir()],
        "summary": {"targetsScanned": scanned_targets},
    }
