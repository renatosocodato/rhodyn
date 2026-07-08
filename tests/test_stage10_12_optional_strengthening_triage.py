"""Regression tests for Stage 10.12 optional-strengthening triage."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_12_optional_strengthening_triage.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_optional_strengthening"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_12_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage1012OptionalStrengtheningTriageTest(unittest.TestCase):
    def test_stage10_12_gate_passes_and_keeps_contact_unsent(self) -> None:
        report = _load_runner().run_stage10_12()

        self.assertEqual(report["status"], "pass")
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(report["external_contact_status"], "not_sent")
        self.assertEqual(report["recommended_local_next_step"], "render_stage10_method_figures")
        self.assertEqual(report["summary_metrics"]["option_count"], 5)
        self.assertEqual(report["summary_metrics"]["figure_count"], 6)
        self.assertEqual(report["summary_metrics"]["planned_panel_count"], 30)

    def test_figure_readiness_uses_complete_stage10_crosswalk(self) -> None:
        _load_runner().run_stage10_12()

        with (OUTPUT_DIR / "stage10_12_figure_render_readiness.tsv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))

        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(int(row["panel_count"]) for row in rows), 30)
        self.assertTrue(all(row["architecture_status"] == "method_first_crosswalk_complete" for row in rows))
        self.assertTrue(all(row["evidence_files_exist"] == "yes" for row in rows))
        self.assertTrue(all(row["render_status"] == "not_rendered_in_stage10" for row in rows))

    def test_option_matrix_separates_local_and_external_strengthening(self) -> None:
        _load_runner().run_stage10_12()

        with (OUTPUT_DIR / "stage10_12_strengthening_option_matrix.tsv").open(encoding="utf-8") as handle:
            rows = {row["option"]: row for row in csv.DictReader(handle, delimiter="\t")}

        self.assertEqual(
            rows["render_stage10_method_figures"]["recommended_decision"],
            "next_local_hardening_before_full_submission",
        )
        self.assertEqual(rows["render_stage10_method_figures"]["local_feasibility"], "high")
        self.assertEqual(
            rows["prospective_collaborator_blind_validation"]["recommended_decision"],
            "defer_not_blocking_presubmission",
        )
        self.assertEqual(
            rows["prospective_collaborator_blind_validation"]["local_feasibility"],
            "low_external_data_required",
        )
        self.assertEqual(rows["full_submission_now"]["recommended_decision"], "do_not_select_without_author_override")

    def test_validation_gap_keeps_prospective_validation_as_new_evidence(self) -> None:
        _load_runner().run_stage10_12()

        with (OUTPUT_DIR / "stage10_12_validation_gap_matrix.tsv").open(encoding="utf-8") as handle:
            rows = {row["validation_layer"]: row for row in csv.DictReader(handle, delimiter="\t")}

        self.assertEqual(
            rows["stage10_4_no_retuning_public_derived_replay"]["decision"],
            "sufficient_for_presubmission_scope",
        )
        self.assertEqual(
            rows["prospective_collaborator_blind_validation"]["decision"],
            "not_locally_closable_in_stage10_12",
        )
        self.assertEqual(
            rows["stage10_rendered_method_figures"]["decision"],
            "highest_value_local_hardening_step",
        )

    def test_memory_records_stage10_12_as_active_without_contact(self) -> None:
        _load_runner().run_stage10_12()

        memory = json.loads((ROOT / "docs" / "roadmap_execution_memory.json").read_text(encoding="utf-8"))
        current = memory["current_position"]
        self.assertEqual(
            current["active_stage"],
            "Stage 10.12 optional-strengthening triage complete; external contact remains not sent",
        )
        stage10 = next(entry for entry in memory["stage_lock"] if entry.get("stage") == 10)
        self.assertEqual(stage10["status"], "stage10_12_complete_optional_strengthening_triage")
        subphase = next(item for item in stage10["subphases"] if item.get("id") == "10.12")
        self.assertEqual(subphase["status"], "complete_optional_strengthening_triage")
        self.assertIn(
            "case_studies/stage10_optional_strengthening/stage10_12_gate_report.json",
            stage10["artifacts"],
        )


if __name__ == "__main__":
    unittest.main()
