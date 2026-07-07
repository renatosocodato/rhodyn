import csv
import importlib.util
import json
from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_stage10_7_benchmark_release_candidate.py"
SPEC = importlib.util.spec_from_file_location("stage10_7", SCRIPT_PATH)
stage10_7 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(stage10_7)


class Stage107BenchmarkReleaseCandidateTests(TestCase):
    def test_runner_writes_passing_release_candidate_gate(self):
        report = stage10_7.run_stage10_7()
        self.assertEqual(report["status"], "pass")
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(report["summary_metrics"]["stage_gate_count"], 6)
        self.assertGreaterEqual(report["summary_metrics"]["checksum_row_count"], 50)
        self.assertEqual(report["summary_metrics"]["safety_hit_count"], 0)
        self.assertEqual(report["next_phase"], "Stage 10.8 adversarial EIC red-team simulation")

        persisted = json.loads(
            (ROOT / "case_studies" / "stage10_release_candidate" / "stage10_7_gate_report.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(persisted["status"], "pass")

    def test_command_index_declares_full_stage10_replay_route(self):
        with (
            ROOT / "case_studies" / "stage10_release_candidate" / "stage10_7_reproducibility_commands.tsv"
        ).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        stages = {row["stage"] for row in rows}
        self.assertTrue({"10.1", "10.2", "10.3", "10.4", "10.5", "10.6", "validation"}.issubset(stages))
        self.assertTrue(all(row["fresh_clone_ready"] == "yes" for row in rows))
        self.assertIn("python3 scripts/run_stage10_6_manuscript_pitch.py", {row["command"] for row in rows})
        self.assertIn("python3 scripts/check_release.py", {row["command"] for row in rows})

    def test_checksum_manifest_covers_docs_scripts_tests_and_outputs(self):
        with (
            ROOT / "case_studies" / "stage10_release_candidate" / "stage10_7_checksum_manifest.tsv"
        ).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        categories = {row["category"] for row in rows}
        self.assertIn("documentation", categories)
        self.assertIn("script", categories)
        self.assertIn("test", categories)
        self.assertIn("case_study_output", categories)
        relpaths = {row["relpath"] for row in rows}
        for relpath in [
            "case_studies/stage10_release_candidate/stage10_7_reproducibility_commands.tsv",
            "scripts/run_stage10_7_benchmark_release_candidate.py",
            "tests/test_stage10_7_benchmark_release_candidate.py",
        ]:
            self.assertIn(relpath, relpaths)
        self.assertTrue(all(len(row["sha256"]) == 64 for row in rows))

    def test_archive_manifest_binds_scope_and_gate_statuses(self):
        payload = json.loads(
            (ROOT / "case_studies" / "stage10_release_candidate" / "stage10_7_archive_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn("stage10.7-benchmark-release-candidate@", payload["release_candidate_id"])
        self.assertEqual(payload["command_index"], "case_studies/stage10_release_candidate/stage10_7_reproducibility_commands.tsv")
        self.assertEqual(payload["checksum_manifest"], "case_studies/stage10_release_candidate/stage10_7_checksum_manifest.tsv")
        self.assertEqual(set(payload["stage_gate_statuses"]), {"10.1", "10.2", "10.3", "10.4", "10.5", "10.6"})
        self.assertIn("does not add biological data", payload["scope"])


if __name__ == "__main__":
    import unittest

    unittest.main()
