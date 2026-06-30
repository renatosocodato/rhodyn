# Stage 7.6 recursive hardening

Stage 7.6 now has two independent checks. The full reproducibility runner rebuilds the Stage 7.1 to Stage 7.5 evidence set from a release-candidate archive, while the recursive hardening audit verifies that the recorded evidence is internally consistent after the run.

## What the recursive audit checks

- The documentation gate report, clean-room report, and case-study gate report are identical.
- The run was produced in `full_release_archive` mode, not by the faster CI path.
- Every deterministic output selected for Stage 7.6 exists in the clean-room source tree, exists in the reference tree, has a full hash, and matches.
- Python, CLI, backend, and frontend-contract parity remain aligned for residence scoring, bounded-coupling decisions, reserve-like summaries, and reduced-architecture comparison.
- The command table still covers Stage 7.1 through Stage 7.5 in order.
- The release-candidate archive manifest includes the required scripts, docs, notebooks, and examples and contains no raw/private-like payloads.
- The interpretation boundary remains explicit. Stage 7.6 supports software reproducibility only and does not add biological evidence.

## Outputs

The machine-readable recursive report is written to `docs/stage7_6_recursive_hardening_report.json` and mirrored under `case_studies/stage7_methods_reproducibility/stage7_6_recursive_hardening_report.json`.

The release archive file inventory is written to `case_studies/stage7_methods_reproducibility/release_archive_manifest.tsv`.

## Scientific boundary

A passing recursive audit means the methods-evidence surface is reproducible and internally traceable from the release-candidate archive. It does not change any residence, reserve, bounded-coupling, routed-output, or held-out validation interpretation, and it does not imply that future user datasets will exhibit the same dynamic-state structure.
