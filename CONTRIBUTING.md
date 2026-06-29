# Contributing to RhoDyn

RhoDyn is a standalone scientific software toolkit for residence-state analysis,
bounded coupling decisions, reserve summaries, reduced-architecture comparison,
uncertainty diagnostics, and reproducible reporting. Contributions should keep
that software boundary clear. The RhoA/microglia manuscript is an optional
reference case study, not a source of hidden private data or untracked analysis
state.

## Development setup

Create a fresh environment and install the development extra.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

For backend work, install the backend extra.

```bash
python -m pip install -e '.[backend]'
```

For notebook or plotting work, use the corresponding optional extras documented
in `docs/optional_extras.md`.

## Local checks before a pull request

Run the release-safety and test checks from the repository root.

```bash
python scripts/check_release.py
python scripts/check_roadmap_memory.py
python scripts/audit_phase6_release_readiness.py --out docs/phase6_release_readiness_report.json
python -m unittest discover tests
mkdocs build --strict
```

Frontend work should also run the Stage 5 browser regression suite.

```bash
npm ci
npx playwright install --with-deps chromium
npm run test:stage5
```

Docker-facing changes should build the backend service image.

```bash
docker build -f deploy/stage4.Dockerfile -t rhodyn-stage4:local .
```

## Scientific and software boundaries

- Do not add raw microscopy, manuscript-private workbooks, credentials, mounted
  volume paths, or local-machine paths to this repository.
- Keep public examples synthetic or explicitly public and redistributable.
- Keep decisions reproducible by preserving input schemas, parameter choices,
  software version, and exported reports.
- Treat manuscript-derived examples as optional reference use cases. Do not imply
  that RhoDyn generated the original manuscript results.
- Distinguish measured signals from derived residence scores, equivalence
  decisions, reserve summaries, and model-derived outputs.

## Pull-request expectations

A useful pull request should include the reason for the change, the user-facing
behavior that changed, the tests or examples that were run, and any scientific
interpretation boundary that remains important for users. New API or CLI
features should include tests, documentation, and a small example where practical.
