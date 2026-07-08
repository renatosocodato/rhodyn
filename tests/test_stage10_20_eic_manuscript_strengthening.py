"""Regression tests for Stage 10.20 EIC/manuscript strengthening."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_20_eic_manuscript_strengthening.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_eic_manuscript_strengthening"
GATE = OUTPUT_DIR / "stage10_20_gate_report.json"
RUBRIC = OUTPUT_DIR / "stage10_20_eic_rubric_crosswalk.tsv"
STAGE_MATRIX = OUTPUT_DIR / "stage10_20_stage10_6_onward_matrix.tsv"
FIGURE_STRENGTHENING = OUTPUT_DIR / "stage10_20_rendered_figure_strengthening.tsv"
PROSPECTIVE_JSON = OUTPUT_DIR / "stage10_20_prospective_validation_predeclaration.json"
PROSPECTIVE_MD = OUTPUT_DIR / "stage10_20_prospective_validation_predeclaration.md"
BOUNDARY_SCAN = OUTPUT_DIR / "stage10_20_boundary_scan.tsv"
MANIFEST = OUTPUT_DIR / "stage10_20_manifest.tsv"
REPORT = OUTPUT_DIR / "stage10_20_strengthening_report.md"
DOC = ROOT / "docs" / "stage10_20_eic_manuscript_strengthening.md"
MEMORY = ROOT / "docs" / "roadmap_execution_memory.json"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_20_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class Stage1020EicManuscriptStrengtheningTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _load_runner().run_stage10_20()
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))
        cls.rubric = _read_tsv(RUBRIC)
        cls.stage_matrix = _read_tsv(STAGE_MATRIX)
        cls.figure_strengthening = _read_tsv(FIGURE_STRENGTHENING)
        cls.prospective = json.loads(PROSPECTIVE_JSON.read_text(encoding="utf-8"))
        cls.prospective_md = PROSPECTIVE_MD.read_text(encoding="utf-8")
        cls.boundary = _read_tsv(BOUNDARY_SCAN)
        cls.manifest = _read_tsv(MANIFEST)
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.doc = DOC.read_text(encoding="utf-8")
        cls.memory = json.loads(MEMORY.read_text(encoding="utf-8"))

    def test_gate_passes_without_external_contact(self) -> None:
        self.assertEqual(self.gate["stage"], "10.20")
        self.assertEqual(self.gate["status"], "pass")
        self.assertTrue(all(self.gate["gates"].values()))
        self.assertEqual(self.gate["external_contact_status"], "not_sent")
        self.assertEqual(
            self.gate["recommendation"],
            "presubmission_query_after_corresponding_author_approval",
        )
        self.assertIn("does not add data", self.gate["interpretation_boundary"])

    def test_parent_subphases_and_eic_rubric_pass(self) -> None:
        self.assertEqual(len(self.stage_matrix), 14)
        self.assertEqual(self.stage_matrix[0]["subphase"], "10.6")
        self.assertEqual(self.stage_matrix[-1]["subphase"], "10.19")
        self.assertTrue(all(row["exists"] == "yes" for row in self.stage_matrix))
        self.assertTrue(all(row["gate_pass"] == "yes" for row in self.stage_matrix))
        self.assertEqual(len(self.rubric), 11)
        self.assertTrue(all(row["status"] == "pass" for row in self.rubric))
        rubric_ids = {row["rubric_id"] for row in self.rubric}
        self.assertTrue({"R-106-001", "R-112-001", "R-112-002"}.issubset(rubric_ids))

    def test_rendered_figures_are_bound_to_author_review(self) -> None:
        self.assertEqual(len(self.figure_strengthening), 6)
        self.assertTrue(
            all(row["decision"] == "ready_for_author_visual_acceptance" for row in self.figure_strengthening)
        )
        self.assertTrue(all(row["packet_reference_status"] == "referenced" for row in self.figure_strengthening))
        self.assertEqual(self.gate["summary_metrics"]["review_figure_count"], 6)
        self.assertEqual(self.gate["summary_metrics"]["ready_review_figure_count"], 6)

    def test_prospective_validation_stays_optional_new_evidence(self) -> None:
        self.assertEqual(self.prospective["status"], "predeclared_optional_new_evidence")
        self.assertIs(self.prospective["not_a_completed_result"], True)
        self.assertEqual(self.prospective["external_contact_status"], "not_sent")
        self.assertIn("inconclusive_or_abstain", self.prospective["decision_states"])
        self.assertIn("not a completed validation result", self.prospective_md)
        self.assertIn("optional new-evidence lane", self.prospective_md)

    def test_boundaries_manifest_and_reader_surfaces_are_clean(self) -> None:
        self.assertEqual(len(self.boundary), 7)
        self.assertTrue(all(row["status"] == "pass" for row in self.boundary))
        self.assertEqual(len(self.manifest), 8)
        self.assertTrue(all(row["exists"] == "yes" and row["sha256"] for row in self.manifest))
        forbidden_local_path = "/" + "Users/"
        forbidden_volume_path = "/" + "Volumes/"
        forbidden_launchagent_path = "Library/" + "LaunchAgents"
        for body in [self.report, self.doc, self.prospective_md]:
            self.assertNotIn(forbidden_local_path, body)
            self.assertNotIn(forbidden_volume_path, body)
            self.assertNotIn(forbidden_launchagent_path, body)
            self.assertNotIn("API_KEY", body)
            self.assertNotIn("TOKEN", body)
            self.assertNotIn("SECRET", body)

    def test_roadmap_memory_marks_stage10_20(self) -> None:
        current = self.memory["current_position"]
        self.assertEqual(
            current["active_stage"],
            "Stage 10.20 EIC/manuscript strengthening complete; external contact remains not sent",
        )
        stage10 = next(entry for entry in self.memory["stage_lock"] if entry.get("stage") == 10)
        self.assertEqual(stage10["status"], "stage10_20_complete_eic_manuscript_strengthening")
        subphase = next(item for item in stage10["subphases"] if item.get("id") == "10.20")
        self.assertEqual(subphase["status"], "complete_eic_manuscript_strengthening")
        self.assertIn(
            "case_studies/stage10_eic_manuscript_strengthening/stage10_20_gate_report.json",
            stage10["artifacts"],
        )


if __name__ == "__main__":
    unittest.main()
