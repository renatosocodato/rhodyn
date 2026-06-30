import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_stage7_2_benchmark_harness.py"
SPEC = importlib.util.spec_from_file_location("stage7_2", SCRIPT_PATH)
stage7_2 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(stage7_2)


class Stage72BenchmarkHarnessTests(TestCase):
    def test_harness_writes_passing_report_with_all_gates(self):
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "stage7_benchmarks"
            report = stage7_2.write_benchmark_outputs(output_dir)

            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["gates"]["stop_condition_no_added_value_beyond_baselines"]["status"], "not_triggered")
            for name, gate in report["gates"].items():
                if name == "stop_condition_no_added_value_beyond_baselines":
                    continue
                self.assertEqual(gate["status"], "pass", name)

            report_path = output_dir / "stage7_2_benchmark_report.json"
            self.assertTrue(report_path.exists())
            persisted = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(persisted["status"], "pass")
            self.assertIn("not a new biological demonstration", persisted["interpretation_boundary"])

    def test_residence_benchmark_detects_known_amplitude_counterexample(self):
        residence_rows, window_rows = stage7_2.benchmark_residence()
        rhodyn_counterexample = next(
            row
            for row in residence_rows
            if row["case_id"] == "counterexample_amplitude_only" and row["method"] == "RhoDyn_residence_window_sensitivity"
        )
        amplitude_counterexample = next(
            row
            for row in residence_rows
            if row["case_id"] == "counterexample_amplitude_only" and row["method"] == "amplitude_peak_threshold"
        )
        ambiguous = next(row for row in window_rows if row["case_id"] == "ambiguous_window_edge")

        self.assertEqual(rhodyn_counterexample["decision"], "not_residence")
        self.assertEqual(rhodyn_counterexample["correct"], 1)
        self.assertEqual(amplitude_counterexample["decision"], "residence_supported")
        self.assertEqual(amplitude_counterexample["correct"], 0)
        self.assertEqual(ambiguous["decision"], "inconclusive")
        self.assertGreater(ambiguous["qualifying_window_count"], 0)
        self.assertLess(ambiguous["qualifying_window_count"], ambiguous["window_count"])

    def test_coupling_model_and_reserve_benchmarks_keep_ambiguous_cases_bounded(self):
        coupling_rows, margin_rows = stage7_2.benchmark_coupling()
        model_rows = stage7_2.benchmark_models()
        reserve_rows = stage7_2.benchmark_reserve()

        coupling_ambiguous = next(
            row
            for row in coupling_rows
            if row["case_id"] == "ambiguous_margin_crossing" and row["method"] == "RhoDyn_interval_plus_rope"
        )
        model_ambiguous = next(
            row
            for row in model_rows
            if row["case_id"] == "ambiguous_close_fit" and row["method"] == "RhoDyn_reduced_architecture_ranking"
        )
        reserve_ambiguous = next(
            row
            for row in reserve_rows
            if row["case_id"] == "ambiguous_midreserve" and row["method"] == "RhoDyn_reserve_coordinate"
        )

        self.assertEqual(coupling_ambiguous["decision"], "inconclusive")
        self.assertEqual(coupling_ambiguous["correct"], 1)
        self.assertEqual(model_ambiguous["decision"], "inconclusive")
        self.assertEqual(model_ambiguous["correct"], 1)
        self.assertEqual(reserve_ambiguous["decision"], "inconclusive")
        self.assertEqual(reserve_ambiguous["correct"], 1)
        self.assertGreaterEqual(len(margin_rows), 21)

    def test_public_fixtures_performance_and_failure_behavior_are_reported(self):
        public_rows = stage7_2.summarize_public_fixtures()
        performance_rows = stage7_2.benchmark_performance()
        with TemporaryDirectory() as tmpdir:
            failure_rows = stage7_2.benchmark_failure_behavior(Path(tmpdir) / "stage7_benchmarks")

        fixture_names = {row["fixture"] for row in public_rows}
        self.assertIn("drg_calcium", fixture_names)
        self.assertIn("erk_gpcr", fixture_names)
        self.assertIn("cell_painting_mitotox", fixture_names)
        self.assertIn("erk_akt_bounded_coupling", fixture_names)
        self.assertTrue(any(int(row.get("disagreement_count", 0) or 0) > 0 for row in public_rows))
        self.assertEqual({row["n_traces"] for row in performance_rows}, {10, 100, 1000})
        self.assertEqual(failure_rows[0]["decision"], "rejected_invalid_input")
        self.assertEqual(failure_rows[0]["correct"], 1)
