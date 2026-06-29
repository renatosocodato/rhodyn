import json
import subprocess
import sys
from unittest import TestCase

from scripts.audit_phase6_release_readiness import audit_phase6_release_readiness


class Phase6ReleaseReadinessTests(TestCase):
    def test_phase6_readiness_audit_reports_current_state(self):
        payload = audit_phase6_release_readiness()
        self.assertIn(payload["status"], {"pass", "needs_work"})
        self.assertEqual(sorted(payload["subphases"]), ["6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7"])
        self.assertTrue(payload["checks"]["6.2::backend_extra_uses_httpx"])
        self.assertTrue(payload["checks"]["6.2::backend_extra_no_httpx2_typo"])
        self.assertTrue(payload["checks"]["6.7::phase6_audit_script_present"])
        self.assertEqual(payload["subphases"]["6.2"]["status"], "pass")
        self.assertEqual(payload["subphases"]["6.3"]["status"], "pass")
        self.assertEqual(payload["subphases"]["6.4"]["status"], "pass")
        self.assertTrue(payload["checks"]["6.4::cross_version_python_matrix"])
        self.assertTrue(payload["checks"]["6.4::docs_build_workflow_present"])
        self.assertTrue(payload["checks"]["6.4::docker_build_workflow_present"])
        self.assertTrue(payload["checks"]["6.4::contribution_docs_present"])
        self.assertEqual(payload["subphases"]["6.5"]["status"], "pass")
        self.assertTrue(payload["checks"]["6.5::github_release_notes_present"])
        self.assertTrue(payload["checks"]["6.5::zenodo_metadata_present"])
        self.assertTrue(payload["checks"]["6.5::checksum_manifest_present"])
        self.assertTrue(payload["checks"]["6.5::checksum_writer_present"])
        self.assertEqual(payload["subphases"]["6.6"]["status"], "pass")
        self.assertTrue(payload["checks"]["6.6::clean_room_report_passed"])
        self.assertTrue(payload["checks"]["6.6::clean_room_report_records_notebooks"])
        self.assertTrue(payload["checks"]["6.6::clean_room_report_records_docs_build"])
        self.assertTrue(payload["checks"]["6.6::clean_room_report_records_workbench_audit"])
        self.assertEqual(payload["subphases"]["6.7"]["status"], "pass")
        self.assertTrue(payload["checks"]["6.7::pypi_dry_run_passed"])
        self.assertTrue(payload["checks"]["6.7::zenodo_dry_run_passed"])
        self.assertTrue(payload["checks"]["6.7::broken_link_scan_passed"])
        self.assertTrue(payload["checks"]["6.7::dependency_review_passed"])
        self.assertTrue(payload["checks"]["6.7::docker_smoke_passed"])
        self.assertTrue(payload["checks"]["6.7::screenshot_regression_passed"])

    def test_phase6_readiness_script_is_executable(self):
        result = subprocess.run(
            [sys.executable, "scripts/audit_phase6_release_readiness.py"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertIn(payload["status"], {"pass", "needs_work"})
