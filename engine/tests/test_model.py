import dataclasses
import unittest
from engine.model import Finding, SEVERITY_ORDER, severity_rank


class TestModel(unittest.TestCase):
    def test_severity_order_has_five_levels(self):
        self.assertEqual(
            set(SEVERITY_ORDER),
            {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"},
        )

    def test_severity_rank_orders_critical_highest(self):
        self.assertGreater(severity_rank("CRITICAL"), severity_rank("HIGH"))
        self.assertGreater(severity_rank("HIGH"), severity_rank("MEDIUM"))

    def test_finding_is_frozen_dataclass(self):
        f = Finding("HIGH", "SEC-002", "auth", "a.java", 3, "msg", "ev", "fix")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            f.severity = "LOW"  # type: ignore


if __name__ == "__main__":
    unittest.main()
