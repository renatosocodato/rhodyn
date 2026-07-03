"""Regression checks for Stage 9.14 Discussion drafting."""

from __future__ import annotations

import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


def _visible_text(markdown: str) -> str:
    return "\n".join(line for line in markdown.splitlines() if not line.startswith("<!--")).strip()


class Stage914DiscussionDraftingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = json.loads((WORKSPACE / "gate_verdicts" / "9.14.json").read_text(encoding="utf-8"))
        self.discussion = (WORKSPACE / "sections" / "discussion.md").read_text(encoding="utf-8")

    def test_gate_passes_and_points_to_methods_stage(self) -> None:
        self.assertIs(self.gate["pass"], True)
        self.assertEqual(self.gate["substage"], "9.14")
        self.assertEqual(self.gate["paragraph_count"], 5)
        self.assertGreaterEqual(self.gate["discussion_word_count"], 650)
        self.assertLessEqual(self.gate["discussion_word_count"], 900)
        self.assertEqual(self.gate["next_substage"], "9.15")
        self.assertTrue(all(check["passed"] for check in self.gate["checks"]))

    def test_discussion_has_no_markdown_subheadings(self) -> None:
        visible = _visible_text(self.discussion)
        self.assertFalse(any(line.startswith("#") for line in visible.splitlines()))
        self.assertNotIn("##", visible)

    def test_limitations_and_future_directions_remain_visible(self) -> None:
        for phrase in [
            "declared biological window",
            "not a causal mechanism",
            "amplitude and endpoint summaries remain useful",
            "inconclusive",
            "slower or context-specific coupling",
            "reserve-like",
            "measured endpoint",
            "direct biochemical interactions",
            "not a new biological result",
            "Future directions",
            "not an automatic mechanism-discovery engine",
        ]:
            self.assertIn(phrase, self.discussion)

    def test_discussion_avoids_scope_overclaims(self) -> None:
        visible = _visible_text(self.discussion)
        for forbidden in [
            "universal residence law",
            "guarantees",
            "therapeutic",
            "clinical",
            "diagnostic",
            "absence of all coupling",
            "proof of no crosstalk",
            "true biological reserve",
            "literal molecular edge",
            "RhoDyn generated the original",
        ]:
            self.assertNotIn(forbidden, visible)

    def test_no_methods_reference_library_or_package_started(self) -> None:
        for rel in [
            "sections/methods.md",
            "refs/references.bib",
            "submission_package/pi_review_packet.md",
            "submission_package/submission_readiness_checklist.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
