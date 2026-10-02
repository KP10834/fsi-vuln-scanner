import unittest

from engine.criteria_map import load_mapping, criteria_for
from engine.rules.common import COMMON_RULES
from engine.rules.java_spring import JAVA_RULES
from engine.rules.go import GO_RULES


class TestCriteria(unittest.TestCase):
    def test_every_rule_has_mapping(self):
        mapping = load_mapping()
        all_ids = [r.rule_id for r in (*COMMON_RULES, *JAVA_RULES, *GO_RULES)]
        missing = [rid for rid in all_ids if rid not in mapping]
        self.assertEqual(missing, [], f"매핑 누락 규칙: {missing}")

    def test_criteria_for_returns_domain(self):
        c = criteria_for("GO-RAND-001")
        self.assertEqual(c["domain"], "시큐어코딩(개발보안)")

    def test_unknown_rule_returns_unmapped(self):
        c = criteria_for("NOPE-999")
        self.assertEqual(c["domain"], "미분류")


if __name__ == "__main__":
    unittest.main()
