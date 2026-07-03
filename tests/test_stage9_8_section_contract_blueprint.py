"""Regression checks for the Stage 9.8 section contract blueprint."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


class Stage98SectionContractBlueprintTests(unittest.TestCase):
    def test_gate_records_section_contract_boundary(self) -> None:
        gate = json.loads((WORKSPACE / "gate_verdicts" / "9.8.json").read_text(encoding="utf-8"))
        self.assertTrue(gate["pass"])
        self.assertEqual(gate["substage"], "9.8")
        self.assertEqual(gate["section_contract_count"], 15)
        self.assertEqual(gate["results_subheading_count"], 6)
        self.assertEqual(gate["methods_subheading_count"], 6)
        self.assertEqual(gate["discussion_subheading_count"], 0)
        self.assertEqual(gate["abstract_word_limit"], 150)
        self.assertTrue(gate["abstract_unreferenced"])
        self.assertEqual(gate["next_substage"], "9.9")
        self.assertTrue(all(row["passed"] for row in gate["checks"]))

    def test_contract_text_carries_venue_structure_rules(self) -> None:
        body = (WORKSPACE / "sections" / "section_contracts.md").read_text(encoding="utf-8")
        for phrase in [
            "not a title draft",
            "not an abstract draft",
            "not Results prose",
            "SEC-002. Abstract",
            "SEC-004. Results",
            "SEC-005. Discussion",
            "SEC-006. Online Methods",
            "Abstract. Maximum 150 words and unreferenced.",
            "Results. Topical subheadings are required.",
            "Discussion. Subheadings are prohibited.",
            "Online Methods. Topical subheadings are required",
            "References. Citation resolution is deferred to Stage 9.20",
        ]:
            self.assertIn(phrase, body)

    def test_results_methods_and_discussion_subheading_rules_are_specific(self) -> None:
        body = (WORKSPACE / "sections" / "section_contracts.md").read_text(encoding="utf-8")
        self.assertIn("Method object and executable truth cases", body)
        self.assertIn("Residence-amplitude separation in public live-cell trajectories", body)
        self.assertIn("Bounded-coupling and uncertainty decisions", body)
        self.assertIn("Software surfaces, versioning, and reproducibility", body)
        discussion_block = body.split("### SEC-005. Discussion", 1)[1].split("### SEC-006. Online Methods", 1)[0]
        self.assertIn("Prohibited content. subheadings", discussion_block)
        self.assertIn("Topical subheadings. none.", discussion_block)

    def test_downstream_manuscript_surfaces_remain_absent(self) -> None:
        for rel in [
            "sections/results.md",
            "sections/introduction.md",
            "sections/discussion.md",
            "sections/methods.md",
            "refs/references.bib",
            "submission_package/pi_review_packet.md",
            "submission_package/submission_readiness_checklist.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
