import importlib.util
import json
from pathlib import Path
from unittest import TestCase

from rhodyn.compare import rank_model_fits
from rhodyn.coupling import equivalence_from_interval
from rhodyn.reserve import ff_over_f0, reserve_coordinate
from rhodyn.residence import ResidenceWindow, score_trace
from rhodyn.sensitivity import residence_window_grid, score_trace_window_sensitivity
from rhodyn.sim import first_passage_time
from rhodyn.uncertainty import bootstrap_interval

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "build_stage7_1_synthetic_truth_cases.py"
SPEC = importlib.util.spec_from_file_location("stage7_truth", SCRIPT_PATH)
stage7_truth = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(stage7_truth)


class Stage71SyntheticTruthTests(TestCase):
    def test_residence_positive_counterexample_and_ambiguous_cases(self):
        cases = stage7_truth.residence_truth_cases()
        window = ResidenceWindow(0.35, 0.75)
        positive = score_trace(cases["positive_residence"], window)
        counterexample = score_trace(cases["counterexample_amplitude_only"], window)
        ambiguous = score_trace(cases["ambiguous_window_edge"], window)

        self.assertGreater(positive.residence_fraction, 0.50)
        self.assertLess(counterexample.residence_fraction, 0.30)
        self.assertGreater(counterexample.max_signal, 0.90)
        self.assertGreater(ambiguous.residence_fraction, 0.0)

        windows = residence_window_grid(low_min=0.30, low_max=0.40, high_min=0.70, high_max=0.80, steps=3)
        sensitivity = score_trace_window_sensitivity(cases["ambiguous_window_edge"], windows, min_residence_fraction=0.45)
        self.assertGreater(sensitivity.qualifying_window_count, 0)
        self.assertLess(sensitivity.qualifying_window_count, len(sensitivity.points))

    def test_reserve_truth_cases_keep_buffered_and_fragile_regimes_apart(self):
        cases = stage7_truth.reserve_truth_cases()
        buffered = [record.response for record in cases["positive_buffered"]]
        fragile = [record.response for record in cases["counterexample_fragile"]]
        buffered_reserve = reserve_coordinate(ff_over_f0(buffered, baseline_points=1), floor=1.0, ceiling=2.0)
        fragile_reserve = reserve_coordinate(ff_over_f0(fragile, baseline_points=1), floor=1.0, ceiling=2.0)
        self.assertGreater(buffered_reserve, 0.85)
        self.assertLess(fragile_reserve, 0.20)

    def test_coupling_truth_cases_pass_only_when_interval_and_rope_are_inside_margin(self):
        decisions = {}
        for name, record in stage7_truth.coupling_truth_cases().items():
            decisions[name] = equivalence_from_interval(
                record.estimate,
                record.ci_low,
                record.ci_high,
                record.margin,
                rope_mass=record.rope_mass,
            )
        self.assertTrue(decisions["positive_equivalent"].passes)
        self.assertFalse(decisions["counterexample_shift"].passes)
        self.assertFalse(decisions["ambiguous_margin_crossing"].passes)

    def test_model_comparison_truth_cases_have_expected_best_models(self):
        cases = stage7_truth.model_truth_cases()
        self.assertEqual(rank_model_fits(cases["positive_routed_best"])[0].model, "routed")
        self.assertEqual(rank_model_fits(cases["counterexample_endpoint_sufficient"])[0].model, "endpoint_only")

    def test_uncertainty_and_timing_truth_cases_include_ambiguous_or_no_crossing_regimes(self):
        cases = stage7_truth.uncertainty_truth_cases()
        stable = bootstrap_interval(cases["positive_stable"], n_resamples=200, seed=7, confidence_level=0.90).interval
        broad = bootstrap_interval(cases["ambiguous_broad"], n_resamples=200, seed=7, confidence_level=0.90).interval
        self.assertGreater(broad.upper - broad.lower, stable.upper - stable.lower)

        self.assertEqual(first_passage_time([0, 1, 2, 3], [0.1, 0.2, 0.8, 0.9], 0.75), 2)
        self.assertIsNone(first_passage_time([0, 1, 2, 3], [0.1, 0.2, 0.3, 0.4], 0.75))

    def test_generator_writes_passing_report_and_fixture_tables(self):
        report = stage7_truth.write_truth_cases(ROOT / "case_studies" / "stage7_synthetic_truth")
        self.assertEqual(report["status"], "pass")
        report_path = ROOT / "case_studies" / "stage7_synthetic_truth" / "stage7_1_synthetic_truth_report.json"
        self.assertTrue(report_path.exists())
        persisted = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["status"], "pass")
        self.assertTrue((ROOT / "case_studies" / "stage7_synthetic_truth" / "trajectory_positive_residence.csv").exists())
        self.assertTrue((ROOT / "case_studies" / "stage7_synthetic_truth" / "endpoint_positive_routed_best.csv").exists())
