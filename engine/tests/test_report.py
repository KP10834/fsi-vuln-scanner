import unittest
import json
from pathlib import Path
import tempfile

from engine.model import Finding
from engine.report import build_payload, write_reports


FINDINGS = [
    Finding("CRITICAL", "GO-RAND-001", "Adapter_Go", "a.go", 5, "weak rand", "x", "use crypto/rand"),
    Finding("HIGH", "SEC-005", "BE_Auth", "b.yml", 2, "actuator open", "y", "restrict"),
]


class TestReport(unittest.TestCase):
    def test_payload_counts_and_criteria(self):
        payload = build_payload(FINDINGS, files_scanned=10, targets=["BE_Auth", "Adapter_Go"])
        self.assertEqual(payload["summary"]["CRITICAL"], 1)
        self.assertEqual(payload["summary"]["HIGH"], 1)
        f0 = next(f for f in payload["findings"] if f["rule"] == "GO-RAND-001")
        self.assertEqual(f0["criteria"]["domain"], "시큐어코딩(개발보안)")
        self.assertIn("domainSummary", payload)

    def test_write_reports_creates_self_contained_html(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            write_reports(FINDINGS, 10, ["BE_Auth", "Adapter_Go"], out)
            html = (out / "security-report.html").read_text(encoding="utf-8")
            self.assertNotIn("http://", html)   # no external resources
            self.assertNotIn("https://cdn", html)
            self.assertIn("보안 점검 리포트", html)
            data = json.loads((out / "security-report.json").read_text(encoding="utf-8"))
            self.assertEqual(data["summary"]["CRITICAL"], 1)


if __name__ == "__main__":
    unittest.main()
