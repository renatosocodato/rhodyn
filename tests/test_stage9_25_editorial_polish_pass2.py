"""Regression checks for Stage 9.25 editorial polish pass II."""

from __future__ import annotations

import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.25.json"
AUDIT_PATH = WORKSPACE / "audits" / "editorial_pass_2.md"
SURFACE_PATHS = [
    WORKSPACE / "sections" / "introduction.md",
    WORKSPACE / "sections" / "results.md",
    WORKSPACE / "sections" / "discussion.md",
    WORKSPACE / "sections" / "methods.md",
    WORKSPACE / "figures" / "figure_legends.md",
]


class Stage925EditorialPolishPass2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        cls.audit = AUDIT_PATH.read_text(encoding="utf-8")
        cls.surfaces = {path.name: path.read_text(encoding="utf-8") for path in SURFACE_PATHS}
        cls.combined = "\n\n".join(cls.surfaces.values())

    def test_gate_passes_and_points_to_reader_surface_hygiene(self) -> None:
        self.assertTrue(self.gate["pass"])
        self.assertEqual(self.gate["substage"], "9.25")
        self.assertEqual(self.gate["next_substage"], "9.25b")
        for field in [
            "paragraph_errors",
            "claim_id_errors",
            "figure_call_errors",
            "style_errors",
            "unsafe_hits",
            "missing_limits",
            "process_hits",
            "reader_stage_hits",
            "downstream_paths",
        ]:
            self.assertEqual(self.gate[field], [], field)
        self.assertEqual(self.gate["terminal_calls"], {})

    def test_all_expected_checks_pass(self) -> None:
        expected = {
            "stage_9_24_gate_passed",
            "meaning_preserved",
            "style_metrics_pass_thresholds",
            "no_claim_broadened",
            "venue_style_replacements_resolved",
            "dynamic_figure_call_flow_preserved",
            "reader_surface_stage_language_absent",
            "no_reader_hygiene_or_package_started",
        }
        actual = {item["name"] for item in self.gate["checks"] if item.get("passed") is True}
        self.assertEqual(actual, expected)

    def test_audit_records_second_polish_scope(self) -> None:
        for phrase in [
            "Stage 9.25 editorial polish pass II",
            "second reader-facing polish loop",
            "venue-style process phrase removal",
            "Paragraph IDs, claim IDs, and Results figure calls were preserved",
            "within threshold",
            "does not broaden the residence",
        ]:
            self.assertIn(phrase, self.audit)

    def test_polished_reader_phrases_are_present(self) -> None:
        expected = {
            "introduction.md": "explicit checks that allow each component to be tested in sequence",
            "results.md": "The held-out analysis therefore keeps pass and inconclusive outcomes side by side",
            "discussion.md": "Reproducibility evidence strengthens the method",
            "methods.md": "Methods section refer to RhoDyn v0.1.0",
            "figure_legends.md": "Non-example panels collect ambiguous regimes",
        }
        for name, phrase in expected.items():
            self.assertIn(phrase, self.surfaces[name], name)

    def test_process_phrases_and_unsafe_claims_are_absent(self) -> None:
        forbidden = [
            "figure-locked order",
            "final Results step",
            "Results unit",
            "Methods draft",
            "software evidence",
            "decision state",
            "automatic equivalence engine",
            "universal residence law",
            "automatic mechanism-discovery",
            "guarantees",
            "absence of all coupling",
            "proof of no crosstalk",
            "true biological reserve",
            "direct live metabolic reserve assay",
            "literal molecular edge",
        ]
        lower = self.combined.lower()
        for phrase in forbidden:
            self.assertNotIn(phrase.lower(), lower, phrase)

    def test_dynamic_figure_call_flow_and_claim_ids_remain_intact(self) -> None:
        for para_id in [
            "PARA-INTRO-001",
            "PARA-INTRO-002",
            "PARA-RESULTS-001",
            "PARA-RESULTS-006",
            "PARA-DISCUSSION-001",
            "PARA-DISCUSSION-002",
        ]:
            self.assertIn(para_id, self.combined)
        terminal_call_pattern = re.compile(r"[^.!?]*\((?:Fig\.|Supplementary Fig\.|Supplementary Table)[^)]+\)\.")
        self.assertIsNone(terminal_call_pattern.search(self.combined))

    def test_downstream_reader_surfaces_remain_unstarted(self) -> None:
        for rel in [
            "audits/reader_surface_hygiene_report.md",
            "audits/internal_peer_review_simulation.md",
            "submission_package/pi_review_packet.md",
            "submission_package/submission_readiness_checklist.md",
            "stage9_completion_report.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
