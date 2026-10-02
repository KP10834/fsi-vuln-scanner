import unittest
from pathlib import Path

from engine.rules.java_spring import JAVA_RULES
from engine.rule_engine import scan_file
from engine.model import Finding

FIX = Path(__file__).parent / "fixtures"


def scan(name: str) -> set[str]:
    findings: list[Finding] = []
    scan_file(FIX / name, FIX, "t", list(JAVA_RULES), findings)
    return {f.rule for f in findings}


class TestJavaRules(unittest.TestCase):
    def test_java_vuln(self):
        rules = scan("java_vuln.java")
        self.assertIn("JAVA-CORS-001", rules)
        self.assertIn("JAVA-SQL-001", rules)
        self.assertIn("JAVA-HASH-001", rules)
        self.assertIn("JAVA-CIPHER-001", rules)

    def test_actuator_yml(self):
        rules = scan("actuator.yml")
        self.assertIn("SEC-005", rules)
        self.assertIn("SEC-006", rules)

    def test_java_safe(self):
        self.assertEqual(scan("java_safe.java"), set())


if __name__ == "__main__":
    unittest.main()
