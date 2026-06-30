import csv
import json
from pathlib import Path
from unittest import TestCase

from rhodyn.schema import read_coupling_csv, read_trajectory_csv


STAGE7_5 = Path("case_studies/stage7_heldout_validation")


class Stage75HeldoutValidationTests(TestCase):
    def test_gate_report_passes_with_mixed_heldout_outcomes(self):
        gate = json.loads((STAGE7_5 / "stage7_5_heldout_validation_gate_report.json").read_text(encoding="utf-8"))
        self.assertEqual(gate["status"], "pass")
        self.assertEqual(gate["completion_state"], "complete_external_heldout_validation")
        self.assertEqual(gate["pass_context_count"], 4)
        self.assertEqual(gate["fail_context_count"], 0)
        self.assertEqual(gate["inconclusive_context_count"], 3)
        checkpoints = gate["validation_checkpoints"]
        for key in [
            "stage7_3_and_7_4_prerequisites_complete",
            "heldout_analysis_plan_fixed_before_outputs",
            "public_access_reviewable",
            "schema_validation_tidy_trajectories",
            "schema_validation_coupling_rows",
            "fixed_windows_margins_baselines_grouping_recorded",
            "no_hidden_tuning_after_result",
            "pass_fail_inconclusive_outcomes_visible",
            "controlled_access_constraints_documented",
            "evidence_set_decision_recorded",
        ]:
            self.assertEqual(checkpoints[key], "pass", key)
        self.assertEqual(gate["stop_condition_access_restriction"], "not_triggered")
        self.assertIn("inconclusive contexts", gate["interpretation_boundary"])

    def test_plan_records_fixed_thresholds_margin_and_grouping(self):
        plan = json.loads((STAGE7_5 / "heldout_analysis_plan.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["primary_margin"], 0.20)
        self.assertEqual(plan["alpha"], 0.05)
        self.assertEqual(plan["fixed_thresholds"], {"erk": 0.7623, "akt": 0.5892})
        self.assertEqual(plan["selection_rule"]["max_cells_per_ligand_inhibitor_experiment"], 20)
        self.assertIn("no hidden", plan["no_hidden_tuning_rule"].lower())
        self.assertEqual(len(plan["heldout_contexts"]), 7)

    def test_tidy_trajectory_and_coupling_tables_validate(self):
        trajectories, trajectory_issues = read_trajectory_csv(STAGE7_5 / "heldout_paired_reporter_tidy_trajectories.csv")
        coupling, coupling_issues = read_coupling_csv(STAGE7_5 / "heldout_bounded_coupling_decisions.csv")
        self.assertEqual(trajectory_issues, [])
        self.assertEqual(coupling_issues, [])
        self.assertEqual(len(trajectories), 21120)
        self.assertEqual(len(coupling), 7)

    def test_bounded_coupling_passes_are_context_limited(self):
        with (STAGE7_5 / "heldout_bounded_coupling_decisions.csv").open(newline="", encoding="utf-8") as handle:
            rows = {row["contrast"]: row for row in csv.DictReader(handle)}
        expected_passes = {
            "heldout_His_PTx_erk_minus_akt_residence",
            "heldout_His_YM_erk_minus_akt_residence",
            "heldout_S1P_PTx_erk_minus_akt_residence",
            "heldout_S1P_ymptx_erk_minus_akt_residence",
        }
        expected_inconclusive = {
            "heldout_His_ymptx_erk_minus_akt_residence",
            "heldout_S1P_YM_erk_minus_akt_residence",
            "heldout_UK_PTx_erk_minus_akt_residence",
        }
        self.assertEqual({key for key, row in rows.items() if row["outcome"] == "pass_bounded_coupling"}, expected_passes)
        self.assertEqual({key for key, row in rows.items() if row["outcome"] == "inconclusive_margin_boundary"}, expected_inconclusive)
        self.assertTrue(all(float(rows[key]["p_tost_holm"]) < 0.05 for key in expected_passes))
        self.assertTrue(all(rows[key]["claim_status"] == "heldout_not_promoted_margin_boundary" for key in expected_inconclusive))
        for row in rows.values():
            self.assertIn("not biochemical equivalence", row["interpretation_boundary"])

    def test_report_keeps_heldout_boundary_visible(self):
        report = (STAGE7_5 / "stage7_5_heldout_validation_report.md").read_text(encoding="utf-8")
        access = (STAGE7_5 / "controlled_access_note.md").read_text(encoding="utf-8")
        self.assertIn("4 contexts passed", report)
        self.assertIn("3 contexts remained margin-boundary inconclusive", report)
        self.assertIn("not be described as a universal external proof", report)
        self.assertIn("No controlled-access", access)
