"""Regression tests for Stage 10.18 author approval dossier."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_18_author_approval_dossier.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_author_approval_dossier"
GATE = OUTPUT_DIR / "stage10_18_gate_report.json"
DOSSIER = OUTPUT_DIR / "stage10_18_corresponding_author_approval_dossier_AUTHOR_ACTION_REQUIRED.md"
CHECKLIST = OUTPUT_DIR / "stage10_18_corresponding_author_approval_checklist.tsv"
ROUTE_LOCK = OUTPUT_DIR / "stage10_18_submission_route_lock.tsv"
MANIFEST = OUTPUT_DIR / "stage10_18_dossier_manifest.tsv"
BOUNDARY = OUTPUT_DIR / "stage10_18_no_send_boundary_scan.tsv"
MEMORY = ROOT / "docs" / "roadmap_execution_memory.json"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_18_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage1018AuthorApprovalDossierTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _load_runner().run_stage10_18()
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))
        cls.dossier = DOSSIER.read_text(encoding="utf-8")
        with CHECKLIST.open(newline="", encoding="utf-8") as handle:
            cls.checklist = list(csv.DictReader(handle, delimiter="\t"))
        with ROUTE_LOCK.open(newline="", encoding="utf-8") as handle:
            cls.routes = list(csv.DictReader(handle, delimiter="\t"))
        with MANIFEST.open(newline="", encoding="utf-8") as handle:
            cls.manifest = list(csv.DictReader(handle, delimiter="\t"))
        with BOUNDARY.open(newline="", encoding="utf-8") as handle:
            cls.boundary = list(csv.DictReader(handle, delimiter="\t"))

    def test_gate_passes_without_external_contact(self) -> None:
        self.assertEqual(self.gate["stage"], "10.18")
        self.assertEqual(self.gate["status"], "pass")
        self.assertTrue(all(self.gate["gates"].values()))
        self.assertEqual(self.gate["external_contact_status"], "not_sent")
        self.assertEqual(
            self.gate["recommendation"],
            "presubmission_query_after_corresponding_author_approval",
        )
        self.assertIn("no-send author-approval dossier", self.gate["interpretation_boundary"])

    def test_author_checklist_retains_required_human_decisions(self) -> None:
        self.assertEqual(len(self.checklist), 9)
        required_author = [
            row for row in self.checklist if row["required"] == "yes" and row["current_status"] == "author_required"
        ]
        self.assertEqual(len(required_author), 5)
        items = {row["item_id"]: row["decision_item"] for row in self.checklist}
        self.assertIn("Approve the presubmission route or choose an alternative", items["CAA-001"])
        self.assertIn("Complete sender identity", items["CAA-004"])
        self.assertIn("Confirm external contact remains manual", items["CAA-009"])

    def test_route_lock_keeps_presubmission_recommended_and_unsent(self) -> None:
        routes = {row["route"]: row for row in self.routes}
        self.assertEqual(routes["presubmission_query"]["local_status"], "recommended_after_author_approval")
        self.assertEqual(routes["full_submission"]["local_status"], "author_override_only")
        self.assertEqual(routes["delay_for_new_external_validation"]["local_status"], "optional_new_evidence")
        self.assertTrue(all(row["send_status"] == "not_sent" for row in self.routes))

    def test_manifest_and_boundaries_are_complete(self) -> None:
        self.assertEqual(len(self.manifest), 10)
        self.assertTrue(all(row["exists"] == "yes" and row["sha256"] for row in self.manifest))
        self.assertEqual(len(self.boundary), 9)
        self.assertTrue(all(row["status"] == "pass" for row in self.boundary))
        self.assertEqual(self.gate["summary_metrics"]["manifest_row_count"], 10)
        self.assertEqual(self.gate["summary_metrics"]["boundary_pass_count"], 9)

    def test_dossier_preserves_author_and_claim_boundaries(self) -> None:
        for phrase in [
            "Author action required",
            "Use the presubmission query route only after corresponding-author approval",
            "cannot approve the sender identity",
            "does not claim that every live-cell system contains a residence regime",
            "prospective blinded collaborator validation has already been completed",
        ]:
            self.assertIn(phrase, self.dossier)
        forbidden = [
            "/" + "Users/",
            "/" + "Volumes/",
            "Library/" + "LaunchAgents",
            "API_KEY",
            "TOKEN",
            "SECRET",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, self.dossier)

    def test_roadmap_memory_marks_stage10_18(self) -> None:
        memory = json.loads(MEMORY.read_text(encoding="utf-8"))
        current = memory["current_position"]
        self.assertEqual(
            current["active_stage"],
            "Stage 10.18 author approval dossier complete; external contact remains not sent",
        )
        stage10 = next(entry for entry in memory["stage_lock"] if entry.get("stage") == 10)
        self.assertEqual(stage10["status"], "stage10_18_complete_author_approval_dossier")
        subphase = next(item for item in stage10["subphases"] if item.get("id") == "10.18")
        self.assertEqual(subphase["status"], "complete_author_approval_dossier")
        self.assertIn(
            "case_studies/stage10_author_approval_dossier/stage10_18_gate_report.json",
            stage10["artifacts"],
        )


if __name__ == "__main__":
    unittest.main()
