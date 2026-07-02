"""Regression checks for Stage 9.2 representative methods-paper corpus."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


class Stage92MethodsPaperCorpusTests(unittest.TestCase):
    def test_stage9_2_gate_passes_with_expected_predicates(self) -> None:
        gate_path = WORKSPACE / "gate_verdicts" / "9.2.json"
        self.assertTrue(gate_path.exists())
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        self.assertTrue(gate.get("pass"))
        self.assertEqual(gate.get("substage"), "9.2")
        self.assertEqual(gate.get("planned_doi_count"), 8)
        self.assertEqual(gate.get("verified_doi_count"), 8)
        check_names = {check.get("name") for check in gate.get("checks", [])}
        for name in {
            "stage_9_1_gate_passed",
            "corpus_has_planned_doi_count",
            "each_entry_records_required_axes",
            "archetype_synthesis_exists",
            "no_downstream_stage9_surfaces_started",
        }:
            self.assertIn(name, check_names)
        self.assertTrue(all(check.get("passed") for check in gate.get("checks", [])))

    def test_corpus_contains_eight_verified_dois_and_required_axes(self) -> None:
        corpus_path = WORKSPACE / "refs" / "representative_methods_papers.md"
        self.assertTrue(corpus_path.exists())
        corpus = corpus_path.read_text(encoding="utf-8")
        for doi in [
            "10.1038/s41592-020-01018-x",
            "10.1038/s41592-021-01358-2",
            "10.1038/s41592-021-01346-6",
            "10.1038/s41587-019-0071-9",
            "10.1038/s41587-021-01206-w",
            "10.1038/s41587-020-0591-3",
            "10.1038/s41587-019-0336-3",
            "10.1038/s41593-018-0209-y",
        ]:
            self.assertIn(doi, corpus)
        for header in ["novelty", "benchmarks", "biology", "software", "limitations", "availability", "rhodyn_pattern"]:
            self.assertIn(header, corpus)
        self.assertFalse((WORKSPACE / "refs" / "references.bib").exists())

    def test_crossref_cache_is_complete(self) -> None:
        cache_dir = WORKSPACE / "refs" / "_cache" / "methods_corpus"
        self.assertTrue(cache_dir.is_dir())
        cache_files = sorted(cache_dir.glob("*.crossref.json"))
        self.assertEqual(len(cache_files), 8)
        for cache_file in cache_files:
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
            self.assertEqual(payload.get("status"), "fetched")
            self.assertEqual(payload.get("http_status"), 200)

    def test_archetype_analysis_points_to_stage9_3_without_drafting(self) -> None:
        archetype_path = WORKSPACE / "audits" / "methods_paper_archetype_analysis.md"
        self.assertTrue(archetype_path.exists())
        archetype = archetype_path.read_text(encoding="utf-8")
        for phrase in [
            "Method object appears early",
            "Benchmarks use shared inputs and simpler alternatives",
            "Stage 9.3",
        ]:
            self.assertIn(phrase, archetype)
        for rel in [
            "sections/results.md",
            "sections/introduction.md",
            "sections/discussion.md",
            "submission_package/pi_review_packet.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists())


if __name__ == "__main__":
    unittest.main()
