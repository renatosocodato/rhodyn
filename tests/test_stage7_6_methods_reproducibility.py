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
AUDIT_PATH = ROOT / "scripts" / "audit_stage7_6_recursive_hardening.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("stage7_6_runner_under_test", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


RUNNER = _load_runner()


def _load_audit_runner():
    spec = importlib.util.spec_from_file_location("stage7_6_recursive_audit_under_test", AUDIT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


AUDIT = _load_audit_runner()


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

    def test_archive_manifest_records_required_files_and_rejects_raw_like_payloads(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel in [
                "pyproject.toml",
                "src/rhodyn/__init__.py",
                "scripts/build_stage7_1_synthetic_truth_cases.py",
                "scripts/run_stage7_2_benchmark_harness.py",
                "scripts/run_stage7_3_public_signaling.py",
                "scripts/run_stage7_4_endpoint_reserve_routing.py",
                "scripts/run_stage7_5_heldout_validation.py",
                "scripts/run_stage7_6_methods_reproducibility.py",
                "scripts/audit_stage7_6_recursive_hardening.py",
                "scripts/run_stage7_7_usability_rehearsal.py",
                "docs/stage7_methods_program.md",
                "docs/stage7_6_api_stability_policy.md",
                "docs/stage7_6_recursive_hardening.md",
                "docs/stage7_usability_rehearsal.md",
                "docs/stage7_user_path_findings.md",
                "docs/stage7_7_gate_report.json",
                "case_studies/stage7_usability_rehearsal/stage7_7_usability_gate_report.json",
                "tests/test_stage7_7_usability_rehearsal.py",
                "notebooks/01_synthetic_residence_primer.ipynb",
                "notebooks/07_stage7_heldout_validation.ipynb",
                "examples/synthetic_trajectory.csv",
                "examples/synthetic_coupling.csv",
            ]:
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("release file\n", encoding="utf-8")

            rows = RUNNER._archive_manifest_rows(root)
            summary = RUNNER._archive_manifest_summary(rows)
            self.assertEqual(summary["manifest_status"], "pass")
            self.assertEqual(summary["raw_private_like_file_count"], 0)
            self.assertEqual(summary["missing_required_files"], [])

            raw_path = root / "private_raw.tif"
            raw_path.write_bytes(b"not for release")
            raw_summary = RUNNER._archive_manifest_summary(RUNNER._archive_manifest_rows(root))
            self.assertEqual(raw_summary["manifest_status"], "fail")
            self.assertEqual(raw_summary["raw_private_like_file_count"], 1)

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
                    "release_archive_manifest_is_complete",
                ]:
                    self.assertEqual(checkpoints[key], "pass", key)
                self.assertEqual(checkpoints["stop_condition_clean_room_failure"], "not_triggered")
                self.assertIn("does not add biological evidence", gate["interpretation_boundary"])
                archive_manifest = gate["release_archive_manifest_summary"]
                self.assertEqual(archive_manifest["manifest_status"], "pass")
                self.assertEqual(archive_manifest["raw_private_like_file_count"], 0)
                self.assertEqual(archive_manifest["missing_required_files"], [])

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

    def test_release_archive_manifest_table_matches_gate_summary(self):
        manifest_rows = _tsv_rows(STAGE7_6 / "release_archive_manifest.tsv")
        gate = json.loads((STAGE7_6 / "stage7_6_methods_reproducibility_gate_report.json").read_text(encoding="utf-8"))
        summary = gate["release_archive_manifest_summary"]

        self.assertEqual(len(manifest_rows), summary["file_count"])
        self.assertGreater(summary["text_file_count"], 0)
        self.assertEqual(summary["raw_private_like_file_count"], 0)
        self.assertEqual(summary["manifest_status"], "pass")
        self.assertIn("scripts/run_stage7_6_methods_reproducibility.py", {row["path"] for row in manifest_rows})
        self.assertTrue(all(len(row["sha256"]) == 64 for row in manifest_rows))

    def test_recursive_hardening_report_passes_and_catches_internal_drift(self):
        report = json.loads((ROOT / "docs" / "stage7_6_recursive_hardening_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "pass")
        for key in [
            "gate_reports_identical",
            "full_archive_mode",
            "deterministic_outputs_match",
            "cross_surface_parity_matches",
            "archive_manifest_complete",
            "workflow_checks_pass",
            "scope_boundary_preserved",
        ]:
            self.assertEqual(report["checks"][key], "pass", key)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            for rel in [
                "docs/stage7_6_gate_report.json",
                "docs/stage7_6_clean_room_report.json",
                "case_studies/stage7_methods_reproducibility/stage7_6_methods_reproducibility_gate_report.json",
                "case_studies/stage7_methods_reproducibility/methods_output_comparison.tsv",
                "case_studies/stage7_methods_reproducibility/cross_surface_parity.tsv",
                "case_studies/stage7_methods_reproducibility/methods_reproducibility_commands.tsv",
                "case_studies/stage7_methods_reproducibility/release_archive_manifest.tsv",
            ]:
                source = ROOT / rel
                destination = temp_root / rel
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            gate_path = temp_root / "docs/stage7_6_gate_report.json"
            gate = json.loads(gate_path.read_text(encoding="utf-8"))
            gate["mode"] = "ci_fast"
            gate_path.write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
            drifted = AUDIT.audit_stage7_6_recursive_hardening(temp_root)

        self.assertEqual(drifted["status"], "fail")
        self.assertTrue(any("full_release_archive" in failure for failure in drifted["failures"]))

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
