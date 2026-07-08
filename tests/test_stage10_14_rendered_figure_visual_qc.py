"""Regression tests for Stage 10.14 rendered-figure visual QA."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_14_rendered_figure_visual_qc.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_rendered_figure_visual_qc"
GATE = OUTPUT_DIR / "stage10_14_gate_report.json"
DEFECTS = OUTPUT_DIR / "stage10_14_parent_visual_defect_matrix.tsv"
QC = OUTPUT_DIR / "stage10_14_review_render_visual_qc.tsv"
INVENTORY = OUTPUT_DIR / "stage10_14_review_render_inventory.tsv"
CONTACT_SHEET = OUTPUT_DIR / "stage10_14_review_render_contact_sheet.png"
MEMORY = ROOT / "docs" / "roadmap_execution_memory.json"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_14_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Stage1014RenderedFigureVisualQCTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _load_runner().run_stage10_14()
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))
        with DEFECTS.open(newline="", encoding="utf-8") as handle:
            cls.defects = list(csv.DictReader(handle, delimiter="\t"))
        with QC.open(newline="", encoding="utf-8") as handle:
            cls.qc = list(csv.DictReader(handle, delimiter="\t"))
        with INVENTORY.open(newline="", encoding="utf-8") as handle:
            cls.inventory = list(csv.DictReader(handle, delimiter="\t"))

    def test_gate_passes_after_recording_parent_visual_failure(self) -> None:
        self.assertEqual(self.gate["stage"], "10.14")
        self.assertEqual(self.gate["status"], "pass")
        self.assertTrue(all(self.gate["gates"].values()))
        self.assertEqual(self.gate["external_contact_status"], "not_sent")
        self.assertEqual(self.gate["parent_stage10_13_visual_status"], "failed_visual_review_recorded")
        self.assertEqual(self.gate["review_render_status"], "pass")
        self.assertEqual(self.gate["summary_metrics"]["parent_visual_failure_count"], 6)
        self.assertEqual(self.gate["summary_metrics"]["planned_panel_count"], 30)
        self.assertEqual(self.gate["summary_metrics"]["review_figure_count"], 6)
        self.assertEqual(self.gate["summary_metrics"]["review_rendered_file_count"], 18)
        self.assertIn("readability only", self.gate["interpretation_boundary"])

    def test_parent_defect_matrix_records_all_six_visual_failures(self) -> None:
        self.assertEqual(len(self.defects), 6)
        for row in self.defects:
            self.assertEqual(row["manual_visual_status"], "fail")
            self.assertIn("case_studies/stage10_rendered_figures/rendered/", row["parent_png"])
            self.assertTrue((ROOT / row["parent_png"]).exists())
            self.assertGreater(len(row["defect_summary"]), 30)
            self.assertIn("review figure", row["correction_strategy"])

    def test_review_inventory_records_six_figures_and_three_formats_each(self) -> None:
        self.assertEqual(len(self.inventory), 18)
        by_fig: dict[str, set[str]] = {}
        for row in self.inventory:
            path = ROOT / row["path"]
            self.assertTrue(path.exists(), row["path"])
            self.assertTrue(row["path"].startswith("case_studies/stage10_rendered_figure_visual_qc/review_rendered/"))
            self.assertEqual(_sha256(path), row["sha256"])
            self.assertGreater(int(row["bytes"]), 1000)
            by_fig.setdefault(row["fig_id"], set()).add(row["format"])
        self.assertEqual(sorted(by_fig), [f"FIG-{idx:03d}" for idx in range(1, 7)])
        self.assertTrue(all(formats == {"pdf", "png", "svg"} for formats in by_fig.values()))

    def test_review_png_visual_qc_passes(self) -> None:
        self.assertEqual(len(self.qc), 6)
        for row in self.qc:
            self.assertEqual(row["visual_qc_pass"], "yes")
            self.assertGreaterEqual(int(row["width_px"]), 2300)
            self.assertGreaterEqual(int(row["height_px"]), 1300)
            self.assertGreaterEqual(int(row["min_edge_margin_px"]), 18)
            self.assertGreater(float(row["nonwhite_fraction"]), 0.02)
        self.assertTrue(CONTACT_SHEET.exists())
        self.assertGreater(CONTACT_SHEET.stat().st_size, 10_000)

    def test_roadmap_memory_marks_stage10_14_without_external_contact(self) -> None:
        memory = json.loads(MEMORY.read_text(encoding="utf-8"))
        current = memory["current_position"]
        self.assertEqual(
            current["active_stage"],
            "Stage 10.14 rendered-figure visual QA complete; external contact remains not sent",
        )
        stage10 = next(entry for entry in memory["stage_lock"] if entry.get("stage") == 10)
        self.assertEqual(stage10["status"], "stage10_14_complete_rendered_figure_visual_qc")
        subphase = next(item for item in stage10["subphases"] if item.get("id") == "10.14")
        self.assertEqual(subphase["status"], "complete_rendered_figure_visual_qc")
        self.assertIn(
            "case_studies/stage10_rendered_figure_visual_qc/stage10_14_gate_report.json",
            stage10["artifacts"],
        )


if __name__ == "__main__":
    unittest.main()
