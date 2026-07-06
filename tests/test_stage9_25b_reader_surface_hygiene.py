"""Regression checks for Stage 9.25b reader-surface hygiene."""

from __future__ import annotations

import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.25b.json"
AUDIT_PATH = WORKSPACE / "audits" / "reader_surface_hygiene_report.md"
SURFACE_PATHS = [
    WORKSPACE / "sections" / "abstract.md",
    WORKSPACE / "sections" / "introduction.md",
    WORKSPACE / "sections" / "results.md",
    WORKSPACE / "sections" / "discussion.md",
    WORKSPACE / "sections" / "methods.md",
    WORKSPACE / "sections" / "data_availability.md",
    WORKSPACE / "sections" / "code_availability.md",
    WORKSPACE / "figures" / "figure_legends.md",
    WORKSPACE / "supplementary" / "supplementary_methods.md",
]


class Stage925bReaderSurfaceHygieneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        cls.audit = AUDIT_PATH.read_text(encoding="utf-8")
        cls.surfaces = {path.relative_to(WORKSPACE).as_posix(): path.read_text(encoding="utf-8") for path in SURFACE_PATHS}
        cls.combined = "\n\n".join(cls.surfaces.values())

    def test_gate_passes_and_points_to_internal_peer_review(self) -> None:
        self.assertTrue(self.gate["pass"])
        self.assertEqual(self.gate["substage"], "9.25b")
        self.assertEqual(self.gate["next_substage"], "9.26")
        for field in [
            "comment_hits",
            "internal_id_hits",
            "stage_language_hits",
            "unsafe_hits",
            "local_path_hits",
            "secret_hits",
            "missing_required_terms",
            "figure_call_errors",
            "downstream_paths",
            "panel_s3_crossrefs",
        ]:
            self.assertEqual(self.gate[field], [], field)
        self.assertEqual(self.gate["terminal_calls"], {})
        self.assertEqual(self.gate["missing_surface_phrases"], {})

    def test_all_expected_checks_pass(self) -> None:
        expected = {
            "stage_9_25_gate_passed",
            "reader_comments_removed",
            "internal_ids_absent_from_reader_surfaces",
            "stage_and_build_language_absent",
            "legends_and_captions_free_of_lineage_language",
            "meaning_and_figure_flow_preserved",
            "claim_boundaries_preserved",
            "local_path_and_secret_scan_clear",
            "no_internal_peer_review_or_package_started",
        }
        actual = {item["name"] for item in self.gate["checks"] if item.get("passed") is True}
        self.assertEqual(actual, expected)

    def test_reader_surfaces_have_no_internal_tokens(self) -> None:
        self.assertNotRegex(
            self.combined,
            r"<!--|-->|\b(?:PARA|CLM|MTH|FIG|SFIG|STBL|STAT|ART|SUPP|REF)-\d{3,4}\b|Stage 9|stage9",
        )
        self.assertIn("# Abstract", self.surfaces["sections/abstract.md"])
        self.assertIn("(1-4)", self.surfaces["sections/introduction.md"])
        self.assertIn("(9,10)", self.surfaces["sections/introduction.md"])
        self.assertIn("(1-8)", self.surfaces["sections/introduction.md"])
        self.assertIn("(10,11)", self.surfaces["sections/introduction.md"])

    def test_scientific_boundaries_and_availability_survive(self) -> None:
        for phrase in [
            "residence-state",
            "bounded-coupling",
            "reserve-like",
            "routed-output",
            "not proof that all coupling is absent",
            "not direct assays of unmeasured biological reserve capacity",
            "does not identify direct biochemical interactions",
            "not a new biological result",
            "10.5281/zenodo.21036616",
            "10.5281/zenodo.21036615",
            "10.5281/zenodo.20811171",
        ]:
            self.assertIn(phrase, self.combined)
        for forbidden in [
            "universal residence law",
            "absence of all coupling",
            "true biological reserve",
            "literal molecular edge",
            "RhoDyn generated the original",
        ]:
            self.assertNotIn(forbidden, self.combined)

    def test_audit_records_reader_surface_scope(self) -> None:
        for phrase in [
            "Stage 9.25b reader-surface hygiene report",
            "Hidden comments were removed",
            "Introduction reference tokens were converted",
            "figure legends remain free of lineage language",
            "does not add new biological evidence",
        ]:
            self.assertIn(phrase, self.audit)

    def test_downstream_surfaces_remain_unstarted(self) -> None:
        for rel in [
            "stage9_completion_report.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
