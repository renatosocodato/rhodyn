import importlib.util
import json
from pathlib import Path
from unittest import TestCase

from rhodyn.compare import rank_model_fits
from rhodyn.coupling import equivalence_from_interval
from rhodyn.method_object import (
    MethodObjectSpec,
    coupling_method_decision,
    reserve_method_decision,
    routed_output_method_decision,
    trajectory_method_decision,
)
from rhodyn.reserve import ff_over_f0, reserve_coordinate
from rhodyn.residence import ResidenceWindow


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_stage10_1_method_object_v2.py"
SPEC = importlib.util.spec_from_file_location("stage10_1", SCRIPT_PATH)
stage10_1 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(stage10_1)

STAGE7_SCRIPT = ROOT / "scripts" / "build_stage7_1_synthetic_truth_cases.py"
STAGE7_SPEC = importlib.util.spec_from_file_location("stage7_truth", STAGE7_SCRIPT)
stage7_truth = importlib.util.module_from_spec(STAGE7_SPEC)
assert STAGE7_SPEC.loader is not None
STAGE7_SPEC.loader.exec_module(stage7_truth)


class Stage101MethodObjectTests(TestCase):
    def test_trajectory_method_object_distinguishes_residence_amplitude_and_abstention(self):
        window = ResidenceWindow(0.35, 0.75)
        calls = {}
        for case_id, (records, uncertainty_width) in stage10_1.trajectory_v2_cases().items():
            calls[case_id] = trajectory_method_decision(
                case_id,
                records,
                window,
                spec=MethodObjectSpec(),
                comparator="peak",
                uncertainty_width=uncertainty_width,
            ).call

        self.assertEqual(calls["trajectory_residence_added"], "residence_added_information")
        self.assertEqual(calls["trajectory_amplitude_sufficient"], "baseline_or_amplitude_sufficient")
        self.assertEqual(calls["trajectory_ambiguous_uncertainty"], "inconclusive")

    def test_coupling_reserve_and_model_calls_include_positive_counterexample_and_ambiguous_cases(self):
        coupling_calls = {}
        for case_id, record in stage7_truth.coupling_truth_cases().items():
            interval = equivalence_from_interval(
                record.estimate,
                record.ci_low,
                record.ci_high,
                record.margin,
                rope_mass=record.rope_mass,
            )
            coupling_calls[case_id] = coupling_method_decision(case_id, interval).call
        self.assertEqual(coupling_calls["positive_equivalent"], "bounded_coupling_within_margin")
        self.assertEqual(coupling_calls["counterexample_shift"], "coupling_shift_exceeds_margin")
        self.assertEqual(coupling_calls["ambiguous_margin_crossing"], "inconclusive")

        reserve_calls = {}
        for case_id, records in stage7_truth.reserve_truth_cases().items():
            normalized = ff_over_f0([record.response for record in records], baseline_points=1)
            value = reserve_coordinate(normalized, floor=1.0, ceiling=2.0)
            reserve_calls[case_id] = reserve_method_decision(case_id, value).call
        self.assertEqual(reserve_calls["positive_buffered"], "reserve_like_buffered")
        self.assertEqual(reserve_calls["counterexample_fragile"], "reserve_like_fragile")
        self.assertEqual(reserve_calls["ambiguous_midreserve"], "inconclusive")

        model_calls = {}
        for case_id, rows in stage7_truth.model_truth_cases().items():
            model_calls[case_id] = routed_output_method_decision(case_id, rank_model_fits(rows)).call
        self.assertEqual(model_calls["positive_routed_best"], "routed_architecture_selected")
        self.assertEqual(model_calls["counterexample_endpoint_sufficient"], "reduced_architecture_selected")
        self.assertEqual(model_calls["ambiguous_close_fit"], "inconclusive")

    def test_stage10_1_runner_writes_passing_method_object_report(self):
        report = stage10_1.write_stage10_1_outputs(ROOT / "case_studies" / "stage10_method_object_v2")
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["decision_count"], 12)
        self.assertTrue(all(report["expectations"].values()))

        report_path = ROOT / "case_studies" / "stage10_method_object_v2" / "stage10_1_method_object_gate_report.json"
        self.assertTrue(report_path.exists())
        persisted = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["status"], "pass")
        self.assertTrue((ROOT / "case_studies" / "stage10_method_object_v2" / "stage10_1_method_object_decisions.csv").exists())
        self.assertTrue((ROOT / "case_studies" / "stage10_method_object_v2" / "stage10_1_method_object_brief.md").exists())
        self.assertTrue((ROOT / "docs" / "stage10_1_api_gap_list.md").exists())
