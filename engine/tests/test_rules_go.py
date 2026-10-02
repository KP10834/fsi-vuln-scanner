import unittest
from pathlib import Path

from engine.rules.go import GO_RULES
from engine.rule_engine import scan_file
from engine.model import Finding

FIX = Path(__file__).parent / "fixtures"


def scan(name: str) -> set[str]:
    findings: list[Finding] = []
    scan_file(FIX / name, FIX, "t", list(GO_RULES), findings)
    return {f.rule for f in findings}


class TestGoRules(unittest.TestCase):
    def test_go_vuln(self):
        rules = scan("go_vuln.go")
        self.assertIn("GO-SQL-001", rules)
        self.assertIn("GO-EXEC-001", rules)
        self.assertIn("GO-RAND-001", rules)
        self.assertIn("GO-TLS-001", rules)
        self.assertIn("GO-HTTP-001", rules)

    def test_go_safe(self):
        self.assertEqual(scan("go_safe.go"), set())


if __name__ == "__main__":
    unittest.main()
