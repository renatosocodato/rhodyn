"""Regression checks for Stage 9.27 submission package assembly."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
PACKAGE = WORKSPACE / "submission_package"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.27.json"


class Stage927SubmissionPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        cls.main_text = (PACKAGE / "main_text_for_submission.md").read_text(encoding="utf-8")
        cls.supplement = (PACKAGE / "supplementary_information_for_submission.md").read_text(encoding="utf-8")
        cls.checklist = (PACKAGE / "submission_readiness_checklist.md").read_text(encoding="utf-8")
        cls.code_for_review = (PACKAGE / "code_for_review.md").read_text(encoding="utf-8")
        cls.author_declarations = (PACKAGE / "author_declarations_REQUIRED.md").read_text(encoding="utf-8")
        cls.ai_disclosure = (PACKAGE / "ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
        cls.title_author_metadata = (PACKAGE / "title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
        cls.reporting_summary_answer_bank = (PACKAGE / "reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
        cls.prior_art_positioning = (PACKAGE / "prior_art_positioning_matrix.md").read_text(encoding="utf-8")
        with (PACKAGE / "figure_file_inventory.csv").open(newline="", encoding="utf-8") as handle:
            cls.figure_rows = list(csv.DictReader(handle))
        with (PACKAGE / "source_data_and_statistics_inventory.csv").open(newline="", encoding="utf-8") as handle:
            cls.source_rows = list(csv.DictReader(handle))

    def test_gate_passes_and_points_to_pi_review(self) -> None:
        self.assertTrue(self.gate["pass"])
        self.assertEqual(self.gate["substage"], "9.27")
        self.assertEqual(self.gate["next_substage"], "9.28")
        self.assertEqual(self.gate["figure_file_count"], 18)
        self.assertEqual(self.gate["source_inventory_rows"], 28)
        self.assertEqual(self.gate["reporting_summary_status"], "placeholder_present_final_form_human_action")

    def test_all_expected_checks_pass(self) -> None:
        expected = {
            "stage_9_26_gate_passed",
            "required_inputs_present",
            "main_text_present",
            "supplement_present",
            "reader_surface_hygiene_passed",
            "cross_document_consistency_gate_passed",
            "legend_gate_passed",
            "figure_files_present",
            "panelforge_status_bound",
            "reporting_summary_present",
            "reporting_summary_answer_bank_present",
            "code_for_review_present",
            "editor_triage_note_present",
            "editorial_pitch_present",
            "prior_art_positioning_matrix_present",
            "software_reporting_checklist_present",
            "article_fit_checklist_present",
            "author_declarations_present",
            "ai_disclosure_draft_present",
            "title_author_metadata_present",
            "package_safety_scan_clear",
            "no_downstream_pi_or_closure_started",
            "package_consistency_audit_passed",
        }
        actual = {item["name"] for item in self.gate["checks"] if item.get("passed") is True}
        self.assertEqual(actual, expected)

    def test_reader_surfaces_are_complete_and_clean(self) -> None:
        for phrase in [
            "# RhoDyn infers residence states in live-cell perturbation data",
            "## Abstract",
            "## Results",
            "## Online Methods",
            "## References",
            "### Main figure legends",
        ]:
            self.assertIn(phrase, self.main_text)
        self.assertNotIn("## Introduction", self.main_text)
        self.assertIn(
            "Live-cell perturbation experiments increasingly record the temporal structure",
            self.main_text,
        )
        for phrase in [
            "# Supplementary Information",
            "## Supplementary Methods",
            "### Supplementary figure legends",
            "### Supplementary table captions",
        ]:
            self.assertIn(phrase, self.supplement)
        forbidden = [
            "/" + "Users/",
            "/" + "Volumes/",
            "Library/" + "LaunchAgents",
            "github" + "_pat_",
            "ghp" + "_",
            "sk" + "-",
        ]
        for body in [self.main_text, self.supplement]:
            for token in forbidden:
                self.assertNotIn(token, body)

    def test_figure_and_source_inventories_are_populated(self) -> None:
        self.assertEqual(len(self.figure_rows), 18)
        self.assertTrue(all(row["exists"] == "true" for row in self.figure_rows))
        self.assertEqual({row["format"] for row in self.figure_rows}, {"pdf", "png", "svg"})
        self.assertEqual(len(self.source_rows), 28)
        self.assertEqual({row["record_type"] for row in self.source_rows}, {"statistic", "source_data"})

    def test_code_and_reporting_surfaces_remain_review_scoped(self) -> None:
        self.assertIn("Reproducibility commands", self.code_for_review)
        self.assertIn("RhoDyn repository root", self.code_for_review)
        self.assertTrue((PACKAGE / "editorial_pitch_for_submission.md").exists())
        pitch = (PACKAGE / "editorial_pitch_for_submission.md").read_text(encoding="utf-8")
        self.assertIn("Cover-letter upload checklist", pitch)
        self.assertIn("not under consideration by another journal", pitch)
        self.assertIn("Prior editor discussions", pitch)
        self.assertIn("Source code supplied for review", (PACKAGE / "software_reporting_checklist.md").read_text(encoding="utf-8"))
        self.assertIn("Content-type decision", (PACKAGE / "article_fit_checklist.md").read_text(encoding="utf-8"))
        self.assertIn("Competing interests", self.author_declarations)
        self.assertIn("AI-assisted content disclosure", self.author_declarations)
        self.assertIn("human action", self.author_declarations)
        self.assertIn("AUTHOR CONFIRMATION REQUIRED", self.ai_disclosure)
        self.assertIn("does not assert final AI use", self.ai_disclosure)
        self.assertIn("Option A", self.ai_disclosure)
        self.assertIn("Option B", self.ai_disclosure)
        self.assertIn("AUTHOR CONFIRMATION REQUIRED", self.title_author_metadata)
        self.assertIn("Author list", self.title_author_metadata)
        self.assertIn("Correspondence and materials", self.title_author_metadata)
        self.assertIn("Double-blind review decision", self.title_author_metadata)
        self.assertIn("AUTHOR CONFIRMATION REQUIRED", self.reporting_summary_answer_bank)
        self.assertIn("Statistics", self.reporting_summary_answer_bank)
        self.assertIn("Software and code", self.reporting_summary_answer_bank)
        self.assertIn("Life-science study design", self.reporting_summary_answer_bank)
        self.assertIn("Materials and experimental systems", self.reporting_summary_answer_bank)
        self.assertIn("Prior-art positioning matrix", self.prior_art_positioning)
        self.assertIn("should not be positioned as the first method to treat live-cell signals as dynamic", self.prior_art_positioning)
        self.assertIn("does not add citations, performance results, biological datasets, or manuscript claims", self.prior_art_positioning)
        self.assertIn("Prior-art positioning matrix | ready", self.checklist)
        self.assertIn("Author declarations | registered", self.checklist)
        self.assertIn("AI disclosure draft | registered", self.checklist)
        self.assertIn("Title and author metadata | registered", self.checklist)
        self.assertIn("Reporting Summary | registered", self.checklist)
        self.assertIn("Reporting Summary answer bank | registered", self.checklist)
        self.assertIn("Springer Nature", self.checklist)
        self.assertIn("human submission action", self.checklist)
        self.assertTrue((PACKAGE / "pi_review_packet.md").exists())
        if (WORKSPACE / "gate_verdicts" / "9.29.json").exists():
            self.assertTrue((WORKSPACE / "stage9_completion_report.md").exists())
        else:
            self.assertFalse((WORKSPACE / "stage9_completion_report.md").exists())


if __name__ == "__main__":
    unittest.main()
