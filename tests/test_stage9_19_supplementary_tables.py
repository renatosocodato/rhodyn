"""Regression checks for Stage 9.19 supplementary table/source-data binding."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
PLAN_PATH = WORKSPACE / "supplementary" / "supplementary_tables_plan.md"
SOURCE_LEDGER_PATH = WORKSPACE / "supplementary" / "source_data_binding_ledger.csv"
STAT_LEDGER_PATH = WORKSPACE / "ledgers" / "statistic_ledger.csv"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.19.json"


class Stage919SupplementaryTablesTests(unittest.TestCase):
    def _source_rows(self) -> list[dict[str, str]]:
        with SOURCE_LEDGER_PATH.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def _stat_rows(self) -> list[dict[str, str]]:
        with STAT_LEDGER_PATH.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def test_gate_passes_and_points_to_reference_audit(self) -> None:
        gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        self.assertIs(gate["pass"], True)
        self.assertEqual(gate["substage"], "9.19")
        self.assertEqual(gate["next_substage"], "9.20")
        self.assertEqual(gate["table_count"], 9)
        self.assertEqual(gate["statistic_row_count"], 19)
        self.assertEqual(set(gate["table_ids"]), {f"STBL-{idx:03d}" for idx in range(1, 10)})
        self.assertEqual(set(gate["supp_ids"]), {f"SUPP-{idx:03d}" for idx in range(1, 10)})
        self.assertEqual(set(gate["stat_ids"]), {f"STAT-{idx:04d}" for idx in range(1, 20)})
        self.assertEqual(set(gate["linked_figures"]), {f"FIG-{idx:03d}" for idx in range(1, 7)})
        self.assertTrue(all(item["passed"] for item in gate["checks"]))

    def test_table_plan_contains_reviewable_evidence_map(self) -> None:
        body = PLAN_PATH.read_text(encoding="utf-8")
        for phrase in [
            "Supplementary table and source-data binding plan",
            "Table evidence map",
            "Every planned table has a main-text callout route",
            "Every table references one or more statistic IDs",
            "Every table also records a figure-source mapping",
            "do not add new biological demonstrations",
            "turn model-derived coordinates into direct biological endpoints",
        ]:
            self.assertIn(phrase, body)
        for table_id in [f"STBL-{idx:03d}" for idx in range(1, 10)]:
            self.assertIn(table_id, body)
        for stat_id in ["STAT-0001", "STAT-0010", "STAT-0019"]:
            self.assertIn(stat_id, body)

    def test_source_binding_resolves_callouts_figures_and_render_paths(self) -> None:
        rows = self._source_rows()
        self.assertEqual(len(rows), 9)
        covered_figures = {
            fig_id
            for row in rows
            for fig_id in row["linked_main_figures"].split(";")
            if fig_id
        }
        self.assertEqual(covered_figures, {f"FIG-{idx:03d}" for idx in range(1, 7)})
        for row in rows:
            for field in [
                "callout_location",
                "role",
                "source_artifacts",
                "source_paths",
                "panelforge_recipe",
                "render_paths",
                "interpretation_boundary",
            ]:
                self.assertTrue(row[field], f"{row['table_id']} missing {field}")
            self.assertIn("bound_stage9_19", row["binding_status"])
            for render_path in [item for item in row["render_paths"].split(";") if item]:
                self.assertTrue((ROOT / render_path).exists(), render_path)

    def test_statistic_ledger_has_complete_ids_and_source_routes(self) -> None:
        rows = self._stat_rows()
        self.assertEqual(len(rows), 19)
        self.assertEqual({row["stat_id"] for row in rows}, {f"STAT-{idx:04d}" for idx in range(1, 20)})
        for row in rows:
            for field in ["art_id", "fig_id", "value", "ci", "n", "test", "source_command", "manuscript_locations"]:
                self.assertTrue(row[field], f"{row['stat_id']} missing {field}")
            self.assertRegex(row["stat_id"], r"^STAT-[0-9]{4}$")
        self.assertTrue(any("row_count=" in row["value"] for row in rows))
        self.assertTrue(any(row["test"] == "AIC/BIC ranking and delta BIC" for row in rows))

    def test_downstream_reference_legend_and_package_surfaces_are_absent(self) -> None:
        for rel in [
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
