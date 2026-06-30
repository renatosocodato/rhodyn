import csv
import importlib.util
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
STAGE7_6 = ROOT / "case_studies" / "stage7_methods_reproducibility"
SCRIPT_PATH = ROOT / "scripts" / "run_stage7_6_methods_reproducibility.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage7_6_runner_under_test", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


RUNNER = _load_runner()


@dataclass
class _Example:
    residence_fraction: float


def _tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class Stage76MethodsReproducibilityTests(TestCase):
    def test_field_value_accepts_dicts_and_typed_objects(self):
        self.assertEqual(RUNNER._field_value({"residence_fraction": 0.75}, "residence_fraction"), 0.75)
        self.assertEqual(RUNNER._field_value(_Example(0.25), "residence_fraction"), 0.25)

    def test_compare_outputs_detects_match_mismatch_and_missing_clean_output(self):
        original_outputs = list(RUNNER.DETERMINISTIC_OUTPUTS)
        try:
            RUNNER.DETERMINISTIC_OUTPUTS = ["same.csv", "different.csv", "missing.csv"]
            with tempfile.TemporaryDirectory() as clean_dir, tempfile.TemporaryDirectory() as ref_dir:
                clean = Path(clean_dir)
                reference = Path(ref_dir)
                (clean / "same.csv").write_text("value\n1\n", encoding="utf-8")
                (reference / "same.csv").write_text("value\n1\n", encoding="utf-8")
                (clean / "different.csv").write_text("value\n1\n", encoding="utf-8")
                (reference / "different.csv").write_text("value\n2\n", encoding="utf-8")
                (reference / "missing.csv").write_text("value\n3\n", encoding="utf-8")

                rows = {row["path"]: row for row in RUNNER._compare_outputs(clean, reference)}

            self.assertEqual(rows["same.csv"]["matches"], 1)
            self.assertEqual(rows["different.csv"]["matches"], 0)
            self.assertEqual(rows["missing.csv"]["clean_room_exists"], 0)
            self.assertEqual(rows["missing.csv"]["matches"], 0)
        finally:
            RUNNER.DETERMINISTIC_OUTPUTS = original_outputs

    def test_archive_surface_scan_detects_private_paths_and_raw_like_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text("RhoDyn clean release text.\n", encoding="utf-8")
            clean_step = RUNNER._archive_surface_scan(root)
            self.assertEqual(clean_step.status, "pass")

            (root / "docs").mkdir()
            private_path = "/" + "Users/example/project"
            (root / "docs" / "leak.md").write_text(f"bad local path {private_path}\n", encoding="utf-8")
            (root / "private.tif").write_bytes(b"not a release payload")
            failed_step = RUNNER._archive_surface_scan(root)

        self.assertEqual(failed_step.status, "fail")
        self.assertIn("local path or credential-like pattern", failed_step.stderr_tail)
        self.assertIn("raw/private-data-like file present", failed_step.stderr_tail)

    def test_workflow_checks_cover_methods_reproducibility_surfaces(self):
        checks = RUNNER._workflow_checks(ROOT)
        expected = {
            "ci_runs_python_tests",
            "ci_runs_package_build",
            "ci_runs_docs_build",
            "ci_runs_docker_build",
            "ci_runs_frontend_regression",
            "ci_runs_methods_reproducibility",
            "ci_runs_notebook_or_methods_examples",
        }
        self.assertEqual(set(checks), expected)
        self.assertTrue(all(value == "pass" for value in checks.values()))

    def test_gate_reports_record_full_release_archive_success(self):
        for path in [
            ROOT / "docs" / "stage7_6_gate_report.json",
            STAGE7_6 / "stage7_6_methods_reproducibility_gate_report.json",
        ]:
            with self.subTest(path=path):
                gate = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(gate["status"], "pass")
                self.assertEqual(gate["mode"], "full_release_archive")
                self.assertEqual(gate["completion_state"], "complete_methods_reproducibility_hardening")
                self.assertEqual(gate["comparison_summary"], {"checked_outputs": 30, "matched_outputs": 30})
                self.assertEqual(gate["parity_summary"], {"checked_operations": 4, "matching_operations": 4})
                self.assertEqual(gate["step_failures"], [])
                self.assertEqual(gate["workflow_failures"], [])
                checkpoints = gate["validation_checkpoints"]
                for key in [
                    "fresh_environment_reproduces_benchmark_tables",
                    "tutorial_outputs_execute",
                    "public_release_scan_finds_no_private_paths_or_secrets",
                    "frontend_backend_cli_python_outputs_agree",
                    "ci_covers_selected_examples_docs_notebooks_benchmarks_package_docker_frontend",
                    "clean_room_reproduction_from_release_archive",
                ]:
                    self.assertEqual(checkpoints[key], "pass", key)
                self.assertEqual(checkpoints["stop_condition_clean_room_failure"], "not_triggered")
                self.assertIn("does not add biological evidence", gate["interpretation_boundary"])

    def test_output_comparison_and_parity_tables_match_gate_summary(self):
        comparison_rows = _tsv_rows(STAGE7_6 / "methods_output_comparison.tsv")
        parity_rows = _tsv_rows(STAGE7_6 / "cross_surface_parity.tsv")
        gate = json.loads((STAGE7_6 / "stage7_6_methods_reproducibility_gate_report.json").read_text(encoding="utf-8"))

        self.assertEqual(len(comparison_rows), gate["comparison_summary"]["checked_outputs"])
        self.assertEqual(sum(row["matches"] == "1" for row in comparison_rows), gate["comparison_summary"]["matched_outputs"])
        self.assertTrue(all(row["reference_exists"] == "1" and row["clean_room_exists"] == "1" for row in comparison_rows))
        self.assertEqual(len(parity_rows), gate["parity_summary"]["checked_operations"])
        self.assertEqual(sum(row["passes"] == "1" for row in parity_rows), gate["parity_summary"]["matching_operations"])
        self.assertEqual(
            {row["operation"] for row in parity_rows},
            {"score_residence", "decide_coupling", "summarize_reserve", "compare_models"},
        )

    def test_reproduction_command_table_covers_stage7_1_through_stage7_5(self):
        rows = _tsv_rows(STAGE7_6 / "methods_reproducibility_commands.tsv")
        phases = [row["phase"] for row in rows]
        for expected in [
            "7.1 synthetic truth cases",
            "7.2 benchmark harness",
            "7.3 public signaling demonstrations",
            "7.4 endpoint reserve routing",
            "7.5 held-out validation",
            "docs",
            "surface parity",
        ]:
            self.assertIn(expected, phases)
        self.assertTrue(all(row["mode"] == "full_release_archive" for row in rows))

    def test_stage7_6_reports_are_sanitized_and_scientifically_scoped(self):
        for path in [
            ROOT / "docs" / "stage7_6_gate_report.json",
            ROOT / "docs" / "stage7_6_clean_room_report.json",
            ROOT / "docs" / "stage7_methods_reproducibility_card.md",
            STAGE7_6 / "stage7_6_methods_reproducibility_report.md",
        ]:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("/" + "Users/", text)
                self.assertNotIn("/" + "Volumes/", text)
                self.assertNotIn("/private/tmp/rhodyn_stage7_6_", text)
                self.assertIn("does not add", text)
