import json
import subprocess
import sys
from unittest import TestCase


class ExampleWorkflowTests(TestCase):
    def test_notebook_style_workflow_runs(self):
        result = subprocess.run(
            [sys.executable, "examples/residence_reserve_workflow.py"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("Residence workflow", result.stdout)
        self.assertIn("Reserve workflow", result.stdout)
        self.assertIn("Bounded-coupling workflow", result.stdout)
        self.assertIn("Reduced-model workflow", result.stdout)
        self.assertIn("model-derived summaries", result.stdout)

    def test_reserve_example_validates(self):
        result = subprocess.run(
            [sys.executable, "-m", "rhodyn.cli", "validate", "examples/synthetic_reserve.csv", "--kind", "reserve"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["rows"], 12)

    def test_coupling_example_validates(self):
        result = subprocess.run(
            [sys.executable, "-m", "rhodyn.cli", "validate", "examples/synthetic_coupling.csv", "--kind", "coupling"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["rows"], 2)
