# Stage 10.14 rendered-figure visual QA

Stage 10.14 records the visual failure mode of the Stage 10.13 PanelForge renders and creates a separate readable review-render package from the same Stage 10.5 crosswalk. The parent renders remain preserved for traceability.

## Status

`pass`

## Visual decision

- Parent Stage 10.13 renders. `failed_visual_review_recorded`
- Review renders. `pass`
- Review figures. `6`
- Review files. `18`
- Final production direction. `not_accepted_without_minimal_text_helvetica_render_pass`

## Outputs

- `case_studies/stage10_rendered_figure_visual_qc/stage10_14_parent_visual_defect_matrix.tsv`
- `case_studies/stage10_rendered_figure_visual_qc/stage10_14_review_render_visual_qc.tsv`
- `case_studies/stage10_rendered_figure_visual_qc/stage10_14_review_render_inventory.tsv`
- `case_studies/stage10_rendered_figure_visual_qc/stage10_14_review_render_contact_sheet.png`
- `case_studies/stage10_rendered_figure_visual_qc/stage10_14_visual_qc_report.md`
- `case_studies/stage10_rendered_figure_visual_qc/stage10_14_gate_report.json`
- `case_studies/stage10_rendered_figure_visual_qc/stage10_14_final_figure_direction_inspection.md`
- `case_studies/stage10_rendered_figure_visual_qc/stage10_14_final_figure_direction_checks.tsv`
- `docs/stage10_14_rendered_figure_visual_qc.md`
- `case_studies/stage10_rendered_figure_visual_qc/review_rendered`

## Boundary

This pass changes figure readability only. It does not add data, retune benchmarks, alter biological claims, replace the historical Stage 9 figures, or send editor contact.

The final-direction inspection accepts the review renders as a scaffold for figure logic and recipe diversity, but not as the final Nature Methods figure surface. Final figures still require minimalist in-panel text, pruned review annotations, Helvetica typography, vector-native PDFs, high-resolution companion PNGs, and collision-safe annotations.
