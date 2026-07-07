# Stage 9.29 closure and version binding

## Closure verdict

Stage 9 is closed for the current Nature Methods manuscript-assembly package. The package remains a methods-manuscript surface for RhoDyn v0.1.0 and does not add new biological datasets, new statistical results, new model outputs, new figure renders, or a journal-upload claim.

## Codex decision on PI-review action items

Codex closed `5` PI-review action items from existing manuscript evidence and retained `1` item as an external journal-submission action rather than a scientific blocker. The official Springer Nature Reporting Summary form, final author declarations, final portal metadata, and author upload approval remain outside repository-derived closure.

| item | decision | closure status | remaining requirement |
|---|---|---|---|
| PI-9.28-MAJ-001 | accept_auto_revision | closed | Final author review should preserve this narrower novelty framing. |
| PI-9.28-MAJ-002 | accept_auto_revision | closed | New datasets would be required for a stronger generality claim. |
| PI-9.28-MAJ-003 | accept_auto_revision | closed | Human review should verify the official Reporting Summary and supplementary tables retain these fields. |
| PI-9.28-MAJ-004 | retain_boundary_without_new_edit | closed | Maintain this wording during final author upload review. |
| PI-9.28-MAJ-005 | close_as_boundary_present | closed | Do not strengthen routed-output language without new mechanistic evidence. |
| PI-9.28-HUMAN-001 | retain_as_external_submission_action | not_blocking_stage9_closure | Complete the official Springer Nature form, author declarations, and portal metadata before journal submission. |

## Bound versions

- Method. `RhoDyn`.
- Software version. `v0.1.0`.
- Pyproject version. `0.1.0`.
- Repository. `https://github.com/renatosocodato/rhodyn`.
- Closure commit. `94dcc5093f4f00e30a2363cdd130f100ebe8cd56`.
- Software archive DOI. `10.5281/zenodo.21036616`.
- Software concept DOI. `10.5281/zenodo.21036615`.
- Evidence version. `stage7.8-methods-readiness@242f06c49e8310b81ac1c06a270bb6810f3f4cfc`.
- Claim-freeze version. `claim-freeze@2026-07-02@beacfd947561f89b2cde213ae1dab0dc13e6b1af`.
- Reference version. `reference-library@2026-07-07@62c2841691ce15ec6960440ea2faba7f60124e81`.
- Package version. `stage9.29-closure@94dcc5093f4f00e30a2363cdd130f100ebe8cd56`.
- PanelForge version. `v3.14.1` with DOI `10.5281/zenodo.20811171`.

## Figure and package state

PanelForge remains unchanged in this closure step. The package has `18` rendered figure files across `6` main figures and `pdf, png, svg` formats. All rendered figure inventory rows still point to existing files.

| package file | sha256 prefix | bytes |
|---|---:|---:|
| `manuscript/nature_methods/submission_package/main_text_for_submission.md` | `26d096530df0` | `36158` |
| `manuscript/nature_methods/submission_package/supplementary_information_for_submission.md` | `d5bf3eadafa0` | `11912` |
| `manuscript/nature_methods/submission_package/submission_manifest.md` | `29930ae1b9f8` | `2900` |
| `manuscript/nature_methods/submission_package/submission_readiness_checklist.md` | `1e62d79e7278` | `2870` |
| `manuscript/nature_methods/submission_package/editor_triage_note_for_cover_letter.md` | `9fc7e15e22fd` | `2079` |
| `manuscript/nature_methods/submission_package/editorial_pitch_for_submission.md` | `94fba2281dd6` | `4692` |
| `manuscript/nature_methods/submission_package/software_reporting_checklist.md` | `34d4d62ebbca` | `4048` |
| `manuscript/nature_methods/submission_package/article_fit_checklist.md` | `e98ff50a846f` | `2408` |
| `manuscript/nature_methods/submission_package/author_declarations_REQUIRED.md` | `93a5448c6ff8` | `2267` |
| `manuscript/nature_methods/submission_package/code_for_review.md` | `669b4108eea3` | `5472` |
| `manuscript/nature_methods/submission_package/package_consistency_audit.md` | `82eb5ac1fb00` | `2470` |
| `manuscript/nature_methods/submission_package/figure_file_inventory.csv` | `e5230d7be7fb` | `4121` |
| `manuscript/nature_methods/submission_package/source_data_and_statistics_inventory.csv` | `7cfc0ef56a00` | `6267` |
| `manuscript/nature_methods/submission_package/references_for_submission.bib` | `c37151ef73f2` | `6973` |
| `manuscript/nature_methods/submission_package/reporting_summary_REQUIRED.md` | `b83b8d2f639e` | `1448` |
| `manuscript/nature_methods/submission_package/submission_package_manifest.json` | `da4a0e182f49` | `6320` |
| `manuscript/nature_methods/submission_package/pi_review_packet.md` | `283a56dc3f67` | `7833` |
| `manuscript/nature_methods/submission_package/pi_review_action_matrix.csv` | `e3acfd583515` | `2203` |
| `manuscript/nature_methods/submission_package/pi_review_revision_log.md` | `c1a65bf119fb` | `1639` |
| `manuscript/nature_methods/submission_package/pi_review_literature_calibration.md` | `923d81a190b4` | `1534` |

## Scientific boundary

The closed package supports a methods claim that RhoDyn provides an inspectable workflow for residence-state inference, amplitude comparison, bounded-coupling decisions, reserve-like endpoint summaries, routed-output comparisons, uncertainty reporting, and reproducible export surfaces. It does not show that every live-cell system has a residence regime, that bounded coupling excludes slower or context-specific coupling, that reserve-like endpoints directly measure biological reserve capacity, or that routed-output parameters identify biochemical edges.

## Remaining human submission actions

1. Complete the official Springer Nature Reporting Summary form.
2. Confirm final author declarations, including competing interests, author contributions, funding and acknowledgements, ethics and materials, and AI-use disclosure if applicable.
3. Confirm final portal metadata, corresponding-author fields, ORCID fields, and journal-specific file names.
4. Perform final author approval of the main text, Supplementary Information, figures, and code-for-review surface before upload.
