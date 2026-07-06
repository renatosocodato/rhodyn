<!-- EDITORIAL-PASS-2 stage=9.25 generated=2026-07-06T07:43:55Z commit=954c0d09ca5115992ee6a6394d0be1e856ed0916 -->
# Stage 9.25 editorial polish pass II

Stage 9.25 performs the second reader-facing polish loop after editorial polish pass I. The pass removes residual process-like phrasing, tightens venue-style readability, varies supplementary-legend openings, and preserves the current evidence boundaries. It does not change statistics, figures, source data, model outputs, figure numbering, or method claims.

## Summary

The second editorial polish pass completed four recursive checks. Paragraph IDs, claim IDs, and Results figure calls were preserved. Paragraph lengths and repeated-start metrics remained within threshold. Claim-strength caps and limitation language stayed present, and no reader-surface hygiene gate, peer-review simulation, PI packet, readiness checklist, or final package assembly was started.

## Recursive polish rounds

| Round | Focus | Status |
|---|---|---|
| 1 | venue-style process phrase removal | pass |
| 2 | paragraph rhythm and repeated-start thresholds | pass |
| 3 | meaning, claim-strength, and limitation retention | pass |
| 4 | figure-call flow and downstream-boundary check | pass |

## Gate checks

| Check | Status | Detail |
|---|---|---|
| stage_9_24_gate_passed | pass | Stage 9.24 editorial polish pass I gate is present and points to Stage 9.25 |
| meaning_preserved | pass | paragraph_errors=[]; claim_id_errors=[]; figure_call_errors=[] |
| style_metrics_pass_thresholds | pass | style_errors=[] |
| no_claim_broadened | pass | unsafe_hits=[]; missing_limit_terms=[] |
| venue_style_replacements_resolved | pass | final_phrase_missing={}; process_hits=[] |
| dynamic_figure_call_flow_preserved | pass | terminal_figure_calls={} |
| reader_surface_stage_language_absent | pass | reader_stage_hits=[] |
| no_reader_hygiene_or_package_started | pass | downstream_paths=[] |

## Style metrics

| Surface | Most common sentence starts | Maximum paragraph words | Maximum repeated sentence start |
|---|---|---:|---:|
| manuscript/nature_methods/sections/introduction.md | {'RhoDyn': 3, 'The': 3, 'For': 2, 'It': 2, 'Live': 1, 'Benchmarking': 1} | 128 | 1 |
| manuscript/nature_methods/sections/results.md | {'In': 6, 'The': 5, 'These': 3, 'Boundary': 1, 'Executable': 1, 'Together': 1} | 161 | 2 |
| manuscript/nature_methods/sections/discussion.md | {'The': 6, 'It': 3, 'They': 3, 'RhoDyn': 2, 'This': 2, 'DRG': 1} | 166 | 3 |
| manuscript/nature_methods/sections/methods.md | {'The': 8, 'For': 5, 'This': 3, 'Each': 2, 'These': 2, 'Trajectory': 1} | 125 | 2 |
| manuscript/nature_methods/figures/figure_legends.md | {'The': 7, 'These': 1, 'Expanded': 1, 'Public': 1, 'Endpoint': 1, 'Measured': 1} | 138 | 3 |

## Replacements applied

| Surface | Replacement status |
|---|---|
| manuscript/nature_methods/sections/introduction.md | replacement_1_already_present |
| manuscript/nature_methods/sections/results.md | replacement_1_already_present, replacement_2_already_present, replacement_3_already_present |
| manuscript/nature_methods/sections/discussion.md | replacement_1_already_present, replacement_2_already_present, replacement_3_already_present |
| manuscript/nature_methods/sections/methods.md | replacement_1_already_present, replacement_2_already_present |
| manuscript/nature_methods/figures/figure_legends.md | replacement_1, replacement_2, replacement_3, replacement_4, replacement_5, replacement_6, replacement_7, replacement_8, replacement_9 |

## Scope boundary

This stage modifies reader-facing prose for venue-style flow only. It does not broaden the residence, bounded-coupling, reserve-like, routed-output, or reproducibility claims. It keeps inconclusive outcomes visible and preserves the distinction between demonstrated software reproducibility and new biological evidence.
