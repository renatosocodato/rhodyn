from unittest import TestCase

from rhodyn.compare import rank_model_fits
from rhodyn.models import simulate_controller
from rhodyn.schema import read_endpoint_csv
from rhodyn.sim import Reaction, first_passage_time, gillespie, tau_leap


class ModelSimCompareTests(TestCase):
    def test_controller_simulation(self):
        rows = simulate_controller(duration=2, dt=1)
        self.assertEqual(len(rows), 3)
        self.assertIn("window_gate", rows[0])
        self.assertTrue(all(0 <= row["reserve"] <= 1 for row in rows))

    def test_first_passage(self):
        self.assertEqual(first_passage_time([0, 1, 2], [0.1, 0.4, 0.8], 0.5), 2)
        self.assertIsNone(first_passage_time([0, 1], [0.1, 0.2], 0.5))

    def test_stochastic_helpers(self):
        reactions = [Reaction("birth", {"x": 1}, lambda state: 1.0)]
        ssa = gillespie({"x": 0}, reactions, duration=1, seed=1)
        leap = tau_leap({"x": 0}, reactions, duration=1, tau=0.5, seed=1)
        self.assertGreaterEqual(len(ssa), 1)
        self.assertEqual(len(leap), 3)

    def test_compare_synthetic_models(self):
        rows, issues = read_endpoint_csv("examples/synthetic_endpoints.csv")
        self.assertEqual(issues, [])
        fits = rank_model_fits(rows)
        self.assertEqual(fits[0].model, "residence_gated")

