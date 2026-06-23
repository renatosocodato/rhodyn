import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase

from rhodyn.paper import (
    PAPER_DATA_DOI,
    PAPER_RELEASE_COMMIT,
    discover_case_study_inputs,
    inspect_case_study_root,
    paper_case_study_metadata,
    read_case_study_tables,
)


class CliAndPaperTests(TestCase):
    def test_paper_metadata_boundary(self):
        meta = paper_case_study_metadata()
        self.assertEqual(meta["release_commit"], PAPER_RELEASE_COMMIT)
        self.assertEqual(meta["data_doi"], PAPER_DATA_DOI)
        self.assertIn("not runtime dependencies", meta["boundary"])

    def test_case_study_adapter_discovers_and_validates_fixture_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source_data").mkdir()
            (root / "results").mkdir()
            (root / "source_data" / "fret_trajectory_rows.csv").write_text(
                "cell_id,time,condition,signal,replicate\ncell_1,0,control,0.2,r1\ncell_1,1,control,0.5,r1\n",
                encoding="utf-8",
            )
            (root / "source_data" / "calcium_reserve_rows.csv").write_text(
                "sample_id,time,condition,response,replicate\ns1,0,stim,1.0,r1\ns1,1,stim,1.2,r1\n",
                encoding="utf-8",
            )
            (root / "results" / "model_comparison_endpoints.csv").write_text(
                "model,endpoint,observed,predicted,weight\nm1,src,0.2,0.21,1\n",
                encoding="utf-8",
            )
            (root / "results" / "rock_coupling_intervals.csv").write_text(
                "contrast,estimate,ci_low,ci_high,margin,rope_mass\nrock_src,0.01,-0.02,0.03,0.2,0.99\n",
                encoding="utf-8",
            )

            discovered = discover_case_study_inputs(root)
            self.assertEqual(discovered["trajectory_tables"][0].rows, 2)
            self.assertEqual(discovered["reserve_tables"][0].rows, 2)
            self.assertEqual(discovered["model_output_tables"][0].rows, 1)
            self.assertEqual(discovered["coupling_tables"][0].rows, 1)

            inspected = inspect_case_study_root(root)
            self.assertEqual(inspected["metadata"]["release_commit"], PAPER_RELEASE_COMMIT)
            self.assertTrue(inspected["folder_status"]["source_data"])
            self.assertIn("not imply", inspected["boundary"])

            loaded = read_case_study_tables(root)
            self.assertEqual(len(loaded["trajectory_tables"][0]), 2)
            self.assertEqual(len(loaded["reserve_tables"][0]), 2)

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

    def test_cli_paper_case_study_reports_data_root_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source_data").mkdir()
            (root / "source_data" / "fret_trajectory_rows.csv").write_text(
                "cell_id,time,condition,signal\ncell_1,0,control,0.2\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, "-m", "rhodyn.cli", "paper-case-study", "--data-root", str(root)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["release_commit"], PAPER_RELEASE_COMMIT)
            self.assertEqual(payload["local_data_root"]["metadata"]["data_doi"], PAPER_DATA_DOI)
            self.assertEqual(payload["local_data_root"]["discovered_tables"]["trajectory_tables"][0]["rows"], 1)
