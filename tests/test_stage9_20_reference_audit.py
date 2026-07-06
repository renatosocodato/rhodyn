"""Regression checks for Stage 9.20 reference-library and citation audit."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
GATE_PATH = WORKSPACE / "gate_verdicts" / "9.20.json"
BIB_PATH = WORKSPACE / "refs" / "references.bib"
CITATION_LEDGER_PATH = WORKSPACE / "refs" / "citation_claim_ledger.csv"
AUDIT_PATH = WORKSPACE / "audits" / "reference_audit.md"
CACHE_PATH = WORKSPACE / "refs" / "_cache" / "reference_library"


class Stage920ReferenceAuditTests(unittest.TestCase):
    def _citation_rows(self) -> list[dict[str, str]]:
        with CITATION_LEDGER_PATH.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def test_gate_passes_and_points_to_cross_document_consistency(self) -> None:
        gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        self.assertIs(gate["pass"], True)
        self.assertEqual(gate["substage"], "9.20")
        self.assertEqual(gate["next_substage"], "9.21")
        self.assertEqual(gate["reference_count"], 13)
        self.assertEqual(gate["reference_cap"], 50)
        self.assertEqual(set(gate["ref_ids"]), {f"REF-{idx:04d}" for idx in range(1, 14)})
        self.assertTrue(all(item["passed"] for item in gate["checks"]))

    def test_bibtex_contains_expected_entries_and_key_dois(self) -> None:
        bib = BIB_PATH.read_text(encoding="utf-8")
        self.assertEqual(bib.count("\n@"), 13)
        for ref_id in [f"REF-{idx:04d}" for idx in range(1, 14)]:
            self.assertIn(ref_id, bib)
        for doi in [
            "10.1038/s41587-019-0071-9",
            "10.1038/s41592-020-01018-x",
            "10.5281/zenodo.14907827",
            "10.5281/zenodo.21036616",
            "10.5281/zenodo.20811171",
        ]:
            self.assertIn(doi, bib)

    def test_citation_ledger_maps_claims_sources_and_retraction_status(self) -> None:
        rows = self._citation_rows()
        self.assertEqual(len(rows), 13)
        self.assertEqual({row["ref_id"] for row in rows}, {f"REF-{idx:04d}" for idx in range(1, 14)})
        self.assertEqual(
            {row["source_type"] for row in rows},
            {"methods", "dataset", "software"},
        )
        for row in rows:
            self.assertRegex(row["doi_or_pmid"], r"^10\.")
            self.assertEqual(row["resolved"], "true")
            self.assertTrue(row["claim_id"].startswith("CLM-"))
            self.assertTrue(row["paragraph_ids"].startswith("PARA-"))
            self.assertIn(row["retraction_check"], {"clear", "not_applicable_zenodo_record"})
        software_rows = [row for row in rows if row["source_type"] == "software"]
        self.assertEqual({row["doi_or_pmid"] for row in software_rows}, {"10.5281/zenodo.21036616", "10.5281/zenodo.20811171"})

    def test_reference_audit_reports_scope_and_counts(self) -> None:
        audit = AUDIT_PATH.read_text(encoding="utf-8")
        for phrase in [
            "Reference count. 13 of 50",
            "DOI-resolved references. 13 of 13",
            "Retraction-check clear or not applicable. 13 of 13",
            "Source-type counts. dataset=3; methods=8; software=2",
            "does not add a new biological demonstration",
            "does not replace the later cross-document consistency audit",
        ]:
            self.assertIn(phrase, audit)

    def test_metadata_cache_and_downstream_surfaces(self) -> None:
        self.assertGreaterEqual(len(list(CACHE_PATH.glob("*.json"))), 13)
        for rel in [
            "stage9_completion_report.md",
        ]:
            self.assertFalse((WORKSPACE / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
