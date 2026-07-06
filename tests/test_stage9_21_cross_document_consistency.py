"""Regression checks for Stage 9.21 cross-document consistency audit."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.21.json"
AUDIT_PATH = WORKSPACE / "audits" / "cross_document_consistency_audit.md"


class Stage921CrossDocumentConsistencyTests(unittest.TestCase):
    def test_gate_passes_and_points_to_statistical_language_audit(self) -> None:
        gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        self.assertIs(gate["pass"], True)
        self.assertEqual(gate["substage"], "9.21")
        self.assertEqual(gate["next_substage"], "9.22")
        self.assertEqual(gate["claim_count"], 5)
        self.assertEqual(gate["figure_count"], 6)
        self.assertEqual(gate["statistic_count"], 19)
        self.assertEqual(gate["source_data_table_count"], 9)
        self.assertEqual(gate["reference_count"], 13)
        self.assertTrue(all(item["passed"] for item in gate["checks"]))

    def test_join_mismatch_sets_are_empty(self) -> None:
        gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        for field in [
            "orphan_claims",
            "unknown_claim_refs",
            "orphan_figures",
            "unknown_figure_refs",
            "orphan_statistics",
            "unknown_statistic_refs",
            "dangling_references",
            "unknown_paragraph_refs",
            "unknown_table_refs",
            "strength_mismatches",
            "missing_render_paths",
            "bad_engine_rows",
            "missing_source_paths",
            "missing_binding_render_paths",
        ]:
            self.assertEqual(gate[field], [], field)

    def test_audit_reports_scope_and_counts(self) -> None:
        audit = AUDIT_PATH.read_text(encoding="utf-8")
        for phrase in [
            "The cross-document joins passed",
            "no orphan claims, no orphan main figures, no orphan statistic IDs, and no dangling references",
            "Frozen claims | 5",
            "Main figures | 6",
            "Statistics | 19",
            "References | 13",
            "Cross-document joins only",
            "does not test live-number phrasing",
            "does not write figure legends",
        ]:
            self.assertIn(phrase, audit)

    def test_downstream_surfaces_remain_unstarted(self) -> None:
        for rel in [
            "stage9_completion_report.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
