import csv
import importlib.util
from pathlib import Path
from unittest import TestCase, skipUnless

from rhodyn.backend_core import (
    compare_endpoint_models,
    decide_coupling_table,
    export_markdown_report,
    score_residence_table,
    summarize_reserve_table,
    validate_table,
)
from rhodyn.compare import rank_model_fits
from rhodyn.coupling import equivalence_from_interval
from rhodyn.report import to_plain
from rhodyn.residence import ResidenceWindow, score_records
from rhodyn.schema import read_coupling_csv, read_endpoint_csv, read_trajectory_csv


def _rows(path: str) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class BackendCoreTests(TestCase):
    def test_validate_endpoint_uses_schema_reader(self):
        rows = _rows("examples/synthetic_trajectory.csv")
        payload = validate_table("trajectory", rows)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["rows"], len(read_trajectory_csv("examples/synthetic_trajectory.csv")[0]))
        self.assertEqual(payload["job"]["kind"], "trajectory")
        self.assertEqual(payload["job"]["software_version"], "0.1.0")

    def test_residence_endpoint_matches_library_output(self):
        rows = _rows("examples/synthetic_trajectory.csv")
        records, issues = read_trajectory_csv("examples/synthetic_trajectory.csv")
        self.assertEqual(issues, [])
        expected = to_plain(score_records(records, ResidenceWindow(0.35, 0.75)))

        payload = score_residence_table(rows, low=0.35, high=0.75)
        repeated = score_residence_table(rows, low=0.35, high=0.75)

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(to_plain(payload["summaries"]), expected)
        self.assertEqual(payload["job"]["job_id"], repeated["job"]["job_id"])
        self.assertEqual(payload["typed_results"][0].provenance.source, "api_payload")

    def test_coupling_endpoint_matches_interval_decision(self):
        rows = _rows("examples/synthetic_coupling.csv")
        records, issues = read_coupling_csv("examples/synthetic_coupling.csv")
        self.assertEqual(issues, [])
        expected = [
            equivalence_from_interval(
                record.estimate,
                record.ci_low,
                record.ci_high,
                record.margin,
                rope_mass=record.rope_mass,
            ).passes
            for record in records
        ]

        payload = decide_coupling_table(rows)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual([decision.passes for decision in payload["decisions"]], expected)
        self.assertEqual([result.passes for result in payload["typed_results"]], expected)
        self.assertEqual(payload["job"]["parameters"], {"rope_threshold": 0.95})

    def test_reserve_endpoint_summarizes_samples(self):
        payload = summarize_reserve_table(
            _rows("examples/synthetic_reserve.csv"),
            floor=1.0,
            ceiling=1.7,
            baseline_points=1,
        )

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(len(payload["summaries"]), 3)
        by_sample = {row["sample_id"]: row for row in payload["summaries"]}
        self.assertGreater(by_sample["reserve_001"]["reserve"], by_sample["reserve_003"]["reserve"])
        self.assertEqual(payload["typed_results"][0].provenance.schema_kind, "reserve")

    def test_model_comparison_endpoint_matches_library_ranking(self):
        rows = _rows("examples/synthetic_endpoints.csv")
        records, issues = read_endpoint_csv("examples/synthetic_endpoints.csv")
        self.assertEqual(issues, [])
        expected = to_plain(rank_model_fits(records, parameter_count=1))

        payload = compare_endpoint_models(rows, parameter_count=1)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(to_plain(payload["fits"]), expected)
        self.assertEqual(payload["typed_result"].best_model, "residence_gated")

    def test_markdown_report_endpoint_exports_rows(self):
        payload = export_markdown_report("Coupling", _rows("examples/synthetic_coupling.csv"))
        self.assertEqual(payload["status"], "pass")
        self.assertIn("# Coupling", payload["markdown"])
        self.assertIn("rock_src", payload["markdown"])


@skipUnless(
    importlib.util.find_spec("fastapi") and importlib.util.find_spec("httpx2"),
    "FastAPI test-client dependencies are not installed",
)
class BackendFastApiTests(TestCase):
    def test_fastapi_app_routes_to_service_core(self):
        from fastapi.testclient import TestClient

        from rhodyn.backend import create_app

        client = TestClient(create_app())
        health = client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "pass")

        response = client.post(
            "/residence/score",
            json={"rows": _rows("examples/synthetic_trajectory.csv"), "low": 0.35, "high": 0.75},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(len(payload["summaries"]), 3)
