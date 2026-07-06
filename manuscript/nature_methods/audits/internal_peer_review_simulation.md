# Stage 9.26 internal peer-review simulation

Generated UTC. 2026-07-06T09:53:23Z

## Overall editorial read

The manuscript is ready to move from reader-surface hygiene into package assembly only with the action matrix kept visible. The central methods claim is coherent and appropriately scoped. RhoDyn is presented as a reviewable method for residence-state inference, bounded-coupling decisions, reserve-like endpoint summaries, routed-output comparisons, and cross-surface reproducibility. The review does not identify a fatal scientific blocker, but it preserves several scoped boundaries that must remain explicit through package assembly.

## PanelForge figure assembly status

- Engine. panelforge-figures 3.14.1 at pinned ref v3.14.1 and commit d8ab4c5d25be6243aa7209ad1ee6af144820c920.
- DOI. 10.5281/zenodo.20811171.
- Main figures rendered. 6 figures, 18 expected PDF/PNG/SVG files.
- Missing rendered files. none.
- Manifest present. True. Render report present. True.
- Legend and caption status. Stage 9.23 pass with 6 main legends, 9 supplementary figure captions, 9 supplementary table captions, and 19 statistic bindings.

Interpretation. The figure assembly lane is currently complete as deterministic publication mockups. It supports manuscript review and package assembly, but the rendered figures remain methods-paper display artifacts tied to the frozen evidence tables rather than new biological results.

## Reviewer perspectives

### 1. Nature Methods handling editor

Primary read. Reader-facing surfaces now state a methods Article scope and separate the RhoA/microglia reference use case from the software generality claim.

| Concern | Claim | Figure | Status | Resolution |
| --- | --- | --- | --- | --- |
| The manuscript must read as a general method Article rather than a companion biology paper. | CLM-0001 | FIG-001 | resolved | Reader-facing surfaces now state a methods Article scope and separate the RhoA/microglia reference use case from the software generality claim. |
| The main text must avoid implying that every biological system contains a residence regime. | CLM-0001 | FIG-003 | narrowed | The Introduction, Results, Discussion, and non-example supplement keep amplitude-sufficient and inconclusive cases visible. |

### 2. Computational methods reviewer

Primary read. Figure 1, Online Methods, and Supplementary Methods define tidy trajectory and endpoint schemas, residence windows, amplitude comparators, and invalid-input behavior.

| Concern | Claim | Figure | Status | Resolution |
| --- | --- | --- | --- | --- |
| The method object needs explicit inputs, outputs, assumptions, and failure modes. | CLM-0001 | FIG-001 | resolved | Figure 1, Online Methods, and Supplementary Methods define tidy trajectory and endpoint schemas, residence windows, amplitude comparators, and invalid-input behavior. |
| Reduced architectures could be overread as exhaustive mechanistic alternatives. | CLM-0004 | FIG-004 | narrowed | Results, Methods, and legends state that routed-output comparisons test endpoint architectures and do not identify direct biochemical interactions. |

### 3. Live-cell signaling reviewer

Primary read. The manuscript states that windows are declared analysis choices and pairs residence outputs with amplitude comparators and sensitivity summaries.

| Concern | Claim | Figure | Status | Resolution |
| --- | --- | --- | --- | --- |
| Residence windows could be mistaken for automatically discovered biological states. | CLM-0001 | FIG-002 | narrowed | The manuscript states that windows are declared analysis choices and pairs residence outputs with amplitude comparators and sensitivity summaries. |
| The public reporter demonstrations must remain independent tests of portability rather than proof of one shared signaling mechanism. | CLM-0001 | FIG-003 | resolved | The public DRG calcium and ERK GPCR examples are framed as independent reporter demonstrations with system-specific windows and uncertainty. |

### 4. Statistics and uncertainty reviewer

Primary read. Figure 4 and Methods require positive margins, interval support, and ROPE/TOST thresholds where available before promotion to bounded coupling.

