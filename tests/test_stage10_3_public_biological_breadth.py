import csv
import importlib.util
import json
from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_stage10_3_public_biological_breadth.py"
SPEC = importlib.util.spec_from_file_location("stage10_3", SCRIPT_PATH)
stage10_3 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(stage10_3)


class Stage103PublicBiologicalBreadthTests(TestCase):
    def test_mlci_summary_contains_residence_and_amplitude_boundary_cases(self):
        rows = stage10_3._mlci_summary_rows()
        self.assertGreaterEqual(len(rows), 20)
        classes = {row["amplitude_residence_class"] for row in rows}
        self.assertIn("residence_only_top_quartile", classes)
        self.assertIn("amplitude_only_top_quartile", classes)
        self.assertTrue(all("window_low" in row and "window_high" in row for row in rows))

    def test_stage10_3_runner_writes_passing_public_breadth_report(self):
        report = stage10_3.evaluate_stage10_3(ROOT / "case_studies" / "stage10_public_breadth")
        self.assertEqual(report["status"], "pass")
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(report["summary_metrics"]["counted_independent_public_systems"], 4)
        self.assertGreaterEqual(report["summary_metrics"]["counted_biological_domains"], 3)
        self.assertEqual(
            set(report["summary_metrics"]["additional_systems_beyond_drg_and_erk"]),
            {"cell_painting_mitotox_seal2023", "mlci_tracking"},
        )
        self.assertFalse(report["summary_metrics"]["birtwistle_counted"])

        report_path = ROOT / "case_studies" / "stage10_public_breadth" / "stage10_3_public_breadth_report.json"
        persisted = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["status"], "pass")

    def test_system_matrix_counts_only_independent_release_safe_public_systems(self):
        with (ROOT / "case_studies" / "stage10_public_breadth" / "stage10_3_public_system_matrix.tsv").open(
            newline="", encoding="utf-8"
        ) as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        counted = [row for row in rows if row["counted_public_system"] == "1"]
        self.assertEqual(len(counted), 4)
        self.assertEqual(
            {row["system_id"] for row in counted},
            {
                "drg_calcium_vonbuchholtz2025",
                "erk_gpcr_wan2021",
                "cell_painting_mitotox_seal2023",
                "mlci_tracking",
            },
        )
        coupling = next(row for row in rows if row["system_id"] == "erk_akt_wan2021_bounded_coupling")
        self.assertEqual(coupling["counted_public_system"], "0")
        self.assertIn("2/4", coupling["primary_result"])

    def test_birtwistle_candidate_is_source_verified_but_not_counted_or_retained(self):
        with (ROOT / "case_studies" / "stage10_public_breadth" / "stage10_3_candidate_resolution.tsv").open(
            newline="", encoding="utf-8"
        ) as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        birtwistle = next(row for row in rows if row["candidate_id"] == "birtwistle_erk_akt_cell_division")
        self.assertEqual(birtwistle["counted"], "0")
        self.assertEqual(birtwistle["decision"], "source_verified_but_deferred")
        retained_derivatives = list((ROOT / "case_studies" / "stage10_public_breadth").glob("*birtwistle*trajectory*"))
        self.assertEqual(retained_derivatives, [])


if __name__ == "__main__":
    import unittest

    unittest.main()
