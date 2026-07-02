"""Regression checks for Stage 7.7/7.8 recursive hardening."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "audit_stage7_7_8_recursive_hardening.py"
DOC_REPORT = ROOT / "docs" / "stage7_7_8_recursive_hardening_report.json"
CASE_REPORT = ROOT / "case_studies" / "stage7_methods_readiness" / "stage7_7_8_recursive_hardening_report.json"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage7_7_8_recursive_audit_under_test", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


AUDIT = _load_runner()


class Stage778RecursiveHardeningTests(unittest.TestCase):
    def test_recursive_hardening_report_passes_and_is_mirrored(self) -> None:
        docs_report = json.loads(DOC_REPORT.read_text(encoding="utf-8"))
        case_report = json.loads(CASE_REPORT.read_text(encoding="utf-8"))
        self.assertEqual(docs_report, case_report)
        self.assertEqual(docs_report["status"], "pass")
        self.assertEqual(docs_report["completion_state"], "stage7_7_8_recursively_hardened")
        for check_name, status in docs_report["checks"].items():
            self.assertEqual(status, "pass", check_name)
        self.assertEqual(docs_report["counts"]["stage7_7_bundles"], 2)
        self.assertEqual(docs_report["counts"]["stage7_8_figure_rows"], 6)
        self.assertEqual(docs_report["counts"]["stage7_8_claim_rows"], 5)
        self.assertIn("does not add biological evidence", docs_report["interpretation_boundary"])
        self.assertIn("Phase 9 is limited to the authorized manuscript-assembly scaffold plus Stage 9.0 evidence lock", docs_report["interpretation_boundary"])
        self.assertEqual(docs_report["counts"]["unauthorized_phase9_files"], 0)
        self.assertEqual(docs_report["counts"]["unauthorized_stage9_draft_files"], 0)
        self.assertEqual(docs_report["counts"]["stage9_checker_status"], "pass")

    def test_recursive_audit_recomputes_current_state(self) -> None:
        report = AUDIT.audit_stage7_7_8_recursive_hardening()
        self.assertEqual(report["status"], "pass")
        self.assertFalse(report["failures"])
        self.assertEqual(report["checks"]["stage7_7_export_bundles_verified"], "pass")
        self.assertEqual(report["checks"]["stage7_8_crosswalks_match_runner_constants"], "pass")
        self.assertEqual(report["checks"]["phase9_boundary_preserved"], "pass")

    def test_bundle_validator_detects_stale_export_manifest_hash(self) -> None:
        original_root = AUDIT.ROOT
        original_stage7_7 = AUDIT.STAGE7_7_DIR
        original_stage7_8 = AUDIT.STAGE7_8_DIR
        original_runner = AUDIT.STAGE7_8_RUNNER
        temp_root = ROOT / ".tmp_stage7_7_8_hash_test"
        if temp_root.exists():
            shutil.rmtree(temp_root)
        try:
            shutil.copytree(ROOT / "case_studies", temp_root / "case_studies")
            shutil.copytree(ROOT / "docs", temp_root / "docs")
            shutil.copytree(ROOT / "scripts", temp_root / "scripts")
            shutil.copytree(ROOT / "tests", temp_root / "tests")
            AUDIT.ROOT = temp_root
            AUDIT.STAGE7_7_DIR = temp_root / "case_studies" / "stage7_usability_rehearsal"
            AUDIT.STAGE7_8_DIR = temp_root / "case_studies" / "stage7_methods_readiness"
            AUDIT.STAGE7_8_RUNNER = temp_root / "scripts" / "run_stage7_8_methods_readiness.py"
            bundle = AUDIT.STAGE7_7_DIR / "biologist_residence_bundle.zip"
            bundle.write_bytes(bundle.read_bytes() + b"stale-hash")
            failures: list[str] = []
            AUDIT._validate_export_bundles(failures)
        finally:
            AUDIT.ROOT = original_root
            AUDIT.STAGE7_7_DIR = original_stage7_7
            AUDIT.STAGE7_8_DIR = original_stage7_8
            AUDIT.STAGE7_8_RUNNER = original_runner
            shutil.rmtree(temp_root, ignore_errors=True)
        self.assertTrue(any("bundle hash mismatch" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
