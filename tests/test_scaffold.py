import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
SKILL = ROOT / "skills" / "check" / "SKILL.md"


class ScaffoldTests(unittest.TestCase):
    def test_plugin_manifest_exists_and_is_valid(self) -> None:
        self.assertTrue(MANIFEST.is_file())

        data = json.loads(MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual(data["name"], "check")
        self.assertEqual(data["version"], "0.1.0")
        self.assertEqual(data["skills"], "./skills/")
        self.assertTrue(data["description"].strip())

    def test_check_skill_exists(self) -> None:
        self.assertTrue(SKILL.is_file())

        text = SKILL.read_text(encoding="utf-8")

        self.assertIn("name: check", text)
        self.assertIn("description:", text)
        for relative in (
            "skills/check/references/contract.md",
            "skills/check/references/verdicts.md",
            "skills/check/references/report-format.md",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
