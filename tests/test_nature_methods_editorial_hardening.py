"""Regression checks for the Nature Methods editorial hardening addendum."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDITS = ROOT / "manuscript" / "nature_methods" / "audits"


class NatureMethodsEditorialHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = (AUDITS / "nature_methods_editor_triage_simulation.md").read_text(encoding="utf-8")
        cls.payload = json.loads((AUDITS / "nature_methods_editor_triage_simulation.json").read_text(encoding="utf-8"))

    def test_triage_simulation_is_scoped_to_author_side_stress_test(self) -> None:
        self.assertEqual(self.payload["status"], "pass")
        self.assertIn("not a journal decision", self.payload["scope"])
        self.assertIn("This is an author-side stress test, not a journal decision.", self.report)
        self.assertNotIn("accepted for review", self.report.lower())
        self.assertNotIn("will proceed to review", self.report.lower())

    def test_triage_criteria_cover_nature_methods_editorial_risks(self) -> None:
        criteria = {row["criterion"] for row in self.payload["criteria"]}
        self.assertEqual(
            criteria,
            {
                "Article content-type fit",
                "Novel method object",
                "Validation breadth and transferability",
                "Performance comparison and alternatives",
                "Reproducibility and software readiness",
                "Biological utility without overclaiming",
                "Submission completeness",
                "Reviewer and editor fit",
                "Desk-rejection residual risk",
            },
        )
        self.assertEqual(self.payload["risk_counts"]["high"], 0)
        self.assertGreaterEqual(self.payload["risk_counts"]["medium"], 1)

    def test_remaining_risks_are_biologically_and_submission_scoped(self) -> None:
        self.assertIn("avoid claiming every reporter has a residence regime", self.report)
        self.assertIn("not a hidden primary biology claim", self.report)
        self.assertIn("Complete the official Reporting Summary", self.report)
        self.assertIn("Verify reviewer access to the public repository and Zenodo archive", self.report)
        self.assertIn("reviewer suggestions method-first", self.report)
        self.assertIn("reviewer/editor fit planner", self.report)

    def test_official_sources_are_recorded(self) -> None:
        sources = self.payload["official_sources"]
        self.assertEqual(sources["nature_methods_content_types"], "https://www.nature.com/nmeth/content")
        self.assertEqual(
            sources["nature_methods_preparing_your_material"],
            "https://www.nature.com/nmeth/submission-guidelines/preparing-your-submission",
        )


if __name__ == "__main__":
    unittest.main()
