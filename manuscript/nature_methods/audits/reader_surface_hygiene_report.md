<!-- READER-SURFACE-HYGIENE stage=9.25b generated=2026-07-06T09:53:23Z commit=adc11681f39660eb65e489d8e7903834da907458 -->
# Stage 9.25b reader-surface hygiene report

Stage 9.25b cleans the manuscript-facing surfaces after the second editorial polish pass. The pass removes internal paragraph IDs, claim IDs, method-statement IDs, reference tokens, source-artifact IDs, stage metadata, and HTML comments from the reader-facing Markdown. It does not change the evidence set, statistics, figures, source data, model outputs, figure calls, biological examples, or interpretation limits.

## Summary

The hygiene pass completed four recursive checks. Hidden comments were removed from the manuscript surfaces, Introduction reference tokens were converted to readable numbered citation calls, the abstract now opens as a clean reader-facing abstract, and figure legends remain free of lineage language. Code and data availability still retain public DOIs, repository URLs, and reproducibility commands where they are scientifically and practically required.

## Recursive hygiene rounds

| Round | Focus | Status |
|---|---|---|
| 1 | hidden metadata and HTML-comment removal | pass |
| 2 | internal ID and REF token removal from reader surfaces | pass |
| 3 | stage, lineage, and figure-caption leakage scan | pass |
| 4 | scientific boundary, citation, figure-call, and availability preservation | pass |

## Gate checks

| Check | Status | Detail |
|---|---|---|
| stage_9_25_gate_passed | pass | Stage 9.25 editorial polish pass II gate is present and points to Stage 9.25b |
| reader_comments_removed | pass | comment_hits=[]; removed_comments={'manuscript/nature_methods/sections/abstract.md': 0, 'manuscript/nature_methods/sections/introduction.md': 0, 'manuscript/nature_methods/sections/results.md': 0, 'manuscript/nature_methods/sections/discussion.md': 0, 'manuscript/nature_methods/sections/methods.md': 0, 'manuscript/nature_methods/sections/data_availability.md': 0, 'manuscript/nature_methods/sections/code_availability.md': 0, 'manuscript/nature_methods/figures/figure_legends.md': 0, 'manuscript/nature_methods/supplementary/supplementary_methods.md': 0} |
| internal_ids_absent_from_reader_surfaces | pass | internal_id_hits=[]; ref_replacements={'manuscript/nature_methods/sections/abstract.md': 0, 'manuscript/nature_methods/sections/introduction.md': 0, 'manuscript/nature_methods/sections/results.md': 0, 'manuscript/nature_methods/sections/discussion.md': 0, 'manuscript/nature_methods/sections/methods.md': 0, 'manuscript/nature_methods/sections/data_availability.md': 0, 'manuscript/nature_methods/sections/code_availability.md': 0, 'manuscript/nature_methods/figures/figure_legends.md': 0, 'manuscript/nature_methods/supplementary/supplementary_methods.md': 0} |
| stage_and_build_language_absent | pass | stage_language_hits=[]; abstract_stage_header_present=False |
| legends_and_captions_free_of_lineage_language | pass | panel_s3_crossrefs=[] |
| meaning_and_figure_flow_preserved | pass | figure_call_errors=[]; terminal_calls={}; missing_required_terms=[]; missing_surface_phrases={} |
| claim_boundaries_preserved | pass | unsafe_hits=[] |
| local_path_and_secret_scan_clear | pass | local_path_hits=[]; secret_hits=[] |
| no_internal_peer_review_or_package_started | pass | downstream_paths=[] |

## Reader-surface cleanup

| Surface | Hidden comments removed | Internal REF tokens replaced |
|---|---:|---:|
| manuscript/nature_methods/sections/abstract.md | 0 | 0 |
| manuscript/nature_methods/sections/introduction.md | 0 | 0 |
| manuscript/nature_methods/sections/results.md | 0 | 0 |
| manuscript/nature_methods/sections/discussion.md | 0 | 0 |
| manuscript/nature_methods/sections/methods.md | 0 | 0 |
| manuscript/nature_methods/sections/data_availability.md | 0 | 0 |
| manuscript/nature_methods/sections/code_availability.md | 0 | 0 |
| manuscript/nature_methods/figures/figure_legends.md | 0 | 0 |
| manuscript/nature_methods/supplementary/supplementary_methods.md | 0 | 0 |

## Scope boundary

This stage is a reader-surface hygiene pass only. It preserves the method claim that residence-state inference, bounded-coupling decisions, reserve-like endpoint summaries, routed-output comparisons, and reproducibility checks are reviewable under declared inputs and limits. It does not add new biological evidence, start the internal peer-review simulation, assemble the submission package, or promote any claim beyond the retained evidence set.
