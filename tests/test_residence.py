from unittest import TestCase

from rhodyn.residence import ResidenceWindow, score_records, score_trace
from rhodyn.schema import TrajectoryRecord, read_trajectory_csv


class ResidenceTests(TestCase):
    def test_score_trace_residence_fraction(self):
        records = [
            TrajectoryRecord("a", 0, "control", 0.2),
            TrajectoryRecord("a", 1, "control", 0.5),
            TrajectoryRecord("a", 2, "control", 0.6),
            TrajectoryRecord("a", 3, "control", 0.9),
        ]
        summary = score_trace(records, ResidenceWindow(0.35, 0.75))
        self.assertAlmostEqual(summary.residence_fraction, 2 / 3)
        self.assertEqual(summary.n_points, 4)
        self.assertEqual(len(summary.segments), 1)

    def test_read_and_score_example(self):
        rows, issues = read_trajectory_csv("examples/synthetic_trajectory.csv")
        self.assertEqual(issues, [])
        summaries = score_records(rows, ResidenceWindow(0.35, 0.75))
        self.assertEqual(len(summaries), 3)
        self.assertTrue(any(item.condition == "perturbed" for item in summaries))

