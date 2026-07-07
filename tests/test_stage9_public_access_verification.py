"""Regression checks for Nature Methods public-access surfaces."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
PACKAGE = WORKSPACE / "submission_package"
REPORT_PATH = WORKSPACE / "audits" / "nature_methods_public_access_verification.json"

FORBIDDEN_PUBLIC_REFERENCE_PATTERNS = [
    "github.com/renatosocodato/windowed_rhoA_model",
    "doi.org/10.5281/zenodo.19796404",
    "doi.org/10.5281/zenodo.19796406",
]

EXPECTED_PUBLIC_URLS = {
    "https://github.com/renatosocodato/rhodyn",
    "https://github.com/renatosocodato/rhodyn/releases/tag/v0.1.0",
    "https://doi.org/10.5281/zenodo.21036616",
    "https://doi.org/10.5281/zenodo.21036615",
    "https://doi.org/10.5281/zenodo.14907827",
    "https://doi.org/10.5281/zenodo.5836623",
    "https://doi.org/10.5281/zenodo.10011861",
    "https://github.com/renatosocodato/panelforge-figures",
    "https://github.com/renatosocodato/panelforge-figures/tree/v3.14.1",
    "https://doi.org/10.5281/zenodo.20811171",
    "https://doi.org/10.5281/zenodo.20811170",
}


class Stage9PublicAccessVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.package_text = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(PACKAGE.glob("*.md"))
        )

    def test_public_access_report_passes(self) -> None:
        self.assertEqual(self.report["status"], "pass")
        self.assertEqual(self.report["failures"], [])
        self.assertEqual(self.report["failed_urls"], [])
        self.assertEqual(self.report["forbidden_public_reference_hits"], [])
        self.assertEqual(self.report["missing_expected_urls"], [])
        self.assertGreaterEqual(self.report["url_count"], 10)
        for check_name in [
            "all_visible_public_urls_resolve",
            "expected_release_dataset_and_renderer_urls_present",
            "unresolved_optional_reference_case_links_not_advertised",
        ]:
            self.assertIs(self.report["checks"][check_name], True)

    def test_expected_release_dataset_and_renderer_urls_were_checked(self) -> None:
        checked = {
            row["url"]
            for row in self.report["checked_urls"]
            if row.get("ok") is True
        }
        checked.update(
            row["raw_url"]
            for row in self.report["checked_urls"]
            if row.get("ok") is True
        )
        missing = sorted(EXPECTED_PUBLIC_URLS - checked)
        self.assertEqual(missing, [])

    def test_unresolved_reference_case_urls_are_not_reader_facing(self) -> None:
        for pattern in FORBIDDEN_PUBLIC_REFERENCE_PATTERNS:
            self.assertNotIn(pattern, self.package_text)
        self.assertIn("controlled reviewer-access repository", self.package_text)
        self.assertIn("journal upload system", self.package_text)

    def test_rhoa_reference_case_is_not_used_as_hidden_method_evidence(self) -> None:
        self.assertIn("optional biological reference use case", self.package_text)
        self.assertIn("do not depend on manuscript-private raw microscopy", self.package_text)


if __name__ == "__main__":
    unittest.main()