| Concern | Claim | Figure | Status | Resolution |
| --- | --- | --- | --- | --- |
| Bounded-coupling claims require declared margins, uncertainty intervals, and visible inconclusive outcomes. | CLM-0002 | FIG-004 | resolved | Figure 4 and Methods require positive margins, interval support, and ROPE/TOST thresholds where available before promotion to bounded coupling. |
| Held-out validation must not become a single pass-rate claim. | CLM-0002 | FIG-005 | resolved | Figure 5 keeps pass, inconclusive, margin-sensitivity, and controlled-access contexts side by side. |

### 5. Endpoint perturbation reviewer

Primary read. The manuscript uses reserve-like endpoint coordinate language and states that these summaries remain tied to the measured assay.

| Concern | Claim | Figure | Status | Resolution |
| --- | --- | --- | --- | --- |
| Reserve-like language could imply direct measurement of unmeasured biological reserve capacity. | CLM-0003 | FIG-004 | narrowed | The manuscript uses reserve-like endpoint coordinate language and states that these summaries remain tied to the measured assay. |
| Endpoint analyses need a clear route for failures to distinguish alternatives. | CLM-0004 | FIG-004 | resolved | Reduced-alternative comparisons, residual summaries, and decision-boundary tables remain visible in the main and supplementary displays. |

### 6. Software reproducibility reviewer

Primary read. Cross-surface parity, export-bundle contents, clean-room reproduction, checksums, and citable software DOI are all surfaced in Figure 6 and availability text.

| Concern | Claim | Figure | Status | Resolution |
| --- | --- | --- | --- | --- |
| Readers must be able to verify that Python, command-line, backend, and workbench surfaces agree. | CLM-0005 | FIG-006 | resolved | Cross-surface parity, export-bundle contents, clean-room reproduction, checksums, and citable software DOI are all surfaced in Figure 6 and availability text. |
| The manuscript must not imply package-index distribution or private-data redistribution that has not occurred. | CLM-0005 | FIG-006 | narrowed | Discussion and Methods state that PyPI-style distribution and controlled-access inputs remain bounded, while the Zenodo/GitHub release is citable. |

### 7. Figure and data-visualization reviewer

Primary read. Stage 9.6b rendered six main figures in PDF, PNG, and SVG; Stage 9.23 resolved legends and captions; Stage 9.25b removed reader-facing lineage wording.

| Concern | Claim | Figure | Status | Resolution |
| --- | --- | --- | --- | --- |
| The six-figure spine must be rendered and captioned without leaking figure-engine or lineage language into reader-facing captions. | CLM-0005 | FIG-006 | resolved | Stage 9.6b rendered six main figures in PDF, PNG, and SVG; Stage 9.23 resolved legends and captions; Stage 9.25b removed reader-facing lineage wording. |
| The archive-count statistic in Figure 6 must match the current release archive manifest. | CLM-0005 | FIG-006 | resolved | The live-number audit refreshed STAT-0018 to the current 632-row release archive manifest and propagated the count to Figure 6. |

### 8. Adoption and usability reviewer

Primary read. The Results and Figure 6 route user-facing workbench paths, CLI/API parity, and export bundles to the same inspectable outputs.

| Concern | Claim | Figure | Status | Resolution |
| --- | --- | --- | --- | --- |
| The workbench and reports need to serve both biologist-facing and quantitative users. | CLM-0005 | FIG-006 | resolved | The Results and Figure 6 route user-facing workbench paths, CLI/API parity, and export bundles to the same inspectable outputs. |
| Submission assembly should not begin before review concerns are visible to the author. | CLM-0005 | FIG-006 | routed_upstream | The action matrix routes remaining human judgment to Stage 9.27 package assembly and Stage 9.28 PI review rather than silently treating this simulation as acceptance. |

## Blocking concern routing

No fatal scientific blocker is left without a resolution status. The retained caution is interpretive, not evidentiary. Residence windows remain declared rather than discovered automatically, bounded coupling remains margin- and context-limited, reserve-like summaries remain tied to measured endpoints, routed-output comparisons remain effective model tests rather than molecular wiring, and software reproducibility remains scoped to the retained evidence set.

## Recommendation before package assembly

Proceed to Stage 9.27 package assembly with the action matrix attached. During assembly, preserve the current claim boundaries, keep the PanelForge figure status tied to the Stage 9.6b render report, and do not convert this internal review into a claim of external peer-review acceptance.
