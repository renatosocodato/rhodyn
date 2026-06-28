# Stage 5 frontend scaffold

Stage 5 scaffold is contract-bound to the frozen Stage 4 API contract.

## Scope

The scaffold in `frontend/stage5/` is a static scientific workbench shell. It loads `api/stage4/frontend_contract.json`, `api/stage4/openapi.json`, and the frozen schema fixture, then exposes the Stage 4 upload, bundle, and durable-submit routes without introducing new analysis logic. The upload screen now shows the selected operation, expected schema columns, editable parameters, serialized parameter payload, route preview, local schema preflight status, and a contract example loader. The trajectory explorer also reports trace counts, condition and replicate counts, signal and time ranges, and per-trace residence summaries for the current signal column and window.

## Screens

- Project dashboard.
- Data upload and schema validation.
- Trajectory explorer.
- Residence-window tuner.
- Coupling/equivalence decision panel.
- Reserve-buffering panel.
- Model-comparison panel.
- Report builder.

## Local run

Start the backend with the backend extra installed.

```bash
RHODYN_JOB_STORE_DIR=.rhodyn_jobs uvicorn rhodyn.backend:app --reload
```

Serve the repository root so the static workbench can load the frozen contract files.

```bash
python -m http.server 9000
```

Then open `http://127.0.0.1:9000/frontend/stage5/` and keep the API field set to `http://127.0.0.1:8000`.

## Upload-flow parity

Every Stage 5 contract operation now has a CLI counterpart and a frozen example CSV. The parity audit runs each operation through the CLI, through `rhodyn.backend_core.run_backend_operation`, and against the frozen upload-run fixture after removing transport-only metadata such as job IDs and source-path labels.

```bash
PYTHONPATH=src python scripts/audit_stage5_upload_flow_parity.py
```

Passing this audit means the frontend route contract, CLI command, and backend core agree for the retained example tables. It does not add a new biological case study or change the interpretation of any result.

## Public MLCI workflow

The dashboard includes **Load MLCI workflow**, which selects residence scoring,
loads `examples/mlci_public_intensity_trajectory.csv`, applies the `13.0` to
`14.5` intensity window, and displays local trajectory inspection before the
user runs the backend upload route. The same result can be reproduced from the
CLI.

```bash
PYTHONPATH=src python -m rhodyn.cli score-residence \
  examples/mlci_public_intensity_trajectory.csv \
  --low 13.0 \
  --high 14.5 \
  --signal-column signal
```

This is a public live-cell tracking workflow derived from Zenodo 7260137. The
intensity signal is a trajectory-analysis example, not a molecular activity
reporter or disease-state measurement.

## Result visualization and export

After a run, the report builder keeps the exact JSON result visible and adds a
compact operation-specific view. Residence results show per-trace residence
fractions, coupling results show interval placement against the declared margin,
reserve results show reserve summaries by sample, and model-comparison results
show ranked fit summaries. These views are presentation surfaces only. The raw
JSON result remains the reproducible source.

The report builder can download the last result as JSON, result rows as CSV,
or a Markdown report with parameter provenance. The bundle route still provides
the backend-generated ZIP with submitted rows, result JSON, result rows,
parameter provenance, and checksums.

## Contract rule

The frontend must consume the frozen Stage 4 contract rather than hard-coding a new biological or analytical surface. New screens may rearrange upload, visualization, parameter inspection, and export workflows, but any new backend route, new algorithm, new public biological system, or new release surface belongs to the relevant roadmap stage before it belongs in this scaffold.

This scaffold does not add new biological systems, algorithms, manuscript interpretation, or product/commercial claims.
