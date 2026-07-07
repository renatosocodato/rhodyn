import csv
import importlib.util
import json
from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_stage10_6_manuscript_pitch.py"
SPEC = importlib.util.spec_from_file_location("stage10_6", SCRIPT_PATH)
stage10_6 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(stage10_6)


class Stage106ManuscriptPitchTests(TestCase):
    def test_runner_writes_passing_method_first_pitch_gate(self):
        report = stage10_6.run_stage10_6()
        self.assertEqual(report["status"], "pass")
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(report["summary_metrics"]["results_subsection_count"], 6)
        self.assertEqual(report["summary_metrics"]["figure_mentions"], 6)
        self.assertEqual(report["summary_metrics"]["abstract_word_count"], 200)

        persisted = json.loads(
            (ROOT / "case_studies" / "stage10_manuscript_pitch" / "stage10_6_gate_report.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(persisted["next_phase"], "Stage 10.7 benchmark-ready release candidate")

    def test_title_abstract_and_pitch_center_method_not_software(self):
        title_abstract = (
            ROOT / "manuscript" / "nature_methods" / "stage10_6" / "title_abstract_v2.md"
        ).read_text(encoding="utf-8")
        pitch = (ROOT / "manuscript" / "nature_methods" / "stage10_6" / "eic_pitch_v2.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Residence-state inference for live-cell perturbation data", title_abstract)
        for term in ["SciPy", "scikit-learn", "HMM", "MiniROCKET", "ruptures-style"]:
            self.assertIn(term, title_abstract)
        for term in ["DRG calcium", "GPCR-linked ERK", "Cell Painting/MitoTox", "MLCI tracking"]:
            self.assertIn(term, title_abstract)
        for term in ["positive", "comparator-sufficient", "inconclusive"]:
            self.assertIn(term, title_abstract)
        self.assertIn("not a wrapper around existing summaries", pitch)
        self.assertIn("software availability by itself", pitch)

    def test_results_follow_method_first_figure_order(self):
        results = (
            ROOT / "manuscript" / "nature_methods" / "stage10_6" / "results_method_first_v2.md"
        ).read_text(encoding="utf-8")
        required_order = [
            "RhoDyn defines residence-state inference as a decision object",
            "Named baselines define when residence-state inference adds value",
            "Public biological breadth tests portability across domains",
            "Endpoint and routed-output decisions extend the method beyond trajectories",
            "Held-out validation keeps pass, comparator-sufficient, and inconclusive outcomes visible",
            "Reproducible software surfaces make the method inspectable",
        ]
        positions = [results.index(item) for item in required_order]
        self.assertEqual(positions, sorted(positions))
        self.assertLess(results.index("Fig. 1"), results.index("Fig. 6"))
        self.assertIn("software surface", results)
        self.assertIn("secondary to the method claim", results)

    def test_boundary_audit_passes_and_rejects_overclaim_language(self):
        with (
            ROOT / "manuscript" / "nature_methods" / "stage10_6" / "stage10_6_claim_boundary_audit.tsv"
        ).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertGreaterEqual(len(rows), 8)
        self.assertTrue(all(row["status"] == "pass" for row in rows))
        audited = {row["boundary_phrase"] for row in rows}
        self.assertIn("universal residence", audited)
        self.assertIn("mechanism-discovery engine", audited)

        main_text = (
            ROOT / "manuscript" / "nature_methods" / "stage10_6" / "main_text_method_first_rescue_draft.md"
        ).read_text(encoding="utf-8")
        for phrase in [
            "universal residence",
            "proves no coupling",
            "absence of all coupling",
            "automatic state discovery",
            "RhoDyn generated the original",
        ]:
            self.assertNotIn(phrase, main_text)
        self.assertIn("not that every system contains residence-state structure", main_text)


if __name__ == "__main__":
    import unittest

    unittest.main()
