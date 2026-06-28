# Stage 4 closeout

Stage 4 API contract is frozen for the first Stage 5 frontend scaffold.

## Frozen surfaces

- `api/stage4/openapi.json` is the committed OpenAPI schema exported from the FastAPI backend.
- `api/stage4/frontend_contract.json` is the frontend-facing operation map used by the Stage 5 scaffold.
- `api/stage4/contract_manifest.json` records the contract version, file hashes, expected paths, and handoff decision.
- `api/stage4/fixtures/` contains canonical request and response fixtures for schema validation, residence scoring, coupling decisions, reserve summaries, model comparison, report export, upload routes, bundle routes, and durable job routes.

## Regeneration

Regenerate the frozen contract only after an intentional Stage 4 API change.

```bash
python scripts/freeze_stage4_api_contract.py
python scripts/audit_stage5_frontend_scaffold.py
```

The generator requires the backend extra because it exports the FastAPI OpenAPI schema and route fixtures.

## Stage 4 gate state

Stage 4 is closed enough for Stage 5 because the backend delegates analysis to the Python library, durable jobs preserve submitted rows and declared parameters, bundles include exact result JSON and hashes, upload routes are smoke-tested, and the committed contract gives the frontend a stable dependency.

This closeout does not add a biological case study, change RhoDyn analysis behavior, or make the project a Stage 6 public release.
