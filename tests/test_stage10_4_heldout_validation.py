import csv
import importlib.util
import json
from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_stage10_4_heldout_validation.py"
SPEC = importlib.util.spec_from_file_location("stage10_4", SCRIPT_PATH)
stage10_4 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(stage10_4)


class Stage104HeldoutValidationTests(TestCase):
    def test_runner_writes_passing_gate_report_with_all_outcome_classes(self):
        report = stage10_4.evaluate_stage10_4(ROOT / "case_studies" / "stage10_heldout_validation")
        self.assertEqual(report["status"], "pass")
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(report["summary_metrics"]["positive_call_count"], 2)
        self.assertEqual(report["summary_metrics"]["negative_call_count"], 1)
        self.assertEqual(report["summary_metrics"]["inconclusive_call_count"], 1)

        persisted = json.loads(
            (ROOT / "case_studies" / "stage10_heldout_validation" / "stage10_4_gate_report.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(persisted["next_phase"], "Stage 10.5 method-first Nature Methods figure architecture")

    def test_predeclaration_records_fixed_splits_and_rules(self):
        payload = json.loads(
            (ROOT / "case_studies" / "stage10_heldout_validation" / "stage10_4_predeclaration.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(payload["stage"], "10.4")
        self.assertEqual(payload["trajectory_decision_rule"]["threshold_source"], "training split only")
        self.assertIn("replicate 00", payload["trajectory_challenges"][0]["train"])
        self.assertIn("replicate 01", payload["trajectory_challenges"][0]["heldout"])
        fixed_plan = payload["paired_reporter_challenge"]["stage7_5_fixed_plan"]
        self.assertEqual(fixed_plan["source_doi"], "10.5281/zenodo.5836623")
        self.assertEqual(fixed_plan["primary_margin"], 0.2)

    def test_decisions_preserve_positive_negative_and_inconclusive_boundaries(self):
        with (ROOT / "case_studies" / "stage10_heldout_validation" / "stage10_4_heldout_decisions.tsv").open(
            newline="", encoding="utf-8"
        ) as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        classes = {row["outcome_class"] for row in rows}
        self.assertEqual(classes, {"positive", "negative", "inconclusive"})
        calls = {row["case_id"]: row["call"] for row in rows}
        self.assertEqual(
            calls["mlci_replicate_01_heldout_residence_amplitude"],
            "positive_residence_changes_interpretation",
        )
        self.assertEqual(
            calls["erk_gpcr_ligand_s1p_heldout_residence_amplitude"],
            "negative_amplitude_or_comparator_largely_sufficient",
        )
        self.assertEqual(
            calls["erk_akt_non_dmso_contexts_margin_inconclusive"],
            "inconclusive_margin_boundary_preserved",
        )
        self.assertTrue(all(row["hidden_tuning_status"] for row in rows))

    def test_object_level_calls_are_heldout_only_and_public_source_scoped(self):
        with (
            ROOT / "case_studies" / "stage10_heldout_validation" / "stage10_4_trajectory_object_calls.csv"
        ).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 74)
        self.assertEqual({row["split"] for row in rows}, {"heldout"})
        self.assertIn("amplitude_only_high", {row["heldout_class"] for row in rows})
        self.assertIn("residence_only_high", {row["heldout_class"] for row in rows})
        self.assertTrue(all(row["source"].startswith("Zenodo DOI") for row in rows))


if __name__ == "__main__":
    import unittest

    unittest.main()
