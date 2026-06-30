"""Regression checks for the Stage 7.8 methods-manuscript readiness package."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "case_studies" / "stage7_methods_readiness"


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _paths_from_cell(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


class Stage78MethodsReadinessTests(unittest.TestCase):
    def test_gate_report_passes_with_all_checkpoints(self) -> None:
        docs_gate = _json(ROOT / "docs" / "stage7_8_gate_report.json")
        case_gate = _json(CASE_DIR / "stage7_8_methods_readiness_gate_report.json")
        self.assertEqual(docs_gate, case_gate)
        self.assertEqual(docs_gate["status"], "pass")
        self.assertEqual(docs_gate["completion_state"], "complete_methods_manuscript_readiness_package")
        for checkpoint, status in docs_gate["validation_checkpoints"].items():
            if checkpoint.startswith("stop_condition_"):
                self.assertEqual(status, "not_triggered", checkpoint)
            else:
                self.assertEqual(status, "pass", checkpoint)
        self.assertEqual(docs_gate["inconclusive_context_count"], 3)

    def test_figure_crosswalk_has_artifacts_and_limitations(self) -> None:
        rows = _tsv(CASE_DIR / "figure_artifact_crosswalk.tsv")
        self.assertEqual(len(rows), 6)
        for row in rows:
            self.assertIn(row["readiness"], {"ready_for_drafting", "ready_for_supplement_or_main_with_scope"})
            for column in ["primary_artifact", "supporting_artifacts", "validation_artifact", "limitation_artifact"]:
                for rel in _paths_from_cell(row[column]):
                    self.assertTrue((ROOT / rel).exists(), f"{row['component']} missing {rel}")
            self.assertTrue(row["scope"])

    def test_claim_crosswalk_has_evidence_and_no_overclaim_status(self) -> None:
        rows = _tsv(CASE_DIR / "claim_evidence_crosswalk.tsv")
        self.assertEqual(len(rows), 5)
        allowed_statuses = {
            "supported_for_methods_drafting",
            "supported_with_inconclusive_contexts_visible",
            "supported_with_reserve_like_language",
            "supported_without_molecular_edge_claim",
            "supported_for_software_reproducibility_claim",
        }
        for row in rows:
            self.assertIn(row["status"], allowed_statuses)
            for column in ["evidence", "validation", "limitation"]:
                for rel in _paths_from_cell(row[column]):
                    self.assertTrue((ROOT / rel).exists(), f"{row['claim_id']} missing {rel}")
        claim_text = " ".join(row["claim"] for row in rows)
        self.assertNotIn("generated the original manuscript", claim_text)
        self.assertNotIn("proves every molecular edge", claim_text)

    def test_readiness_docs_preserve_scope_boundaries(self) -> None:
        evidence_index = (ROOT / "docs" / "stage7_methods_evidence_index.md").read_text(encoding="utf-8")
        claim_crosswalk = (ROOT / "docs" / "stage7_claim_evidence_crosswalk.md").read_text(encoding="utf-8")
        readiness = (ROOT / "docs" / "stage7_methods_submission_readiness.md").read_text(encoding="utf-8")
        self.assertIn("does not add analyses or biological claims", evidence_index)
        self.assertIn("paired with a limitation artifact", claim_crosswalk)
        self.assertIn("does not add a biological system", readiness)
        self.assertIn("Known inconclusive cases are visible", readiness)

    def test_submission_checklist_is_all_pass(self) -> None:
        rows = _tsv(CASE_DIR / "methods_readiness_checklist.tsv")
        self.assertGreaterEqual(len(rows), 6)
        self.assertTrue(all(row["status"] == "pass" for row in rows))
        evidence = " ".join(row["evidence"] for row in rows)
        self.assertIn("docs/stage7_1_gate_report.json through docs/stage7_7_gate_report.json", evidence)
        self.assertIn("heldout_validation_outcomes.tsv", evidence)


if __name__ == "__main__":
    unittest.main()
