"""Regression tests for Stage 10.16 route-decision triage."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_16_route_decision_triage.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_route_decision_triage"
GATE = OUTPUT_DIR / "stage10_16_gate_report.json"
OPEN_ITEMS = OUTPUT_DIR / "stage10_16_open_item_resolution.tsv"
ROUTES = OUTPUT_DIR / "stage10_16_route_decision_triage.tsv"
BOUNDARY = OUTPUT_DIR / "stage10_16_no_send_boundary_scan.tsv"
RECOMMENDATION = OUTPUT_DIR / "stage10_16_route_recommendation.md"
MEMORY = ROOT / "docs" / "roadmap_execution_memory.json"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_16_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage1016RouteDecisionTriageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _load_runner().run_stage10_16()
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))
        with OPEN_ITEMS.open(newline="", encoding="utf-8") as handle:
            cls.open_items = list(csv.DictReader(handle, delimiter="\t"))
        with ROUTES.open(newline="", encoding="utf-8") as handle:
            cls.routes = list(csv.DictReader(handle, delimiter="\t"))
        with BOUNDARY.open(newline="", encoding="utf-8") as handle:
            cls.boundary = list(csv.DictReader(handle, delimiter="\t"))

    def test_gate_passes_without_external_contact(self) -> None:
        self.assertEqual(self.gate["stage"], "10.16")
        self.assertEqual(self.gate["status"], "pass")
        self.assertTrue(all(self.gate["gates"].values()))
        self.assertEqual(self.gate["external_contact_status"], "not_sent")
        self.assertEqual(self.gate["recommendation"], "presubmission_query_after_author_approval")
        self.assertIn("no-send decision-triage", self.gate["interpretation_boundary"])

    def test_open_items_separate_local_author_and_new_evidence_decisions(self) -> None:
        self.assertEqual(len(self.open_items), self.gate["summary_metrics"]["open_item_count"])
        resolutions = {row["item_id"]: row["codex_resolution"] for row in self.open_items}
        self.assertEqual(resolutions["AVR-002"], "author_only_not_sent")
        self.assertEqual(resolutions["AVR-003"], "author_only_metadata")
        self.assertEqual(resolutions["AVR-010"], "new_evidence_optional_not_blocking")
        local_resolved = [row for row in self.open_items if row["codex_resolution"].startswith("codex_resolved")]
        self.assertEqual(len(local_resolved), 6)

    def test_route_triage_preserves_selected_and_fallback_routes(self) -> None:
        routes = {row["route"]: row for row in self.routes}
        self.assertEqual(
            routes["presubmission_query_author_review_required"]["stage10_16_recommendation"],
            "recommended_next_route_after_author_approval",
        )
        self.assertEqual(
            routes["full_submission"]["stage10_16_recommendation"],
            "viable_only_with_author_override",
        )
        self.assertEqual(
            routes["delay_for_another_dataset"]["stage10_16_recommendation"],
            "optional_new_evidence_not_required_for_presubmission",
        )
        self.assertEqual(
            routes["venue_pivot"]["stage10_16_recommendation"],
            "retain_as_fallback_not_current_route",
        )

    def test_boundary_scan_and_recommendation_preserve_no_send_scope(self) -> None:
        self.assertEqual(len(self.boundary), self.gate["summary_metrics"]["boundary_count"])
        self.assertTrue(all(row["status"] == "pass" for row in self.boundary))
        text = RECOMMENDATION.read_text(encoding="utf-8")
        self.assertIn("Retain the presubmission query", text)
        self.assertIn("not a journal contact", text)
        self.assertIn("not a new scientific result", text)

    def test_roadmap_memory_marks_stage10_16(self) -> None:
        memory = json.loads(MEMORY.read_text(encoding="utf-8"))
        current = memory["current_position"]
        self.assertEqual(
            current["active_stage"],
            "Stage 10.16 route-decision triage complete; external contact remains not sent",
        )
        stage10 = next(entry for entry in memory["stage_lock"] if entry.get("stage") == 10)
        self.assertEqual(stage10["status"], "stage10_16_complete_route_decision_triage")
        subphase = next(item for item in stage10["subphases"] if item.get("id") == "10.16")
        self.assertEqual(subphase["status"], "complete_route_decision_triage")
        self.assertIn(
            "case_studies/stage10_route_decision_triage/stage10_16_gate_report.json",
            stage10["artifacts"],
        )


if __name__ == "__main__":
    unittest.main()
