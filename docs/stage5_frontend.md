# Stage 5 frontend scaffold

Stage 5 scaffold is contract-bound to the frozen Stage 4 API contract.

## Scope

The scaffold in `frontend/stage5/` is a static scientific workbench shell. It loads `api/stage4/frontend_contract.json`, `api/stage4/openapi.json`, and the frozen schema fixture, then exposes the Stage 4 upload, bundle, and durable-submit routes without introducing new analysis logic. The upload screen now shows the selected operation, expected schema columns, editable parameters, serialized parameter payload, route preview, local schema preflight status, and a contract example loader. The trajectory explorer also reports trace counts, condition and replicate counts, signal and time ranges, and per-trace residence summaries for the current signal column and window.

## Screens

- Project dashboard.
- Data upload and schema validation.
- Trajectory explorer.
- Simulation Workbench.
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

## Browser regression

The Stage 5 workbench has a Playwright screenshot-regression harness for the
operation-specific comparison panels, the public MLCI trajectory workflow, and
an adversarial bounded-coupling case with long labels and near-margin intervals.
The tests run in desktop and mobile Chromium viewports, verify that the page
does not create horizontal overflow, and keep formal bounded-coupling language
from drifting into a claim of zero coupling.

```bash
npm ci
npx playwright install chromium
npm run test:stage5
```

Use `npm run test:stage5:update-screenshots` only when a deliberate visual
change has been reviewed. The committed baselines are platform-specific for
Darwin and Linux, because Chromium font metrics differ slightly between local
macOS review and Ubuntu CI. Both platforms retain separate desktop and mobile
Chromium snapshots.

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


## Simulation Workbench

The Simulation Workbench exposes the existing deterministic controller simulation from `rhodyn.models.simulate_controller` and the `rhodyn simulate` CLI command. It provides declared presets, editable controller parameters, RhoA window, Src, reserve, burden, and Myh9/Myh10 route trajectories, first-passage timing for a burden threshold, a compact row table, and JSON, CSV, and Markdown exports.

This is a narrow Stage 5.1 repair. The screen mirrors the deterministic controller for parameter exploration. It is not a new backend route, does not add stochastic inference, does not fit data, and does not create a biological result.

## Result visualization and export

After a run, the report builder keeps the exact JSON result visible and adds a
professional operation-specific comparison suite. Residence results show a
metric strip, ranked per-trace residence fractions, and a compact trace table.
Coupling results place confidence intervals against each declared margin and
label bounded-coupling decisions without implying zero coupling. Reserve
results rank samples by the derived reserve coordinate, and model-comparison
results rank reduced architectures by delta BIC, BIC, AIC, RMSE, and RSS. These
views are presentation surfaces only. The raw JSON result remains the
reproducible source.

The report builder can download the last result as JSON, result rows as CSV,
or a Markdown report with parameter provenance. The bundle route still provides
the backend-generated ZIP with submitted rows, result JSON, result rows,
parameter provenance, and checksums.

## Contract rule

The frontend must consume the frozen Stage 4 contract rather than hard-coding a new biological or analytical surface. New screens may rearrange upload, visualization, parameter inspection, and export workflows, but any new backend route, new algorithm, new public biological system, or new release surface belongs to the relevant roadmap stage before it belongs in this scaffold.

This scaffold does not add new biological systems, algorithms, manuscript interpretation, or product/commercial claims.
