"""Regression checks for Stage 9.17 availability assembly."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
DATA_PATH = WORKSPACE / "sections" / "data_availability.md"
CODE_PATH = WORKSPACE / "sections" / "code_availability.md"
COMMAND_PATH = WORKSPACE / "ledgers" / "reproducibility_command_index.md"
REPORTING_PATH = WORKSPACE / "submission_package" / "reporting_summary_REQUIRED.md"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.17.json"


class Stage917AvailabilityAssemblyTests(unittest.TestCase):
    def test_gate_passes_and_points_to_supplementary_methods(self) -> None:
        gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        self.assertIs(gate["pass"], True)
        self.assertEqual(gate["substage"], "9.17")
        self.assertEqual(gate["next_substage"], "9.18")
        self.assertEqual(gate["software_version"], "v0.1.0")
        self.assertEqual(gate["release_commit"], "4b1211cadd1fb3af34a1ec3e21f62383ffd9e368")
        self.assertEqual(gate["software_version_doi"], "10.5281/zenodo.21036616")
        self.assertEqual(gate["software_concept_doi"], "10.5281/zenodo.21036615")
        self.assertEqual(gate["panel_engine_version_doi"], "10.5281/zenodo.20811171")
        self.assertEqual(gate["panel_engine_render_command"], "figures render manuscript/nature_methods/figures/figures.manifest.yaml")
        self.assertIs(gate["reporting_summary_required"], True)
        self.assertGreaterEqual(gate["command_count"], 10)
        self.assertTrue(all(item["passed"] for item in gate["checks"]))

    def test_availability_surfaces_contain_release_and_data_identifiers(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [DATA_PATH, CODE_PATH, COMMAND_PATH, REPORTING_PATH]
        )
        for phrase in [
            "https://github.com/renatosocodato/rhodyn",
            "https://github.com/renatosocodato/rhodyn/releases/tag/v0.1.0",
            "4b1211cadd1fb3af34a1ec3e21f62383ffd9e368",
            "https://doi.org/10.5281/zenodo.21036616",
            "https://doi.org/10.5281/zenodo.21036615",
            "https://doi.org/10.5281/zenodo.14907827",
            "https://doi.org/10.5281/zenodo.5836623",
            "https://doi.org/10.5281/zenodo.10011861",
            "https://github.com/renatosocodato/windowed_rhoA_model",
            "e63cc93a4b23d8b3d27cf25136b00d53fa6144f4",
            "https://doi.org/10.5281/zenodo.19796404",
            "https://doi.org/10.5281/zenodo.19796406",
            "https://doi.org/10.5281/zenodo.20811171",
            "figures render manuscript/nature_methods/figures/figures.manifest.yaml",
            "Reporting Summary REQUIRED",
            "not the completed journal form",
        ]:
            self.assertIn(phrase, combined)

    def test_no_request_only_or_local_path_language(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in [DATA_PATH, CODE_PATH, COMMAND_PATH, REPORTING_PATH]
        )
        for phrase in [
            "upon request",
            "available on request",
            "available from the authors",
            "/users/",
            "/volumes/",
            "library/launchagents",
            "sk-",
            "ghp_",
            "github_pat_",
        ]:
            self.assertNotIn(phrase, combined)

    def test_command_index_rows_have_required_schema_fields(self) -> None:
        command_index = COMMAND_PATH.read_text(encoding="utf-8")
        self.assertIn("| Command ID | Analysis output | Command | Expected output | Software version | Purpose |", command_index)
        self.assertEqual(command_index.count("| CMD-"), 12)
        self.assertIn("python scripts/run_stage7_3_public_signaling.py", command_index)
        self.assertIn("python scripts/run_stage7_4_endpoint_reserve_routing.py", command_index)
        self.assertIn("python scripts/run_stage7_8_methods_readiness.py", command_index)
        self.assertIn("python scripts/check_release.py", command_index)

    def test_downstream_submission_surfaces_remain_unstarted(self) -> None:
        forbidden = [
            "audits/reader_surface_hygiene_report.md",
            "submission_package/pi_review_packet.md",
            "submission_package/submission_readiness_checklist.md",
        ]
        for rel in forbidden:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
