# Optional live-cell prior-art citation candidate

This note records one evidence-safe prior-art addition candidate for a later package-promotion pass. It is not promoted into the closed Stage 9.29 package by this runner.

## Candidate reference

Copperman, J. et al. Morphodynamical cell state description via live-cell imaging trajectory embedding. Communications Biology 6, 484 (2023). doi:10.1038/s42003-023-04837-8.

## Why this may help

The current Introduction already cites trajectory inference, dynamic transient-state modeling, state-space visualization, CellRank, Cellpose, Squidpy, scvi-tools, and DeepLabCut. A Nature Methods editor may still ask whether live-cell morphodynamic trajectory embedding is directly acknowledged. This reference would sharpen the claim that RhoDyn is not claiming novelty for time-lapse trajectory analysis itself, but for the integrated residence, bounded-coupling, reserve-like, routed-output, and reproducibility decision object.

## Candidate insertion

In the third Introduction paragraph, revise the citation range in the sentence beginning `The novelty claimed here is not...` so that live-cell morphodynamic trajectory embedding is explicitly included among established prior dynamic live-cell approaches.

## Promotion requirements

- Renumber dataset, software, and PanelForge references consistently in `main_text_for_submission.md`, `references.bib`, `references_for_submission.bib`, citation ledgers, and availability sections.
- Re-run package assembly and Stage 9 validation after promotion.
- Do not add this citation if the final author decision is to keep the reference list compact for triage.
