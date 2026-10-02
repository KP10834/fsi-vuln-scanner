import unittest
from pathlib import Path

from engine.rules.common import COMMON_RULES
from engine.rule_engine import scan_file
from engine.model import Finding

FIX = Path(__file__).parent / "fixtures"


def scan(name: str) -> list[Finding]:
    findings: list[Finding] = []
    # .txt -> common ruleset only; copy fixture content into a .java for doc_safe parity
    scan_file(FIX / name, FIX, "t", list(COMMON_RULES), findings)
    return findings


class TestCommonRules(unittest.TestCase):
    def test_vuln_fixture_triggers_expected_rules(self):
        rules = {f.rule for f in scan("common_vuln.txt")}
        self.assertIn("SEC-001", rules)  # private key
        self.assertIn("SEC-002", rules)  # api key
        self.assertIn("SEC-003", rules)  # hardcoded secret
        self.assertIn("SEC-004", rules)  # sensitive logging
        self.assertIn("SEC-007", rules)  # wildcard CORS

    def test_safe_fixture_has_no_findings(self):
        self.assertEqual(scan("common_safe.txt"), [])


if __name__ == "__main__":
    unittest.main()
