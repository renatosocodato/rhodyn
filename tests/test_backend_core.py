import csv
import hashlib
import importlib.util
import json
import tempfile
import zipfile
from pathlib import Path
from unittest import TestCase, skipUnless

from rhodyn.backend_core import (
    FileJobStore,
    build_analysis_bundle,
    compare_endpoint_models,
    decide_coupling_table,
    export_markdown_report,
    run_backend_operation,
    score_residence_table,
    summarize_reserve_table,
    validate_table,
    write_analysis_bundle,
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

    def test_run_backend_operation_dispatches_to_same_residence_result(self):
        rows = _rows("examples/synthetic_trajectory.csv")
        direct = score_residence_table(rows, low=0.35, high=0.75)
        dispatched = run_backend_operation("score_residence", rows, parameters={"low": 0.35, "high": 0.75})
        self.assertEqual(to_plain(dispatched["summaries"]), to_plain(direct["summaries"]))
        self.assertEqual(dispatched["job"], direct["job"])

    def test_analysis_bundle_is_deterministic_and_checksummed(self):
        rows = _rows("examples/synthetic_endpoints.csv")
        parameters = {"parameter_count": 1}
        bundle = build_analysis_bundle("compare_models", rows, parameters=parameters)
        repeated = build_analysis_bundle("compare_models", rows, parameters=parameters)

        self.assertEqual(bundle.data, repeated.data)
        self.assertEqual(bundle.sha256, hashlib.sha256(bundle.data).hexdigest())
        self.assertTrue(bundle.filename.startswith("rhodyn_compare_models_"))
        self.assertEqual(bundle.content_type, "application/zip")

        with tempfile.TemporaryDirectory() as tmp:
            bundle_file = Path(tmp) / "rhodyn_bundle_test.zip"
            bundle_file.write_bytes(bundle.data)
            with zipfile.ZipFile(bundle_file) as archive:
                names = set(archive.namelist())
                self.assertEqual(
                    names,
                    {
                        "README.md",
                        "input_rows.csv",
                        "manifest.json",
                        "parameters.json",
                        "report.md",
                        "result.json",
                        "result_rows.csv",
                    },
                )
                manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
                self.assertEqual(manifest["bundle_format"], "rhodyn.analysis_bundle.v1")
                self.assertEqual(manifest["operation"], "compare_models")
                self.assertEqual(manifest["status"], "pass")
                files = {item["path"]: item for item in manifest["files"]}
                for name in names - {"manifest.json"}:
                    data = archive.read(name)
                    self.assertEqual(files[name]["sha256"], hashlib.sha256(data).hexdigest())
                result = json.loads(archive.read("result.json").decode("utf-8"))
                self.assertEqual(result["typed_result"]["best_model"], "residence_gated")
                self.assertIn("residence_gated", archive.read("result_rows.csv").decode("utf-8"))

    def test_write_analysis_bundle_creates_downloadable_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bundle.zip"
            bundle = write_analysis_bundle(
                path,
                "decide_coupling",
                _rows("examples/synthetic_coupling.csv"),
                parameters={"rope_threshold": 0.95},
            )
            self.assertEqual(path.read_bytes(), bundle.data)
            with zipfile.ZipFile(path) as archive:
                manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            self.assertEqual(manifest["operation"], "decide_coupling")

    def test_file_job_store_persists_exact_result_and_bundle(self):
        rows = _rows("examples/synthetic_trajectory.csv")
        parameters = {"low": 0.35, "high": 0.75}
        direct = run_backend_operation("score_residence", rows, parameters=parameters)

        with tempfile.TemporaryDirectory() as tmp:
            store = FileJobStore(tmp)
            stored = store.submit("score_residence", rows, parameters=parameters)
            repeated = store.submit("score_residence", rows, parameters=parameters)

            self.assertEqual(stored.job_id, direct["job"]["job_id"])
            self.assertEqual(stored.metadata, repeated.metadata)
            self.assertEqual(stored.result, to_plain(direct))
            self.assertEqual(store.get_result(stored.job_id), to_plain(direct))
            self.assertEqual(
                store.get_metadata(stored.job_id)["job"]["parameters"],
                {"low": 0.35, "high": 0.75, "signal_column": "signal"},
            )
            self.assertEqual(store.list_jobs()[0]["job_id"], stored.job_id)

            metadata, bundle_data = store.read_bundle(stored.job_id)
            self.assertEqual(metadata["bundle_sha256"], hashlib.sha256(bundle_data).hexdigest())
            with zipfile.ZipFile(Path(tmp) / stored.job_id / "bundle.zip") as archive:
                result = json.loads(archive.read("result.json").decode("utf-8"))
            self.assertEqual(result, to_plain(direct))

    def test_file_job_store_rejects_unsafe_job_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileJobStore(tmp)
            with self.assertRaises(ValueError):
                store.get_metadata("../not_a_job")


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

        run_response = client.post(
            "/jobs/run",
            json={
                "operation": "score_residence",
                "parameters": {"low": 0.35, "high": 0.75},
                "rows": _rows("examples/synthetic_trajectory.csv"),
            },
        )
        self.assertEqual(run_response.status_code, 200)
        self.assertEqual(run_response.json()["job"]["operation"], "score_residence")

        bundle_response = client.post(
            "/jobs/bundle",
            json={
                "operation": "compare_models",
                "parameters": {"parameter_count": 1},
                "rows": _rows("examples/synthetic_endpoints.csv"),
            },
        )
        self.assertEqual(bundle_response.status_code, 200)
        self.assertEqual(bundle_response.headers["content-type"], "application/zip")
        self.assertEqual(
            bundle_response.headers["x-rhodyn-bundle-sha256"],
            hashlib.sha256(bundle_response.content).hexdigest(),
        )

    def test_fastapi_durable_job_routes_require_configured_store(self):
        from fastapi.testclient import TestClient

        from rhodyn.backend import create_app

        client = TestClient(create_app())
        response = client.get("/jobs")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["status"], "fail")

    def test_fastapi_durable_job_routes_persist_and_retrieve_bundle(self):
        from fastapi.testclient import TestClient

        from rhodyn.backend import create_app

        with tempfile.TemporaryDirectory() as tmp:
            client = TestClient(create_app(job_store_dir=tmp))
            rows = _rows("examples/synthetic_endpoints.csv")
            response = client.post(
                "/jobs/submit",
                json={
                    "operation": "compare_models",
                    "parameters": {"parameter_count": 1},
                    "rows": rows,
                },
            )
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["status"], "pass")
            job_id = payload["stored_job"]["job_id"]
            self.assertEqual(payload["result"]["typed_result"]["best_model"], "residence_gated")

            listing = client.get("/jobs")
            self.assertEqual(listing.status_code, 200)
            self.assertEqual([job["job_id"] for job in listing.json()["jobs"]], [job_id])

            metadata = client.get(f"/jobs/{job_id}")
            self.assertEqual(metadata.status_code, 200)
            self.assertEqual(metadata.json()["stored_job"]["bundle_sha256"], payload["stored_job"]["bundle_sha256"])

            result = client.get(f"/jobs/{job_id}/result")
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.json()["result"], payload["result"])

            bundle = client.get(f"/jobs/{job_id}/bundle")
            self.assertEqual(bundle.status_code, 200)
            self.assertEqual(bundle.headers["content-type"], "application/zip")
            self.assertEqual(
                bundle.headers["x-rhodyn-bundle-sha256"],
                hashlib.sha256(bundle.content).hexdigest(),
            )
