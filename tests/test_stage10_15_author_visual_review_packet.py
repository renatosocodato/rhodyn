"""Regression tests for Stage 10.15 author visual-review packet."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_15_author_visual_review_packet.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_author_visual_review_packet"
GATE = OUTPUT_DIR / "stage10_15_gate_report.json"
MANIFEST = OUTPUT_DIR / "stage10_15_author_visual_review_manifest.tsv"
CHECKLIST = OUTPUT_DIR / "stage10_15_author_decision_checklist.tsv"
BOUNDARY = OUTPUT_DIR / "stage10_15_no_send_boundary_scan.tsv"
FIGURE_GUIDE = OUTPUT_DIR / "stage10_15_figure_review_guide.md"
MEMORY = ROOT / "docs" / "roadmap_execution_memory.json"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_15_runner", RUNNER)
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


class Stage1015AuthorVisualReviewPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _load_runner().run_stage10_15()
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))
        with MANIFEST.open(newline="", encoding="utf-8") as handle:
            cls.manifest = list(csv.DictReader(handle, delimiter="\t"))
        with CHECKLIST.open(newline="", encoding="utf-8") as handle:
            cls.checklist = list(csv.DictReader(handle, delimiter="\t"))
        with BOUNDARY.open(newline="", encoding="utf-8") as handle:
            cls.boundary = list(csv.DictReader(handle, delimiter="\t"))

    def test_gate_passes_and_keeps_no_send_boundary(self) -> None:
        self.assertEqual(self.gate["stage"], "10.15")
        self.assertEqual(self.gate["status"], "pass")
        self.assertTrue(all(self.gate["gates"].values()))
        self.assertEqual(self.gate["external_contact_status"], "not_sent")
        self.assertEqual(self.gate["summary_metrics"]["figure_render_reference_count"], 18)
        self.assertGreaterEqual(self.gate["summary_metrics"]["author_required_item_count"], 2)
        self.assertIn("author-review packaging", self.gate["interpretation_boundary"])
        self.assertIn("without adding new data", self.gate["interpretation_boundary"])

    def test_manifest_checksums_existing_surfaces(self) -> None:
        self.assertEqual(len(self.manifest), self.gate["summary_metrics"]["manifest_row_count"])
        figure_rows = [row for row in self.manifest if row["surface"].startswith("review_render_")]
        self.assertEqual(len(figure_rows), 18)
        figures = {row["surface"].split("_")[2] for row in figure_rows}
        self.assertEqual(figures, {f"FIG-{idx:03d}" for idx in range(1, 7)})
        for row in self.manifest:
            self.assertEqual(row["exists"], "yes", row["path"])
            path = ROOT / row["path"]
            self.assertTrue(path.exists(), row["path"])
            self.assertGreater(int(row["bytes"]), 0)
            self.assertEqual(_sha256(path), row["sha256"])

    def test_checklist_keeps_author_decisions_explicit(self) -> None:
        self.assertEqual(len(self.checklist), self.gate["summary_metrics"]["checklist_item_count"])
        author_required = [row for row in self.checklist if row["status"] == "author_required"]
        self.assertGreaterEqual(len(author_required), 2)
        labels = {row["item_id"]: row for row in self.checklist}
        self.assertEqual(labels["AVR-002"]["status"], "not_sent")
        self.assertEqual(labels["AVR-010"]["status"], "separate_new_evidence_decision")

    def test_boundary_scan_passes_without_contact_or_new_claims(self) -> None:
        self.assertEqual(len(self.boundary), self.gate["summary_metrics"]["boundary_count"])
        self.assertTrue(all(row["status"] == "pass" for row in self.boundary))
        joined = "\n".join(row["boundary"] for row in self.boundary)
        self.assertIn("No external contact", joined)
        self.assertIn("does not add new biological evidence", joined)
        guide = FIGURE_GUIDE.read_text(encoding="utf-8")
        self.assertIn("Stage 10.14 review renders", guide)
        self.assertIn("FIG-001", guide)
        self.assertIn("FIG-006", guide)

    def test_roadmap_memory_marks_stage10_15_without_external_contact(self) -> None:
        memory = json.loads(MEMORY.read_text(encoding="utf-8"))
        current = memory["current_position"]
        self.assertEqual(
            current["active_stage"],
            "Stage 10.15 author visual-review packet complete; external contact remains not sent",
        )
        stage10 = next(entry for entry in memory["stage_lock"] if entry.get("stage") == 10)
        self.assertEqual(stage10["status"], "stage10_15_complete_author_visual_review_packet")
        subphase = next(item for item in stage10["subphases"] if item.get("id") == "10.15")
        self.assertEqual(subphase["status"], "complete_author_visual_review_packet")
        self.assertIn(
            "case_studies/stage10_author_visual_review_packet/stage10_15_gate_report.json",
            stage10["artifacts"],
        )


if __name__ == "__main__":
    unittest.main()
