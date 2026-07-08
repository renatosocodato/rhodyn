"""Regression tests for Stage 10.17 no-send message integrity."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_17_message_integrity.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_message_integrity"
GATE = OUTPUT_DIR / "stage10_17_gate_report.json"
MANIFEST = OUTPUT_DIR / "stage10_17_message_manifest.tsv"
AUDIT = OUTPUT_DIR / "stage10_17_message_integrity_audit.tsv"
BOUNDARY = OUTPUT_DIR / "stage10_17_no_send_boundary_scan.tsv"
POLISHED_QUERY = OUTPUT_DIR / "stage10_17_presubmission_query_polished_AUTHOR_REVIEW_REQUIRED.md"
POLISHED_PITCH = OUTPUT_DIR / "stage10_17_one_page_pitch_polished.md"
MEMORY = ROOT / "docs" / "roadmap_execution_memory.json"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_17_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage1017MessageIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _load_runner().run_stage10_17()
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))
        cls.query = POLISHED_QUERY.read_text(encoding="utf-8")
        cls.pitch = POLISHED_PITCH.read_text(encoding="utf-8")
        with MANIFEST.open(newline="", encoding="utf-8") as handle:
            cls.manifest = list(csv.DictReader(handle, delimiter="\t"))
        with AUDIT.open(newline="", encoding="utf-8") as handle:
            cls.audit = list(csv.DictReader(handle, delimiter="\t"))
        with BOUNDARY.open(newline="", encoding="utf-8") as handle:
            cls.boundary = list(csv.DictReader(handle, delimiter="\t"))

    def test_gate_passes_without_external_contact(self) -> None:
        self.assertEqual(self.gate["stage"], "10.17")
        self.assertEqual(self.gate["status"], "pass")
        self.assertTrue(all(self.gate["gates"].values()))
        self.assertEqual(self.gate["external_contact_status"], "not_sent")
        self.assertIn("no-send message-integrity pass", self.gate["interpretation_boundary"])

    def test_polished_surfaces_are_candidate_only_and_author_scoped(self) -> None:
        self.assertIn("Author review required", self.query)
        self.assertIn(
            "[Author name, affiliation, and contact details to be completed by the corresponding author]",
            self.query,
        )
        self.assertIn("Would this scope fit Nature Methods for presubmission evaluation?", self.query)
        self.assertIn("Residual boundaries for the editor-facing version", self.pitch)
        self.assertIn("not a prospective blinded collaborator study", self.pitch)
        send_surface = {row["surface"]: row["send_surface"] for row in self.manifest}
        self.assertEqual(send_surface["polished_query"], "candidate_after_author_approval")
        self.assertEqual(send_surface["polished_pitch"], "candidate_after_author_approval")

    def test_audit_and_boundary_rows_all_pass(self) -> None:
        self.assertEqual(len(self.audit), 10)
        self.assertTrue(all(row["status"] == "pass" for row in self.audit))
        self.assertEqual(len(self.boundary), 7)
        self.assertTrue(all(row["status"] == "pass" for row in self.boundary))
        self.assertEqual(self.gate["summary_metrics"]["audit_pass_count"], 10)
        self.assertEqual(self.gate["summary_metrics"]["boundary_pass_count"], 7)
        self.assertLessEqual(self.gate["summary_metrics"]["polished_query_words"], 260)
        self.assertLessEqual(self.gate["summary_metrics"]["polished_pitch_words"], 320)

    def test_no_send_and_no_new_science_boundaries_are_explicit(self) -> None:
        boundaries = {row["boundary_id"]: row for row in self.boundary}
        self.assertEqual(boundaries["B-001"]["status"], "pass")
        self.assertIn("unsent", boundaries["B-001"]["boundary"])
        self.assertIn("candidate review text", boundaries["B-003"]["boundary"])
        self.assertIn("No new data, figures, benchmarks, or manuscript claims", boundaries["B-007"]["boundary"])
        forbidden = [
            "/" + "Users/",
            "/" + "Volumes/",
            "Library/" + "LaunchAgents",
            "BEGIN PRIVATE",
            "API_KEY",
            "TOKEN",
            "SECRET",
        ]
        combined = self.query + "\n" + self.pitch
        for phrase in forbidden:
            self.assertNotIn(phrase, combined)

    def test_roadmap_memory_marks_stage10_17(self) -> None:
        memory = json.loads(MEMORY.read_text(encoding="utf-8"))
        current = memory["current_position"]
        self.assertEqual(
            current["active_stage"],
            "Stage 10.17 message integrity complete; external contact remains not sent",
        )
        self.assertEqual(
            current["next_stage"],
            "Corresponding-author review of polished presubmission text, sender metadata, and route approval",
        )
        stage10 = next(entry for entry in memory["stage_lock"] if entry.get("stage") == 10)
        self.assertEqual(stage10["status"], "stage10_17_complete_message_integrity")
        subphase = next(item for item in stage10["subphases"] if item.get("id") == "10.17")
        self.assertEqual(subphase["status"], "complete_message_integrity")
        self.assertIn(
            "case_studies/stage10_message_integrity/stage10_17_gate_report.json",
            stage10["artifacts"],
        )


if __name__ == "__main__":
    unittest.main()
