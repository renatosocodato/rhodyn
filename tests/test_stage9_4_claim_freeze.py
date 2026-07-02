"""Regression checks for Stage 9.4 claim-freeze registration."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


class Stage94ClaimFreezeTests(unittest.TestCase):
    def test_stage9_4_gate_passes_with_expected_predicates(self) -> None:
        gate_path = WORKSPACE / "gate_verdicts" / "9.4.json"
        self.assertTrue(gate_path.exists())
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        self.assertTrue(gate.get("pass"))
        self.assertEqual(gate.get("substage"), "9.4")
        self.assertEqual(gate.get("claim_count"), 5)
        self.assertGreaterEqual(gate.get("non_claim_count", 0), 5)
        check_names = {check.get("name") for check in gate.get("checks", [])}
        for name in {
            "stage_9_3_gate_passed",
            "claim_hierarchy_validates",
            "every_central_claim_has_evidence",
            "every_claim_has_strength_cap",
            "non_claims_ledger_is_non_empty",
            "no_downstream_stage9_surfaces_started",
        }:
            self.assertIn(name, check_names)
        self.assertTrue(all(check.get("passed") for check in gate.get("checks", [])))

    def test_claim_hierarchy_csv_has_stable_claims_and_strength_caps(self) -> None:
        csv_path = WORKSPACE / "ledgers" / "claim_hierarchy.csv"
        self.assertTrue(csv_path.exists())
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([row["claim_id"] for row in rows], [f"CLM-000{idx}" for idx in range(1, 6)])
        for row in rows:
            self.assertTrue(row["evidence_art_ids"].startswith("ART-"))
            self.assertIn("pending_stage9.6", row["fig_ids"])
            self.assertTrue(row["strength_cap"])
            self.assertTrue(row["confidence"])

    def test_claim_markdown_and_non_claims_preserve_boundaries(self) -> None:
        claim_md = (WORKSPACE / "ledgers" / "claim_hierarchy.md").read_text(encoding="utf-8")
        non_claims = (WORKSPACE / "ledgers" / "non_claims_and_scope_boundaries.md").read_text(encoding="utf-8")
        for phrase in [
            "Residence-window summaries",
            "Bounded-coupling decisions",
            "Reserve-like summaries",
            "Reduced-architecture comparison",
            "source distribution",
        ]:
            self.assertIn(phrase, claim_md)
        for phrase in [
            "RhoDyn did not generate the original RhoA/microglia manuscript results",
            "Bounded coupling is not proof of no crosstalk",
            "Reserve-like summaries are not automatically biological reserve",
            "Reduced-architecture parameters are not literal molecular edges",
        ]:
            self.assertIn(phrase, non_claims)

    def test_stage9_4_does_not_start_downstream_manuscript_surfaces(self) -> None:
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
