# Stage 9 machine-gate specification

Every executable Stage 9 substage writes `manuscript/nature_methods/gate_verdicts/<substage>.json`.

Required fields.

- `substage`
- `checks`
- `pass`
- `timestamp`
- `evidence_version`

`pass` is the logical AND of all check rows. A substage may promote staged outputs only when `pass` is true. Failed staging output is moved to `_quarantine/<substage>/<timestamp>/` and the blocker is written to `docs/stage9_execution_memory.json`.

This scaffold executes only `9.-1`. Future gates are serialized in `contracts/stage9_substage_registry.json` but are not created as passing verdicts until their substages are actually run.

Stage 9.6b is the first substage allowed to clone `panelforge-figures`, create `.venv-panelforge`, write `.panelforge_commit`, validate a real `figures.manifest.yaml`, or render panels. The scaffold may only write placeholder paths and preparatory instructions for that future substage.
