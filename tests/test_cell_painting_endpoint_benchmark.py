import csv
import json
from pathlib import Path
from unittest import TestCase

from rhodyn.schema import read_endpoint_csv


class CellPaintingEndpointBenchmarkTests(TestCase):
    def test_endpoint_model_rows_have_expected_stage3c_shape(self):
        path = Path("case_studies/cell_painting_mitotox_endpoint_model_rows.csv")
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 35532)
        self.assertEqual(len({row["compound_index"] for row in rows}), 658)
        self.assertEqual(len({row["endpoint"] for row in rows}), 9)
        self.assertEqual(
            {row["model"] for row in rows},
            {
                "endpoint_prevalence",
                "morphology_magnitude_5nn",
                "cells_block_5nn",
                "cytoplasm_block_5nn",
                "nuclei_block_5nn",
                "compartment_route_5nn",
            },
        )

        endpoint_rows, issues = read_endpoint_csv(path)
        self.assertFalse(issues)
        self.assertEqual(len(endpoint_rows), 35532)

    def test_model_ranking_identifies_routed_compartment_architecture(self):
        path = Path("case_studies/cell_painting_mitotox_model_ranking.csv")
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[0]["model"], "compartment_route_5nn")
        self.assertEqual(rows[0]["rank"], "1")
        self.assertLess(float(rows[0]["weighted_rmse"]), float(rows[1]["weighted_rmse"]))
        self.assertGreater(float(rows[1]["delta_bic"]), 200.0)
        self.assertGreater(
            float(rows[0]["mean_predicted_probability_on_active_endpoints"]),
            float(rows[1]["mean_predicted_probability_on_active_endpoints"]),
        )

    def test_benchmark_provenance_preserves_source_and_boundary(self):
        path = Path("case_studies/cell_painting_mitotox_model_comparison.provenance.json")
        provenance = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(provenance["zenodo_doi"], "10.5281/zenodo.10011861")
        self.assertEqual(provenance["license"], "CC-BY-4.0")
        self.assertEqual(provenance["diagnostics"]["compound_count"], 658)
        self.assertEqual(provenance["diagnostics"]["endpoint_count"], 9)
        self.assertEqual(provenance["diagnostics"]["best_model_by_bic"], "compartment_route_5nn")
        self.assertIn("not retained", provenance["raw_file_policy"])
        self.assertIn("does not infer drug mechanism", provenance["interpretation_boundary"])
