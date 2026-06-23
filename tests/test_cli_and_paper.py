import json
import subprocess
import sys
from unittest import TestCase

from rhodyn.paper import PAPER_DATA_DOI, PAPER_RELEASE_COMMIT, paper_case_study_metadata


class CliAndPaperTests(TestCase):
    def test_paper_metadata_boundary(self):
        meta = paper_case_study_metadata()
        self.assertEqual(meta["release_commit"], PAPER_RELEASE_COMMIT)
        self.assertEqual(meta["data_doi"], PAPER_DATA_DOI)
        self.assertIn("not runtime dependencies", meta["boundary"])

    def test_cli_validate(self):
        result = subprocess.run(
            [sys.executable, "-m", "rhodyn.cli", "validate", "examples/synthetic_trajectory.csv"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")

