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
`deploy/stage4.env.example`.

| variable | meaning |
| --- | --- |
| `RHODYN_JOB_STORE_DIR` | Persistent directory for stored jobs. If unset, durable routes return HTTP 503. |
| `RHODYN_JOB_RETENTION_MAX_JOBS` | Optional maximum number of stored jobs. Oldest jobs are pruned first. |
| `RHODYN_JOB_RETENTION_MAX_BYTES` | Optional maximum total stored bundle bytes. Oldest jobs are pruned first. |
| `RHODYN_JOB_RETENTION_MAX_AGE_SECONDS` | Optional maximum job age in seconds. |

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

`GET /jobs/summary` returns job count, stored bundle bytes, configured
retention policy, and stored job IDs without reading submitted input tables.
`POST /jobs/prune` applies the configured retention policy. Pass
`{"dry_run": true}` to preview removal without deleting job directories.

Retention policy is deliberately simple in Stage 4. Jobs are pruned by age,
then count, then total bundle bytes, always removing the oldest stored jobs
first. Pruning never changes a retained job's result JSON or bundle.

## Stage 4 gate

- Backend outputs must match the Python library outputs exactly.
- Each response carries a deterministic job identifier, input-row count,
  input hash, parameter choices, and RhoDyn version.
- Downloadable bundles must preserve submitted rows, parameters, exact JSON
  result, result table, Markdown report, and file checksums.
- No uploaded table is stored by default. Durable storage occurs only through
  explicit job-store configuration and the `/jobs/submit` route.
- Stored jobs must preserve submitted rows, parameters, exact JSON result,
  downloadable bundle bytes, and RhoDyn version without re-running analysis on
  retrieval.
- Retention policy must remove whole job directories only. It must not edit
  retained result JSON, input rows, reports, or bundles.
- Biological interpretation remains scoped to the submitted rows and declared
  parameters.
