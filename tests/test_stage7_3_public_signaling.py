import csv
import json
from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
STAGE7_3 = ROOT / "case_studies" / "stage7_public_signaling"


class Stage73PublicSignalingTests(TestCase):
    def test_gate_report_passes_with_two_public_systems(self):
        report = json.loads((STAGE7_3 / "stage7_3_public_signaling_gate_report.json").read_text(encoding="utf-8"))

        self.assertEqual(report["status"], "pass")
        self.assertEqual(set(report["selected_datasets"]), {"drg_calcium_vonbuchholtz2025", "erk_gpcr_wan2021"})
        self.assertGreaterEqual(len(report["system_classes"]), 2)
        self.assertEqual(report["validation_checkpoints"]["stop_condition_public_dataset_failure"], "not_triggered")
        self.assertIn("does not imply that RhoDyn generated", report["interpretation_boundary"])

    def test_tidy_trajectory_tables_preserve_time_and_grouping(self):
        expected = {
            "drg_calcium_tidy_trajectories.csv": (72000, {"mouse", "ganglion", "roi"}),
            "erk_gpcr_tidy_trajectories.csv": (4320, {"ligand", "experiment", "source_object"}),
        }
        for filename, (row_count, required_columns) in expected.items():
            with (STAGE7_3 / filename).open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), row_count, filename)
            self.assertTrue(required_columns.issubset(rows[0].keys()), filename)
            self.assertTrue(all(row["time"] != "" and row["signal"] != "" for row in rows[:50]), filename)

    def test_each_case_has_amplitude_and_residence_disagreement(self):
        for filename in ["drg_calcium_residence_amplitude_summary.csv", "erk_gpcr_residence_amplitude_summary.csv"]:
            with (STAGE7_3 / filename).open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            classes = {row["amplitude_residence_class"] for row in rows}
            self.assertIn("amplitude_only_top_quartile", classes, filename)
            self.assertIn("residence_only_top_quartile", classes, filename)
            self.assertIn("amplitude_and_residence_top_quartile", classes, filename)

    def test_case_reports_and_provenance_are_scoped(self):
        for stem, doi in [
            ("drg_calcium", "10.5281/zenodo.14907827"),
            ("erk_gpcr", "10.5281/zenodo.5836623"),
        ]:
            provenance = json.loads((STAGE7_3 / f"{stem}_provenance.json").read_text(encoding="utf-8"))
            report = (STAGE7_3 / f"{stem}_case_report.md").read_text(encoding="utf-8")
            self.assertEqual(provenance["zenodo_doi"], doi)
            self.assertIn("raw source files are not retained", provenance["raw_file_policy"])
            self.assertIn("Source citation", report)
            self.assertIn("Access route", report)
            self.assertIn("What RhoDyn adds", report)
            self.assertIn("Interpretation boundary", report)
