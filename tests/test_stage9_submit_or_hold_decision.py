"""Regression checks for the Nature Methods submit-or-hold decision."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
REPORT_PATH = WORKSPACE / "audits" / "nature_methods_submit_or_hold_decision.json"
MD_PATH = WORKSPACE / "audits" / "nature_methods_submit_or_hold_decision.md"


class Stage9SubmitOrHoldDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.markdown = MD_PATH.read_text(encoding="utf-8")

    def test_decision_separates_science_readiness_from_upload_readiness(self) -> None:
        self.assertEqual(self.report["status"], "hold_for_human_upload_actions")
        self.assertIs(self.report["collaborator_review_ready"], True)
        self.assertIs(self.report["journal_upload_ready"], False)
        self.assertIn("ready for collaborator and PI review", self.report["decision"])
        self.assertIn("Final journal upload should remain on hold", self.report["decision"])

    def test_science_package_checks_pass(self) -> None:
        failed = [
            check["name"]
            for check in self.report["science_package_checks"]
            if check.get("passed") is not True
        ]
        self.assertEqual(failed, [])
        names = {check["name"] for check in self.report["science_package_checks"]}
        for expected in [
            "nature_methods_article_fit",
            "figures_present_in_three_formats",
            "public_urls_resolve",
            "unresolved_reference_case_links_not_public_facing",
            "code_and_data_availability_present",
            "stage9_closure_passed",
        ]:
            self.assertIn(expected, names)

    def test_upload_hold_checks_pass_and_include_ai_disclosure_decision(self) -> None:
        failed = [
            check["name"]
            for check in self.report["upload_hold_checks"]
            if check.get("passed") is not True
        ]
        self.assertEqual(failed, [])
        self.assertTrue(
            any("AI-assisted content disclosure" in action for action in self.report["human_submission_actions"])
        )
        self.assertTrue(
            any("official Springer Nature Reporting Summary" in action for action in self.report["human_submission_actions"])
        )

    def test_markdown_is_collaborator_readable(self) -> None:
        self.assertIn("Decision. `hold_for_human_upload_actions`.", self.markdown)
        self.assertIn("## Science package checks", self.markdown)
        self.assertIn("## Upload hold checks", self.markdown)
        self.assertIn("## Required human submission actions", self.markdown)
        self.assertIn("does not add data, analyses, figures, citations, or manuscript claims", self.markdown)


if __name__ == "__main__":
    unittest.main()
