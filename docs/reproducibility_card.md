# Reproducibility card

This card records the current reproducibility target for the private RhoDyn
release-candidate line. It is a software-release surface, not a manuscript
claim.

## Software identity

- Package name. `rhodyn`
- Current version. `0.1.0`
- License. Apache-2.0
- Python support target. Python 3.10 and newer
- Core runtime dependencies. None beyond the Python standard library

## Optional extras

- `rhodyn[pandas]` for larger table handling.
- `rhodyn[stats]` for SciPy-backed TOST calculations.
- `rhodyn[plots]` for Matplotlib diagnostics.
- `rhodyn[backend]` for FastAPI, HTTP test-client support, and Uvicorn.
- `rhodyn[notebooks]` for Jupyter tutorials.
- `rhodyn[dev]` for package builds, documentation builds, and publication dry
  runs.

## Clean-room command target

A release candidate should pass this sequence from a fresh clone and fresh
virtual environment.

```bash
python -m pip install --upgrade pip
python -m pip install '.[dev]'
python -m build --sdist --wheel
python -m pip install --force-reinstall --no-deps dist/*.whl
rhodyn validate examples/synthetic_trajectory.csv
rhodyn score-residence examples/synthetic_trajectory.csv --low 0.35 --high 0.75
rhodyn decide-coupling examples/synthetic_coupling.csv
rhodyn summarize-reserve examples/synthetic_reserve.csv --floor 1.0 --ceiling 1.7 --baseline-points 1
rhodyn compare examples/synthetic_endpoints.csv
rhodyn simulate --duration 5 --dt 1
python examples/residence_reserve_workflow.py
mkdocs build --strict
```

## Data included in the software repository

The repository includes small synthetic examples, public derived case-study
tables, frozen API fixtures, documentation, tests, and the Stage 5 static
workbench. The repository should not include raw microscopy, manuscript-private
source files, local machine paths, credentials, mounted-volume paths, or
generated debug outputs.

## Manuscript reference case

The RhoA/microglia manuscript repository and its Zenodo software/data archives
are optional reference use-case inputs. They are not package dependencies and
should not be described as outputs produced by RhoDyn.

## Current release status

Phase 6 is active. The package should not be described as professionally
citable until packaging, documentation, release automation, archive/citation,
clean-room reproducibility, and final ultra-hardening checks pass together.
