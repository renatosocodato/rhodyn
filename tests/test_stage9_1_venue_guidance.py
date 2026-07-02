"""Regression checks for Stage 9.1 venue guidance registration."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"


class Stage91VenueGuidanceTests(unittest.TestCase):
    def test_stage9_1_gate_passes_with_sourced_article_budget(self) -> None:
        gate_path = WORKSPACE / "gate_verdicts" / "9.1.json"
        self.assertTrue(gate_path.exists())
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        self.assertEqual(gate.get("substage"), "9.1")
        self.assertIs(gate.get("pass"), True)
        checks = {item["name"]: item for item in gate.get("checks", [])}
        for check_name in [
            "stage_9_0_gate_passed",
            "official_sources_fetched",
            "content_type_budget_is_sourced",
            "cached_sources_have_url_and_access_date",
            "verified_venue_constraints_are_explicit",
            "freshness_assertion_passes",
            "no_downstream_stage9_surfaces_started",
        ]:
            self.assertIn(check_name, checks)
            self.assertIs(checks[check_name]["passed"], True)

    def test_guidance_register_contains_required_constraints(self) -> None:
        register = (WORKSPACE / "refs" / "nature_methods_guidance_register.md").read_text(encoding="utf-8")
        flat_register = " ".join(register.split())
        required_phrases = [
            "Nature Methods Article",
            "Up to 150 words, unreferenced",
            "3,000 words",
            "up to 5,000 words",
            "Up to six figures and/or tables",
            "Discussion does not contain subheadings",
            "Reporting Summary",
            "Code Availability Statement",
            "GitHub link alone is not sufficient",
            "permanent identifier",
            "exact sample sizes",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, flat_register)

    def test_cached_sources_have_url_access_date_and_hash(self) -> None:
        cache_dir = WORKSPACE / "refs" / "_cache"
        meta_paths = sorted(cache_dir.glob("*.meta.json"))
        text_paths = sorted(cache_dir.glob("*.txt"))
        self.assertEqual(len(meta_paths), 7)
        self.assertEqual(len(text_paths), 7)
        for meta_path in meta_paths:
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata.get("status"), "fetched")
            self.assertTrue(str(metadata.get("url", "")).startswith("https://"))
            self.assertTrue(str(metadata.get("accessed_utc", "")).startswith("2026-07-02"))
            self.assertTrue(metadata.get("sha256"))
            self.assertTrue((ROOT / metadata["cache_file"]).exists())
            self.assertTrue((ROOT / metadata["metadata_file"]).exists())

    def test_no_downstream_manuscript_surfaces_started(self) -> None:
        forbidden = [
            WORKSPACE / "sections" / "results.md",
            WORKSPACE / "sections" / "introduction.md",
            WORKSPACE / "sections" / "discussion.md",
            WORKSPACE / "sections" / "methods.md",
            WORKSPACE / "sections" / "abstract.md",
            WORKSPACE / "refs" / "references.bib",
            WORKSPACE / "submission_package" / "pi_review_packet.md",
            WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
            WORKSPACE / "figures" / ".panelforge_commit",
            WORKSPACE / "audits" / "panelforge_render_report.md",
            ROOT / ".venv-panelforge",
            ROOT / "tools" / "panelforge-figures" / ".git",
        ]
        for path in forbidden:
            self.assertFalse(path.exists(), f"unexpected downstream Stage 9 surface exists: {path}")
        rendered = [
            path
            for path in (WORKSPACE / "figures" / "rendered").rglob("*")
            if path.is_file() and path.suffix.lower() in {".png", ".pdf", ".svg"}
        ]
        self.assertFalse(rendered)


if __name__ == "__main__":
    unittest.main()
