"""Regression checks for the Stage 9 scaffold-only manuscript workspace."""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECK_PATH = ROOT / "scripts" / "check_stage9_scaffold.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("stage9_scaffold_checker_under_test", CHECK_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


CHECKER = _load_checker()


class Stage9ScaffoldTests(unittest.TestCase):
    def test_stage9_scaffold_or_evidence_lock_passes_and_is_non_drafting(self) -> None:
        payload = CHECKER.check_stage9_scaffold(ROOT)
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["failures"])
        self.assertEqual(payload["substage_count"], 33)
        self.assertEqual(payload["schema_count"], 13)
        self.assertEqual(payload["checks"]["scaffold_only_boundary_preserved"], "pass")
        self.assertEqual(payload["checks"]["figure_engine_binding_serialized"], "pass")

    def test_stage9_checker_rejects_unauthorized_reader_facing_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            shutil.copytree(ROOT / "manuscript", temp_root / "manuscript")
            shutil.copytree(ROOT / "tools", temp_root / "tools")
            (temp_root / "docs").mkdir()
            for rel in ["stage9_execution_memory.json", "stage9_manuscript_assembly_plan.md"]:
                shutil.copy2(ROOT / "docs" / rel, temp_root / "docs" / rel)
            draft = temp_root / "manuscript" / "nature_methods" / "sections" / "discussion.md"
            draft.write_text("# Discussion\n\nThis draft should not exist before Stage 9.13.\n", encoding="utf-8")
            payload = CHECKER.check_stage9_scaffold(temp_root)
        self.assertEqual(payload["status"], "fail")
        self.assertTrue(any("scaffold-only" in failure for failure in payload["failures"]))

    def test_stage9_checker_rejects_post_9_12_gate_verdicts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            shutil.copytree(ROOT / "manuscript", temp_root / "manuscript")
            shutil.copytree(ROOT / "tools", temp_root / "tools")
            (temp_root / "docs").mkdir()
            for rel in ["stage9_execution_memory.json", "stage9_manuscript_assembly_plan.md"]:
                shutil.copy2(ROOT / "docs" / rel, temp_root / "docs" / rel)
            future_gate = temp_root / "manuscript" / "nature_methods" / "gate_verdicts" / "9.13.json"
            future_gate.write_text('{"substage": "9.13", "pass": true, "checks": []}\n', encoding="utf-8")
            payload = CHECKER.check_stage9_scaffold(temp_root)
        self.assertEqual(payload["status"], "fail")
        self.assertTrue(any("post-9.12 gate verdicts" in failure for failure in payload["failures"]))


if __name__ == "__main__":
    unittest.main()
