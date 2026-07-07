# Stage 10.4 held-out validation report

Stage 10.4 adds the no-retuning validation layer that the Nature Methods rescue roadmap requires. The stage deliberately includes positive, negative, and inconclusive calls, because a method-level claim is stronger when unsupported calls remain visible.

## Decisions

| case | challenge | outcome class | call | boundary |
| --- | --- | --- | --- | --- |
| mlci_replicate_01_heldout_residence_amplitude | trajectory_residence_amplitude_holdout | positive | positive_residence_changes_interpretation | Tracking intensity is a public trajectory stress test for schema portability and residence/amplitude divergence, not a molecular signaling reporter. |
| erk_gpcr_ligand_s1p_heldout_residence_amplitude | trajectory_residence_amplitude_holdout | negative | negative_amplitude_or_comparator_largely_sufficient | A concordant held-out ligand supports an amplitude/comparator-sufficient boundary for this split, not a claim that ERK dynamics are always amplitude-sufficient. |
| erk_akt_non_dmso_contexts_bounded_coupling_pass | paired_reporter_margin_holdout | positive | positive_bounded_coupling_preserved | Passing contexts support bounded coupling of derived ERK/Akt residence summaries in those ligand-inhibitor contexts only. |
| erk_akt_non_dmso_contexts_margin_inconclusive | paired_reporter_margin_holdout | inconclusive | inconclusive_margin_boundary_preserved | Inconclusive contexts remain visible when fixed margins do not support promotion. |

## Gate result

Status. `pass`.

- Positive held-out call present. `True`.
- Negative or amplitude-sufficient held-out call present. `True`.
- Inconclusive held-out call present. `True`.
- No-retuning predeclaration present. `True`.
- Stage 10.3 public breadth prerequisite passed. `True`.

## Interpretation

The held-out challenge strengthens RhoDyn's method reading because the same decision framework can preserve a residence-divergence call, withhold a margin-boundary call, and identify a comparator-sufficient boundary without rewriting the rule for each outcome. The result is still scoped. It is not a claim that every public biological system contains a residence regime or that RhoDyn always outperforms simpler summaries.
