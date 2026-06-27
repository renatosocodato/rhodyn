# Stage 4 backend

Stage 4 makes the frozen Stage 3 analysis surfaces executable as a service. The
backend does not introduce new biological interpretation or new fitting logic.
Each endpoint delegates to the same Python functions used by the library and
CLI, then returns JSON with the input schema, parameter choices, software
version, and a deterministic job identifier.

## Install

The core RhoDyn package still has no required runtime dependencies. Install the
backend extra only when the FastAPI service is needed.

```bash
python -m pip install 'rhodyn[backend]'
uvicorn rhodyn.backend:app --reload
```

Durable server-side storage is explicit. Set `RHODYN_JOB_STORE_DIR` when the
service should persist uploaded rows, parameters, result JSON, and bundles.

```bash
RHODYN_JOB_STORE_DIR=.rhodyn_jobs uvicorn rhodyn.backend:app --reload
```

An example deployment environment file is provided at
`deploy/stage4.env.example`. Container templates are provided at
`deploy/stage4.Dockerfile` and `deploy/docker-compose.stage4.yml`.

| variable | meaning |
| --- | --- |
| `RHODYN_JOB_STORE_DIR` | Persistent directory for stored jobs. If unset, durable routes return HTTP 503. |
| `RHODYN_API_KEYS` | Optional comma-separated API keys. If set, protected analysis and job routes require `X-RhoDyn-API-Key` or `Authorization: Bearer`. |
| `RHODYN_MAX_ROWS` | Optional maximum number of rows accepted in one submitted table. |
| `RHODYN_MAX_UPLOAD_BYTES` | Optional maximum byte size for raw CSV upload routes. |
| `RHODYN_JOB_RETENTION_MAX_JOBS` | Optional maximum number of stored jobs. Oldest jobs are pruned first. |
| `RHODYN_JOB_RETENTION_MAX_BYTES` | Optional maximum total stored bundle bytes. Oldest jobs are pruned first. |
| `RHODYN_JOB_RETENTION_MAX_AGE_SECONDS` | Optional maximum job age in seconds. |

## Authentication and limits

Authentication is optional in Stage 4 so local development remains simple. If
`RHODYN_API_KEYS` is unset, routes behave as an open local service. If one or
more keys are configured, `/health` and `/schemas` remain public, while analysis
routes, CSV upload routes, bundle routes, and durable job routes require either
`X-RhoDyn-API-Key: <key>` or `Authorization: Bearer <key>`.

Service limits are explicit and deterministic. `RHODYN_MAX_ROWS` bounds the
number of submitted rows for JSON and CSV-upload jobs. `RHODYN_MAX_UPLOAD_BYTES`
bounds raw CSV upload size before the table is parsed. Limit violations return
HTTP 413 and do not run analysis or write durable job files.

## Endpoint contract

Every analysis response carries a `job` object with a deterministic job ID,
input-row count, input hash, parameter choices, operation name, table kind, and
RhoDyn version. The same submitted rows and parameters produce the same job ID.

### Health and schemas

- `GET /health`
- `GET /schemas`
- `POST /schemas/validate`

The validation endpoint accepts a table kind and rows. Supported kinds are
`trajectory`, `endpoint`, `reserve`, and `coupling`.

```json
{
  "kind": "trajectory",
  "rows": [
    {"cell_id": "a", "time": 0, "condition": "control", "signal": 0.2},
    {"cell_id": "a", "time": 1, "condition": "control", "signal": 0.5}
  ]
}
```

### Residence scoring

- `POST /residence/score`

This endpoint scores dwell time inside a declared low/high window. It returns
the same residence summaries produced by `rhodyn.residence.score_records`.

```json
{
  "low": 0.35,
  "high": 0.75,
  "rows": [
    {"cell_id": "a", "time": 0, "condition": "control", "signal": 0.2},
    {"cell_id": "a", "time": 1, "condition": "control", "signal": 0.5}
  ]
}
```

### Bounded-coupling decisions

- `POST /coupling/decide`

This endpoint classifies supplied interval or ROPE rows under the declared
margin. A passing decision means the interval lies inside the declared
biological-negligibility margin and, when supplied, the ROPE mass clears the
threshold. It does not mean zero coupling.

```json
{
  "rows": [
    {
      "contrast": "rock_src",
      "estimate": 0.01,
      "ci_low": -0.03,
      "ci_high": 0.04,
      "margin": 0.20,
      "rope_mass": 0.99
    }
  ]
}
```

### Reserve summaries

- `POST /reserve/summarize`

This endpoint groups reserve-like response rows by condition and sample,
optionally normalizes each sample by `F/F0`, and maps the peak response to a
bounded reserve coordinate with `rhodyn.reserve.reserve_coordinate`.

```json
{
  "floor": 1.0,
  "ceiling": 1.7,
  "baseline_points": 1,
  "rows": [
    {"sample_id": "s1", "time": 0, "condition": "control", "response": 1.0},
    {"sample_id": "s1", "time": 1, "condition": "control", "response": 1.2}
  ]
}
```

### Reduced-architecture model comparison

- `POST /models/compare`

This endpoint ranks endpoint model predictions with the same BIC/RSS rule used
by `rhodyn.compare.rank_model_fits`.

```json
{
  "parameter_count": 1,
  "rows": [
    {"model": "amplitude_only", "endpoint": "src", "observed": 0.3, "predicted": 0.5},
    {"model": "residence_gated", "endpoint": "src", "observed": 0.3, "predicted": 0.32}
  ]
}
```

