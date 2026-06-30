# Stage 7.6 API stability and methods reproducibility policy

Stage 7.6 treats the RhoDyn method surface as a reviewable scientific instrument. The goal is not to add a new biological demonstration. The goal is to make the Stage 7.1 to Stage 7.5 evidence set reproducible from a release-candidate archive, with stable method objects, explicit commands, and aligned Python, CLI, backend, and workbench-contract outputs.

## Stable method surfaces

The following surfaces are treated as stable for the methods-program evidence set.

- Tidy trajectory, endpoint, reserve-like, and coupling input schemas exposed through `rhodyn.schema`.
- Residence-window scoring through `rhodyn.residence` and the `score-residence` CLI command.
- Reserve-like summaries through `rhodyn.reserve` and the `summarize-reserve` CLI command.
- Bounded-coupling decisions through `rhodyn.coupling` and the `decide-coupling` CLI command.
- Reduced-architecture and routed-output model comparison through `rhodyn.compare` and the `compare` CLI command.
- Backend operation bundles exposed through `rhodyn.backend_core`.
- Stage 4 service contracts and Stage 5 frontend fixture contracts.
- Stage 7.1 to Stage 7.5 case-study output schemas used by the methods evidence set.

The stable surface is intentionally narrower than the full repository. Internal plotting helpers, tutorial prose, documentation layout, and non-public helper functions may evolve as long as they do not change the declared method decisions or serialized result fields without versioned notice.

## Deprecation policy

RhoDyn should prefer additive changes until the methods-paper evidence surface is frozen.

1. New fields may be added to result objects, CSV outputs, JSON reports, and backend bundles when existing fields remain valid.
2. Field removals, semantic renames, and changed decision thresholds require a deprecation note, a release-note entry, and a migration path.
3. A deprecated public field or command should remain available for at least one minor release or one authorized Stage 7 subphase, whichever is longer.
4. Breaking changes before Stage 7.8 require explicit authorization and a regenerated clean-room report.
5. Decision rules for residence, bounded coupling, reserve-like summaries, and reduced-architecture ranking must not silently change. Any such change is a method change, not a formatting change.

## Reproducibility commands

The methods evidence set is rebuilt by the Stage 7.6 runner.

```bash
python scripts/run_stage7_6_methods_reproducibility.py
```

The full runner builds a source distribution, extracts it into a temporary clean-room workspace, installs the release-candidate archive, regenerates the Stage 7.1 to Stage 7.5 outputs, executes retained tutorials, builds the documentation site, checks cross-surface parity, and compares selected deterministic output tables and reports against the committed snapshots.

Continuous integration uses the faster current-checkout mode.

```bash
python scripts/run_stage7_6_methods_reproducibility.py --ci-fast
```

The fast mode is not a substitute for the full clean-room archive run. It confirms that CI exercises the retained examples, tutorials, docs-adjacent checks, backend/frontend parity, and release safety checks on each change.

## Cross-surface parity rule

A method result is treated as stable only when the same input table and parameters produce the same decision through the relevant Python API, CLI command, backend operation, and frozen frontend-contract fixture. The Stage 7.6 report records parity for residence scoring, bounded-coupling decisions, reserve summaries, and model comparison.

## Interpretation boundary

Stage 7.6 supports software maturity and methods-paper reproducibility. It does not add a new biological system, does not change the Stage 7.3 to Stage 7.5 biological interpretations, and does not imply that all future user datasets will show residence-amplitude divergence, bounded coupling, reserve-like buffering, or routed-output structure.
