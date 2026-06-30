"""Regression checks for the Stage 7.7 usability and adoption rehearsal."""

from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "case_studies" / "stage7_usability_rehearsal"


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


class Stage77UsabilityRehearsalTests(unittest.TestCase):
    def test_gate_reports_pass_and_match_completion_state(self) -> None:
        docs_gate = _json(ROOT / "docs" / "stage7_7_gate_report.json")
        case_gate = _json(CASE_DIR / "stage7_7_usability_gate_report.json")
        self.assertEqual(docs_gate, case_gate)
        self.assertEqual(docs_gate["status"], "pass")
        self.assertEqual(docs_gate["completion_state"], "complete_usability_adoption_rehearsal")
        checkpoints = docs_gate["validation_checkpoints"]
        for checkpoint in [
            "stage7_6_prerequisite_complete",
            "biologist_task_reaches_interpretable_decision",
            "quantitative_user_reproduces_cli_python_backend_output",
            "workbench_public_tutorial_flow_present",
            "exports_include_parameters_schema_grouping_version",
            "tutorial_or_interface_fixes_preserve_analysis_contract",
            "no_unvalidated_analysis_routes_added",
        ]:
            self.assertEqual(checkpoints[checkpoint], "pass")
        self.assertEqual(checkpoints["stop_condition_user_cannot_interpret_result"], "not_triggered")

    def test_biologist_public_mlci_task_is_scoped_and_reproducible(self) -> None:
        result = _json(CASE_DIR / "biologist_residence_task_result.json")
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["python_cli_backend_parity"])
        self.assertEqual(result["trace_count"], 24)
        self.assertEqual(result["high_residence_count"], 6)
        self.assertEqual(result["amplitude_only_count"], 7)
        self.assertEqual(result["residence_only_count"], 6)
        decision = str(result["interpretable_decision"])
        self.assertIn("residence-versus-amplitude software example", decision)
        self.assertIn("not as molecular activity or disease-state biology", decision)

    def test_quantitative_bounded_coupling_task_preserves_panel_boundaries(self) -> None:
        result = _json(CASE_DIR / "quantitative_reproduction_result.json")
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["python_cli_backend_coupling_parity"])
        self.assertTrue(result["cli_backend_residence_parity"])
        decisions = {row["contrast"]: row for row in result["coupling_decisions"]}
        self.assertTrue(decisions["rock_src"]["passes"])
        self.assertFalse(decisions["myh10_src"]["passes"])
        self.assertFalse(decisions["myh10_src"]["interval_inside_margin"])

    def test_workbench_flow_keeps_public_tutorial_controls_visible(self) -> None:
        flow = _json(CASE_DIR / "workbench_flow_check.json")
        self.assertEqual(flow["status"], "pass")
        for check_name, status in flow["checks"].items():
            self.assertTrue(status, check_name)
        self.assertIn("does not add a new frontend analysis route", flow["interpretation_boundary"])

    def test_export_bundles_include_schema_grouping_parameters_and_version(self) -> None:
        manifest_path = CASE_DIR / "export_examples_manifest.tsv"
        with manifest_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row["has_parameters"], "1")
            self.assertEqual(row["has_input_schema"], "1")
            self.assertEqual(row["has_grouping"], "1")
            self.assertEqual(row["software_version"], "0.1.0")
            bundle_path = ROOT / row["bundle_path"]
            self.assertTrue(bundle_path.exists(), row["bundle_path"])
            with zipfile.ZipFile(bundle_path) as archive:
                names = set(archive.namelist())
                self.assertIn("parameter_provenance.json", names)
                self.assertIn("parameter_provenance.md", names)
                self.assertIn("result.json", names)
                self.assertIn("result_rows.csv", names)
                provenance = json.loads(archive.read("parameter_provenance.json"))
            self.assertEqual(provenance["software_version"], "0.1.0")
            self.assertTrue(provenance["effective_parameters"])
            self.assertTrue(provenance["input_schema"]["required"])
            self.assertTrue(provenance["grouping"]["observed_grouping_fields"])
            self.assertIn("interpretation_boundary", provenance)

    def test_docs_preserve_no_new_biological_system_boundary(self) -> None:
        rehearsal_doc = (ROOT / "docs" / "stage7_usability_rehearsal.md").read_text(encoding="utf-8")
        findings_doc = (ROOT / "docs" / "stage7_user_path_findings.md").read_text(encoding="utf-8")
        self.assertIn("does not add a new biological system", rehearsal_doc)
        self.assertIn("does not add a new analysis route", rehearsal_doc)
        self.assertIn("not a new biological demonstration", findings_doc)


if __name__ == "__main__":
    unittest.main()
