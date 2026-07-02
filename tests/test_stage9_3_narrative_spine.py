"""Regression checks for Stage 9.3 narrative-spine registration."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


class Stage93NarrativeSpineTests(unittest.TestCase):
    def test_stage9_3_gate_passes_with_expected_predicates(self) -> None:
        gate_path = WORKSPACE / "gate_verdicts" / "9.3.json"
        self.assertTrue(gate_path.exists())
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        self.assertTrue(gate.get("pass"))
        self.assertEqual(gate.get("substage"), "9.3")
        self.assertEqual(gate.get("content_type"), "Article")
        check_names = {check.get("name") for check in gate.get("checks", [])}
        for name in {
            "stage_9_2_gate_passed",
            "content_type_matches_sourced_budget",
            "narrative_spine_exists",
            "discovery_versus_demonstration_decision_is_evidence_bound",
            "no_downstream_stage9_surfaces_started",
        }:
            self.assertIn(name, check_names)
        self.assertTrue(all(check.get("passed") for check in gate.get("checks", [])))

    def test_narrative_spine_records_article_archetype_without_drafting(self) -> None:
        spine_path = WORKSPACE / "stage9_narrative_spine.md"
        self.assertTrue(spine_path.exists())
        spine = spine_path.read_text(encoding="utf-8")
        for phrase in [
            "Nature Methods Article",
            "residence-state inference",
            "dynamic operating-state",
            "Discovery-versus-demonstration decision",
            "Stage 9.4 must freeze",
            "claim hierarchy",
        ]:
            self.assertIn(phrase, spine)
        for rel in [
            "sections/results.md",
            "sections/introduction.md",
            "sections/discussion.md",
            "sections/methods.md",
            "refs/references.bib",
            "submission_package/pi_review_packet.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists())

    def test_venue_fit_rationale_preserves_methods_article_boundary(self) -> None:
        rationale_path = WORKSPACE / "audits" / "venue_fit_rationale.md"
        self.assertTrue(rationale_path.exists())
        rationale = rationale_path.read_text(encoding="utf-8")
        for phrase in [
            "Nature Methods Article fit",
            "computational methods Article",
            "should not claim",
            "Stage 9.4 must freeze claim hierarchy",
        ]:
            self.assertIn(phrase, rationale)
        self.assertNotIn("references.bib", rationale)


if __name__ == "__main__":
    unittest.main()
