"""Regression checks for the Stage 9.10 Results subsection architecture."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


class Stage910ResultsArchitectureTests(unittest.TestCase):
    def test_gate_records_results_architecture_boundary(self) -> None:
        gate = json.loads((WORKSPACE / "gate_verdicts" / "9.10.json").read_text(encoding="utf-8"))
        self.assertTrue(gate["pass"])
        self.assertEqual(gate["substage"], "9.10")
        self.assertEqual(gate["results_unit_count"], 6)
        self.assertEqual(gate["figure_ids"], ["FIG-001", "FIG-002", "FIG-003", "FIG-004", "FIG-005", "FIG-006"])
        self.assertEqual(gate["next_substage"], "9.11")
        self.assertEqual(
            gate["claim_ids"],
            ["CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"],
        )
        self.assertEqual(
            gate["paragraph_ids"],
            [
                "PARA-RESULTS-001",
                "PARA-RESULTS-002",
                "PARA-RESULTS-003",
                "PARA-RESULTS-004",
                "PARA-RESULTS-005",
                "PARA-RESULTS-006",
            ],
        )
        self.assertGreaterEqual(gate["art_id_count"], 30)
        self.assertTrue(all(row["passed"] for row in gate["checks"]))
        self.assertIn("No Results prose", gate["scope_boundary"])

    def test_results_blueprint_is_figure_locked_and_evidence_bearing(self) -> None:
        body = (WORKSPACE / "sections" / "results_blueprint.md").read_text(encoding="utf-8")
        for phrase in [
            "Results unit map",
            "FIG-001",
            "FIG-002",
            "FIG-003",
            "FIG-004",
            "FIG-005",
            "FIG-006",
            "ART-0025",
            "ART-0053",
            "Allowed conclusion",
            "Strength cap",
            "Prohibited overclaim",
            "not Results prose",
        ]:
            self.assertIn(phrase, body)
        self.assertLess(body.index("| RES-001 |"), body.index("| RES-002 |"))
        self.assertLess(body.index("| RES-002 |"), body.index("| RES-003 |"))
        self.assertLess(body.index("| RES-003 |"), body.index("| RES-004 |"))
        self.assertLess(body.index("| RES-004 |"), body.index("| RES-005 |"))
        self.assertLess(body.index("| RES-005 |"), body.index("| RES-006 |"))

    def test_results_units_preserve_claim_boundaries(self) -> None:
        body = (WORKSPACE / "sections" / "results_blueprint.md").read_text(encoding="utf-8")
        for phrase in [
            "Do not imply that every live-cell dataset contains a residence regime",
            "Do not describe synthetic truth cases as new biological evidence",
            "Do not claim that residence logic replaces amplitude analysis in all reporters",
            "Do not claim absence of all coupling",
            "Do not convert inconclusive or margin-sensitive held-out behavior into equivalence language",
            "Do not claim PyPI publication",
        ]:
            self.assertIn(phrase, body)
        for forbidden in [
            "therapeutic",
            "clinical",
            "diagnostic",
        ]:
            self.assertNotIn(forbidden, body)

    def test_downstream_manuscript_surfaces_remain_absent(self) -> None:
        for rel in [
            "sections/results.md",
            "sections/introduction.md",
            "sections/discussion.md",
            "sections/methods.md",
            "refs/references.bib",
            "submission_package/pi_review_packet.md",
            "submission_package/submission_readiness_checklist.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
