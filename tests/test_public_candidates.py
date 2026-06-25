import csv
from pathlib import Path
from unittest import TestCase


class PublicCandidateTests(TestCase):
    def test_public_candidate_matrix_has_primary_and_shortlist(self):
        path = Path("case_studies/public_data_candidates.tsv")
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))

        shortlisted = [row for row in rows if row["status"] == "shortlisted"]
        primary = [row for row in rows if row["priority"] == "primary_v0.3"]

        self.assertGreaterEqual(len(shortlisted), 3)
        self.assertEqual(len(primary), 1)
        self.assertNotIn("to_be_verified", primary[0]["license"])
        self.assertNotIn("to_be_verified", primary[0]["url"])

    def test_public_candidate_note_preserves_no_claim_boundary(self):
        text = Path("docs/public_case_study_candidates.md").read_text(encoding="utf-8")
        self.assertIn("No biological claim is made", text)
        self.assertIn("Primary v0.3.0 tutorial target", text)
        self.assertIn("ERK/KTR and NF-kB", text)
