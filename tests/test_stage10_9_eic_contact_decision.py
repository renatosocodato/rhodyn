"""Regression tests for Stage 10.9 EIC-contact decision."""

from __future__ import annotations

import csv
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_9_eic_contact_decision.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_eic_contact_decision"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_9_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage109EicContactDecisionTest(unittest.TestCase):
    def test_stage10_9_selects_presubmission_without_sending(self) -> None:
        report = _load_runner().run_stage10_9()

        self.assertEqual(report["status"], "pass")
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(report["selected_route"], "presubmission_query_author_review_required")
        self.assertEqual(report["external_contact_status"], "not_sent")
        self.assertEqual(report["summary_metrics"]["selected_route_count"], 1)
        self.assertEqual(report["summary_metrics"]["message_beat_count"], 6)

        gate_report = json.loads((OUTPUT_DIR / "stage10_9_gate_report.json").read_text(encoding="utf-8"))
        self.assertEqual(gate_report["next_phase"], "Author review and optional EIC presubmission contact")
        self.assertIn("does not send any message", gate_report["interpretation_boundary"])

    def test_stage10_9_route_matrix_preserves_alternatives(self) -> None:
        _load_runner().run_stage10_9()

        with (OUTPUT_DIR / "stage10_9_route_decision_matrix.tsv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))

        decisions = {row["route"]: row["decision"] for row in rows}
        self.assertEqual(decisions["presubmission_query_author_review_required"], "selected")
        self.assertEqual(decisions["full_submission"], "not_selected_now")
        self.assertEqual(decisions["delay_for_another_dataset"], "not_selected_now")
        self.assertEqual(decisions["pivot_venue"], "fallback_only")
        self.assertTrue(any("prospective collaborator-blind validation" in row["rationale"] for row in rows))

    def test_stage10_9_pitch_contains_method_first_evidence_and_boundaries(self) -> None:
        _load_runner().run_stage10_9()

        pitch = (OUTPUT_DIR / "stage10_9_one_page_pitch.md").read_text(encoding="utf-8")
        email = (OUTPUT_DIR / "stage10_9_presubmission_email_draft_AUTHOR_REVIEW_REQUIRED.md").read_text(
            encoding="utf-8"
        )
        memo = (OUTPUT_DIR / "stage10_9_decision_memo.md").read_text(encoding="utf-8")

        for phrase in [
            "residence-state inference method",
            "SciPy peak summaries",
            "scikit-learn feature models",
            "DRG calcium dynamics",
            "GPCR-linked ERK trajectories",
            "Cell Painting/MitoTox endpoint profiling",
            "MLCI tracking",
            "sealed no-retuning validation route",
            "not a biology-only manuscript",
            "not a software wrapper",
        ]:
            self.assertIn(phrase, pitch)
        self.assertIn("Author review required", email)
        self.assertIn("Do not ask the EIC to reconsider the Stage 9.29 package alone", memo)


if __name__ == "__main__":
    unittest.main()
