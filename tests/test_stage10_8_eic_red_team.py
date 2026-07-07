"""Regression tests for Stage 10.8 adversarial EIC red-team simulation."""

from __future__ import annotations

import csv
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_stage10_8_eic_red_team.py"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_eic_red_team"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage10_8_runner", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stage108EicRedTeamTest(unittest.TestCase):
    def test_stage10_8_red_team_gate_and_outputs(self) -> None:
        module = _load_runner()
        report = module.run_stage10_8()

        self.assertEqual(report["status"], "pass")
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(report["summary_metrics"]["perspective_count"], 6)
        self.assertGreaterEqual(report["summary_metrics"]["action_row_count"], 10)
        self.assertEqual(report["summary_metrics"]["unresolved_high_severity_count"], 0)
        self.assertEqual(report["summary_metrics"]["verdict_category_count"], 5)
        self.assertEqual(report["next_phase"], "Stage 10.9 EIC-contact decision")

        gate_report = json.loads((OUTPUT_DIR / "stage10_8_gate_report.json").read_text(encoding="utf-8"))
        self.assertEqual(gate_report["status"], "pass")
        self.assertIn("does not add biological data", gate_report["interpretation_boundary"])

    def test_stage10_8_required_perspectives_domains_and_verdicts(self) -> None:
        _load_runner().run_stage10_8()

        with (OUTPUT_DIR / "stage10_8_red_team_action_matrix.tsv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        with (OUTPUT_DIR / "stage10_8_verdict_rubric.tsv").open(encoding="utf-8") as handle:
            verdict_rows = list(csv.DictReader(handle, delimiter="\t"))

        self.assertEqual(
            {row["perspective"] for row in rows},
            {
                "Nature Methods EIC",
                "methods editor",
                "computational methods reviewer",
                "live-cell signaling biologist",
                "statistician/benchmarking reviewer",
                "software reproducibility reviewer",
            },
        )
        self.assertTrue(
            {"novelty", "validation_breadth", "named_benchmarking", "overclaiming"}.issubset(
                {row["risk_domain"] for row in rows}
            )
        )
        self.assertEqual(
            {row["verdict_category"] for row in verdict_rows},
            {
                "desk-reject likely",
                "presubmission only",
                "full submission viable",
                "delay for another dataset",
                "pivot venue",
            },
        )
        self.assertFalse(
            [
                row
                for row in rows
                if row["risk_domain"] in {"novelty", "validation_breadth", "named_benchmarking", "overclaiming"}
                and row["unresolved_high_severity"] == "yes"
            ]
        )

    def test_stage10_8_text_boundaries_and_decision_brief(self) -> None:
        _load_runner().run_stage10_8()

        report = (OUTPUT_DIR / "stage10_8_red_team_report.md").read_text(encoding="utf-8")
        decision = (OUTPUT_DIR / "stage10_8_decision_brief.md").read_text(encoding="utf-8")
        doc = (ROOT / "docs" / "stage10_8_adversarial_eic_red_team.md").read_text(encoding="utf-8")

        self.assertIn("not a universal claim", report)
        self.assertIn("Software reproducibility supports the method claim but is not the primary scientific advance", report)
        self.assertIn("Presubmission-style contact", decision)
        self.assertIn("does not add biological data", doc)


if __name__ == "__main__":
    unittest.main()
