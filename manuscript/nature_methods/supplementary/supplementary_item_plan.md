# Stage 9.7 supplementary display item plan

Generated UTC. 2026-07-02T12:27:22.270410Z

Supplementary-plan version. supplementary-plan@2026-07-02@523b7c69eefa95dc12986bb36f0e8b9b19e7752e

Stage. 9.7 supplementary display item planning.

Scope. This file plans supplementary figures and tables for a future Nature
Methods Article. It is not Supplementary Information prose, not figure legends,
not citation resolution, and not a submission package.

## Planning rule

Supplementary material should make the main method argument reproducible,
inspectable, and appropriately bounded. It should not carry central evidence
that belongs in the six main display items, and it should not become an
unstructured archive of every intermediate table.

It is not a data dump.

## Supplementary item map

| supp_id | display | linked_main_figure | role | callout_location | support_function |
| --- | --- | --- | --- | --- | --- |
| SUPP-001 | SFIG-001 / STBL-001 | FIG-001 | essential | PARA-RESULTS-001; PARA-METHODS-001 | Extends the method-object figure with tidy-input requirements, residence-window definitions, and positive, negative, and ambiguous truth-case examples. |
| SUPP-002 | SFIG-002 / STBL-002 | FIG-002 | essential | PARA-RESULTS-001; PARA-METHODS-001 | Keeps full synthetic benchmark tables visible while the main figure shows the compressed benchmark logic. |
| SUPP-003 | SFIG-003 / STBL-003 | FIG-003 | essential | PARA-RESULTS-002; PARA-METHODS-001 | Provides the public-data adapter details and window-sensitivity summaries behind the DRG calcium and ERK GPCR main panels. |
| SUPP-004 | SFIG-004 / STBL-004 | FIG-004 | essential | PARA-RESULTS-003; PARA-METHODS-002 | Shows the declared margins, interval decisions, and inconclusive bounded-coupling cases that are compressed in the endpoint main figure. |
| SUPP-005 | SFIG-005 / STBL-005 | FIG-004 | essential | PARA-RESULTS-004; PARA-METHODS-003 | Separates endpoint-level buffering coordinates from unmeasured biological reserve and exposes the uncertainty summaries. |
| SUPP-006 | SFIG-006 / STBL-006 | FIG-004 | essential | PARA-RESULTS-005; PARA-METHODS-004 | Provides the reduced alternatives and model-comparison diagnostics behind the routed-output main display item. |
| SUPP-007 | SFIG-007 / STBL-007 | FIG-005 | essential | PARA-RESULTS-003; PARA-DISCUSSION-002 | Keeps pass, inconclusive, margin-sensitivity, and controlled-access cases visible rather than hiding them behind a single validation score. |
| SUPP-008 | SFIG-008 / STBL-008 | FIG-006 | essential | PARA-RESULTS-006; PARA-METHODS-005 | Shows how Python, CLI, backend, exported bundles, source-distribution checks, and archive records preserve the same analysis choices. |
| SUPP-009 | SFIG-009 / STBL-009 | FIG-001 | supportive | PARA-DISCUSSION-001; PARA-DISCUSSION-002 | Collects failure modes, non-claims, and biological-scope limits so the main narrative can stay concise without hiding caveats. |

## Planned item details

### SUPP-001. Input contracts, method definitions, and executable truth cases

- Planned display. `SFIG-001` plus `STBL-001`.
- Linked main figure. `FIG-001`.
- Planned callout. `PARA-RESULTS-001; PARA-METHODS-001`.
- Source artifacts. `ART-0016;ART-0017;ART-0025;ART-0026`.
- Planned panels. A tidy trajectory and endpoint schemas; B residence-window metric definitions; C executable truth-case examples; D limitation and failure-mode matrix.
- Interpretation boundary. Supports method definition and counterexamples only. It does not add biological evidence.

### SUPP-002. Synthetic benchmark grid, baseline comparisons, and failure behavior

- Planned display. `SFIG-002` plus `STBL-002`.
- Linked main figure. `FIG-002`.
- Planned callout. `PARA-RESULTS-001; PARA-METHODS-001`.
- Source artifacts. `ART-0027;ART-0028;ART-0029;ART-0030;ART-0031`.
- Planned panels. A known-truth regime grid; B residence versus amplitude baseline comparison; C model-comparison table; D negative and ambiguous boundary cases.
- Interpretation boundary. Synthetic benchmarks validate decision behavior. They are not independent biological demonstrations.

