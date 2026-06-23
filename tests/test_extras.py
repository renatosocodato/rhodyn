import json
import subprocess
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from rhodyn.extras import MissingOptionalDependency, extra_plan, require_extra


class OptionalExtrasTests(TestCase):
    def test_pyproject_declares_optional_extras_without_core_dependencies(self):
        text = Path("pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("dependencies = []", text)
        self.assertIn("[project.optional-dependencies]", text)
        self.assertIn("pandas = [", text)
        self.assertIn("stats = [", text)
        self.assertIn("plots = [", text)
        self.assertIn("notebooks = [", text)
        self.assertIn("all = [", text)

    def test_extra_plan_names_first_use_groups(self):
        extras = {item.name: item for item in extra_plan()}
        self.assertIn("pandas", extras)
        self.assertIn("TOST", " ".join(extras["stats"].first_uses))
        self.assertIn("margin-sensitivity curves", extras["plots"].first_uses)

    def test_missing_extra_message_is_actionable(self):
        with patch("rhodyn.extras.find_spec", return_value=None):
            with self.assertRaises(MissingOptionalDependency) as raised:
                require_extra("notebooks", feature="interactive tutorial rendering")
        message = str(raised.exception)
        self.assertIn("rhodyn[notebooks]", message)
        self.assertIn("interactive tutorial rendering", message)

    def test_cli_extras_reports_optional_dependency_groups(self):
        result = subprocess.run(
            [sys.executable, "-m", "rhodyn.cli", "extras"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        names = {item["name"] for item in payload["extras"]}
        self.assertTrue({"pandas", "stats", "plots", "notebooks"}.issubset(names))
