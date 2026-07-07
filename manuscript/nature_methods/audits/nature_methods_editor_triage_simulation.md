# Nature Methods simulated editor triage

This is an author-side stress test, not a journal decision. It reads the current package against Nature Methods Article criteria for a novel method or tool, strong validation, reproducibility, general applicability, practical biological utility, and complete submission materials.

## Simulated initial read

Potentially suitable for full editorial consideration after author upload actions. The package now presents RhoDyn as a computational methods Article rather than a disease-biology manuscript or software-only resource. The strongest editorial argument is the validation ladder across synthetic truth cases, public live-cell reporter examples, public endpoint or paired-reporter demonstrations, held-out contexts, and software parity checks. The main residual risk is not manuscript content that Codex can safely edit, but author-side upload completion and continued restraint around generality.

## Criterion-level read

| criterion | risk | simulated editor read | recommended author action |
|---|---|---|---|
| Article content-type fit | low | The package reads as an Article describing a computational method/tool rather than a pure resource or biological application. | Keep Article framing visible in the cover letter and avoid recasting RhoDyn as only a software resource. |
| Novel method object | low | The novelty is credible if framed as an integrated decision workflow, not as the observation that live-cell signals are dynamic. | Preserve the narrow novelty framing during author edits and upload. |
| Validation breadth and transferability | low | The validation ladder is legible as method portability and decision-boundary testing rather than as a single-system biology claim. | Keep examples as method stress tests and avoid claiming every reporter has a residence regime. |
| Performance comparison and alternatives | low | The paper answers why residence adds information in selected regimes while retaining amplitude-sufficient and unresolved cases. | Do not remove the amplitude-sufficient and withheld-decision examples. |
| Reproducibility and software readiness | low | Software reproducibility is strong for review if access links, version, and sample workflows remain available at upload. | Verify reviewer access to the public repository and Zenodo archive immediately before submission. |
| Biological utility without overclaiming | low | The use case helps show biological utility as long as it remains a demonstration of method behavior, not a hidden primary biology claim. | Keep the RhoA/microglia language scoped to reference-use-case evidence. |
| Submission completeness | medium | Repository-derived package contents are complete and the final upload runbook reduces portal-entry drift, but journal forms and portal fields remain author actions. | Complete the official Reporting Summary, author declarations, portal metadata, and author approval using the final upload runbook before upload. |
| Reviewer and editor fit | low | Reviewer selection is structurally aligned with the method claim if the author team fills the planner with experts covering live-cell dynamics, computational time-series inference, statistical decision rules, perturbation endpoints, and reproducible software rather than only RhoA or microglial biology. | Use the reviewer/editor fit planner and final upload runbook to confirm reviewer suggestions, exclusions, and any editor-fit wording with the author team before upload. |
| Desk-rejection residual risk | low | The package is suitable for a serious initial editor read if the author-side upload fields are completed, and the cover-letter draft now foregrounds Article fit, validation breadth, software reproducibility, and calibrated scope. | Use the author-confirmed cover-letter draft to preserve Article fit, validation breadth, software reproducibility, and calibrated scope during upload. |

## Likely editor questions

1. Is RhoDyn a method Article rather than a package note or a biological case study?
2. Does residence-state inference outperform or complement endpoint, amplitude, threshold, and generic trajectory summaries in enough settings?
3. Are declared windows, equivalence margins, reserve-like endpoints, and routed-output alternatives transparent enough for immediate use?
4. Can reviewers run the software and reproduce representative outputs without private manuscript data?
5. Are the RhoA/microglia examples clearly separated from the method-validation evidence?
6. Does the suggested-reviewer mix cover the method, statistics, software, and biological reference-use-case scope without reducing the paper to RhoA/microglia biology?

## Decision pressure points

- Keep the cover letter focused on method object, validation ladder, software reproducibility, and calibrated scope.
- Do not claim that RhoDyn discovers biological states automatically or that every live-cell system contains a residence regime.
- Keep reviewer suggestions method-first and author-confirmed rather than inferred from repository history or citation overlap.
- Complete the official Reporting Summary, author declarations, portal metadata, and author approval before submission.

## Most useful final author actions

1. Confirm the author-side declarations and portal fields without inferring them from repository files.
2. Verify that GitHub and Zenodo review links resolve from a clean browser session.
3. Confirm reviewer suggestions, exclusions, and editor-fit wording from the reviewer/editor fit planner.
4. Use the package-bound cover-letter draft as the upload text, preserving the limitation language.
