"""Regression checks for the Stage 9.0 evidence intake lock."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _split_paths(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


class Stage90EvidenceLockTests(unittest.TestCase):
    def test_gate_passes_and_records_only_evidence_intake(self) -> None:
        gate = _json(WORKSPACE / "gate_verdicts" / "9.0.json")
        self.assertEqual(gate["substage"], "9.0")
        self.assertTrue(gate["pass"])
        self.assertTrue(str(gate["evidence_version"]).startswith("stage7.8-methods-readiness@"))
        scope = str(gate["scope_boundary"])
        self.assertIn("Evidence intake only", scope)
        self.assertIn("No drafting", scope)
        for check in gate["checks"]:
            self.assertTrue(check["passed"], check)

    def test_evidence_manifest_rows_resolve_and_share_version(self) -> None:
        rows = _csv(WORKSPACE / "ledgers" / "stage9_evidence_manifest.csv")
        self.assertGreaterEqual(len(rows), 20)
        versions = {row["evidence_version"] for row in rows}
        self.assertEqual(len(versions), 1)
        self.assertTrue(next(iter(versions)).startswith("stage7.8-methods-readiness@"))
        art_ids = [row["art_id"] for row in rows]
        self.assertEqual(len(art_ids), len(set(art_ids)))
        self.assertEqual(art_ids[0], "ART-0001")
        for row in rows:
            self.assertEqual(row["status"], "locked", row)
            self.assertTrue((ROOT / row["path"]).exists(), row["path"])

    def test_claims_and_display_components_are_mapped_to_artifacts(self) -> None:
        manifest_paths = {row["path"] for row in _csv(WORKSPACE / "ledgers" / "stage9_evidence_manifest.csv")}
        figure_rows = _tsv(ROOT / "case_studies" / "stage7_methods_readiness" / "figure_artifact_crosswalk.tsv")
        claim_rows = _tsv(ROOT / "case_studies" / "stage7_methods_readiness" / "claim_evidence_crosswalk.tsv")
        self.assertEqual(len(figure_rows), 6)
        self.assertEqual(len(claim_rows), 5)
        for row in figure_rows:
            for rel in _split_paths(row["primary_artifact"]):
                self.assertIn(rel, manifest_paths, row["component"])
        for row in claim_rows:
            for rel in _split_paths(row["evidence"]):
                self.assertIn(rel, manifest_paths, row["claim_id"])

    def test_downstream_surfaces_remain_unstarted(self) -> None:
        forbidden = [
            WORKSPACE / "sections" / "results.md",
            WORKSPACE / "sections" / "introduction.md",
            WORKSPACE / "sections" / "discussion.md",
            WORKSPACE / "sections" / "methods.md",
            WORKSPACE / "refs" / "references.bib",
            WORKSPACE / "submission_package" / "pi_review_packet.md",
            WORKSPACE / "figures" / ".panelforge_commit",
            WORKSPACE / "audits" / "panelforge_render_report.md",
            ROOT / ".venv-panelforge",
            ROOT / "tools" / "panelforge-figures" / ".git",
        ]
        for path in forbidden:
            self.assertFalse(path.exists(), path)
        rendered = [
            path
            for path in (WORKSPACE / "figures" / "rendered").rglob("*")
            if path.is_file() and path.suffix.lower() in {".png", ".pdf", ".svg"}
        ]
        self.assertEqual(rendered, [])


if __name__ == "__main__":
    unittest.main()
