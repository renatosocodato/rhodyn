"""Regression tests for Stage 10.11 author-review readiness."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_11_author_review_readiness.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_author_review_readiness"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_11_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage1011AuthorReviewReadinessTest(unittest.TestCase):
    def test_stage10_11_gate_passes_without_external_contact(self) -> None:
        report = _load_runner().run_stage10_11()

        self.assertEqual(report["status"], "pass")
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(report["selected_route"], "presubmission_query_author_review_required")
        self.assertEqual(report["external_contact_status"], "not_sent")
        self.assertEqual(report["summary_metrics"]["author_review_item_count"], 12)
        self.assertEqual(report["summary_metrics"]["boundary_pass_count"], report["summary_metrics"]["boundary_count"])
        self.assertIn("does not send any external message", report["interpretation_boundary"])

    def test_clean_query_is_author_review_only_and_blocks_overreads(self) -> None:
        _load_runner().run_stage10_11()
        query = (OUTPUT_DIR / "stage10_11_presubmission_query_clean_AUTHOR_REVIEW_REQUIRED.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Author review required. Do not send from repository.", query)
        self.assertIn("[Author name, affiliation, and contact details", query)
        self.assertIn("residence-state inference method", query)
        self.assertIn("does not claim that every live-cell system contains a residence regime", query)
        self.assertNotIn("take another look", query)
        self.assertNotIn("prospective blinded", query)
        self.assertNotIn("/" + "Users/", query)
        self.assertNotIn("github" + "_pat_", query)

    def test_author_checklist_and_manifest_preserve_human_action_gate(self) -> None:
        _load_runner().run_stage10_11()

        with (OUTPUT_DIR / "stage10_11_author_review_checklist.tsv").open(encoding="utf-8") as handle:
            checklist_rows = list(csv.DictReader(handle, delimiter="\t"))
        with (OUTPUT_DIR / "stage10_11_editor_contact_packet_manifest.tsv").open(encoding="utf-8") as handle:
            manifest_rows = list(csv.DictReader(handle, delimiter="\t"))

        self.assertEqual(len(checklist_rows), 12)
        self.assertGreaterEqual(sum(row["required"] == "yes" for row in checklist_rows), 10)
        statuses = {row["status"] for row in checklist_rows}
        self.assertIn("author_required", statuses)
        self.assertIn("not_sent", statuses)
        surfaces = {row["surface"]: row for row in manifest_rows}
        self.assertEqual(
            surfaces["clean_presubmission_query"]["send_ready_status"],
            "author_review_required_not_sent",
        )
        self.assertEqual(surfaces["gate_report"]["send_ready_status"], "not_a_send_surface")

    def test_boundary_scan_keeps_method_claim_scoped(self) -> None:
        _load_runner().run_stage10_11()

        with (OUTPUT_DIR / "stage10_11_boundary_scan.tsv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        boundaries = {row["boundary"]: row for row in rows}

        for key in [
            "method_advance_present",
            "comparator_classes_present",
            "public_breadth_present",
            "heldout_validation_scoped",
            "software_support_not_primary_claim",
            "universal_residence_blocked",
            "mechanism_discovery_blocked",
            "old_package_not_contact_basis",
            "external_contact_not_sent",
        ]:
            self.assertIn(key, boundaries)
            self.assertEqual(boundaries[key]["status"], "pass")
        self.assertIn("prospective collaborator-blind", boundaries["heldout_validation_scoped"]["unsafe_overread_blocked"])

    def test_memory_records_stage10_11_without_contact(self) -> None:
        _load_runner().run_stage10_11()

        memory = json.loads((ROOT / "docs" / "roadmap_execution_memory.json").read_text(encoding="utf-8"))
        current = memory["current_position"]
        self.assertEqual(
            current["active_stage"],
            "Stage 10.11 author-review readiness complete; external contact remains not sent",
        )
        stage10 = next(entry for entry in memory["stage_lock"] if entry.get("stage") == 10)
        self.assertEqual(stage10["status"], "stage10_11_complete_author_review_readiness")
        self.assertTrue(any(item.get("id") == "10.11" for item in stage10["subphases"]))
        self.assertIn(
            "case_studies/stage10_author_review_readiness/stage10_11_gate_report.json",
            stage10["artifacts"],
        )


if __name__ == "__main__":
    unittest.main()
