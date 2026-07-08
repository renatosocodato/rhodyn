"""Regression tests for Stage 10.10 recursive hardening."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_10_recursive_hardening.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_recursive_hardening"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_10_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage1010RecursiveHardeningTest(unittest.TestCase):
    def test_stage10_10_gate_passes_without_contact(self) -> None:
        report = _load_runner().run_stage10_10()

        self.assertEqual(report["status"], "pass")
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(report["summary_metrics"]["audited_phase_count"], 10)
        self.assertEqual(report["summary_metrics"]["phase_pass_count"], 10)
        self.assertEqual(report["summary_metrics"]["high_risk_gap_count"], 0)
        self.assertEqual(report["selected_route"], "presubmission_query_author_review_required")
        self.assertEqual(report["external_contact_status"], "not_sent")
        self.assertIn("does not add datasets", report["interpretation_boundary"])

    def test_phase_and_evidence_matrices_cover_stage10_chain(self) -> None:
        _load_runner().run_stage10_10()

        with (OUTPUT_DIR / "stage10_10_phase_gate_matrix.tsv").open(encoding="utf-8") as handle:
            phase_rows = list(csv.DictReader(handle, delimiter="\t"))
        with (OUTPUT_DIR / "stage10_10_evidence_chain_audit.tsv").open(encoding="utf-8") as handle:
            evidence_rows = list(csv.DictReader(handle, delimiter="\t"))

        self.assertEqual([row["phase"] for row in phase_rows], [f"10.{idx}" for idx in range(10)])
        self.assertTrue(all(row["status"] == "pass" for row in phase_rows))
        self.assertTrue(all(row["evidence_read"] == "yes" for row in phase_rows))
        self.assertTrue(all(row["status"] == "pass" for row in evidence_rows))
        self.assertIn("method_object_primary", {row["evidence_node"] for row in evidence_rows})
        self.assertIn("named_tool_benchmarking", {row["evidence_node"] for row in evidence_rows})
        self.assertIn("public_biological_breadth", {row["evidence_node"] for row in evidence_rows})
        self.assertIn("red_team_risk_clearance", {row["evidence_node"] for row in evidence_rows})

    def test_claim_boundaries_prevent_overreads(self) -> None:
        _load_runner().run_stage10_10()

        with (OUTPUT_DIR / "stage10_10_claim_boundary_matrix.tsv").open(encoding="utf-8") as handle:
            boundary_rows = list(csv.DictReader(handle, delimiter="\t"))

        boundaries = {row["claim_boundary"]: row for row in boundary_rows}
        for key in [
            "method_not_software_wrapper",
            "not_universal_residence",
            "not_mechanism_discovery",
            "not_prospective_blinded",
            "old_package_not_contact_basis",
            "external_contact_not_sent",
        ]:
            self.assertIn(key, boundaries)
            self.assertEqual(boundaries[key]["status"], "pass")
        self.assertIn("do not prove a molecular mechanism", boundaries["not_mechanism_discovery"]["safe_reading"])
        self.assertIn("Stage 10 evidence ladder", boundaries["old_package_not_contact_basis"]["safe_reading"])

    def test_patch_recommendations_keep_human_review_as_next_action(self) -> None:
        _load_runner().run_stage10_10()

        with (OUTPUT_DIR / "stage10_10_patch_recommendations.tsv").open(encoding="utf-8") as handle:
            patch_rows = list(csv.DictReader(handle, delimiter="\t"))
        decisions = {row["item"]: row for row in patch_rows}

        self.assertEqual(decisions["External editor contact"]["status"], "not_sent")
        self.assertEqual(decisions["External editor contact"]["decision"], "retain_author_review_required")
        self.assertEqual(decisions["Stage 9.29 package alone as EIC basis"]["decision"], "forbid")
        self.assertEqual(decisions["Stage 10.0 through 10.9 evidence ladder"]["status"], "complete")

    def test_memory_records_stage10_10_boundary(self) -> None:
        _load_runner().run_stage10_10()

        memory = json.loads((ROOT / "docs" / "roadmap_execution_memory.json").read_text(encoding="utf-8"))
        current = memory["current_position"]
        self.assertEqual(
            current["active_stage"],
            "Stage 10.10 recursive hardening complete; external contact remains not sent",
        )
        stage10 = next(entry for entry in memory["stage_lock"] if entry.get("stage") == 10)
        self.assertEqual(stage10["status"], "stage10_10_complete_recursive_hardening")
        self.assertTrue(any(item.get("id") == "10.10" for item in stage10["subphases"]))
        self.assertIn(
            "case_studies/stage10_recursive_hardening/stage10_10_gate_report.json",
            stage10["artifacts"],
        )


if __name__ == "__main__":
    unittest.main()
