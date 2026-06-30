# Stage 7.5 held-out analysis plan

Stage 7.5 tests RhoDyn on a held-out non-DMSO inhibitor slice from the public Wan et al. 2021 ERK/Akt GPCR archive. The held-out contexts are His/PTx, His/YM, His/ymptx, S1P/PTx, S1P/YM, S1P/ymptx, UK/PTx. These records are separated from the DMSO-control slice used in the Stage 7.4 promoted bounded-coupling example.

## Fixed inputs

- Source dataset. Wan et al. 2021 public Zenodo archive, DOI 10.5281/zenodo.5836623.
- ERK high-state threshold. 0.7623.
- Akt high-state threshold. 0.5892.
- Primary margin. +/-0.20 ERK-minus-Akt residence-fraction units.
- Alpha. 0.05.
- Selection rule. Up to 20 cells per ligand-inhibitor-experiment context.
- Grouping. Experiment labels are retained for grouped bootstrap sensitivity.

## Decision rule

A held-out context passes bounded coupling when the 90 percent TOST interval for ERK-minus-Akt high-state residence is inside +/-0.20 and the Holm-adjusted TOST p value is below 0.05. A context fails when the 90 percent interval is entirely outside the margin. Contexts that do not pass and do not fail are reported as inconclusive.

## Interpretation boundary

A passing context supports bounded coupling of derived residence summaries for that ligand-inhibitor condition. It does not establish biochemical equivalence, absence of all pathway crosstalk, or a universal GPCR signaling rule.
