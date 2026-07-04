<!-- FIGURE-LEGEND-AUDIT stage=9.23 generated=2026-07-04T12:08:40Z commit=7764057031acb6b01d773aad79e9cc6d76fb0f3d -->
# Stage 9.23 figure legend and caption audit

Stage 9.23 writes the first reader-facing legend and caption surface for the six main display items, nine planned supplementary figures, and nine planned supplementary tables. The visible legend text uses standard figure and table names, while this audit checks the hidden joins to figure panels, statistics, supplementary support, and claim boundaries.

## Summary

The figure legend and caption audit passed. Six main figure legends, nine supplementary figure legends, and nine supplementary table captions were written. All main figure panel letters are represented, every figure and table statistic binding resolves to the current statistic ledger, and the reader-facing legend text contains no internal identifiers, paths, PanelForge wording, or absent-mechanism claims.

## Gate checks

| Check | Status | Detail |
|---|---|---|
| stage_9_22_gate_passed | pass | Stage 9.22 statistical and quantitative language gate is present and passed |
| each_main_figure_has_legend | pass | main_figure_legends=6; missing=[] |
| each_supplementary_figure_and_table_has_caption | pass | supplementary_figures=9; supplementary_tables=9; missing_figures=[]; missing_tables=[] |
| main_figure_panel_coverage_complete | pass | missing_panel_mentions=[] |
| legend_statistics_resolve | pass | stat_resolution_errors=[]; statistic_ids=19 |
| supplementary_callouts_resolve_to_captions | pass | supplementary_link_errors=[] |
| legends_do_not_assert_absent_claims | pass | unsafe_claim_hits=[] |
| legend_seed_text_has_no_internal_or_panelforge_leakage | pass | leakage_patterns=[] |
| no_final_package_started | pass | forbidden_package_paths=[] |

## Main figure statistic bindings checked

| Figure | Statistic IDs | Panel structure |
|---|---|---|
| FIG-001 | STAT-0001;STAT-0002;STAT-0003;STAT-0019 | A method object and input contract; B residence-window metrics; C failure modes and interpretation boundaries; D executable truth-case ladder. |
| FIG-002 | STAT-0004;STAT-0005 | A synthetic regime grid; B residence-versus-amplitude benchmark; C reduced-alternative comparison; D negative and ambiguous failure behavior. |
| FIG-003 | STAT-0006;STAT-0007;STAT-0008 | A public-data adapter map; B DRG calcium residence-amplitude separation; C ERK GPCR residence-amplitude separation; D window-sensitivity and uncertainty summary. |
| FIG-004 | STAT-0009;STAT-0010;STAT-0011;STAT-0012;STAT-0013;STAT-0014 | A endpoint schema contract; B bounded-coupling decisions under declared margins; C reserve-like endpoint coordinate; D routed-output reduced-architecture comparison; E measurement-scoped limitations. |
| FIG-005 | STAT-0015;STAT-0016 | A held-out analysis plan; B bounded-coupling pass contexts; C inconclusive margin-boundary contexts; D margin sensitivity; E controlled-access boundary. |
| FIG-006 | STAT-0017;STAT-0018 | A Python, CLI, backend, and workbench parity; B export bundle anatomy; C source-distribution clean-room reproduction; D archive and checksum provenance; E adoption and user-path rehearsal. |

## Supplementary table statistic bindings checked

| Table | Statistic IDs | Interpretation boundary |
|---|---|---|
| STBL-001 | STAT-0001;STAT-0002;STAT-0003 | Method definition and counterexample support only; not independent biological evidence. |
| STBL-002 | STAT-0004;STAT-0005 | Synthetic benchmark behavior only; not a new biological system. |
| STBL-003 | STAT-0006;STAT-0007;STAT-0008 | Demonstrates two public live-cell reporter systems without claiming universal residence behavior. |
| STBL-004 | STAT-0009;STAT-0010 | Bounded coupling is margin- and context-limited; it is not proof of no crosstalk. |
| STBL-005 | STAT-0011;STAT-0012 | Reserve-like means measured endpoint preservation; it is not a direct live metabolic reserve assay. |
| STBL-006 | STAT-0013;STAT-0014 | Effective routed terms constrain endpoint architecture but do not identify literal molecular edges. |
| STBL-007 | STAT-0015;STAT-0016 | Supports scoped transfer of declared decisions rather than a universal coupling rule. |
| STBL-008 | STAT-0017;STAT-0018 | Supports reproducibility of retained evidence surfaces; it does not claim private-data reproduction or PyPI publication. |
| STBL-009 | STAT-0019 | A claim-boundary support surface, not a new result. |

## Reader-facing language boundary

The legend file does not expose internal IDs, source paths, render paths, engine provenance, commit identifiers, or package-build language. Bounded coupling is described as a declared-margin decision, reserve-like output is described as endpoint-scoped buffering behavior, and routed-output comparisons are described as tested endpoint architectures rather than direct molecular edges.

## Scope boundary

This stage writes figure legends and table captions only. It does not assemble the full manuscript, create a PI review packet, run editorial polish, change figures, introduce new analyses, or modify biological claims.
