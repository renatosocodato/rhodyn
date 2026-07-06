"""Regression checks for Stage 9.24 editorial polish pass I."""

from __future__ import annotations

import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.24.json"
AUDIT_PATH = WORKSPACE / "audits" / "editorial_pass_1.md"
SECTION_PATHS = [
    WORKSPACE / "sections" / "introduction.md",
    WORKSPACE / "sections" / "results.md",
    WORKSPACE / "sections" / "discussion.md",
    WORKSPACE / "sections" / "methods.md",
    WORKSPACE / "figures" / "figure_legends.md",
]


class Stage924EditorialPolishPass1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        cls.audit = AUDIT_PATH.read_text(encoding="utf-8")
        cls.sections = {path.name: path.read_text(encoding="utf-8") for path in SECTION_PATHS}
        cls.combined = "\n\n".join(cls.sections.values())

    def test_gate_passes_and_points_to_editorial_pass_2(self) -> None:
        self.assertTrue(self.gate["pass"])
        self.assertEqual(self.gate["substage"], "9.24")
        self.assertEqual(self.gate["next_substage"], "9.25")
        for field in [
            "paragraph_errors",
            "unsafe_hits",
            "missing_limits",
            "reader_stage_hits",
            "downstream_paths",
        ]:
            self.assertEqual(self.gate[field], [], field)
        self.assertEqual(self.gate["terminal_calls"], {})

    def test_all_expected_checks_pass(self) -> None:
        expected = {
            "stage_9_23_gate_passed",
            "paragraph_id_set_unchanged",
            "strength_caps_hold",
            "limitations_remain_present",
            "dynamic_figure_call_flow_preserved",
            "reader_surface_stage_language_absent",
            "recursive_editorial_replacements_resolved",
            "no_downstream_stage_started",
        }
        actual = {item["name"] for item in self.gate["checks"] if item.get("passed") is True}
        self.assertEqual(actual, expected)

    def test_audit_records_recursive_reader_surface_polish(self) -> None:
        for phrase in [
            "Stage 9.24 editorial polish pass I",
            "cadence and sentence flow",
            "claim-strength and limitation retention",
            "reader-surface leakage and downstream-boundary check",
            "Paragraph IDs were preserved",
            "claim-strength caps remained intact",
            "limitations stayed present",
            "does not broaden the residence",
        ]:
            self.assertIn(phrase, self.audit)

    def test_polished_reader_phrases_are_present(self) -> None:
        expected = {
            "introduction.md": "For perturbation biology, the practical problem",
            "results.md": "Together, these definitions establish RhoDyn",
            "discussion.md": "Taken together, the present evidence supports RhoDyn",
            "methods.md": "not evidence that the software generated the motivating RhoA/microglia manuscript",
            "figure_legends.md": "before biological demonstrations are interpreted",
        }
        for name, phrase in expected.items():
            self.assertIn(phrase, self.sections[name], name)

    def test_call_flow_remains_intact_and_reader_tokens_are_clean(self) -> None:
        self.assertNotRegex(self.combined, r"\b(?:PARA|CLM|MTH|FIG|SFIG|STBL|STAT|ART|SUPP|REF)-\d{3,4}\b|<!--")
        terminal_call_pattern = re.compile(r"[^.!?]*\((?:Fig\.|Supplementary Fig\.|Supplementary Table)[^)]+\)\.")
        self.assertIsNone(terminal_call_pattern.search(self.combined))

    def test_claim_boundaries_and_downstream_surfaces_remain_safe(self) -> None:
        for phrase in [
            "universal residence law",
            "automatic mechanism-discovery",
            "guarantees",
            "proves",
            "absence of all coupling",
            "proof of no crosstalk",
            "no crosstalk",
            "true biological reserve",
            "direct live metabolic reserve assay",
            "literal molecular edge",
        ]:
            self.assertNotIn(phrase.lower(), self.combined.lower(), phrase)
        for rel in [
            "stage9_completion_report.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
