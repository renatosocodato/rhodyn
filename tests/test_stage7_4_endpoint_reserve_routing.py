import csv
import json
from pathlib import Path
from unittest import TestCase

from rhodyn.schema import read_coupling_csv, read_endpoint_csv, read_reserve_csv


STAGE7_4 = Path("case_studies/stage7_endpoint_reserve_routing")


class Stage74EndpointReserveRoutingTests(TestCase):
    def test_gate_report_passes_with_required_boundaries(self):
        gate = json.loads((STAGE7_4 / "stage7_4_endpoint_reserve_routing_gate_report.json").read_text(encoding="utf-8"))
        self.assertEqual(gate["status"], "pass")
        self.assertEqual(gate["completion_state"], "complete_endpoint_reserve_routing_demonstrations")
        checkpoints = gate["validation_checkpoints"]
        for key in [
            "declared_margins_present_for_bounded_coupling",
            "model_comparisons_include_reduced_alternatives",
            "routed_output_comparison_distinguishes_alternatives",
            "reserve_like_labels_scoped_to_measurement",
            "schema_validation_endpoint_rows",
            "schema_validation_reserve_like_rows",
            "schema_validation_coupling_rows",
            "uncertainty_present_for_reserve_like_coordinate",
            "examples_do_not_imply_manuscript_generation",
        ]:
            self.assertEqual(checkpoints[key], "pass", key)
        self.assertEqual(checkpoints["stop_condition_non_trajectory_model_indistinguishable"], "not_triggered")
        self.assertIn("not live metabolic reserve", gate["interpretation_boundary"])

    def test_tidy_endpoint_and_reserve_like_tables_validate(self):
        endpoint_records, endpoint_issues = read_endpoint_csv(STAGE7_4 / "cell_painting_tidy_endpoint_model_rows.csv")
        reserve_records, reserve_issues = read_reserve_csv(STAGE7_4 / "cell_painting_reserve_like_endpoint_rows.csv")
        self.assertEqual(endpoint_issues, [])
        self.assertEqual(reserve_issues, [])
        self.assertEqual(len(endpoint_records), 35532)
        self.assertEqual(len(reserve_records), 658)
        self.assertTrue(all(0.0 <= record.response <= 1.0 for record in reserve_records))

        with (STAGE7_4 / "cell_painting_reserve_like_endpoint_rows.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertIn("mitochondrial disruption up", rows[0]["endpoint_set"])
        self.assertIn("not live metabolic reserve", rows[0]["interpretation_boundary"])

    def test_routed_model_comparison_keeps_reduced_alternatives(self):
        with (STAGE7_4 / "cell_painting_routed_model_comparison.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(rows[0]["model"], "compartment_route_5nn")
        self.assertEqual(rows[0]["decision"], "retained")
        self.assertEqual(rows[0]["rank"], "1")

        with (STAGE7_4 / "cell_painting_reduced_alternative_decisions.tsv").open(newline="", encoding="utf-8") as handle:
            alternatives = {row["reduced_alternative"]: row for row in csv.DictReader(handle, delimiter="\t")}
        self.assertGreater(float(alternatives["endpoint_prevalence"]["delta_bic_vs_routed"]), 200.0)
        self.assertGreater(float(alternatives["morphology_magnitude_5nn"]["delta_bic_vs_routed"]), 300.0)
        self.assertEqual(alternatives["endpoint_prevalence"]["decision"], "fails_relative_to_routed")

    def test_bounded_coupling_promotes_only_context_limited_uk_claim(self):
        records, issues = read_coupling_csv(STAGE7_4 / "erk_akt_bounded_coupling_decisions.csv")
        self.assertEqual(issues, [])
        self.assertEqual(len(records), 4)
        with (STAGE7_4 / "erk_akt_bounded_coupling_decisions.csv").open(newline="", encoding="utf-8") as handle:
            rows = {row["contrast"]: row for row in csv.DictReader(handle)}
        self.assertEqual(rows["erk_minus_akt_residence_UK"]["claim_status"], "primary_context_limited_bounded_coupling")
        self.assertEqual(rows["erk_minus_akt_residence_His"]["claim_status"], "not_promoted_beyond_declared_margin")
        self.assertEqual(rows["erk_minus_akt_residence_S1P"]["claim_status"], "not_promoted_beyond_declared_margin")
        self.assertAlmostEqual(float(rows["erk_minus_akt_residence_UK"]["margin"]), 0.20)
        self.assertAlmostEqual(float(rows["erk_minus_akt_residence_UK"]["minimum_passing_margin"]), 0.10)
        self.assertIn("not biochemical equivalence", rows["erk_minus_akt_residence_UK"]["interpretation_boundary"])

    def test_reports_state_what_rhodyn_adds_without_manuscript_generation_claim(self):
        summary = (STAGE7_4 / "stage7_4_case_summary.tsv").read_text(encoding="utf-8")
        report = (STAGE7_4 / "stage7_4_case_report.md").read_text(encoding="utf-8")
        self.assertIn("Routed compartment architecture", summary)
        self.assertIn("cell-health endpoint preservation", report)
        self.assertIn("does not imply that RhoDyn generated", report)
