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
        cls.editor_objection_response = (PACKAGE / "editor_objection_response_map.md").read_text(encoding="utf-8")
        cls.editor_two_minute_triage = (PACKAGE / "editor_two_minute_triage_simulation.md").read_text(encoding="utf-8")
        cls.current_policy_preflight = (PACKAGE / "current_nature_methods_policy_preflight.md").read_text(encoding="utf-8")
        cls.reviewer_editor_fit = (PACKAGE / "reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
        cls.validation_breadth_map = (PACKAGE / "validation_breadth_and_boundary_map.md").read_text(encoding="utf-8")
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
            "validation_breadth_map_present",
            "editor_objection_response_map_present",
            "editor_two_minute_triage_simulation_present",
            "current_policy_preflight_present",
            "reviewer_editor_fit_planner_present",
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
        self.assertIn("Article-level computational method, not a software wrapper around existing summaries", pitch)
        self.assertIn("not the broad observation that cell signaling is dynamic", pitch)
        self.assertIn("reference use case rather than as hidden evidence for every methods claim", pitch)
        self.assertIn("rather than as a software note or a single-system biological study", pitch)
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
        self.assertIn("Validation breadth and boundary map", self.validation_breadth_map)
        self.assertIn("does not add data, analyses, citations, figures, datasets, performance claims, or manuscript text", self.validation_breadth_map)
        self.assertIn("Known-truth synthetic regimes", self.validation_breadth_map)
        self.assertIn("Public live-cell trajectory examples", self.validation_breadth_map)
        self.assertIn("Public-derived endpoint and paired-reporter demonstrations", self.validation_breadth_map)
        self.assertIn("Held-out contexts and margin sensitivity", self.validation_breadth_map)
        self.assertIn("It does not claim that every biological system contains a residence regime", self.validation_breadth_map)
        self.assertIn("Validation breadth map | ready", self.checklist)
        self.assertIn("Editor-objection response map", self.editor_objection_response)
        self.assertIn("likely Nature Methods desk-review objections", self.editor_objection_response)
        self.assertIn("does not add evidence, citations, figures, datasets, performance claims, or manuscript text", self.editor_objection_response)
        self.assertIn("If answering an objection would require new data, new benchmarking, or a stronger biological claim", self.editor_objection_response)
        self.assertIn("Editor-objection response map | ready", self.checklist)
        self.assertIn("Two-minute editor triage simulation", self.editor_two_minute_triage)
        self.assertIn("does not add evidence, citations, analyses, figures, datasets, performance claims, or manuscript text", self.editor_two_minute_triage)
        self.assertIn("What an editor can see quickly", self.editor_two_minute_triage)
        self.assertIn("The current package should be readable as a Nature Methods computational-methods Article", self.editor_two_minute_triage)
        self.assertIn("If an editor can answer these three questions in the first two minutes", self.editor_two_minute_triage)
        self.assertIn("Two-minute editor triage simulation | ready", self.checklist)
        self.assertIn("Current Nature Methods policy preflight", self.current_policy_preflight)
        self.assertIn("does not add evidence, citations, analyses, figures, datasets, performance claims, or manuscript text", self.current_policy_preflight)
        self.assertIn("Article is a report describing a novel method or tool", self.current_policy_preflight)
        self.assertIn("Abstract up to 150 words", self.current_policy_preflight)
        self.assertIn("Code and algorithm availability", self.current_policy_preflight)
        self.assertIn("Reporting Summary remains a human submission action", self.current_policy_preflight)
        self.assertIn("Current Nature Methods policy preflight | ready", self.checklist)
        self.assertIn("Reviewer and editor fit planner", self.reviewer_editor_fit)
        self.assertIn("does not nominate reviewers, infer conflicts, or add manuscript evidence", self.reviewer_editor_fit)
        self.assertIn("Expertise coverage needed", self.reviewer_editor_fit)
        self.assertIn("Suggested reviewer template", self.reviewer_editor_fit)
        self.assertIn("Exclusion template", self.reviewer_editor_fit)
        self.assertIn("The RhoA/microglia reference use case should not dominate reviewer assignment", self.reviewer_editor_fit)
        self.assertIn("Reviewer and editor fit planner | registered", self.checklist)
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
