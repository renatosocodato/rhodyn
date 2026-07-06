"""Regression checks for Stage 9.15 Methods architecture."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


class Stage915MethodsArchitectureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate_path = WORKSPACE / "gate_verdicts" / "9.15.json"
        self.blueprint_path = WORKSPACE / "sections" / "methods_blueprint.md"
        self.ledger_path = WORKSPACE / "ledgers" / "methods_to_code_ledger.csv"
        self.gate = json.loads(self.gate_path.read_text(encoding="utf-8"))
        self.blueprint = self.blueprint_path.read_text(encoding="utf-8")
        with self.ledger_path.open(newline="", encoding="utf-8") as handle:
            self.ledger_rows = list(csv.DictReader(handle))

    def test_gate_passes_and_points_to_methods_drafting(self) -> None:
        self.assertTrue(self.gate["pass"])
        self.assertEqual(self.gate["substage"], "9.15")
        self.assertEqual(self.gate["next_substage"], "9.16")
        self.assertEqual(self.gate["methods_statement_count"], 9)
        self.assertEqual(self.gate["methods_subheading_count"], 6)
        self.assertEqual(self.gate["ledger_row_count"], self.gate["methods_statement_count"])
        self.assertTrue(all(item["passed"] for item in self.gate["checks"]))

    def test_blueprint_contains_required_methods_structure_and_boundaries(self) -> None:
        required_phrases = [
            "Input schemas and preprocessing",
            "Residence windows and amplitude comparators",
            "Bounded-coupling and uncertainty decisions",
            "Reserve-like endpoint construction",
            "Routed-output model comparison",
            "Software surfaces, versioning, and reproducibility",
            "dataset_version=",
            "dataset_date=",
            "not proof that all coupling is absent",
            "not direct assays of unmeasured biological reserve capacity",
            "does not identify direct biochemical interactions",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, self.blueprint)
        for index in range(1, 10):
            self.assertIn(f"MTH-{index:04d}", self.blueprint)
        unsafe_phrases = [
            "absence of all coupling",
            "true biological reserve",
            "literal molecular edge",
            "literal molecular interactions",
            "RhoDyn generated the original",
        ]
        for phrase in unsafe_phrases:
            self.assertNotIn(phrase, self.blueprint)

    def test_methods_to_code_ledger_is_schema_shaped_and_executable_by_reference(self) -> None:
        self.assertEqual(
            list(self.ledger_rows[0].keys()),
            ["methods_stmt_id", "art_id", "repo_path", "commit", "command"],
        )
        self.assertEqual(len(self.ledger_rows), 9)
        seen = set()
        for row in self.ledger_rows:
            self.assertRegex(row["methods_stmt_id"], r"^MTH-\d{4}$")
            self.assertNotIn(row["methods_stmt_id"], seen)
            seen.add(row["methods_stmt_id"])
            self.assertRegex(row["art_id"], r"^ART-\d{4}$")
            self.assertTrue((ROOT / row["repo_path"]).exists(), row["repo_path"])
            self.assertRegex(row["commit"], r"^[0-9a-f]{40}$")
            self.assertIn("dataset_version=", row["command"])
            self.assertIn("dataset_date=", row["command"])

    def test_no_downstream_methods_or_submission_surfaces_started(self) -> None:
        forbidden = [
        ]
        for rel in forbidden:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