### SUPP-003. Public live-cell signaling adapters and residence-amplitude sensitivity

- Planned display. `SFIG-003` plus `STBL-003`.
- Linked main figure. `FIG-003`.
- Planned callout. `PARA-RESULTS-002; PARA-METHODS-001`.
- Source artifacts. `ART-0032;ART-0033;ART-0034;ART-0035`.
- Planned panels. A public-data adapter contract; B DRG calcium residence-amplitude cases; C ERK GPCR residence-amplitude cases; D window and uncertainty sensitivity.
- Interpretation boundary. Demonstrates two public live-cell trajectory systems without claiming universal residence behavior across all reporters.

### SUPP-004. Bounded-coupling decisions under declared margins

- Planned display. `SFIG-004` plus `STBL-004`.
- Linked main figure. `FIG-004`.
- Planned callout. `PARA-RESULTS-003; PARA-METHODS-002`.
- Source artifacts. `ART-0036;ART-0037;ART-0040`.
- Planned panels. A endpoint pairing contract; B declared margin table; C bounded-coupling forest plot; D inconclusive decision examples.
- Interpretation boundary. Bounded coupling remains margin- and context-limited. It is not proof of no crosstalk.

### SUPP-005. Reserve-like endpoint construction and uncertainty

- Planned display. `SFIG-005` plus `STBL-005`.
- Linked main figure. `FIG-004`.
- Planned callout. `PARA-RESULTS-004; PARA-METHODS-003`.
- Source artifacts. `ART-0039;ART-0049;ART-0050`.
- Planned panels. A measured endpoint components; B reserve-like coordinate construction; C uncertainty summary; D label-scope table.
- Interpretation boundary. Reserve-like means scoped endpoint preservation. It is not a direct live metabolic reserve assay.

### SUPP-006. Routed-output reduced-architecture comparison

- Planned display. `SFIG-006` plus `STBL-006`.
- Linked main figure. `FIG-004`.
- Planned callout. `PARA-RESULTS-005; PARA-METHODS-004`.
- Source artifacts. `ART-0038;ART-0051`.
- Planned panels. A routed architecture matrix; B reduced-alternative comparison; C residual profile; D decision boundary table.
- Interpretation boundary. Effective model terms constrain the endpoint architecture but do not identify literal molecular edges.

### SUPP-007. Held-out validation pass and boundary cases

- Planned display. `SFIG-007` plus `STBL-007`.
- Linked main figure. `FIG-005`.
- Planned callout. `PARA-RESULTS-003; PARA-DISCUSSION-002`.
- Source artifacts. `ART-0041;ART-0042;ART-0043;ART-0044;ART-0048`.
- Planned panels. A fixed held-out plan; B pass contexts; C margin-boundary inconclusive contexts; D margin sensitivity; E access boundary.
- Interpretation boundary. Held-out validation supports scoped transfer of declared decisions, not a universal biological law.

### SUPP-008. Software parity, clean-room reproduction, and archive contents

- Planned display. `SFIG-008` plus `STBL-008`.
- Linked main figure. `FIG-006`.
- Planned callout. `PARA-RESULTS-006; PARA-METHODS-005`.
- Source artifacts. `ART-0010;ART-0021;ART-0022;ART-0023;ART-0024;ART-0045;ART-0046;ART-0047;ART-0052;ART-0053`.
- Planned panels. A cross-surface parity matrix; B export-bundle anatomy; C clean-room reproduction summary; D archive manifest and checksums; E usability-path boundary.
- Interpretation boundary. Supports reproducibility of retained evidence surfaces. It does not imply PyPI publication or private-data reproduction.

### SUPP-009. Interpretation boundaries and non-example cases

- Planned display. `SFIG-009` plus `STBL-009`.
- Linked main figure. `FIG-001`.
- Planned callout. `PARA-DISCUSSION-001; PARA-DISCUSSION-002`.
- Source artifacts. `ART-0017`.
- Planned panels. A non-example matrix; B ambiguous regime examples; C claim-strength caps; D recommended wording boundaries.
- Interpretation boundary. A limitation display supports interpretation discipline. It is not a new result.

## Main-text visibility rule

Every essential supplementary item has a planned Results or Methods callout.
Supportive items are retained only when they clarify interpretation boundaries
or reproducibility without becoming an uncited data store.

## Rendering boundary

No supplementary display item is rendered in Stage 9.7. The PanelForge manifest
records the planned supplementary items as non-rendered metadata so later
legend, table, and supplementary-methods substages can resolve callouts without
changing the main figure spine.