### Markdown report export

- `POST /reports/markdown`

This endpoint converts submitted rows into a compact Markdown table. It is a
first report-export surface, not a substitute for full figure generation.

### Job run and bundle export

- `POST /jobs/run`
- `POST /jobs/bundle`
- `POST /jobs/upload/run`
- `POST /jobs/upload/bundle`

The job endpoint accepts an `operation`, `parameters`, and `rows`, then routes
to the same service core used by the specific endpoints above. Supported
operations are `validate`, `score_residence`, `decide_coupling`,
`summarize_reserve`, `compare_models`, and `export_markdown`.

```json
{
  "operation": "compare_models",
  "parameters": {"parameter_count": 1},
  "rows": [
    {"model": "amplitude_only", "endpoint": "src", "observed": 0.3, "predicted": 0.5},
    {"model": "residence_gated", "endpoint": "src", "observed": 0.3, "predicted": 0.32}
  ]
}
```

The CSV upload routes are intended for larger tables that should not be encoded
as JSON rows by the client. They accept a raw CSV request body, an `operation`
query parameter, and an optional `parameters_json` query parameter containing a
JSON object. They return the same result JSON or bundle ZIP that the equivalent
JSON `/jobs/run` or `/jobs/bundle` request would produce.

```bash
curl -X POST \
  -H 'Content-Type: text/csv' \
  --data-binary @examples/synthetic_trajectory.csv \
  'http://localhost:8000/jobs/upload/run?operation=score_residence&parameters_json=%7B%22low%22%3A0.35%2C%22high%22%3A0.75%7D'
```

The bundle endpoint returns a ZIP archive containing:

- `README.md`
- `input_rows.csv`
- `parameters.json`
- `result.json`
- `result_rows.csv`
- `report.md`
- `manifest.json`

The archive uses fixed internal timestamps and a manifest with SHA-256
checksums for every payload file. The HTTP response also carries
`X-RhoDyn-Bundle-SHA256` so downloaded bundles can be checked immediately.

### Durable server-side job storage

- `POST /jobs/submit`
- `GET /jobs`
- `GET /jobs/summary`
- `POST /jobs/prune`
- `POST /jobs/upload/submit`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/result`
- `GET /jobs/{job_id}/bundle`

Durable routes require `RHODYN_JOB_STORE_DIR` or
`create_app(job_store_dir=...)`. Without an explicit store, these routes return
HTTP 503 instead of silently writing uploaded tables to a hidden location.

Submitting a job runs the same operation path as `/jobs/run`, builds the same
downloadable bundle as `/jobs/bundle`, then writes one directory named by the
deterministic job ID. The stored directory contains:

- `job.json`
- `input_rows.csv`
- `parameters.json`
- `result.json`
- `result_rows.csv`
- `report.md`
- `bundle_manifest.json`
- `bundle.zip`

Reading a stored job returns the persisted JSON or ZIP. It does not re-run the
analysis. The stored job ID remains a function of operation, input rows,
parameters, table kind, and RhoDyn version, so repeated submission of identical
payloads resolves to the same stored job.

`POST /jobs/upload/submit` combines the CSV upload route with durable job
storage. It accepts the same query parameters as `/jobs/upload/run` and writes
the same stored job files as `/jobs/submit`.

`GET /jobs/summary` returns job count, stored bundle bytes, configured
retention policy, and stored job IDs without reading submitted input tables.
`POST /jobs/prune` applies the configured retention policy. Pass
`{"dry_run": true}` to preview removal without deleting job directories.

Retention policy is deliberately simple in Stage 4. Jobs are pruned by age,
then count, then total bundle bytes, always removing the oldest stored jobs
first. Pruning never changes a retained job's result JSON or bundle.

## Service-contract audit

Run the Stage 4 service-contract audit from the repository root.

```bash
PYTHONPATH=src python scripts/audit_stage4_service_contract.py
```

The audit checks every retained Stage 4 operation against four surfaces.

- Direct backend helper.
- Generic `/jobs/run` dispatcher logic through `run_backend_operation`.
- Deterministic downloadable bundle and manifest checksums.
- Durable filesystem job store result and bundle retrieval.

The audit passes only when all four surfaces return the same result for the
same submitted rows and declared parameters. It does not add a new biological
case study or new interpretation.

## Stage 4 gate

- Backend outputs must match the Python library outputs exactly.
- Each response carries a deterministic job identifier, input-row count,
  input hash, parameter choices, and RhoDyn version.
- Downloadable bundles must preserve submitted rows, parameters, exact JSON
  result, result table, Markdown report, and file checksums.
- Optional authentication must protect analysis, upload, bundle, and durable job
  routes when API keys are configured, while keeping local unauthenticated
  development possible when no key is configured.
- Configured row and upload limits must fail before analysis or durable writes.
- CSV upload routes must return the same results and bundles as equivalent JSON
  jobs.
- No uploaded table is stored by default. Durable storage occurs only through
  explicit job-store configuration and the `/jobs/submit` route.
- Stored jobs must preserve submitted rows, parameters, exact JSON result,
  downloadable bundle bytes, and RhoDyn version without re-running analysis on
  retrieval.
- Retention policy must remove whole job directories only. It must not edit
  retained result JSON, input rows, reports, or bundles.
- Biological interpretation remains scoped to the submitted rows and declared
  parameters.
