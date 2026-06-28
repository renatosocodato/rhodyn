# Stage 5 frontend scaffold

Stage 5 scaffold is contract-bound to the frozen Stage 4 API contract.

## Scope

The scaffold in `frontend/stage5/` is a static scientific workbench shell. It loads `api/stage4/frontend_contract.json` and `api/stage4/openapi.json`, then exposes the Stage 4 upload, bundle, and durable-submit routes without introducing new analysis logic.

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

## Contract rule

The frontend must consume the frozen Stage 4 contract rather than hard-coding a new biological or analytical surface. New screens may rearrange upload, visualization, parameter inspection, and export workflows, but any new backend route, new algorithm, new public biological system, or new release surface belongs to the relevant roadmap stage before it belongs in this scaffold.

This scaffold does not add new biological systems, algorithms, manuscript interpretation, or product/commercial claims.
