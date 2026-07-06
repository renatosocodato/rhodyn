"""Regression checks for Stage 9.26 internal peer-review simulation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.26.json"
REPORT_PATH = WORKSPACE / "audits" / "internal_peer_review_simulation.md"
MATRIX_PATH = WORKSPACE / "audits" / "reviewer_action_matrix.csv"


class Stage926InternalPeerReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        cls.report = REPORT_PATH.read_text(encoding="utf-8")
        with MATRIX_PATH.open(encoding="utf-8", newline="") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_gate_passes_and_points_to_package_assembly(self) -> None:
        self.assertTrue(self.gate["pass"])
        self.assertEqual(self.gate["substage"], "9.26")
        self.assertEqual(self.gate["next_substage"], "9.27")
        self.assertEqual(self.gate["reviewer_perspective_count"], 8)
        self.assertEqual(self.gate["action_row_count"], 16)
        for field in [
            "missing_perspectives",
            "unsupported_rows",
            "blocking_without_resolution",
            "schema_errors",
            "downstream_paths",
        ]:
            self.assertEqual(self.gate[field], [], field)

    def test_all_expected_checks_pass(self) -> None:
        expected = {
            "stage_9_25b_gate_passed",
            "all_eight_perspectives_present",
            "blocking_concerns_have_resolution_status",
            "unsupported_central_claims_are_routed",
            "panelforge_figure_assembly_status_recorded",
            "no_submission_package_started",
        }
        actual = {item["name"] for item in self.gate["checks"] if item.get("passed") is True}
        self.assertEqual(actual, expected)

    def test_reviewer_action_matrix_has_complete_resolution_status(self) -> None:
        expected_fields = {
            "reviewer_perspective",
            "concern",
            "claim_id",
            "fig_id",
            "resolution_status",
            "resolution",
        }
        self.assertEqual(set(self.rows[0]), expected_fields)
        self.assertEqual(len(self.rows), 16)
        self.assertEqual({row["reviewer_perspective"] for row in self.rows}, {
            "Nature Methods handling editor",
            "Computational methods reviewer",
            "Live-cell signaling reviewer",
            "Statistics and uncertainty reviewer",
            "Endpoint perturbation reviewer",
            "Software reproducibility reviewer",
            "Figure and data-visualization reviewer",
            "Adoption and usability reviewer",
        })
        self.assertTrue(all(row["resolution"].strip() for row in self.rows))
        self.assertLessEqual({row["resolution_status"] for row in self.rows}, {"resolved", "narrowed", "routed_upstream"})

    def test_panelforge_status_is_recorded_without_missing_outputs(self) -> None:
        status = self.gate["panelforge_status"]
        self.assertEqual(status["engine"]["name"], "panelforge-figures")
        self.assertEqual(status["engine"]["version"], "3.14.1")
        self.assertEqual(status["engine"]["pinned_ref"], "v3.14.1")
        self.assertEqual(status["engine"]["version_doi"], "10.5281/zenodo.20811171")
        self.assertEqual(status["rendered_figures"], [f"FIG-00{idx}" for idx in range(1, 7)])
        self.assertEqual(status["rendered_file_count"], 18)
        self.assertEqual(status["missing_rendered_paths"], [])
        self.assertTrue(status["manifest_present"])
        self.assertTrue(status["render_report_present"])
        self.assertTrue(status["legend_gate_pass"])
        self.assertEqual(status["legend_gate_counts"]["main_figure_legend_count"], 6)
        self.assertEqual(status["legend_gate_counts"]["statistic_count"], 19)

    def test_report_preserves_scientific_boundaries_and_next_step(self) -> None:
        for phrase in [
            "Stage 9.26 internal peer-review simulation",
            "PanelForge figure assembly status",
            "No fatal scientific blocker is left without a resolution status",
            "Proceed to Stage 9.27 package assembly with the action matrix attached",
            "bounded coupling remains margin- and context-limited",
            "do not identify direct biochemical interactions",
            "rather than new biological results",
        ]:
            self.assertIn(phrase, self.report)

    def test_submission_package_remains_unstarted(self) -> None:
        for rel in [
            "submission_package/pi_review_packet.md",
            "submission_package/submission_readiness_checklist.md",
            "stage9_completion_report.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
