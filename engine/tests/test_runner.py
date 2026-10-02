import unittest
from pathlib import Path
import tempfile

from engine.runner import scan_targets


class TestRunner(unittest.TestCase):
    def test_scan_targets_collects_findings_per_target(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            t1 = root / "proj1"; (t1 / "src").mkdir(parents=True)
            (t1 / "src" / "A.go").write_text(
                'q := fmt.Sprintf("SELECT * FROM u WHERE id = %s", id)\n', encoding="utf-8")
            result = scan_targets([t1])
            self.assertEqual(result["summary"]["targetsScanned"], 1)
            rules = {f.rule for f in result["findings"]}
            self.assertIn("GO-SQL-001", rules)

    def test_missing_target_is_skipped_with_warning(self):
        result = scan_targets([Path("C:/no/such/path/xyz")])
        self.assertEqual(result["findings"], [])
        self.assertTrue(result["warnings"])


if __name__ == "__main__":
    unittest.main()
