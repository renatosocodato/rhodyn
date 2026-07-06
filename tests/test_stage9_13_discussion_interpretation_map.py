"""Regression checks for Stage 9.13 Discussion interpretation map."""

from __future__ import annotations

import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


def _visible_text(markdown: str) -> str:
    return "\n".join(line for line in markdown.splitlines() if not line.startswith("<!--")).strip()


class Stage913DiscussionInterpretationMapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = json.loads((WORKSPACE / "gate_verdicts" / "9.13.json").read_text(encoding="utf-8"))
        self.blueprint = (WORKSPACE / "sections" / "discussion_blueprint.md").read_text(encoding="utf-8")

    def test_gate_passes_and_points_to_discussion_drafting(self) -> None:
        self.assertIs(self.gate["pass"], True)
        self.assertEqual(self.gate["substage"], "9.13")
        self.assertEqual(self.gate["paragraph_count"], 5)
        self.assertEqual(self.gate["next_substage"], "9.14")
        self.assertTrue(all(check["passed"] for check in self.gate["checks"]))

    def test_map_has_no_markdown_subheadings(self) -> None:
        visible = _visible_text(self.blueprint)
        self.assertFalse(any(line.startswith("#") for line in visible.splitlines()))
        self.assertNotIn("##", visible)
        self.assertGreaterEqual(len(re.findall(r"\b[\w-]+\b", visible)), 250)

    def test_stage7_limitations_are_explicitly_represented(self) -> None:
        for phrase in [
            "declared biological window",
            "not a causal mechanism",
            "amplitude or endpoint summaries can be sufficient",
            "inconclusive",
            "slower or context-specific coupling",
            "reserve-like",
            "measured endpoint",
            "direct biochemical interactions",
            "not a new biological result",
            "reference use case",
        ]:
            self.assertIn(phrase, self.blueprint)

    def test_map_does_not_start_downstream_surfaces(self) -> None:
        for rel in [
            "submission_package/pi_review_packet.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
