"""Regression checks for Stage 9.12 Introduction literature binding."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


def _visible_text(markdown: str) -> str:
    return re.sub(r"<!--.*?-->", "", markdown, flags=re.S).strip()


class Stage912IntroductionLiteratureBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = json.loads((WORKSPACE / "gate_verdicts" / "9.12.json").read_text(encoding="utf-8"))
        self.introduction = (WORKSPACE / "sections" / "introduction.md").read_text(encoding="utf-8")
        with (WORKSPACE / "refs" / "introduction_citation_ledger.csv").open(encoding="utf-8", newline="") as handle:
            self.ledger_rows = list(csv.DictReader(handle))

    def test_gate_passes_with_word_budget_and_next_substage(self) -> None:
        self.assertIs(self.gate["pass"], True)
        self.assertEqual(self.gate["substage"], "9.12")
        self.assertEqual(self.gate["paragraph_count"], 4)
        self.assertGreaterEqual(self.gate["introduction_word_count"], 450)
        self.assertLessEqual(self.gate["introduction_word_count"], 650)
        self.assertEqual(self.gate["citation_count"], 11)
        self.assertLessEqual(self.gate["review_source_share"], self.gate["review_source_threshold"])
        self.assertEqual(self.gate["next_substage"], "9.13")
        self.assertTrue(all(check["passed"] for check in self.gate["checks"]))

    def test_introduction_has_expected_claim_scaffold_without_headings(self) -> None:
        visible = _visible_text(self.introduction)
        self.assertNotIn("#", visible)
        self.assertNotIn("##", visible)
        for phrase in [
            "PARA-INTRO-001",
            "PARA-INTRO-002",
            "CLM-0001",
            "CLM-0002",
            "REF-0001",
            "REF-0011",
            "residence-state",
            "bounded-coupling",
            "reserve-like",
            "routed-output",
            "reproducibility",
        ]:
            self.assertIn(phrase, self.introduction)

    def test_reference_tokens_match_resolved_citation_ledger(self) -> None:
        visible_refs = set(re.findall(r"REF-\d{4}", _visible_text(self.introduction)))
        ledger_refs = {row["ref_id"] for row in self.ledger_rows}
        self.assertEqual(visible_refs, ledger_refs)
        self.assertEqual(len(ledger_refs), 11)
        for row in self.ledger_rows:
            self.assertEqual(row["resolved"], "true")
            self.assertRegex(row["doi_or_pmid"], r"^(10\.\d+/.+|PMID:\d+)$")
            self.assertTrue((ROOT / row["source_file"]).exists(), row["source_file"])

    def test_source_mix_is_methods_and_dataset_only_under_review_threshold(self) -> None:
        source_types = {row["source_type"] for row in self.ledger_rows}
        self.assertEqual(source_types, {"methods", "dataset"})
        review_count = sum(row["source_type"] == "review" for row in self.ledger_rows)
        self.assertLessEqual(review_count / len(self.ledger_rows), 0.25)

    def test_claim_boundaries_and_downstream_surfaces_hold(self) -> None:
        visible = _visible_text(self.introduction)
        for forbidden in [
            "universal",
            "guarantees",
            "therapeutic",
            "clinical",
            "diagnostic",
            "RhoDyn generated the original",
            "absence of all coupling",
            "proof of no crosstalk",
            "true biological reserve",
            "literal molecular edge",
        ]:
            self.assertNotIn(forbidden, visible)
        for rel in [
            "refs/references.bib",
            "submission_package/pi_review_packet.md",
            "submission_package/submission_readiness_checklist.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
