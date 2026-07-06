"""Regression checks for the Stage 9.9 title and abstract strategy."""

from __future__ import annotations

import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


def _abstract_text() -> str:
    body = (WORKSPACE / "sections" / "abstract.md").read_text(encoding="utf-8")
    if "## Abstract" in body:
        return body.split("## Abstract", 1)[1].strip()
    return body.split("# Abstract", 1)[1].strip()


class Stage99TitleAbstractStrategyTests(unittest.TestCase):
    def test_gate_records_front_matter_strategy_boundary(self) -> None:
        gate = json.loads((WORKSPACE / "gate_verdicts" / "9.9.json").read_text(encoding="utf-8"))
        self.assertTrue(gate["pass"])
        self.assertEqual(gate["substage"], "9.9")
        self.assertEqual(gate["title_option_count"], 4)
        self.assertEqual(gate["preferred_title_option"], "TITLE-001")
        self.assertLessEqual(gate["abstract_word_count"], 150)
        self.assertEqual(gate["abstract_word_limit"], 150)
        self.assertTrue(gate["abstract_unreferenced"])
        self.assertEqual(
            gate["abstract_claim_ids"],
            ["CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"],
        )
        self.assertEqual(gate["next_substage"], "9.10")
        self.assertTrue(all(row["passed"] for row in gate["checks"]))

    def test_title_options_are_claim_bounded(self) -> None:
        body = (WORKSPACE / "sections" / "title_options.md").read_text(encoding="utf-8")
        for phrase in [
            "RhoDyn infers residence states in live-cell perturbation data",
            "preferred working option",
            "TITLE-002",
            "TITLE-003",
            "TITLE-004",
            "Does not imply that every dataset contains a residence regime",
            "not a submission title decision",
        ]:
            self.assertIn(phrase, body)

    def test_abstract_strategy_keeps_the_venue_budget_and_claim_map(self) -> None:
        body = (WORKSPACE / "sections" / "abstract_strategy.md").read_text(encoding="utf-8")
        for phrase in [
            "150 words and is",
            "unreferenced",
            "CLM-0001;CLM-0002;CLM-0003;CLM-0004",
            "CLM-0005",
            "not automatically discovered",
            "bounded-coupling",
            "not a submission package",
        ]:
            self.assertIn(phrase, body)

    def test_abstract_is_unreferenced_and_scoped(self) -> None:
        abstract = _abstract_text()
        words = re.findall(r"\b[\w-]+\b", abstract)
        self.assertLessEqual(len(words), 150)
        for phrase in [
            "RhoDyn is a computational method",
            "residence-state inference",
            "bounded coupling under declared margins",
            "measurement-scoped reserve-like endpoint summaries",
            "routed-output alternatives",
            "matched, inspectable outputs",
            "literal mechanism",
        ]:
            self.assertIn(phrase, abstract)
        for forbidden in [
            "doi:",
            "http://",
            "https://",
            "REF-",
            "universal mechanism",
            "therapeutic",
            "clinical",
            "diagnostic",
            "RhoDyn generated the original",
        ]:
            self.assertNotIn(forbidden, abstract)
        self.assertIsNone(re.search(r"\(\d+(?:-\d+|,\s*\d+)*\)", abstract))

    def test_downstream_manuscript_surfaces_remain_absent(self) -> None:
        for rel in [
            "submission_package/pi_review_packet.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
