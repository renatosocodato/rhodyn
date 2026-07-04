"""Regression checks for Stage 9.18 Supplementary Methods drafting."""

from __future__ import annotations

import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SUPPLEMENTARY_PATH = WORKSPACE / "supplementary" / "supplementary_methods.md"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.18.json"


def _visible_text(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.startswith("<!--"))


class Stage918SupplementaryMethodsTests(unittest.TestCase):
    def test_gate_passes_and_points_to_supplementary_tables(self) -> None:
        gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        self.assertIs(gate["pass"], True)
        self.assertEqual(gate["substage"], "9.18")
        self.assertEqual(gate["next_substage"], "9.19")
        self.assertEqual(gate["supplementary_methods_section_count"], 7)
        self.assertGreaterEqual(gate["supplementary_methods_word_count"], 900)
        self.assertEqual(set(gate["supp_ids"]), {f"SUPP-{idx:03d}" for idx in range(1, 10)})
        self.assertEqual(set(gate["claim_ids"]), {f"CLM-{idx:04d}" for idx in range(1, 6)})
        self.assertTrue(all(item["passed"] for item in gate["checks"]))

    def test_supplementary_methods_cover_support_items_and_callout_routes(self) -> None:
        body = SUPPLEMENTARY_PATH.read_text(encoding="utf-8")
        hidden_supp_ids = {
            item
            for group in re.findall(r"supp_ids=([^ ]+)", body)
            for item in group.split(";")
            if item
        }
        hidden_claim_ids = {
            item
            for group in re.findall(r"claim_ids=([^ ]+)", body)
            for item in group.split(";")
            if item
        }
        self.assertEqual(hidden_supp_ids, {f"SUPP-{idx:03d}" for idx in range(1, 10)})
        self.assertEqual(hidden_claim_ids, {f"CLM-{idx:04d}" for idx in range(1, 6)})
        for phrase in [
            "main_text_callouts=PARA-RESULTS-001; PARA-METHODS-001",
            "main_text_callouts=PARA-RESULTS-006; PARA-METHODS-005",
            "main_text_callouts=PARA-DISCUSSION-001; PARA-DISCUSSION-002",
        ]:
            self.assertIn(phrase, body)

    def test_visible_text_contains_methods_depth_and_boundaries(self) -> None:
        visible = _visible_text(SUPPLEMENTARY_PATH.read_text(encoding="utf-8"))
        for phrase in [
            "# Supplementary Methods",
            "Input contracts, method definitions, and truth cases",
            "Public live-cell signaling adapters",
            "Bounded-coupling decisions and held-out contexts",
            "Reserve-like endpoint construction",
            "Routed-output reduced-architecture comparison",
            "Software parity, export bundles, and archive reproduction",
            "Non-example cases and interpretation boundaries",
            "not independent biological evidence",
            "not proof that all coupling is absent",
            "not direct assays of unmeasured biological reserve capacity",
            "does not identify direct biochemical interactions",
            "does not imply PyPI publication",
            "not a universal biological rule",
        ]:
            self.assertIn(phrase, visible)
        self.assertIn(r"\(I_W(t_k)\)", visible)
        self.assertIn(r"\(-\Delta \le L \le U \le \Delta\)", visible)
        self.assertIn(r"\(H=\mathrm{clip}", visible)
        self.assertIn(r"\(RSS_m=\sum_j", visible)
        self.assertNotRegex(visible, r"\b(CLM|ART|SUPP|PARA|FIG|STBL|SFIG)-\d{3,4}\b")

    def test_forbidden_claim_inflation_and_downstream_surfaces_are_absent(self) -> None:
        visible = _visible_text(SUPPLEMENTARY_PATH.read_text(encoding="utf-8")).lower()
        for phrase in [
            "universal residence law",
            "automatic mechanism-discovery",
            "true biological reserve",
            "literal molecular edge",
            "absence of all coupling",
            "private-data reproduction claim",
            "pypi publication is claimed",
        ]:
            self.assertNotIn(phrase, visible)
        for rel in [
            "figures/figure_legends.md",
            "submission_package/pi_review_packet.md",
            "submission_package/submission_readiness_checklist.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
