import json
from pathlib import Path
from unittest import TestCase

from scripts.audit_stage3_case_study_bank import audit_stage3


class Stage3CaseStudyBankTests(TestCase):
    def test_audit_report_passes_original_stage3_gate(self):
        report = audit_stage3(Path("."))

        self.assertEqual(report["status"], "pass")
        self.assertEqual(
            report["gates"]["two_biological_systems_show_residence_amplitude_distinction"]["status"],
            "pass",
        )
        self.assertEqual(
            report["gates"]["one_public_endpoint_case_shows_model_comparison"]["status"],
            "pass",
        )
        self.assertEqual(
            report["gates"]["one_case_shows_bounded_coupling_or_reserve_logic"]["status"],
            "pass",
        )
        self.assertEqual(
            report["gates"]["examples_do_not_imply_manuscript_generated_original_results"]["status"],
            "pass",
        )

    def test_committed_gate_report_matches_current_audit(self):
        path = Path("case_studies/stage3_case_study_bank_gate_report.json")
        committed = json.loads(path.read_text(encoding="utf-8"))
        current = audit_stage3(Path("."))

        self.assertEqual(committed, current)

    def test_notebook_surfaces_exist_and_remain_lightweight(self):
        report = audit_stage3(Path("."))
        notebooks = report["deliverables"]["tutorial_notebooks"]["files"]
        self.assertTrue(all(notebooks.values()))

        for notebook in notebooks:
            payload = json.loads(Path(notebook).read_text(encoding="utf-8"))
            self.assertEqual(payload["nbformat"], 4)
            self.assertGreaterEqual(len(payload["cells"]), 3)
            text = json.dumps(payload)
            self.assertNotIn("/" + "Users/", text)
            self.assertNotIn("/" + "Volumes/", text)

    def test_case_study_bank_keeps_manuscript_independence_boundary(self):
        report = audit_stage3(Path("."))
        boundary = report["interpretation_boundary"]

        self.assertIn("retained derived public tables", boundary)
        self.assertIn("do not imply", boundary)
        self.assertIn("RhoA/microglia manuscript results", boundary)
