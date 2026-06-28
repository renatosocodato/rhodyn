# Stage 5 public MLCI trajectory workflow

This workflow gives Stage 5 a real public-data path without making RhoDyn a
manuscript-reproduction pipeline. The input is the small Zenodo-derived MLCI
tracking subset already used in the Stage 3 public tutorial. The workflow starts
from a committed RhoDyn trajectory table so the frontend, CLI, and backend all
exercise the same frozen Stage 4 upload operation.

Public source: https://zenodo.org/records/7260137  
Concept DOI: https://doi.org/10.5281/zenodo.7260136  
Version DOI: https://doi.org/10.5281/zenodo.7260137  
License: CC-BY-4.0

## Input table

The Stage 5 workflow table is:

```text
examples/mlci_public_intensity_trajectory.csv
```

It was derived from `case_studies/mlci_public_track_features_subset.csv` with:

```bash
PYTHONPATH=src python -m rhodyn.cli ctc-to-trajectory \
  case_studies/mlci_public_track_features_subset.csv \
  --signal intensity \
  --condition mlci_public_segmentation_features \
  --replicate zenodo_7260137 \
  --output examples/mlci_public_intensity_trajectory.csv
```

The output uses the standard trajectory schema with `cell_id`, `time`,
`condition`, `signal`, and `replicate`. Sequence identity is retained in both
track and replicate labels, which keeps sequence `00` and sequence `01`
separate for inspection.

## CLI path

The residence-window analysis can be reproduced without the frontend.

```bash
PYTHONPATH=src python -m rhodyn.cli score-residence \
  examples/mlci_public_intensity_trajectory.csv \
  --low 13.0 \
  --high 14.5 \
  --signal-column signal
```

The window is an analysis setting over the public intensity summary. It is not a
biological threshold unless a separate calibration is supplied.

## Frontend path

Start the backend with the optional backend extra installed.

```bash
RHODYN_JOB_STORE_DIR=.rhodyn_jobs uvicorn rhodyn.backend:app --reload
```

Serve the repository root in a second terminal.

```bash
python -m http.server 9000
```

Open `http://127.0.0.1:9000/frontend/stage5/` and choose **Load MLCI workflow**.
The workbench selects the residence-scoring operation, loads the public
trajectory table, applies the `13.0` to `14.5` signal window, renders the
trajectory preview, displays per-trace residence summaries, and prepares the
upload route with the same parameter payload used by the CLI command.

## What this workflow shows

The workflow shows that a public live-cell tracking table can move from a
trajectory schema into local trajectory inspection, residence-window scoring,
backend upload, durable job submission, and downloadable bundle export.

## What it does not show

The MLCI intensity signal is not a molecular activity reporter, and this
workflow does not assign cell fate, disease state, or mechanism. It tests the
software path for dynamic trajectory inspection and upload reproducibility using
a public live-cell dataset.
