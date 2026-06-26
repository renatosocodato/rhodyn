import csv
import json
from pathlib import Path
from unittest import TestCase

from rhodyn.schema import read_coupling_csv


class ErkAktBoundedCouplingBenchmarkTests(TestCase):
    def test_residence_summary_preserves_paired_public_cells(self):
        path = Path("case_studies/erk_gpcr_erk_akt_residence_summary.csv")
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 180)
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["ligand"]] = counts.get(row["ligand"], 0) + 1
            self.assertEqual(row["dataset"], "erk_gpcr_ktr_wan2021")
            self.assertGreaterEqual(float(row["erk_residence_fraction"]), 0.0)
            self.assertLessEqual(float(row["erk_residence_fraction"]), 1.0)
            self.assertGreaterEqual(float(row["akt_residence_fraction"]), 0.0)
            self.assertLessEqual(float(row["akt_residence_fraction"]), 1.0)

        self.assertEqual(counts, {"His": 60, "S1P": 60, "UK": 60})
        self.assertAlmostEqual(float(rows[0]["erk_threshold"]), 0.7623, places=4)
        self.assertAlmostEqual(float(rows[0]["akt_threshold"]), 0.5892, places=4)

    def test_bounded_coupling_table_validates_and_keeps_context_limit(self):
        path = Path("case_studies/erk_gpcr_erk_akt_bounded_coupling.csv")
        records, issues = read_coupling_csv(path)
        self.assertEqual(issues, [])
        self.assertEqual(len(records), 4)

        with path.open(newline="", encoding="utf-8") as handle:
            rows = {row["contrast"]: row for row in csv.DictReader(handle)}

        self.assertEqual(rows["erk_minus_akt_residence_UK"]["passes"], "1")
        self.assertEqual(rows["erk_minus_akt_residence_His"]["passes"], "0")
        self.assertEqual(rows["erk_minus_akt_residence_S1P"]["passes"], "0")
        self.assertEqual(rows["erk_minus_akt_residence_all"]["passes"], "1")
        self.assertEqual(rows["erk_minus_akt_residence_UK"]["method"], "normal_approximation")
        self.assertAlmostEqual(float(rows["erk_minus_akt_residence_UK"]["margin"]), 0.20)

    def test_provenance_records_public_source_and_boundary(self):
        path = Path("case_studies/erk_gpcr_erk_akt_bounded_coupling.provenance.json")
        provenance = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(provenance["zenodo_doi"], "10.5281/zenodo.5836623")
        self.assertEqual(provenance["license"], "CC-BY-4.0")
        self.assertEqual(provenance["selected_cell_count"], 180)
        self.assertIn("erk_minus_akt_residence_UK", provenance["passed_contrasts"])
        self.assertIn("erk_minus_akt_residence_His", provenance["failed_contrasts"])
        self.assertIn("erk_minus_akt_residence_S1P", provenance["failed_contrasts"])
        boundary = provenance["interpretation_boundary"]
        self.assertIn("not biochemical equivalence", boundary)
        self.assertIn("not absence of all GPCR pathway crosstalk", boundary)

    def test_margin_sensitivity_preserves_context_specific_decision(self):
        path = Path("case_studies/erk_gpcr_erk_akt_margin_sensitivity.csv")
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 40)
        by_contrast: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            by_contrast.setdefault(row["contrast"], []).append(row)

        def min_passing_margin(contrast: str) -> float | None:
            passing = [
                float(row["tested_margin"])
                for row in by_contrast[contrast]
                if row["passes"] == "1"
            ]
            return min(passing) if passing else None

        self.assertAlmostEqual(min_passing_margin("erk_minus_akt_residence_UK"), 0.10)
        self.assertAlmostEqual(min_passing_margin("erk_minus_akt_residence_all"), 0.05)
        self.assertAlmostEqual(min_passing_margin("erk_minus_akt_residence_His"), 0.25)
        self.assertAlmostEqual(min_passing_margin("erk_minus_akt_residence_S1P"), 0.30)

    def test_threshold_sensitivity_keeps_primary_claim_context_limited(self):
        path = Path("case_studies/erk_gpcr_erk_akt_threshold_sensitivity.csv")
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 24)
        by_contrast: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            by_contrast.setdefault(row["contrast"], []).append(row)

        self.assertTrue(all(row["passes"] == "1" for row in by_contrast["erk_minus_akt_residence_UK"]))
        self.assertTrue(all(row["passes"] == "1" for row in by_contrast["erk_minus_akt_residence_all"]))
        self.assertTrue(all(row["passes"] == "0" for row in by_contrast["erk_minus_akt_residence_His"]))
        self.assertTrue(all(row["passes"] == "0" for row in by_contrast["erk_minus_akt_residence_S1P"]))

    def test_hardening_report_records_scope_and_unavailable_replicate_sensitivity(self):
        path = Path("case_studies/erk_gpcr_erk_akt_hardening_report.json")
        report = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["replicate_sensitivity_status"], "not_available")
        self.assertIn("one experiment label per ligand", report["replicate_sensitivity_reason"])
        self.assertEqual(report["minimum_passing_margin_by_contrast"]["erk_minus_akt_residence_UK"], 0.1)
        self.assertEqual(report["minimum_passing_margin_by_contrast"]["erk_minus_akt_residence_His"], 0.25)
        self.assertEqual(report["minimum_passing_margin_by_contrast"]["erk_minus_akt_residence_S1P"], 0.3)
        interpretation = report["stage3d_closure_interpretation"]
        self.assertIn("public bounded-coupling case", interpretation)
        self.assertIn("secondary", interpretation)
