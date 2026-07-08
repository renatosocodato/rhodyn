"""Regression tests for Stage 10.13 rendered method figures."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_13_rendered_method_figures.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_rendered_figures"
GATE = OUTPUT_DIR / "stage10_13_gate_report.json"
MANIFEST = OUTPUT_DIR / "stage10_13_figures.manifest.yaml"
INVENTORY = OUTPUT_DIR / "stage10_13_render_inventory.tsv"
COVERAGE = OUTPUT_DIR / "stage10_13_panel_coverage.tsv"
MEMORY = ROOT / "docs" / "roadmap_execution_memory.json"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_13_runner", RUNNER)
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


class Stage1013RenderedMethodFiguresTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _load_runner().run_stage10_13()
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        with INVENTORY.open(newline="", encoding="utf-8") as handle:
            cls.inventory = list(csv.DictReader(handle, delimiter="\t"))
        with COVERAGE.open(newline="", encoding="utf-8") as handle:
            cls.coverage = list(csv.DictReader(handle, delimiter="\t"))

    def test_gate_passes_with_all_stage10_13_boundaries(self) -> None:
        self.assertEqual(self.gate["status"], "pass")
        self.assertEqual(self.gate["stage"], "10.13")
        self.assertTrue(all(self.gate["gates"].values()))
        self.assertEqual(self.gate["external_contact_status"], "not_sent")
        self.assertEqual(self.gate["summary_metrics"]["figure_count"], 6)
        self.assertEqual(self.gate["summary_metrics"]["planned_panel_count"], 30)
        self.assertEqual(self.gate["summary_metrics"]["manifest_panel_count"], 30)
        self.assertEqual(self.gate["summary_metrics"]["rendered_file_count"], 18)
        self.assertEqual(self.gate["summary_metrics"]["stage9_rendered_file_count"], 18)
        self.assertIn("does not add data", self.gate["interpretation_boundary"])
        self.assertIn("overwrite Stage 9 renders", self.gate["interpretation_boundary"])

    def test_manifest_is_stage10_scoped_and_matches_crosswalk_panel_count(self) -> None:
        runner = _load_runner()
        rebuilt = runner.build_manifest(runner.crosswalk_rows())
        self.assertEqual(len(rebuilt["figures"]), 6)
        self.assertEqual(sum(len(figure["panels"]) for figure in rebuilt["figures"]), 30)
        self.assertEqual(len(self.manifest["figures"]), 6)
        self.assertEqual(sum(len(figure["panels"]) for figure in self.manifest["figures"]), 30)
        for figure in self.manifest["figures"]:
            outdir = figure["export"]["outdir"]
            self.assertTrue(outdir.startswith("case_studies/stage10_rendered_figures/rendered/"))
            self.assertNotIn("manuscript/nature_methods/figures/rendered", outdir)

    def test_inventory_records_six_figures_and_three_formats_each(self) -> None:
        self.assertEqual(len(self.inventory), 18)
        by_fig: dict[str, set[str]] = {}
        for row in self.inventory:
            path = ROOT / row["path"]
            self.assertTrue(path.exists(), row["path"])
            self.assertEqual(_sha256(path), row["sha256"])
            by_fig.setdefault(row["fig_id"], set()).add(row["format"])
            self.assertGreater(int(row["bytes"]), 1000)
        self.assertEqual(sorted(by_fig), [f"FIG-{idx:03d}" for idx in range(1, 7)])
        self.assertTrue(all(formats == {"pdf", "png", "svg"} for formats in by_fig.values()))

    def test_panel_coverage_retains_thirty_panels_and_complete_evidence(self) -> None:
        self.assertEqual(len(self.coverage), 6)
        self.assertEqual(sum(int(row["panel_count"]) for row in self.coverage), 30)
        expected_panels = {
            "FIG-001": "A,B,C,D",
            "FIG-002": "A,B,C,D,E",
            "FIG-003": "A,B,C,D,E,F",
            "FIG-004": "A,B,C,D,E",
            "FIG-005": "A,B,C,D,E",
            "FIG-006": "A,B,C,D,E",
        }
        for row in self.coverage:
            self.assertEqual(row["panels"], expected_panels[row["fig_id"]])
            self.assertEqual(row["evidence_files_exist"], "yes")
            self.assertEqual(row["rendered_formats"], "pdf,png,svg")
            self.assertEqual(row["render_status"], "rendered")

    def test_roadmap_memory_marks_stage10_13_without_external_contact(self) -> None:
        memory = json.loads(MEMORY.read_text(encoding="utf-8"))
        current = memory["current_position"]
        self.assertEqual(
            current["active_stage"],
            "Stage 10.13 rendered method figures complete; external contact remains not sent",
        )
        stage10 = next(entry for entry in memory["stage_lock"] if entry.get("stage") == 10)
        self.assertEqual(stage10["status"], "stage10_13_complete_rendered_method_figures")
        subphase = next(item for item in stage10["subphases"] if item.get("id") == "10.13")
        self.assertEqual(subphase["status"], "complete_rendered_method_figures")
        self.assertIn(
            "case_studies/stage10_rendered_figures/stage10_13_gate_report.json",
            stage10["artifacts"],
        )


if __name__ == "__main__":
    unittest.main()
