"""Regression checks for the Stage 9.7 supplementary display plan."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


class Stage97SupplementaryDisplayPlanTests(unittest.TestCase):
    def test_gate_records_supplementary_plan_boundary(self) -> None:
        gate = json.loads((WORKSPACE / "gate_verdicts" / "9.7.json").read_text(encoding="utf-8"))
        self.assertTrue(gate["pass"])
        self.assertEqual(gate["substage"], "9.7")
        self.assertEqual(gate["supplementary_item_count"], 9)
        self.assertEqual(gate["essential_item_count"], 8)
        self.assertEqual(gate["supportive_item_count"], 1)
        self.assertEqual(gate["next_substage"], "9.8")
        check_names = {row["name"] for row in gate["checks"]}
        for expected in {
            "stage_9_6b_gate_passed",
            "supplementary_ledger_validates",
            "each_item_has_callout_and_role",
            "essential_items_have_main_text_callouts",
            "central_evidence_remains_in_main_figures",
            "manifest_contains_nonrendered_supplementary_plan",
            "no_downstream_stage9_surfaces_started",
        }:
            self.assertIn(expected, check_names)
        self.assertTrue(all(row["passed"] for row in gate["checks"]))

    def test_callout_ledger_has_planned_roles_and_main_figure_links(self) -> None:
        with (WORKSPACE / "ledgers" / "supplementary_callout_ledger.csv").open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 9)
        self.assertEqual([row["supp_id"] for row in rows], [f"SUPP-00{idx}" for idx in range(1, 10)])
        self.assertEqual({row["role"] for row in rows}, {"essential", "supportive"})
        self.assertTrue(all(row["fig_id"] in {f"FIG-00{idx}" for idx in range(1, 7)} for row in rows))
        self.assertEqual([row["tbl_id"] for row in rows], [f"STBL-00{idx}" for idx in range(1, 10)])
        self.assertTrue(all("PARA-" in row["callout_location"] for row in rows if row["role"] == "essential"))

    def test_plan_text_preserves_supplementary_support_boundary(self) -> None:
        body = (WORKSPACE / "supplementary" / "supplementary_item_plan.md").read_text(encoding="utf-8")
        for phrase in [
            "not Supplementary Information prose",
            "not a data dump",
            "SUPP-001",
            "SUPP-009",
            "not proof of no crosstalk",
            "not a direct live metabolic reserve assay",
            "No supplementary display item is rendered in Stage 9.7",
        ]:
            self.assertIn(phrase, body)

    def test_manifest_records_nonrendered_supplementary_metadata(self) -> None:
        manifest = json.loads((WORKSPACE / "figures" / "figures.manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["figures"]), 6)
        self.assertEqual(len(manifest["supplementary_items"]), 9)
        self.assertEqual(manifest["supplementary_plan_status"], "planned_stage9.7_not_rendered")
        self.assertTrue(
            all(item["render_status"] == "not_rendered_stage9.7_plan_only" for item in manifest["supplementary_items"])
        )

    def test_downstream_manuscript_surfaces_are_not_started(self) -> None:
        for rel in [
            "sections/results.md",
            "sections/introduction.md",
            "sections/discussion.md",
            "sections/methods.md",
            "sections/abstract.md",
            "refs/references.bib",
            "submission_package/pi_review_packet.md",
            "submission_package/submission_readiness_checklist.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
