"""Regression checks for Stage 9.23 figure legend and caption audit."""

from __future__ import annotations

import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.23.json"
LEGENDS_PATH = WORKSPACE / "figures" / "figure_legends.md"
AUDIT_PATH = WORKSPACE / "audits" / "figure_legend_audit.md"


class Stage923FigureLegendAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        cls.legends = LEGENDS_PATH.read_text(encoding="utf-8")
        cls.audit = AUDIT_PATH.read_text(encoding="utf-8")

    def test_gate_passes_and_points_to_editorial_polish(self) -> None:
        self.assertTrue(self.gate["pass"])
        self.assertEqual(self.gate["substage"], "9.23")
        self.assertEqual(self.gate["next_substage"], "9.24")
        self.assertEqual(self.gate["main_figure_legend_count"], 6)
        self.assertEqual(self.gate["supplementary_figure_caption_count"], 9)
        self.assertEqual(self.gate["supplementary_table_caption_count"], 9)
        self.assertEqual(self.gate["statistic_count"], 19)
        for field in [
            "panel_coverage_errors",
            "stat_resolution_errors",
            "supplementary_link_errors",
            "leakage_hits",
            "unsafe_claim_hits",
            "forbidden_package_paths",
        ]:
            self.assertEqual(self.gate[field], [], field)

    def test_all_expected_checks_pass(self) -> None:
        expected = {
            "stage_9_22_gate_passed",
            "each_main_figure_has_legend",
            "each_supplementary_figure_and_table_has_caption",
            "main_figure_panel_coverage_complete",
            "legend_statistics_resolve",
            "supplementary_callouts_resolve_to_captions",
            "legends_do_not_assert_absent_claims",
            "legend_seed_text_has_no_internal_or_panelforge_leakage",
            "no_final_package_started",
        }
        actual = {item["name"] for item in self.gate["checks"] if item.get("passed") is True}
        self.assertEqual(actual, expected)

    def test_main_figure_panel_letters_are_present(self) -> None:
        expected_panels = {
            "Figure 1": "abcd",
            "Figure 2": "abcd",
            "Figure 3": "abcd",
            "Figure 4": "abcde",
            "Figure 5": "abcde",
            "Figure 6": "abcde",
        }
        for figure, letters in expected_panels.items():
            pattern = rf"### {re.escape(figure)} \|.*?(?=\n### Figure|\n## Supplementary figure legends)"
            match = re.search(pattern, self.legends, flags=re.S)
            self.assertIsNotNone(match, figure)
            section = match.group(0)
            for letter in letters:
                self.assertIn(f"**{letter}**", section, f"{figure}{letter}")

    def test_reader_facing_legends_have_no_internal_or_absent_claim_leakage(self) -> None:
        forbidden_patterns = [
            r"\b(?:FIG|SFIG|STBL|SUPP|STAT|ART|CLM|PARA|MTH)-\d{3,}\b",
            r"\bPanelForge\b",
            r"\bpanelforge\b",
            r"\bStage\s*9\b",
            r"\bstage9\b",
            r"\bmanifest\b",
            r"\bledger\b",
            r"\baudit\b",
            r"\bprovenance\b",
            r"\brender_path\b",
            r"\bsource_paths\b",
            "/" + "Users/",
            "/" + "Volumes/",
        ]
        for pattern in forbidden_patterns:
            self.assertIsNone(re.search(pattern, self.legends), pattern)
        for phrase in [
            "no crosstalk",
            "absence of all pathway communication",
            "literal molecular edge",
            "direct live metabolic reserve assay",
            "universal coupling rule",
            "PyPI publication",
        ]:
            self.assertNotIn(phrase.lower(), self.legends.lower())

    def test_legend_and_audit_report_expected_scope(self) -> None:
        for phrase in [
            "Figure 1 | RhoDyn defines residence-state inference as an executable method object.",
            "Figure 6 | Software parity and archive reproduction make RhoDyn decisions inspectable.",
            "Supplementary Fig. 9 | Interpretation boundaries and non-example cases.",
            "Supplementary Table 9 | Failure modes, ambiguous regimes, claim-strength caps, and wording boundaries",
        ]:
            self.assertIn(phrase, self.legends)
        for phrase in [
            "The figure legend and caption audit passed",
            "Six main figure legends, nine supplementary figure legends, and nine supplementary table captions were written",
            "every figure and table statistic binding resolves",
            "does not assemble the full manuscript",
        ]:
            self.assertIn(phrase, self.audit)

    def test_downstream_editorial_and_package_surfaces_remain_unstarted(self) -> None:
        for rel in [
            "audits/editorial_pass_1.md",
            "audits/editorial_pass_2.md",
            "audits/reader_surface_hygiene_report.md",
            "submission_package/pi_review_packet.md",
            "submission_package/submission_readiness_checklist.md",
            "stage9_completion_report.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
