"""Regression tests for Stage 10.19 full-chain no-send closeout."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_19_full_chain_closeout.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_full_chain_closeout"
GATE = OUTPUT_DIR / "stage10_19_gate_report.json"
PHASE_MATRIX = OUTPUT_DIR / "stage10_19_phase_closeout_matrix.tsv"
NO_SEND_BOUNDARY = OUTPUT_DIR / "stage10_19_no_send_boundary_scan.tsv"
AUTHOR_ACTIONS = OUTPUT_DIR / "stage10_19_author_action_carryforward.tsv"
MANIFEST = OUTPUT_DIR / "stage10_19_closeout_manifest.tsv"
REPORT = OUTPUT_DIR / "stage10_19_closeout_report.md"
MEMORY = ROOT / "docs" / "roadmap_execution_memory.json"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_19_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class Stage1019FullChainCloseoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _load_runner().run_stage10_19()
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))
        cls.phase_matrix = _read_tsv(PHASE_MATRIX)
        cls.boundary = _read_tsv(NO_SEND_BOUNDARY)
        cls.author_actions = _read_tsv(AUTHOR_ACTIONS)
        cls.manifest = _read_tsv(MANIFEST)
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.memory = json.loads(MEMORY.read_text(encoding="utf-8"))

    def test_gate_passes_without_external_contact(self) -> None:
        self.assertEqual(self.gate["stage"], "10.19")
        self.assertEqual(self.gate["status"], "pass")
        self.assertTrue(all(self.gate["gates"].values()))
        self.assertEqual(self.gate["external_contact_status"], "not_sent")
        self.assertEqual(
            self.gate["recommendation"],
            "presubmission_query_after_corresponding_author_approval",
        )
        self.assertIn("no-send closeout", self.gate["interpretation_boundary"])

    def test_phase_matrix_closes_all_stage10_subphases(self) -> None:
        self.assertEqual(len(self.phase_matrix), 19)
        self.assertEqual(self.phase_matrix[0]["subphase"], "10.0")
        self.assertEqual(self.phase_matrix[-1]["subphase"], "10.18")
        self.assertTrue(all(row["exists"] == "yes" for row in self.phase_matrix))
        self.assertTrue(all(row["gate_pass"] == "yes" for row in self.phase_matrix))
        self.assertEqual(self.gate["summary_metrics"]["audited_subphase_count"], 19)
        self.assertEqual(self.gate["summary_metrics"]["subphase_pass_count"], 19)

    def test_no_send_boundaries_and_author_actions_are_carried_forward(self) -> None:
        self.assertEqual(len(self.boundary), 9)
        self.assertTrue(all(row["status"] == "pass" for row in self.boundary))
        self.assertEqual(len(self.author_actions), 9)
        required = [
            row
            for row in self.author_actions
            if row["carryforward_decision"] == "human_required_before_any_external_action"
        ]
        self.assertEqual(len(required), 5)
        self.assertEqual(self.gate["summary_metrics"]["required_author_action_count"], 5)
        self.assertEqual(self.gate["summary_metrics"]["route_count"], 4)

    def test_manifest_and_report_are_complete_and_clean(self) -> None:
        self.assertEqual(len(self.manifest), 6)
        self.assertTrue(all(row["exists"] == "yes" and row["sha256"] for row in self.manifest))
        self.assertIn("does not add biological systems", self.report)
        self.assertIn("corresponding-author approval", self.report)
        forbidden = [
            "/" + "Users/",
            "/" + "Volumes/",
            "Library/" + "LaunchAgents",
            "API_KEY",
            "TOKEN",
            "SECRET",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, self.report)

    def test_roadmap_memory_marks_stage10_19(self) -> None:
        current = self.memory["current_position"]
        self.assertEqual(
            current["active_stage"],
            "Stage 10.19 full-chain closeout complete; external contact remains not sent",
        )
        stage10 = next(entry for entry in self.memory["stage_lock"] if entry.get("stage") == 10)
        self.assertEqual(stage10["status"], "stage10_19_complete_full_chain_closeout")
        subphase = next(item for item in stage10["subphases"] if item.get("id") == "10.19")
        self.assertEqual(subphase["status"], "complete_full_chain_closeout")
        self.assertIn(
            "case_studies/stage10_full_chain_closeout/stage10_19_gate_report.json",
            stage10["artifacts"],
        )


if __name__ == "__main__":
    unittest.main()
