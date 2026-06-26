import csv
import json
from collections import Counter
from pathlib import Path
from unittest import TestCase


class ErkGpcrBenchmarkTests(TestCase):
    def test_retained_benchmark_has_expected_stage3b_shape(self):
        path = Path("case_studies/erk_gpcr_residence_amplitude_benchmark.csv")
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 180)
        self.assertEqual(len({row["cell_id"] for row in rows}), 180)
        self.assertEqual(
            Counter(row["ligand"] for row in rows),
            {
                "His": 60,
                "S1P": 60,
                "UK": 60,
            },
        )
        self.assertTrue(all(row["dataset"] == "erk_gpcr_ktr_wan2021" for row in rows))
        self.assertTrue(all(row["inhibitor"] == "DMSO" for row in rows))

    def test_benchmark_contains_amplitude_and_residence_separation(self):
        path = Path("case_studies/erk_gpcr_residence_amplitude_benchmark.csv")
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        classes = Counter(row["amplitude_residence_class"] for row in rows)

        self.assertEqual(classes["amplitude_and_residence_top_quartile"], 34)
        self.assertEqual(classes["amplitude_only_top_quartile"], 11)
        self.assertEqual(classes["residence_only_top_quartile"], 11)
        self.assertEqual(classes["neither_top_quartile"], 124)

    def test_benchmark_provenance_preserves_source_and_boundary(self):
        path = Path("case_studies/erk_gpcr_residence_amplitude_benchmark.provenance.json")
        provenance = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(provenance["zenodo_doi"], "10.5281/zenodo.5836623")
        self.assertEqual(provenance["license"], "CC-BY-4.0")
        self.assertEqual(provenance["archive_file"], "Figure_3.zip")
        self.assertEqual(provenance["benchmark_rows"], 180)
        self.assertEqual(provenance["selected_cell_count"], 180)
        self.assertIn("not retained", provenance["raw_file_policy"])
        self.assertIn("not a calibrated biological activation boundary", provenance["interpretation_boundary"])
