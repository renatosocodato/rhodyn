<!-- EDITORIAL-PASS-1 stage=9.24 generated=2026-07-06T09:53:23Z commit=adc11681f39660eb65e489d8e7903834da907458 -->
# Stage 9.24 editorial polish pass I

Stage 9.24 performs the first reader-facing polish loop after the figure legend and caption audit. The pass improves cadence, reduces mechanical transitions, and keeps claim language inside the frozen method boundaries. It does not change evidence files, statistics, figures, model outputs, figure numbering, or the biological-method claims.

## Summary

The editorial polish pass completed three recursive checks. Paragraph IDs were preserved, claim-strength caps remained intact, limitations stayed present, and no downstream editorial polish, reader-hygiene gate, PI packet, readiness checklist, or final package assembly was started.

## Recursive polish rounds

| Round | Focus | Status |
|---|---|---|
| 1 | cadence and sentence flow | pass |
| 2 | claim-strength and limitation retention | pass |
| 3 | reader-surface leakage and downstream-boundary check | pass |

## Gate checks

| Check | Status | Detail |
|---|---|---|
| stage_9_23_gate_passed | pass | Stage 9.23 figure legend and caption gate is present and points to Stage 9.24 |
| paragraph_id_set_unchanged | pass | paragraph_id_errors=[] |
| strength_caps_hold | pass | unsafe_hits=[] |
| limitations_remain_present | pass | missing_limit_terms=[] |
| dynamic_figure_call_flow_preserved | pass | terminal_figure_calls={} |
| reader_surface_stage_language_absent | pass | reader_stage_hits=[] |
| recursive_editorial_replacements_resolved | pass | replacement_missing={} |
| no_downstream_stage_started | pass | downstream_paths=[] |

## Cadence metrics

| Surface | Most common sentence starts | Maximum paragraph words |
|---|---|---|
| manuscript/nature_methods/sections/introduction.md | {'RhoDyn': 3, 'The': 3, 'For': 2, 'It': 2, 'Live': 1} | 126 |
| manuscript/nature_methods/sections/results.md | {'In': 6, 'The': 5, 'These': 3, 'Boundary': 1, 'Executable': 1} | 161 |
| manuscript/nature_methods/sections/discussion.md | {'The': 6, 'It': 3, 'They': 3, 'RhoDyn': 2, 'This': 2} | 166 |
| manuscript/nature_methods/sections/methods.md | {'The': 8, 'For': 5, 'This': 3, 'Each': 2, 'These': 2} | 125 |
| manuscript/nature_methods/figures/figure_legends.md | {'Panels': 9, 'The': 5, 'These': 1} | 138 |

## Replacements applied

| Surface | Replacement status |
|---|---|
| manuscript/nature_methods/sections/introduction.md |  |
| manuscript/nature_methods/sections/results.md | replacement_3_already_present, replacement_6_already_present, replacement_7_already_present, replacement_8_already_present |
| manuscript/nature_methods/sections/discussion.md | replacement_1_already_present, replacement_5_already_present |
| manuscript/nature_methods/sections/methods.md | replacement_2_already_present |
| manuscript/nature_methods/figures/figure_legends.md | replacement_1, replacement_2, replacement_3 |

## Scope boundary

This stage modifies reader-facing prose for flow only. It does not broaden the residence, bounded-coupling, reserve-like, routed-output, or reproducibility claims. It keeps inconclusive outcomes visible and preserves the distinction between demonstrated software reproducibility and new biological evidence.
