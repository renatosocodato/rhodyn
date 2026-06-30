# Stage 7.5 held-out biological validation

Stage 7.5 tests RhoDyn on held-out non-DMSO inhibitor contexts from the public Wan et al. 2021 ERK/Akt GPCR archive. The analysis keeps the Stage 7.4 DMSO-derived ERK and Akt residence thresholds fixed and uses the same declared +/-0.20 ERK-minus-Akt residence-fraction margin.

## Biological question

The case asks whether bounded ERK/Akt residence coupling observed in the retained DMSO-control demonstration behaves as a reviewable rule under held-out inhibitor contexts, or whether RhoDyn reports boundary behavior when coupling becomes context-dependent.

## Outcome

The held-out result is mixed and therefore useful. The mixed outcome includes four bounded-coupling pass contexts and three margin-boundary inconclusive contexts. Numerically, 4 contexts passed the fixed bounded-coupling rule, 3 contexts remained margin-boundary inconclusive, and 0 contexts failed by lying entirely outside the declared margin. This supports RhoDyn as a scoped decision framework rather than a success-only demonstration path.

| Ligand | Inhibitor | Cells | Experiments | ERK-minus-Akt estimate | 90 percent CI | Holm TOST p | Outcome | Grouped sensitivity |
|---|---:|---:|---:|---:|---:|---:|---|---|
| His | PTx | 60 | 3 | -0.03986 | -0.09788 to 0.01817 | 1.973e-05 | pass_bounded_coupling | group_bootstrap_inside_margin |
| His | YM | 60 | 3 | -0.07609 | -0.1361 to -0.01609 | 0.001361 | pass_bounded_coupling | group_bootstrap_crosses_margin |
| His | ymptx | 60 | 3 | -0.2043 | -0.2817 to -0.127 | 0.6837 | inconclusive_margin_boundary | group_bootstrap_crosses_margin |
| S1P | PTx | 60 | 3 | 0.03986 | -0.02653 to 0.1062 | 0.00021 | pass_bounded_coupling | group_bootstrap_inside_margin |
| S1P | YM | 60 | 3 | 0.1348 | 0.05167 to 0.2179 | 0.2952 | inconclusive_margin_boundary | group_bootstrap_crosses_margin |
| S1P | ymptx | 80 | 4 | 0.08098 | 0.03174 to 0.1302 | 0.00021 | pass_bounded_coupling | group_bootstrap_inside_margin |
| UK | PTx | 60 | 3 | -0.1841 | -0.2484 to -0.1197 | 0.6837 | inconclusive_margin_boundary | group_bootstrap_crosses_margin |

## Interpretation boundary

Passing contexts support bounded coupling of derived ERK/Akt residence summaries in that ligand-inhibitor condition. They do not establish biochemical equivalence, absence of all pathway crosstalk, or a universal GPCR signaling law. Inconclusive contexts remain visible because their intervals approach or cross the declared margin under the fixed thresholds and selection rule.

## Evidence-set decision

This case enters the Stage 7 evidence set as scoped held-out boundary validation. It is suitable for a methods-program supplement or limitation-aware validation figure, but it should not be described as a universal external proof that all ERK/Akt GPCR inhibitor contexts are bounded-coupled.
