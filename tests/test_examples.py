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

    def test_stage5_public_mlci_workflow_validates_and_scores(self):
        validate = subprocess.run(
            [
                sys.executable,
                "-m",
                "rhodyn.cli",
                "validate",
                "examples/mlci_public_intensity_trajectory.csv",
                "--kind",
                "trajectory",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        validate_payload = json.loads(validate.stdout)
        self.assertEqual(validate_payload["status"], "pass")
        self.assertEqual(validate_payload["rows"], 62)

        score = subprocess.run(
            [
                sys.executable,
                "-m",
                "rhodyn.cli",
                "score-residence",
                "examples/mlci_public_intensity_trajectory.csv",
                "--low",
                "13.0",
                "--high",
                "14.5",
                "--signal-column",
                "signal",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        score_payload = json.loads(score.stdout)
        self.assertEqual(score_payload["status"], "pass")
        self.assertGreater(len(score_payload["summaries"]), 5)
        self.assertEqual(score_payload["window"], {"low": 13.0, "high": 14.5})
