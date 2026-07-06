"""Regression checks for Stage 9.16 Methods drafting."""

from __future__ import annotations

import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
METHODS_PATH = WORKSPACE / "sections" / "methods.md"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.16.json"


def _visible_text(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.startswith("<!--"))


class Stage916MethodsDraftingTests(unittest.TestCase):
    def test_gate_passes_and_points_to_availability_substage(self) -> None:
        gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        self.assertIs(gate["pass"], True)
        self.assertEqual(gate["substage"], "9.16")
        self.assertEqual(gate["next_substage"], "9.17")
        self.assertGreaterEqual(gate["methods_word_count"], 900)
        self.assertLessEqual(gate["methods_word_count"], 3000)
        self.assertEqual(gate["methods_paragraph_count"], 10)
        self.assertEqual(gate["software_version"], "v0.1.0")
        self.assertEqual(gate["methods_statement_ids"], [f"MTH-{idx:04d}" for idx in range(1, 10)])
        self.assertTrue(all(item["passed"] for item in gate["checks"]))

    def test_methods_visible_text_contains_required_scientific_boundaries(self) -> None:
        methods = METHODS_PATH.read_text(encoding="utf-8")
        visible = _visible_text(methods)
        for phrase in [
            "# Online Methods",
            "Input schemas and preprocessing",
            "Residence windows and amplitude comparators",
            "Bounded-coupling and uncertainty decisions",
            "Reserve-like endpoint construction",
            "Routed-output model comparison",
            "Software surfaces, versioning, and reproducibility",
            "RhoDyn v0.1.0",
            "declared analysis choice",
            "not proof that all coupling is absent",
            "not direct assays of unmeasured biological reserve capacity",
            "does not identify direct biochemical interactions",
        ]:
            self.assertIn(phrase, visible)
        self.assertNotRegex(visible, r"\b(MTH|ART|CLM)-\d{4}\b")

    def test_methods_statement_ids_remain_in_gate_not_reader_surface(self) -> None:
        methods = METHODS_PATH.read_text(encoding="utf-8")
        gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(set(gate["methods_statement_ids"]), {f"MTH-{idx:04d}" for idx in range(1, 10)})
        self.assertNotRegex(methods, r"methods_stmt_ids=|claim_ids=|repo_paths=|<!--|MTH-\d{4}|CLM-\d{4}")

    def test_downstream_surfaces_remain_unstarted(self) -> None:
        forbidden = [
            "submission_package/pi_review_packet.md",
        ]
        for rel in forbidden:
            self.assertFalse((WORKSPACE / rel).exists(), rel)

    def test_forbidden_methods_phrases_are_absent(self) -> None:
        visible = _visible_text(METHODS_PATH.read_text(encoding="utf-8")).lower()
        for phrase in [
            "standard methods",
            "standard pipeline",
            "default settings",
            "as described previously",
            "as described elsewhere",
            "manufacturer's instructions",
            "using default",
            "absence of all coupling",
            "true biological reserve",
            "literal molecular edge",
            "rhodyn generated the original",
        ]:
            self.assertNotIn(phrase, visible)


if __name__ == "__main__":
    unittest.main()
