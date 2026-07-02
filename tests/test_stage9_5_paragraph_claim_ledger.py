"""Regression checks for Stage 9.5 paragraph-level claim-ledger registration."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


class Stage95ParagraphClaimLedgerTests(unittest.TestCase):
    def test_stage9_5_gate_passes_with_expected_predicates(self) -> None:
        gate_path = WORKSPACE / "gate_verdicts" / "9.5.json"
        self.assertTrue(gate_path.exists())
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        self.assertTrue(gate.get("pass"))
        self.assertEqual(gate.get("substage"), "9.5")
        self.assertGreaterEqual(gate.get("paragraph_count", 0), 10)
        self.assertEqual(gate.get("claim_count"), 5)
        check_names = {check.get("name") for check in gate.get("checks", [])}
        for name in {
            "stage_9_4_gate_passed",
            "ledger_validates",
            "every_para_id_resolves_to_clm_id",
            "every_frozen_claim_has_paragraph_coverage",
            "paragraph_strength_does_not_exceed_claim_strength",
            "downstream_surfaces_remain_pending",
            "no_downstream_stage9_surfaces_started",
        }:
            self.assertIn(name, check_names)
        self.assertTrue(all(check.get("passed") for check in gate.get("checks", [])))

    def test_paragraph_claim_ledger_resolves_to_frozen_claims(self) -> None:
        claim_path = WORKSPACE / "ledgers" / "claim_hierarchy.csv"
        paragraph_path = WORKSPACE / "ledgers" / "paragraph_claim_ledger.csv"
        self.assertTrue(paragraph_path.exists())
        with claim_path.open("r", encoding="utf-8", newline="") as handle:
            claims = {row["claim_id"]: row for row in csv.DictReader(handle)}
        with paragraph_path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreaterEqual(len(rows), 10)
        para_ids = [row["para_id"] for row in rows]
        self.assertEqual(len(para_ids), len(set(para_ids)))
        self.assertTrue(all(para_id.startswith("PARA-") for para_id in para_ids))
        self.assertEqual(set(claims), {row["claim_id"] for row in rows})
        for row in rows:
            self.assertIn(row["claim_id"], claims)
            self.assertEqual(row["strength_cap"], claims[row["claim_id"]]["strength_cap"])
            self.assertTrue(row["fig_ids"].startswith("pending_stage9.6"))
            self.assertEqual(row["stat_ids"], "pending_stage9.8")
            self.assertEqual(row["ref_ids"], "pending_stage9.7")
            self.assertTrue(row["purpose"])
            self.assertTrue(row["caveat"])

    def test_strength_rules_define_drafting_boundary(self) -> None:
        rules = (WORKSPACE / "ledgers" / "claim_strength_rules.md").read_text(encoding="utf-8")
        for phrase in [
            "Each paragraph row must resolve to one frozen `CLM` identifier",
            "not exceed the copied `strength_cap`",
            "not manuscript prose",
            "not authorize citation",
        ]:
            self.assertIn(phrase, rules)

    def test_stage9_5_does_not_start_downstream_manuscript_surfaces(self) -> None:
        for rel in [
            "sections/results.md",
            "sections/introduction.md",
            "sections/discussion.md",
            "sections/methods.md",
            "refs/references.bib",
            "submission_package/pi_review_packet.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists())


if __name__ == "__main__":
    unittest.main()
