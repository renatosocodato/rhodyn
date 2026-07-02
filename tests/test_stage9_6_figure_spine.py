"""Regression checks for Stage 9.6 figure-first manuscript-spine registration."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class Stage96FigureSpineTests(unittest.TestCase):
    def test_stage9_6_gate_passes_with_expected_predicates(self) -> None:
        gate_path = WORKSPACE / "gate_verdicts" / "9.6.json"
        self.assertTrue(gate_path.exists())
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        self.assertTrue(gate.get("pass"))
        self.assertEqual(gate.get("substage"), "9.6")
        self.assertEqual(gate.get("main_display_count"), 6)
        self.assertEqual(gate.get("main_display_budget"), 6)
        check_names = {check.get("name") for check in gate.get("checks", [])}
        for name in {
            "stage_9_5_gate_passed",
            "figure_ledger_validates",
            "every_figure_resolves_to_claims_and_artifacts",
            "figure_count_respects_sourced_budget",
            "central_evidence_is_not_buried_in_supplement",
            "rendering_is_deferred_to_stage_9_6b",
            "no_downstream_stage9_surfaces_started",
        }:
            self.assertIn(name, check_names)
        self.assertTrue(all(check.get("passed") for check in gate.get("checks", [])))

    def test_figure_ledger_resolves_to_claims_and_locked_artifacts(self) -> None:
        figure_rows = _csv_rows(WORKSPACE / "ledgers" / "figure_to_claim_to_artifact.csv")
        claim_rows = {row["claim_id"]: row for row in _csv_rows(WORKSPACE / "ledgers" / "claim_hierarchy.csv")}
        artifact_rows = {row["art_id"]: row for row in _csv_rows(WORKSPACE / "ledgers" / "stage9_evidence_manifest.csv")}
        self.assertEqual([row["fig_id"] for row in figure_rows], [f"FIG-00{idx}" for idx in range(1, 7)])
        all_claims = set()
        for row in figure_rows:
            self.assertEqual(row["placement"], "main")
            self.assertEqual(row["engine_version"], "panelforge-figures@v3.14.1")
            self.assertEqual(row["engine_commit"], "d8ab4c5d25be6243aa7209ad1ee6af144820c920")
            self.assertEqual(row["drift_ok"], "accepted_stage9.6b")
            self.assertEqual(row["stat_ids"], "pending_stage9.22")
            self.assertTrue(row["render_path"].endswith(f"{row['fig_id']}/{row['fig_id']}.svg"))
            self.assertTrue((ROOT / row["render_path"]).exists())
            self.assertTrue(row["recipe"].startswith("panelforge:"))
            self.assertTrue(row["panel_structure"])
            self.assertTrue(row["rejected_alternative"])
            row_claims = set(row["claim_id"].split(";"))
            row_artifacts = set(row["art_ids"].split(";"))
            self.assertTrue(row_claims.issubset(claim_rows))
            self.assertTrue(row_artifacts.issubset(artifact_rows))
            self.assertTrue(all(artifact_rows[artifact_id]["status"] == "locked" for artifact_id in row_artifacts))
            all_claims.update(row_claims)
        self.assertEqual(all_claims, set(claim_rows))

    def test_main_spine_and_display_plan_record_rendering_boundary(self) -> None:
        spine = (WORKSPACE / "figures" / "main_figure_spine.md").read_text(encoding="utf-8")
        plan = (WORKSPACE / "figures" / "display_item_plan.md").read_text(encoding="utf-8")
        plan_flat = " ".join(plan.split())
        for phrase in [
            "FIG-001",
            "FIG-006",
            "not a rendered figure set",
            "central evidence",
            "Stage 9.6b",
        ]:
            self.assertIn(phrase, spine)
        for phrase in [
            "Use six main display items",
            "All five frozen central claims appear",
            "PanelForge rendering is deferred",
            "No supplementary figure is created in Stage 9.6",
        ]:
            self.assertIn(phrase, plan_flat)

    def test_stage9_6b_rendering_does_not_start_manuscript_surfaces(self) -> None:
        for rel in [
            "sections/results.md",
            "sections/introduction.md",
            "sections/discussion.md",
            "sections/methods.md",
            "refs/references.bib",
            "submission_package/pi_review_packet.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists())
        rendered = [
            path
            for path in (WORKSPACE / "figures" / "rendered").rglob("*")
            if path.is_file() and path.suffix.lower() in {".png", ".pdf", ".svg"}
        ]
        self.assertEqual(len(rendered), 18)
        self.assertTrue((WORKSPACE / "figures" / ".panelforge_commit").exists())
        self.assertTrue((WORKSPACE / "audits" / "panelforge_render_report.md").exists())


if __name__ == "__main__":
    unittest.main()
