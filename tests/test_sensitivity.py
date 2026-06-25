import json
import subprocess
import sys
from unittest import TestCase

from rhodyn.schema import TrajectoryRecord, read_trajectory_csv
from rhodyn.sensitivity import residence_window_grid, score_records_window_sensitivity, score_trace_window_sensitivity


class ResidenceSensitivityTests(TestCase):
    def test_window_grid_filters_invalid_windows(self):
        windows = residence_window_grid(low_min=0.2, low_max=0.6, high_min=0.5, high_max=0.8, steps=3)
        self.assertTrue(all(window.low < window.high for window in windows))
        self.assertGreater(len(windows), 0)

    def test_trace_sensitivity_exposes_residence_amplitude_disagreement(self):
        records = [
            TrajectoryRecord("low_residence_high_amp", 0, "perturbed", 0.1),
            TrajectoryRecord("low_residence_high_amp", 1, "perturbed", 0.9),
            TrajectoryRecord("low_residence_high_amp", 2, "perturbed", 0.1),
            TrajectoryRecord("low_residence_high_amp", 3, "perturbed", 0.9),
        ]
        windows = residence_window_grid(low_min=0.35, low_max=0.45, high_min=0.55, high_max=0.65, steps=2)
        curve = score_trace_window_sensitivity(records, windows, min_residence_fraction=0.25)

        self.assertGreater(curve.points[0].max_signal, 0.8)
        self.assertEqual(curve.qualifying_window_count, 0)
        self.assertTrue(all(point.residence_fraction == 0.0 for point in curve.points))

    def test_records_sensitivity_scores_all_trajectories(self):
        rows, issues = read_trajectory_csv("examples/synthetic_trajectory.csv")
        self.assertEqual(issues, [])
        windows = residence_window_grid(low_min=0.3, low_max=0.4, high_min=0.6, high_max=0.8, steps=2)
        curves = score_records_window_sensitivity(rows, windows, min_residence_fraction=0.25)

        self.assertEqual(len(curves), 3)
        self.assertTrue(all(curve.provenance.schema_kind == "trajectory" for curve in curves))

    def test_cli_sensitivity_outputs_curves(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "rhodyn.cli",
                "sensitivity",
                "examples/synthetic_trajectory.csv",
                "--low-min",
                "0.3",
                "--low-max",
                "0.4",
                "--high-min",
                "0.6",
                "--high-max",
                "0.8",
                "--steps",
                "2",
                "--min-residence-fraction",
                "0.25",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(len(payload["curves"]), 3)
        self.assertGreater(payload["window_count"], 0)
