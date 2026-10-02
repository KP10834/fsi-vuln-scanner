import unittest
from pathlib import Path
import tempfile

from engine.scanner import files_to_scan, masked, rulesets_for


class TestScanner(unittest.TestCase):
    def test_skips_build_and_git_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir()
            (root / "build").mkdir()
            (root / ".git").mkdir()
            (root / "src" / "A.java").write_text("class A {}", encoding="utf-8")
            (root / "build" / "B.java").write_text("x", encoding="utf-8")
            (root / ".git" / "C.java").write_text("x", encoding="utf-8")
            found = {p.name for p in files_to_scan(root)}
            self.assertEqual(found, {"A.java"})

    def test_masked_hides_secret_value(self):
        self.assertNotIn("supersecret", masked('password = "supersecret"'))

    def test_masked_hides_quoted_value_with_spaces(self):
        out = masked('password = "value with space"')
        self.assertNotIn("value with space", out)
        self.assertIn("***", out)

    def test_rulesets_select_by_extension(self):
        self.assertEqual(rulesets_for(Path("x.go")), ("common", "go"))
        self.assertEqual(rulesets_for(Path("x.java")), ("common", "java_spring"))
        self.assertEqual(rulesets_for(Path("x.yml")), ("common", "java_spring"))
        self.assertEqual(rulesets_for(Path("x.md")), ("common",))


if __name__ == "__main__":
    unittest.main()
