"""Regression tests for Stage 10.21 figure recipe diversification."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_21_figure_recipe_diversification.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_figure_recipe_diversification"
GATE = OUTPUT_DIR / "stage10_21_gate_report.json"
FIGURE_LOGIC = OUTPUT_DIR / "stage10_21_figure_logic_binding.tsv"
PANEL_BINDING = OUTPUT_DIR / "stage10_21_panel_recipe_binding.tsv"
RECIPE_AUDIT = OUTPUT_DIR / "stage10_21_recipe_diversity_audit.tsv"
MANIFEST = OUTPUT_DIR / "stage10_21_manifest.tsv"
REPORT = OUTPUT_DIR / "stage10_21_recipe_diversification_report.md"
DOC = ROOT / "docs" / "stage10_21_figure_recipe_diversification.md"
MEMORY = ROOT / "docs" / "roadmap_execution_memory.json"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_21_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class Stage1021FigureRecipeDiversificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _load_runner().run_stage10_21()
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))
        cls.figure_logic = _read_tsv(FIGURE_LOGIC)
        cls.panel_binding = _read_tsv(PANEL_BINDING)
        cls.recipe_audit = _read_tsv(RECIPE_AUDIT)
        cls.manifest = _read_tsv(MANIFEST)
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.doc = DOC.read_text(encoding="utf-8")
        cls.memory = json.loads(MEMORY.read_text(encoding="utf-8"))

    def test_gate_passes_without_external_contact(self) -> None:
        self.assertEqual(self.gate["stage"], "10.21")
        self.assertEqual(self.gate["status"], "pass")
        self.assertTrue(all(self.gate["gates"].values()))
        self.assertEqual(self.gate["external_contact_status"], "not_sent")
        self.assertIn("does not add data", self.gate["interpretation_boundary"])

    def test_six_figure_jobs_match_blueprint(self) -> None:
        self.assertEqual(len(self.figure_logic), 6)
        self.assertTrue(all(row["status"] == "bound" for row in self.figure_logic))
        jobs = {row["public_label"]: row["figure_job"] for row in self.figure_logic}
        self.assertEqual(jobs["Fig. 1"], "Define the RhoDyn method object and decision divergence.")
        self.assertEqual(jobs["Fig. 2"], "Show synthetic truth and named-baseline benchmarking.")
        self.assertEqual(jobs["Fig. 3"], "Demonstrate public biological breadth.")
        self.assertEqual(
            jobs["Fig. 4"],
            "Demonstrate endpoint, reserve-like, bounded-coupling, and routed-output extension.",
        )
        self.assertEqual(jobs["Fig. 5"], "Show held-out validation and uncertainty boundaries.")
        self.assertEqual(jobs["Fig. 6"], "Show reproducibility and user adoption.")

    def test_all_panels_are_bound_to_recipes_and_motifs(self) -> None:
        self.assertEqual(len(self.panel_binding), 30)
        self.assertTrue(all(row["status"] == "bound" for row in self.panel_binding))
        self.assertTrue(all(row["variation_axis"] for row in self.panel_binding))
        recipe_set = {row["panelforge_recipe"] for row in self.panel_binding}
        motif_set = {row["review_motif"] for row in self.panel_binding}
        self.assertGreaterEqual(len(recipe_set), 7)
        self.assertGreaterEqual(len(motif_set), 24)
        self.assertEqual(self.gate["summary_metrics"]["panel_count"], 30)
        self.assertEqual(self.gate["summary_metrics"]["bound_panel_count"], 30)

    def test_every_figure_passes_diversity_policy(self) -> None:
        self.assertEqual(len(self.recipe_audit), 6)
        self.assertTrue(all(row["status"] == "pass" for row in self.recipe_audit))
        for row in self.recipe_audit:
            self.assertGreaterEqual(int(row["unique_panelforge_recipes"]), 3)
            self.assertGreaterEqual(int(row["unique_review_motifs"]), 4)
            self.assertLessEqual(int(row["max_recipe_reuse"]), 3)
            self.assertLessEqual(int(row["max_motif_reuse"]), 1)
        self.assertEqual(self.gate["summary_metrics"]["diversity_pass_figure_count"], 6)

    def test_manifest_and_reader_surfaces_are_clean(self) -> None:
        self.assertEqual(len(self.manifest), 5)
        self.assertTrue(all(row["exists"] == "yes" and row["sha256"] for row in self.manifest))
        forbidden_local_path = "/" + "Users/"
        forbidden_volume_path = "/" + "Volumes/"
        forbidden_launchagent_path = "Library/" + "LaunchAgents"
        for body in [self.report, self.doc]:
            self.assertNotIn(forbidden_local_path, body)
            self.assertNotIn(forbidden_volume_path, body)
            self.assertNotIn(forbidden_launchagent_path, body)
            self.assertNotIn("API_KEY", body)
            self.assertNotIn("TOKEN", body)
            self.assertNotIn("SECRET", body)

    def test_roadmap_memory_marks_stage10_21(self) -> None:
        current = self.memory["current_position"]
        self.assertEqual(
            current["active_stage"],
            "Stage 10.21 figure recipe diversification complete; external contact remains not sent",
        )
        stage10 = next(entry for entry in self.memory["stage_lock"] if entry.get("stage") == 10)
        self.assertEqual(stage10["status"], "stage10_21_complete_figure_recipe_diversification")
        subphase = next(item for item in stage10["subphases"] if item.get("id") == "10.21")
        self.assertEqual(subphase["status"], "complete_figure_recipe_diversification")
        self.assertIn(
            "case_studies/stage10_figure_recipe_diversification/stage10_21_gate_report.json",
            stage10["artifacts"],
        )


if __name__ == "__main__":
    unittest.main()
