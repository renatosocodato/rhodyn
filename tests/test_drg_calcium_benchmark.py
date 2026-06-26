import csv
import json
from collections import Counter
from pathlib import Path
from unittest import TestCase


class DrgCalciumBenchmarkTests(TestCase):
    def test_retained_benchmark_has_expected_stage3a_shape(self):
        path = Path("case_studies/drg_calcium_residence_amplitude_benchmark.csv")
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 360)
        self.assertEqual(len({row["cell_id"] for row in rows}), 120)
        self.assertEqual(
            Counter(row["condition"] for row in rows),
            {
                "drg_calcium_episode_1": 120,
                "drg_calcium_episode_2": 120,
                "drg_calcium_episode_3": 120,
            },
        )

    def test_benchmark_contains_amplitude_and_residence_separation(self):
        path = Path("case_studies/drg_calcium_residence_amplitude_benchmark.csv")
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        classes = Counter(row["amplitude_residence_class"] for row in rows)

        self.assertGreater(classes["amplitude_only_top_quartile"], 0)
        self.assertGreater(classes["residence_only_top_quartile"], 0)
        self.assertGreater(classes["amplitude_and_residence_top_quartile"], 0)

    def test_benchmark_provenance_preserves_source_and_boundary(self):
        path = Path("case_studies/drg_calcium_residence_amplitude_benchmark.provenance.json")
        provenance = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(provenance["zenodo_doi"], "10.5281/zenodo.14907827")
        self.assertEqual(provenance["license"], "CC-BY-4.0")
        self.assertEqual(provenance["benchmark_rows"], 360)
        self.assertEqual(provenance["selected_cell_count"], 120)
        self.assertIn("not retained", provenance["raw_file_policy"])
        self.assertIn("does not assign stimulus identity", provenance["interpretation_boundary"])
