import unittest
from pathlib import Path
import tempfile

from engine.rule_engine import Rule, scan_file
from engine.model import Finding


SAMPLE_RULE = Rule(
    rule_id="T-001",
    severity="HIGH",
    pattern=r"FORBIDDEN",
    message="forbidden token found",
    recommendation="remove it",
    rulesets=("common",),
    documentation_safe=False,
)


class TestRuleEngine(unittest.TestCase):
    def test_scan_file_matches_rule(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.go"
            p.write_text("ok\nFORBIDDEN here\n", encoding="utf-8")
            findings: list[Finding] = []
            scan_file(p, Path(d), "tgt", [SAMPLE_RULE], findings)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].rule, "T-001")
            self.assertEqual(findings[0].line, 2)

    def test_documentation_safe_false_skips_markdown(self):
        md_rule = Rule("D", "LOW", r"SECRETWORD", "m", "r", ("common",), False)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.md"
            p.write_text("SECRETWORD\n", encoding="utf-8")
            findings: list[Finding] = []
            scan_file(p, Path(d), "tgt", [md_rule], findings)
            self.assertEqual(findings, [])

    def test_rule_not_applied_outside_its_ruleset(self):
        go_only = Rule("G", "LOW", r"X", "m", "r", ("go",), False)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.md"  # md -> common only
            p.write_text("X\n", encoding="utf-8")
            findings: list[Finding] = []
            scan_file(p, Path(d), "tgt", [go_only], findings)
            self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
