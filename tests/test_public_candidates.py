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
        stage3a = [row for row in rows if row["priority"] == "stage3a_signaling"]
        stage3b = [row for row in rows if row["priority"] == "stage3b_signaling"]
        stage3c = [row for row in rows if row["priority"] == "stage3c_endpoint"]
        stage3d = [row for row in rows if row["priority"] == "stage3d_coupling"]

        self.assertGreaterEqual(len(shortlisted), 3)
        self.assertEqual(len(primary), 1)
        self.assertEqual(len(stage3a), 1)
        self.assertEqual(len(stage3b), 1)
        self.assertEqual(len(stage3c), 1)
        self.assertEqual(len(stage3d), 1)
        self.assertEqual(stage3a[0]["candidate_id"], "drg_calcium_vonbuchholtz2025")
        self.assertEqual(stage3b[0]["candidate_id"], "erk_gpcr_wan2021")
        self.assertEqual(stage3c[0]["candidate_id"], "cell_painting_mitotox_seal2023")
        self.assertEqual(stage3d[0]["candidate_id"], "erk_akt_wan2021_bounded_coupling")
        self.assertNotIn("to_be_verified", primary[0]["license"])
        self.assertNotIn("to_be_verified", primary[0]["url"])

    def test_public_candidate_note_preserves_no_claim_boundary(self):
        text = Path("docs/public_case_study_candidates.md").read_text(encoding="utf-8")
        self.assertIn("No biological claim is made", text)
        self.assertIn("Primary v0.3.0 tutorial target", text)
        self.assertIn("Selected Stage 3A live-cell signaling benchmark", text)
        self.assertIn("Selected Stage 3B kinase-signaling benchmark", text)
        self.assertIn("Selected Stage 3C endpoint/model-comparison benchmark", text)
        self.assertIn("Selected Stage 3D bounded-coupling benchmark", text)
        self.assertIn("NF-kB live-cell dynamics remains a high-value target", text)
        self.assertIn("ERK/KTR dynamics is no longer only a watchlist item", text)
        self.assertIn("Stage 3 can now be frozen for the v0.3 evidence bank", text)
