<!-- STATISTICAL-LANGUAGE-AUDIT stage=9.22 generated=2026-07-06T09:53:12Z commit=adc11681f39660eb65e489d8e7903834da907458 -->
# Stage 9.22 statistical and quantitative language audit

Stage 9.22 recomputes live-number bindings from the frozen Stage 7 evidence surfaces and checks whether the manuscript-facing quantitative language stays inside declared statistical bounds. This pass updates the statistic ledger where a source table has changed, binds each main figure to explicit statistic IDs, and does not write or modify figure legends or final submission assembly.

## Summary

The live-number audit passed. Nineteen statistic IDs were recomputed or inspected against their source artifacts. One stale live number was corrected. `STAT-0018`, the release-archive manifest file count for the reproducibility figure, changed from `row_count=625` to `row_count=632` after the latest archive refresh. This changes traceability count reporting only and does not alter a biological result, model comparison, or bounded-coupling decision.

## Gate checks

| Check | Status | Detail |
|---|---|---|
| stage_9_21_gate_passed | pass | Stage 9.21 cross-document consistency gate is present and passed |
| every_statistic_recomputes_within_tolerance | pass | checked=19; updated=1; failures=0 |
| quantitative_statements_have_statistic_ids | pass | figures_with_pending_stats=0; unknown_figure_stat_ids=0; unsupported_reader_surface_statements=0 |
| equivalence_claims_state_bounds | pass | unsafe_hits=[]; methods_terms=['\\Delta', 'TOST', 'ROPE', '0.95']; results_margin_scoped=True |
| live_numbers_diff_written | pass | diff_rows=19 |
| no_figure_legend_or_package_started | pass | No PI packet, readiness checklist, or completion report detected; this statistical pass did not write or modify figure legends |
| scope_boundary_preserved | pass | Live-number/statistical-language audit only; no new data, model outputs, biological claims, figure-legend changes, or submission package |

## Live-number diff

| Statistic ID | Expected value | Previous manuscript value | Status |
|---|---|---|---|
| STAT-0001 | displayed definitions for tidy trajectory, residence window, dwell fraction, dwell time, segment count, and amplitude comparators | displayed definitions for tidy trajectory, residence window, dwell fraction, dwell time, segment count, and amplitude comparators | inspection_only_pass |
| STAT-0002 | positive, negative, and ambiguous executable examples represented | positive, negative, and ambiguous executable examples represented | inspection_only_pass |
| STAT-0003 | failure modes and interpretation boundaries represented | failure modes and interpretation boundaries represented | inspection_only_pass |
| STAT-0004 | row_count=12 | row_count=12 | pass |
| STAT-0005 | row_count=1 | row_count=1 | pass |
| STAT-0006 | row_count=360 | row_count=360 | pass |
| STAT-0007 | row_count=180 | row_count=180 | pass |
| STAT-0008 | DRG and ERK public adapter reports represented | DRG and ERK public adapter reports represented | inspection_only_pass |
| STAT-0009 | row_count=4 | row_count=4 | pass |
| STAT-0010 | not_promoted_beyond_declared_margin=2;primary_context_limited_bounded_coupling=1;secondary_pooled_or_contextual_summary=1 | not_promoted_beyond_declared_margin=2;primary_context_limited_bounded_coupling=1;secondary_pooled_or_contextual_summary=1 | pass |
| STAT-0011 | row_count=6 | row_count=6 | pass |
| STAT-0012 | row_count=2 | row_count=2 | pass |
| STAT-0013 | row_count=6 | row_count=6 | pass |
| STAT-0014 | row_count=5 | row_count=5 | pass |
| STAT-0015 | context_count=7;pass_count=4;fail_count=0;inconclusive_count=3 | context_count=7;pass_count=4;fail_count=0;inconclusive_count=3 | pass |
| STAT-0016 | row_count=70 | row_count=70 | pass |
| STAT-0017 | row_count=4 | row_count=4 | pass |
| STAT-0018 | row_count=632 | row_count=625 | updated |
| STAT-0019 | failure modes, ambiguous regimes, and claim-strength caps represented | failure modes, ambiguous regimes, and claim-strength caps represented | inspection_only_pass |

## Figure-level statistic bindings

| Figure | Statistic IDs |
|---|---|
| FIG-001 | STAT-0001;STAT-0002;STAT-0003;STAT-0019 |
| FIG-002 | STAT-0004;STAT-0005 |
| FIG-003 | STAT-0006;STAT-0007;STAT-0008 |
| FIG-004 | STAT-0009;STAT-0010;STAT-0011;STAT-0012;STAT-0013;STAT-0014 |
| FIG-005 | STAT-0015;STAT-0016 |
| FIG-006 | STAT-0017;STAT-0018 |

## Equivalence and bounded-coupling language

The bounded-coupling language remains scoped to declared margins. The Methods surface contains the `TOST`, `ROPE`, `\Delta`, and `0.95` decision terms, and the Results surface describes bounded-coupling decisions as margin-scoped rather than as proof of no pathway communication. Unsafe phrases detected in Results or Methods. []

## Reader-facing numerical scan

Unsupported exact statistic phrases found in Results or Methods. []

## Scope boundary

Updated statistic IDs. STAT-0018

This audit does not write or modify figure legends, does not create the PI review packet, does not assemble the final manuscript package, and does not add new data, figures, analyses, model outputs, or biological claims. It only makes the quantitative traceability layer match the frozen evidence surfaces and confirms that statistical language remains bounded.
