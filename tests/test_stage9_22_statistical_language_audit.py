"""Regression checks for Stage 9.22 statistical and quantitative language audit."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.22.json"
AUDIT_PATH = WORKSPACE / "audits" / "statistical_language_audit.md"
DIFF_PATH = WORKSPACE / "audits" / "live_numbers_diff.csv"
STATISTIC_LEDGER_PATH = WORKSPACE / "ledgers" / "statistic_ledger.csv"
FIGURE_LEDGER_PATH = WORKSPACE / "ledgers" / "figure_to_claim_to_artifact.csv"
ARCHIVE_MANIFEST_PATH = ROOT / "case_studies" / "stage7_methods_reproducibility" / "release_archive_manifest.tsv"


class Stage922StatisticalLanguageAuditTests(unittest.TestCase):
    def _rows(self, path: Path) -> list[dict[str, str]]:
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def _archive_row_count_value(self) -> str:
        with ARCHIVE_MANIFEST_PATH.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        return f"row_count={len(rows)}"

    def test_gate_passes_and_points_to_figure_legend_audit(self) -> None:
        gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        self.assertIs(gate["pass"], True)
        self.assertEqual(gate["substage"], "9.22")
        self.assertEqual(gate["next_substage"], "9.23")
        self.assertEqual(gate["statistic_count"], 19)
        self.assertEqual(gate["live_number_row_count"], 19)
        self.assertEqual(gate["updated_statistic_count"], len(gate["updated_stat_ids"]))
        self.assertLessEqual(set(gate["updated_stat_ids"]), {"STAT-0018"})
        self.assertTrue(gate["figure_stat_id_map_complete"])
        self.assertEqual(gate["failed_stat_ids"], [])
        self.assertEqual(gate["unsupported_quantitative_statements"], [])
        self.assertTrue(all(item["passed"] for item in gate["checks"]))

    def test_live_number_diff_records_stale_archive_count_update(self) -> None:
        rows = self._rows(DIFF_PATH)
        self.assertEqual(len(rows), 19)
        statuses = {row["status"] for row in rows}
        self.assertLessEqual(statuses, {"pass", "updated", "inspection_only_pass"})
        stat18 = next(row for row in rows if row["stat_id"] == "STAT-0018")
        self.assertEqual(stat18["expected_value"], self._archive_row_count_value())
        self.assertRegex(stat18["manuscript_value"], r"^row_count=\d+$")
        self.assertIn(stat18["status"], {"pass", "updated"})

    def test_statistic_ledger_and_figure_bindings_are_current(self) -> None:
        stat_rows = {row["stat_id"]: row for row in self._rows(STATISTIC_LEDGER_PATH)}
        self.assertEqual(len(stat_rows), 19)
        self.assertEqual(stat_rows["STAT-0018"]["value"], self._archive_row_count_value())
        self.assertEqual(stat_rows["STAT-0018"]["n"], self._archive_row_count_value())

        figure_rows = {row["fig_id"]: row for row in self._rows(FIGURE_LEDGER_PATH)}
        expected = {
            "FIG-001": "STAT-0001;STAT-0002;STAT-0003;STAT-0019",
            "FIG-002": "STAT-0004;STAT-0005",
            "FIG-003": "STAT-0006;STAT-0007;STAT-0008",
            "FIG-004": "STAT-0009;STAT-0010;STAT-0011;STAT-0012;STAT-0013;STAT-0014",
            "FIG-005": "STAT-0015;STAT-0016",
            "FIG-006": "STAT-0017;STAT-0018",
        }
        self.assertEqual({fig_id: row["stat_ids"] for fig_id, row in figure_rows.items()}, expected)
        self.assertNotIn("pending_stage9.22", FIGURE_LEDGER_PATH.read_text(encoding="utf-8"))

    def test_audit_reports_scope_and_boundaries(self) -> None:
        audit = AUDIT_PATH.read_text(encoding="utf-8")
        for phrase in [
            "The live-number audit passed",
            "Nineteen statistic IDs were recomputed or inspected",
            "`STAT-0018`, the release-archive manifest file count",
            "bounded-coupling language remains scoped to declared margins",
            "does not write or modify figure legends",
            "does not add new data, figures, analyses, model outputs, or biological claims",
        ]:
            self.assertIn(phrase, audit)

    def test_downstream_surfaces_remain_unstarted(self) -> None:
        for rel in [
            "audits/reader_surface_hygiene_report.md",
            "audits/reader_surface_hygiene_report.md",
            "submission_package/pi_review_packet.md",
            "submission_package/submission_readiness_checklist.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
