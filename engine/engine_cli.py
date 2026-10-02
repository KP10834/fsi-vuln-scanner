from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from engine.runner import scan_targets
from engine.report import write_reports
from engine.model import severity_rank, SEVERITY_ORDER


def emit(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main() -> int:
    ap = argparse.ArgumentParser(description="FSI 취약점 분석 엔진")
    ap.add_argument("--targets", required=True, help="콤마로 구분한 대상 폴더 경로")
    ap.add_argument("--fail-on", choices=SEVERITY_ORDER, default="CRITICAL")
    ap.add_argument("--output-dir", type=Path, default=Path("out"))
    ap.add_argument("--format", choices=["json", "text"], default="json")
    args = ap.parse_args()

    targets = [Path(p.strip()) for p in args.targets.split(",") if p.strip()]
    result = scan_targets(targets)
    for w in result["warnings"]:
        emit({"type": "warning", "message": w})
    payload = write_reports(
        result["findings"], result["filesScanned"], result["targetLabels"], args.output_dir)
    payload["reportPath"] = str((args.output_dir / "security-report.html").resolve())
    if args.format == "json":
        emit({"type": "result", **payload})
    else:
        print(f"findings={len(result['findings'])} report={payload['reportPath']}")
    threshold = severity_rank(args.fail_on)
    return 1 if any(severity_rank(f.severity) >= threshold for f in result["findings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
