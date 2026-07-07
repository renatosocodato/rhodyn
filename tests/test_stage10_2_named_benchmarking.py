import csv
import importlib.util
import json
from pathlib import Path
from unittest import TestCase

from rhodyn.named_baselines import named_baseline_decisions, trajectory_features


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_stage10_2_named_benchmarking.py"
SPEC = importlib.util.spec_from_file_location("stage10_2", SCRIPT_PATH)
stage10_2 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(stage10_2)


class Stage102NamedBenchmarkingTests(TestCase):
    def test_named_baselines_cover_expected_families(self):
        case = stage10_2.synthetic_named_benchmark_cases(n_per_regime=1)[0]
        features = trajectory_features(str(case["case_id"]), case["records"])
        families = {decision.method_family for decision in named_baseline_decisions(features)}
        self.assertIn("internal_simple_summary", families)
        self.assertIn("scipy_signal_peak_detection", families)
        self.assertIn("catch22_feature_family", families)
        self.assertIn("tsfresh_feature_family", families)
        self.assertIn("rocket_interval_kernel_family", families)
        self.assertIn("ruptures_changepoint_family", families)
        self.assertIn("hmmlearn_gaussian_hmm_family", families)

    def test_synthetic_named_benchmark_preserves_rhodyn_truth_and_named_rows(self):
        rows = stage10_2.evaluate_synthetic_named_baselines()
        rhodyn_rows = [row for row in rows if row["method_family"] == "rhodyn_method_object"]
        self.assertEqual(len(rhodyn_rows), 36)
        self.assertTrue(all(int(row["correct"]) == 1 for row in rhodyn_rows))
        self.assertTrue(
            any(
                row["method_family"] == "internal_simple_summary"
                and row["method"] == "peak_amplitude"
                and row["regime"] == "amplitude_regime"
                and row["call"] == "baseline_or_amplitude_sufficient"
                for row in rows
            )
        )
        self.assertGreaterEqual(
            len({row["method_family"] for row in rows if row["method_family"] not in {"rhodyn_method_object", "internal_simple_summary"}}),
            5,
        )

    def test_stage10_2_runner_writes_passing_named_benchmark_report(self):
        report = stage10_2.write_stage10_2_outputs(ROOT / "case_studies" / "stage10_named_benchmarks")
        self.assertEqual(report["status"], "pass")
        self.assertTrue(all(report["gates"].values()))
        self.assertGreaterEqual(report["summary_metrics"]["named_external_family_count"], 5)

        report_path = ROOT / "case_studies" / "stage10_named_benchmarks" / "stage10_2_named_benchmark_report.json"
        self.assertTrue(report_path.exists())
        persisted = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["status"], "pass")

        with (ROOT / "case_studies" / "stage10_named_benchmarks" / "stage10_2_synthetic_named_baseline_benchmark.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            benchmark_rows = list(csv.DictReader(handle))
        self.assertEqual(len(benchmark_rows), 468)
        with (ROOT / "case_studies" / "stage10_named_benchmarks" / "stage10_2_public_input_named_baseline_summary.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            public_rows = list(csv.DictReader(handle))
        self.assertEqual({row["dataset"] for row in public_rows}, {"drg_calcium", "erk_gpcr"})
        self.assertTrue((ROOT / "docs" / "stage10_2_named_benchmarking.md").exists())
