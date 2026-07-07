import csv
import importlib.util
import json
from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_stage10_5_figure_architecture.py"
SPEC = importlib.util.spec_from_file_location("stage10_5", SCRIPT_PATH)
stage10_5 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(stage10_5)


class Stage105FigureArchitectureTests(TestCase):
    def test_runner_writes_passing_method_first_gate_report(self):
        report = stage10_5.run_stage10_5()
        self.assertEqual(report["status"], "pass")
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(report["summary_metrics"]["figure_count"], 6)
        self.assertGreaterEqual(report["summary_metrics"]["panel_count"], 30)
        self.assertEqual(report["figure_roles"]["FIG-001"], "method_object_first")
        self.assertEqual(report["figure_roles"]["FIG-002"], "named_baseline_benchmarking")
        self.assertEqual(report["figure_roles"]["FIG-003"], "public_biological_breadth")
        self.assertEqual(report["figure_roles"]["FIG-006"], "software_reproducibility_secondary")

        persisted = json.loads(
            (ROOT / "case_studies" / "stage10_figure_architecture" / "stage10_5_gate_report.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(persisted["next_phase"], "Stage 10.6 manuscript and cover-letter pitch transformation")

    def test_panel_crosswalk_links_every_panel_to_existing_evidence_and_scripts(self):
        with (ROOT / "manuscript" / "nature_methods" / "figures" / "stage10_5_panel_evidence_crosswalk.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len({row["fig_id"] for row in rows}), 6)
        for row in rows:
            self.assertTrue(row["evidence_files"], row["panel_id"])
            self.assertTrue(row["source_scripts"], row["panel_id"])
            for rel in row["evidence_files"].split(";"):
                self.assertTrue((ROOT / rel).exists(), f"{row['panel_id']} missing evidence {rel}")
            for rel in row["source_scripts"].split(";"):
                self.assertTrue((ROOT / rel).exists(), f"{row['panel_id']} missing script {rel}")

    def test_figure_sequence_addresses_editorial_vulnerabilities_before_software(self):
        with (ROOT / "manuscript" / "nature_methods" / "figures" / "stage10_5_panel_evidence_crosswalk.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            rows = list(csv.DictReader(handle))
        vulnerabilities_by_fig = {
            fig: {row["vulnerability_addressed"] for row in rows if row["fig_id"] == fig}
            for fig in sorted({row["fig_id"] for row in rows})
        }
        self.assertIn("method_novelty", vulnerabilities_by_fig["FIG-001"])
        self.assertIn("limited_named_tool_benchmarking", vulnerabilities_by_fig["FIG-002"])
        self.assertIn("small_public_biological_demonstration_count", vulnerabilities_by_fig["FIG-003"])
        self.assertIn("heldout_validation", vulnerabilities_by_fig["FIG-005"])
        software_figures = {row["fig_id"] for row in rows if "software" in row["role_class"]}
        self.assertEqual(software_figures, {"FIG-006"})

    def test_supplementary_map_has_exactly_one_existing_parent_per_item(self):
        with (ROOT / "manuscript" / "nature_methods" / "figures" / "stage10_5_panel_evidence_crosswalk.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            panel_ids = {row["panel_id"] for row in csv.DictReader(handle)}
        with (ROOT / "manuscript" / "nature_methods" / "figures" / "stage10_5_supplementary_map.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreaterEqual(len(rows), 6)
        self.assertEqual(len({row["supp_id"] for row in rows}), len(rows))
        for row in rows:
            self.assertIn(row["parent_panel"], panel_ids)
            self.assertTrue(row["role"])


if __name__ == "__main__":
    import unittest

    unittest.main()
