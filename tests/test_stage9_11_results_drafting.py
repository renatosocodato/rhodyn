"""Regression checks for the Stage 9.11 Results drafting pass."""

from __future__ import annotations

import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


def _visible_results_text() -> str:
    body = (WORKSPACE / "sections" / "results.md").read_text(encoding="utf-8")
    return "\n".join(line for line in body.splitlines() if not line.startswith("<!--")).strip()


class Stage911ResultsDraftingTests(unittest.TestCase):
    def test_gate_records_results_drafting_boundary(self) -> None:
        gate = json.loads((WORKSPACE / "gate_verdicts" / "9.11.json").read_text(encoding="utf-8"))
        self.assertTrue(gate["pass"])
        self.assertEqual(gate["substage"], "9.11")
        self.assertEqual(gate["paragraph_count"], 6)
        self.assertEqual(gate["next_substage"], "9.12")
        self.assertEqual(gate["figure_callouts"], ["Fig. 1", "Fig. 2", "Fig. 3", "Fig. 4", "Fig. 5", "Fig. 6"])
        self.assertEqual(
            gate["para_ids"],
            [
                "PARA-RESULTS-001",
                "PARA-RESULTS-002",
                "PARA-RESULTS-003",
                "PARA-RESULTS-004",
                "PARA-RESULTS-005",
                "PARA-RESULTS-006",
            ],
        )
        self.assertEqual(
            gate["claim_ids"],
            ["CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"],
        )
        self.assertTrue(all(row["passed"] for row in gate["checks"]))
        self.assertIn("Results draft only", gate["scope_boundary"])

    def test_results_draft_is_figure_ordered_and_reader_clean(self) -> None:
        body = (WORKSPACE / "sections" / "results.md").read_text(encoding="utf-8")
        self.assertIn("# Results", body)
        self.assertEqual(len(re.findall(r"^## ", body, flags=re.MULTILINE)), 6)
        for phrase in [
            "RhoDyn defines residence-state inference as an executable method object",
            "Software parity and archive reproduction make the method inspectable",
            "Fig. 1a",
            "Fig. 6e",
            "bounded-coupling",
            "reserve-like",
            "routed-output",
            "cross-surface reproducibility",
        ]:
            self.assertIn(phrase, body)
        visible = _visible_results_text()
        self.assertNotRegex(visible, r"PARA-RESULTS-\d{3}|CLM-\d{4}|FIG-\d{3}|<!--")
        first_positions = [visible.index(f"Fig. {idx}") for idx in range(1, 7)]
        self.assertEqual(first_positions, sorted(first_positions))

    def test_results_draft_preserves_strength_caps_and_deferred_surfaces(self) -> None:
        visible = _visible_results_text()
        for forbidden in [
            "universal",
            "guarantees",
            "therapeutic",
            "clinical",
            "diagnostic",
            "proves no crosstalk",
            "absence of all coupling",
            "literal molecular edge",
            "RhoDyn generated the original",
            "doi:",
            "http://",
            "https://",
            "REF-",
        ]:
            self.assertNotIn(forbidden, visible)
        self.assertIsNone(re.search(r"\(\d+(?:-\d+|,\s*\d+)*\)", visible))
        for rel in [
            "submission_package/pi_review_packet.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
