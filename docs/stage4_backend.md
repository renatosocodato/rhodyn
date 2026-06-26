# Stage 4 backend

Stage 4 starts by making the frozen Stage 3 analysis surfaces executable as a
stateless service. The backend does not introduce new biological interpretation
or new fitting logic. Each endpoint delegates to the same Python functions used
by the library and CLI, then returns JSON with the input schema, parameter
choices, software version, and a deterministic job identifier.

## Install

The core RhoDyn package still has no required runtime dependencies. Install the
backend extra only when the FastAPI service is needed.

```bash
python -m pip install 'rhodyn[backend]'
uvicorn rhodyn.backend:app --reload
```

## Endpoint contract

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

## Stage 4 gate

- Backend outputs must match the Python library outputs exactly.
- Each response carries a deterministic job identifier, input-row count,
  input hash, parameter choices, and RhoDyn version.
- No uploaded table is stored by the service core.
- Biological interpretation remains scoped to the submitted rows and declared
  parameters.
