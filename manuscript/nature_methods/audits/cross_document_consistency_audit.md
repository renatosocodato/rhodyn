<!-- CROSS-DOCUMENT-CONSISTENCY stage=9.21 generated=2026-07-07T10:51:23Z commit=62c2841691ce15ec6960440ea2faba7f60124e81 -->
# Stage 9.21 cross-document consistency audit

Stage 9.21 checks whether the manuscript's frozen claim system is internally coherent across claims, paragraphs, main figures, statistics, supplementary support, source-data tables, and references. This is a keyed-ledger consistency pass only. It does not rewrite the manuscript, recompute numerical results, write figure legends, audit statistical phrasing, or assemble the final submission package.

## Summary

The cross-document joins passed. The current manuscript state contains no orphan claims, no orphan main figures, no orphan statistic IDs, and no dangling references. Figure-engine versioning, rendered figure paths, source-data paths, and paragraph-level strength caps remain coherent with the frozen claim hierarchy.

| Surface | Count | Join basis |
|---|---:|---|
| Frozen claims | 5 | Claim hierarchy and paragraph/figure/source/reference ledgers |
| Main figures | 6 | Figure-to-claim ledger, statistic ledger, supplementary callouts, and source-data bindings |
| Statistics | 19 | Statistic ledger and supplementary source-data binding ledger |
| References | 14 | Citation-claim ledger and BibTeX library |
| Supplementary tables | 9 | Source-data binding ledger |

## Gate checks

| Check | Status | Detail |
|---|---|---|
| stage_9_20_gate_passed | pass | Stage 9.20 reference library is present and passed |
| orphan_claim_set_empty | pass | orphan=0; unknown_refs=0 |
| orphan_figure_set_empty | pass | orphan=0; unknown_refs=0 |
| orphan_statistic_set_empty | pass | orphan=0; unknown_refs=0 |
| dangling_reference_set_empty | pass | dangling_refs=0; unresolved_refs=0; unknown_paragraphs=0; unknown_tables=0 |
| version_and_strength_coherence_hold | pass | strength_mismatches=0; missing_render_paths=0; bad_engine_rows=0; missing_source_paths=0; missing_binding_render_paths=0 |
| no_statistical_language_legend_or_package_started | pass | Closed Stage 9.29 package refresh allowed existing downstream surfaces |
| scope_boundary_preserved | pass | Cross-document joins only; no statistics recomputed, legends written, or final package assembled |

## Empty mismatch sets

- Orphan claims. []
- Unknown claim references. []
- Orphan figures. []
- Unknown figure references. []
- Orphan statistics. []
- Unknown statistic references. []
- Dangling or unresolved references. []
- Unknown paragraph references. []
- Unknown source-data table references. []

## Version and strength coherence

- PanelForge engine version. `panelforge-figures@v3.14.1`
- Missing rendered main-figure paths. []
- Bad figure-engine rows. []
- Missing source paths. []
- Missing source-data render paths. []
- Paragraph strength-cap mismatches. []

## Scope boundary

The biological interpretation remains unchanged. This audit supports manuscript assembly by showing that the current Results, Methods, figures, source-data support, and references point to the same bounded method claims. It does not test live-number phrasing, does not write figure legends, and does not create the PI review or submission-readiness package. Those remain downstream Stage 9 steps.
