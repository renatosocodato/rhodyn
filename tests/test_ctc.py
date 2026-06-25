import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase

from rhodyn.ctc import (
    ctc_features_to_trajectory_records,
    ctc_lineage_coverage_issues,
    read_ctc_feature_csv,
    read_ctc_lineage,
)
from rhodyn.schema import read_trajectory_csv


class CtcAdapterTests(TestCase):
    def test_read_ctc_lineage_and_features(self):
        lineage, lineage_issues = read_ctc_lineage("examples/mlci_man_track.txt")
        features, feature_issues = read_ctc_feature_csv("examples/mlci_ctc_features.csv")

        self.assertEqual(lineage_issues, [])
        self.assertEqual(feature_issues, [])
        self.assertEqual(len(lineage), 2)
        self.assertEqual(len(features), 6)
        self.assertEqual(ctc_lineage_coverage_issues(features, lineage), [])

    def test_convert_ctc_features_to_speed_trajectory(self):
        features, issues = read_ctc_feature_csv("examples/mlci_ctc_features.csv")
        self.assertEqual(issues, [])
        records = ctc_features_to_trajectory_records(
            features,
            signal="speed",
            condition="mlci_fixture",
            replicate="schema_fixture",
        )

        self.assertEqual(len(records), 6)
        track_1 = [record.signal for record in records if record.cell_id == "track_1"]
        track_2 = [record.signal for record in records if record.cell_id == "track_2"]
        self.assertEqual(track_1, [0.0, 5.0, 5.0])
        self.assertEqual(track_2, [0.0, 3.0, 4.0])
        self.assertTrue(all(record.condition == "mlci_fixture" for record in records))

    def test_cli_ctc_to_trajectory_writes_valid_trajectory_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "trajectory.csv"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "rhodyn.cli",
                    "ctc-to-trajectory",
                    "examples/mlci_ctc_features.csv",
                    "--lineage",
                    "examples/mlci_man_track.txt",
                    "--signal",
                    "speed",
                    "--condition",
                    "mlci_fixture",
                    "--replicate",
                    "schema_fixture",
                    "--output",
                    str(output),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(result.stdout)
            rows, issues = read_trajectory_csv(output)

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["trajectory_rows"], 6)
        self.assertEqual(issues, [])
        self.assertEqual(len(rows), 6)

    def test_public_case_study_workflow_runs(self):
        result = subprocess.run(
            [sys.executable, "examples/mlci_public_case_study_workflow.py"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(result.stdout)

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["trajectory_rows"], 6)
        self.assertIn("fixture validates workflow only", payload["interpretation_boundary"])
        self.assertIn(payload["plot_status"], {"matplotlib_not_installed", "plot_constructed_without_display"})
