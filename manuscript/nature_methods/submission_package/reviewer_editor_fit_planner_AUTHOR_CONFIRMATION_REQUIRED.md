# Reviewer and editor fit planner AUTHOR CONFIRMATION REQUIRED

This file is a collaborator-review aid for choosing reviewer suggestions, reviewer exclusions, and editor-facing fit language during Nature Methods upload. It does not nominate reviewers, infer conflicts, or add manuscript evidence. Author confirmation is required before any name, exclusion, or portal text is entered into the journal system.

## Purpose and boundary

RhoDyn should be evaluated as a computational method for live-cell perturbation data rather than as a software note or a single RhoA/microglia biology paper. Reviewer suggestions should therefore cover the method object, uncertainty logic, perturbation biology, software reproducibility, and biological reference-use-case scope. The RhoA/microglia reference use case should not dominate reviewer assignment.

## Expertise coverage needed

| Expertise area | Why it is needed | Package evidence | Suggested reviewer profile | Exclusion or conflict notes |
| --- | --- | --- | --- | --- |
| Live-cell signaling dynamics and reporter trajectories | The method compares residence, amplitude, dwell time, and segment behavior in live-cell traces. | Main text, Fig. 1-3, Supplementary Methods, trajectory schema, public calcium and ERK examples. | A reviewer experienced with live-cell reporters, signaling dynamics, or perturbation time courses. | Exclude only if the author team confirms a collaboration, competition, institutional conflict, or other journal-relevant conflict. |
| Computational methods and time-series state inference | RhoDyn is a decision workflow for declared residence states, amplitude comparators, uncertainty, and failure modes. | Methods, method specification, limitations matrix, synthetic truth cases, benchmark reports. | A quantitative reviewer who can assess time-series summaries, state definitions, uncertainty, and benchmark design. | Avoid reviewers who would evaluate only biological novelty without assessing the method definition. |
| Perturbation endpoint analysis and bounded-coupling decisions | Figures 4 and 5 extend the method beyond single-reporter trajectories into endpoint, reserve-like, and routed-output decisions. | Bounded-coupling Methods, source-data/statistics inventory, margin-sensitivity reports, endpoint demonstrations. | A reviewer familiar with perturbation biology, equivalence or bounded-effect reasoning, and endpoint-model comparison. | Do not suggest a reviewer who would require unreported wet-lab mechanisms for all effective parameters. |
| Bioimage, screening, or scientific-software reproducibility | The package includes figure-ready outputs, workbench routes, command-indexed reproduction, GitHub, Zenodo, and checksum surfaces. | Fig. 6, code-for-review file, software checklist, release checks, source-distribution and clean-room reports. | A reviewer who can judge reusable software, documented examples, release engineering, and reproducible scientific computing. | Exclude only with author-confirmed conflict, not because a reviewer may be technically demanding. |
| Statistical decision rules and uncertainty reporting | Passing, failing, and inconclusive calls are all part of the method claim. | Bounded-coupling decisions, interval summaries, ROPE-style fields where used, source-data/statistics inventory. | A reviewer who understands uncertainty, equivalence-margin logic, and the distinction between non-significance and equivalence. | Do not use reviewers whose likely critique depends on treating all non-significant contrasts as equivalence. |
| Biological reference-use-case expertise | The optional RhoA/microglia use case can test whether the method language remains biologically interpretable. | Reference-use-case wording, limitations, and controlled-access boundary statements. | A domain biologist may be useful after the method and software expertise are covered. | Domain expertise should not replace the quantitative and software-methods review mix. |

## Reviewer balance rule

Use a balanced reviewer set only after author confirmation. A strong set should include at least one live-cell signaling or perturbation-dynamics reviewer, one computational methods or time-series reviewer, and one software or reproducibility reviewer. Add a disease or cell-biology domain reviewer only if the method expertise is already represented.

## Suggested reviewer template

Complete one row per author-approved suggested reviewer.

| Field | Author-confirmed value |
| --- | --- |
| Reviewer name | [name] |
| Institution | [institution] |
| Email or ORCID if requested by portal | [email or ORCID] |
| Expertise match | [live-cell signaling, time-series methods, perturbation endpoints, reproducibility, statistics, or domain biology] |
| Why this reviewer can evaluate RhoDyn | [short evidence-based reason] |
| Conflict check | [author-confirmed no conflict, or do not suggest] |

## Exclusion template

Complete one row per author-approved exclusion.

| Field | Author-confirmed value |
| --- | --- |
| Excluded reviewer name | [name] |
| Institution | [institution] |
| Reason for exclusion | [collaboration, direct competition, conflict, confidentiality, or other journal-acceptable reason] |
| Scientific relevance of exclusion | [short reason if needed] |
| Author confirmation | [confirmed by author team] |

## Editor-facing fit note

Use this only as draft language for a portal note or cover-letter sentence if the journal provides a reviewer-fit field.

RhoDyn is best evaluated by reviewers spanning live-cell perturbation dynamics, computational method validation, statistical decision rules, and reproducible scientific software. The RhoA/microglia reference use case should not dominate reviewer assignment because the Article-level claim is the reusable residence-state inference method and its validation ladder across synthetic, public trajectory, endpoint, and software-reproducibility examples.

## Upload checks

- Confirm every suggested or excluded reviewer with all authors before upload.
- Do not infer conflicts from repository history, manuscript drafts, citation overlap, or personal assumptions.
- Do not suggest only RhoA, microglia, or Alzheimer's disease specialists unless the method-review expertise is already covered.
- Preserve the method claim during reviewer selection. RhoDyn is not submitted as a single-system biological discovery paper.
