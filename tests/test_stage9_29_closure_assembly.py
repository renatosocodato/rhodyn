"""Regression checks for Stage 9.29 closure and version binding."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
PACKAGE = WORKSPACE / "submission_package"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.29.json"


class Stage929ClosureAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        cls.report = (WORKSPACE / "stage9_completion_report.md").read_text(encoding="utf-8")
        cls.binding = json.loads((WORKSPACE / "stage9_closure_version_binding.json").read_text(encoding="utf-8"))
        cls.package_manifest = json.loads((PACKAGE / "submission_package_manifest.json").read_text(encoding="utf-8"))
        cls.submission_manifest = (PACKAGE / "submission_manifest.md").read_text(encoding="utf-8")
        cls.checklist = (PACKAGE / "submission_readiness_checklist.md").read_text(encoding="utf-8")
        with (PACKAGE / "pi_review_action_decisions.csv").open(newline="", encoding="utf-8") as handle:
            cls.action_rows = list(csv.DictReader(handle))

    def test_gate_is_terminal_and_passes(self) -> None:
        self.assertTrue(self.gate["pass"])
        self.assertEqual(self.gate["substage"], "9.29")
        self.assertEqual(self.gate["next_substage"], "none")
        self.assertEqual(self.gate["closure_status"], "complete_stage9_closed_version_bound")
        self.assertEqual(self.gate["action_decision_rows"], 6)
        self.assertEqual(self.gate["human_submission_action_rows"], 1)
        self.assertEqual(self.gate["package_file_count"], 19)
        self.assertEqual(self.gate["rendered_figure_file_count"], 18)

    def test_all_expected_closure_checks_pass(self) -> None:
        expected = {
            "stage_9_28_gate_passed",
            "all_stage9_gates_pass",
            "quarantine_has_no_unresolved_blocker",
            "package_files_present",
            "package_version_bound",
            "evidence_version_bound",
            "release_version_bound",
            "limitation_version_bound",
            "pi_review_action_decisions_recorded",
            "human_submission_actions_retained",
            "completion_report_present",
            "version_binding_present",
            "package_safety_scan_clear",
            "panelforge_status_bound",
        }
        actual = {item["name"] for item in self.gate["checks"] if item.get("passed") is True}
        self.assertEqual(actual, expected)

    def test_version_binding_records_package_evidence_release_and_figures(self) -> None:
        self.assertEqual(self.binding["software_version"], "v0.1.0")
        self.assertEqual(self.binding["pyproject_version"], "0.1.0")
        self.assertEqual(self.binding["software_archive_doi"], "10.5281/zenodo.21036616")
        self.assertEqual(self.binding["software_concept_doi"], "10.5281/zenodo.21036615")
        self.assertEqual(self.binding["figure_engine"]["pinned_ref"], "v3.14.1")
        self.assertEqual(self.binding["figure_engine"]["version_doi"], "10.5281/zenodo.20811171")
        self.assertEqual(self.binding["figure_status"]["rendered_file_count"], 18)
        self.assertTrue(self.binding["figure_status"]["all_files_exist"])
        self.assertIn("stage7.8-methods-readiness", self.binding["evidence_version"])
        self.assertIn("reference-library", self.binding["reference_version"])

    def test_pi_review_actions_are_closed_or_submission_only(self) -> None:
        self.assertEqual(len(self.action_rows), 6)
        statuses = {row["closure_status"] for row in self.action_rows}
        self.assertEqual(statuses, {"closed", "not_blocking_stage9_closure"})
        self.assertEqual(sum(row["closure_status"] == "not_blocking_stage9_closure" for row in self.action_rows), 1)
        decisions = {row["codex_decision"] for row in self.action_rows}
        self.assertIn("close_as_boundary_present", decisions)
        self.assertIn("retain_as_external_submission_action", decisions)

    def test_report_preserves_scientific_boundaries(self) -> None:
        for phrase in [
            "does not add new biological datasets",
            "does not show that every live-cell system has a residence regime",
            "bounded coupling excludes slower or context-specific coupling",
            "reserve-like endpoints directly measure biological reserve capacity",
            "routed-output parameters identify biochemical edges",
        ]:
            self.assertIn(phrase, self.report)
        self.assertIn("Complete the official Springer Nature Reporting Summary form.", self.report)

    def test_package_manifest_and_reader_surfaces_record_closure(self) -> None:
        self.assertEqual(self.package_manifest["current_substage"], "9.29")
        self.assertEqual(self.package_manifest["next_substage"], "none")
        self.assertEqual(self.package_manifest["closure_status"], "complete_stage9_closure_version_bound")
        self.assertEqual(self.package_manifest["not_started"], [])
        self.assertIn("manuscript/nature_methods/stage9_completion_report.md", self.package_manifest["package_files"])
        self.assertIn("| Stage 9 completion report | `../stage9_completion_report.md` |", self.submission_manifest)
        self.assertIn("Stage 9 closure | ready", self.checklist)


if __name__ == "__main__":
    unittest.main()
