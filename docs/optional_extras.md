# Optional extras

RhoDyn core imports use only the Python standard library. Optional extras are
declared for users who want richer table handling, statistical routines,
plotting, or interactive tutorials.

## Install forms

```bash
python -m pip install 'rhodyn[pandas]'
python -m pip install 'rhodyn[stats]'
python -m pip install 'rhodyn[plots]'
python -m pip install 'rhodyn[backend]'
python -m pip install 'rhodyn[notebooks]'
python -m pip install 'rhodyn[all]'
```

## Planned roles

| extra | package | first intended use |
| --- | --- | --- |
| `pandas` | `pandas` | larger trajectory tables, paper case-study adapters, wide-to-tidy conversion |
| `stats` | `scipy` | Welch TOST, bootstrap intervals, distribution diagnostics |
| `plots` | `matplotlib` | residence traces, margin-sensitivity curves, model residual plots |
| `backend` | `fastapi`, `uvicorn` | stateless service endpoints around frozen Stage 3 analysis surfaces |
| `notebooks` | `jupyterlab` | interactive synthetic and case-study tutorials |

The base package should continue to validate tables, score residence, normalize
reserve-like responses, classify supplied coupling intervals, simulate the
minimal controller, and rank endpoint fits without optional dependencies.

## Graceful failure pattern

Functions that require an optional dependency should call `require_extra()` and
name the feature that needs the dependency.

```python
from rhodyn.extras import require_extra

require_extra("stats", feature="Welch TOST from raw arrays")
```

If the extra is missing, RhoDyn raises `MissingOptionalDependency` with an
install command and the missing package list.
