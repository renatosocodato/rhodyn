"""Regression checks for Stage 9.28 PI-review auto-revision."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
PACKAGE = WORKSPACE / "submission_package"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.28.json"


class Stage928PiReviewAutoRevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        cls.packet = (PACKAGE / "pi_review_packet.md").read_text(encoding="utf-8")
        cls.revision_log = (PACKAGE / "pi_review_revision_log.md").read_text(encoding="utf-8")
        cls.literature = (PACKAGE / "pi_review_literature_calibration.md").read_text(encoding="utf-8")
        cls.package_manifest = json.loads((PACKAGE / "submission_package_manifest.json").read_text(encoding="utf-8"))
        cls.submission_manifest = (PACKAGE / "submission_manifest.md").read_text(encoding="utf-8")
        cls.checklist = (PACKAGE / "submission_readiness_checklist.md").read_text(encoding="utf-8")
        with (PACKAGE / "pi_review_action_matrix.csv").open(newline="", encoding="utf-8") as handle:
            cls.action_rows = list(csv.DictReader(handle))

    def test_gate_passes_and_points_to_closure_substage(self) -> None:
        self.assertTrue(self.gate["pass"])
        self.assertEqual(self.gate["substage"], "9.28")
        self.assertEqual(self.gate["next_substage"], "9.29")
        self.assertEqual(self.gate["auto_revision_count"], 5)
        self.assertEqual(self.gate["major_review_item_count"], 7)
        self.assertEqual(self.gate["minor_review_item_count"], 8)
        self.assertEqual(self.gate["action_matrix_rows"], 6)

    def test_all_expected_checks_pass(self) -> None:
        expected = {
            "stage_9_27_package_regenerated",
            "persona_prompt_available",
            "pi_review_packet_present",
            "required_review_headings_exact",
            "major_minor_review_items_present",
            "confidential_recommendation_allowed",
            "review_surface_hygiene_passed",
            "safe_source_revisions_applied",
            "action_matrix_present",
            "revision_log_present",
            "literature_calibration_present",
            "reader_surface_hygiene_passed",
            "package_safety_scan_clear",
            "panelforge_status_unchanged",
            "no_stage9_closure_started",
        }
        actual = {item["name"] for item in self.gate["checks"] if item.get("passed") is True}
        self.assertEqual(actual, expected)

    def test_review_packet_has_exact_required_sections(self) -> None:
        headings = [line[2:].strip() for line in self.packet.splitlines() if line.startswith("# ")]
        self.assertEqual(
            headings,
            ["Executive Summary", "Revision Aspects", "Confidential Recommendation to the Editor"],
        )
        self.assertIn("## Major", self.packet)
        self.assertIn("## Minor", self.packet)
        recommendation = self.packet.split("# Confidential Recommendation to the Editor", 1)[1].strip().splitlines()[0]
        self.assertEqual(recommendation, "Potentially Accept after Major Revision and Re-review")

    def test_action_matrix_and_revision_log_preserve_evidence_boundary(self) -> None:
        self.assertEqual(len(self.action_rows), 6)
        statuses = {row["status"] for row in self.action_rows}
        self.assertIn("auto_revised", statuses)
        self.assertIn("human_action_required", statuses)
        for edit_id in [f"REV-9.28-00{idx}" for idx in range(1, 6)]:
            self.assertIn(edit_id, self.revision_log)
        self.assertIn("No new biological datasets, analyses, model outputs, or figure renders were created.", self.revision_log)
        self.assertIn("No new reference was added in Stage 9.28", self.literature)

    def test_package_safety_and_closure_boundary(self) -> None:
        forbidden = [
            "/" + "Users/",
            "/" + "Volumes/",
            "Library/" + "LaunchAgents",
            "github" + "_pat_",
            "ghp" + "_",
            "sk" + "-",
        ]
        for body in [self.packet, self.revision_log, self.literature]:
            for token in forbidden:
                self.assertNotIn(token, body)
        if (WORKSPACE / "gate_verdicts" / "9.29.json").exists():
            self.assertTrue((WORKSPACE / "stage9_completion_report.md").exists())
        else:
            self.assertFalse((WORKSPACE / "stage9_completion_report.md").exists())

    def test_submission_manifests_record_pi_review_as_complete(self) -> None:
        self.assertIn(self.package_manifest["current_substage"], {"9.28", "9.29"})
        self.assertEqual(self.package_manifest["pi_review_status"], "complete_pi_review_packet")
        self.assertIn("manuscript/nature_methods/submission_package/pi_review_packet.md", self.package_manifest["package_files"])
        self.assertNotIn("manuscript/nature_methods/submission_package/pi_review_packet.md", self.package_manifest["not_started"])
        self.assertIn("| PI review packet | `pi_review_packet.md` |", self.submission_manifest)
        self.assertIn("PI review packet | ready", self.checklist)


if __name__ == "__main__":
    unittest.main()
