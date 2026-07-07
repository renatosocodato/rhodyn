# Cover letter for submission AUTHOR CONFIRMATION REQUIRED

This draft is prepared for Nature Methods upload after author confirmation. It does not add data, analyses, citations, figures, datasets, performance claims, manuscript text, reviewer names, conflicts, declarations, or portal metadata. Before upload, the authors must confirm related-manuscript status, prior editor discussions, author approval, reviewer suggestions or exclusions if used, double-blind review choice, declarations, and the official Reporting Summary.

Dear Nature Methods editors,

We submit "RhoDyn infers residence states in live-cell perturbation data" as a computational methods Article for consideration in Nature Methods. Many live-cell signaling, imaging, perturbation, and screening studies collect trajectories but still make biological decisions from endpoints, peaks, thresholds, means, or generic time-series features. RhoDyn addresses this gap with a reusable method for asking when the time a cell spends inside a declared response regime changes interpretation relative to amplitude-based summaries.

The contribution is not the broad observation that cell signaling is dynamic, and it is not a claim that residence should replace trajectory inference, state-space analysis, or endpoint summaries in every setting. RhoDyn defines an inspectable decision workflow that combines declared residence windows, dwell fraction, dwell time, segment count, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, uncertainty summaries, and explicit failure modes. The method tells users when residence adds information beyond amplitude, when amplitude or endpoint summaries are sufficient, and when the supplied data should withhold a stronger interpretation.

The validation ladder is designed to avoid a single-case methods claim. The manuscript includes known-truth synthetic regimes, public DRG calcium trajectories, public ERK reporter trajectories, public-derived endpoint and paired-reporter demonstrations, held-out bounded-coupling contexts, margin-sensitivity checks, inconclusive examples, and parity across Python, command-line, backend, workbench, export-bundle, source-distribution, checksum, GitHub, and Zenodo surfaces. The RhoA/microglia material is treated as a reference use case rather than as hidden evidence for every method claim.

We believe the manuscript fits Nature Methods because it presents an Article-level computational method with immediate practical relevance for live-cell perturbation studies that now reduce trajectories to endpoints. A biologist can use RhoDyn to decide whether a tidy live-cell or endpoint perturbation table supports residence-state interpretation, amplitude-only interpretation, bounded coupling, reserve-like buffering, routed-output comparison, or a withheld conclusion. A quantitative reader can inspect the same decision through declared windows, margins, uncertainty summaries, versioned commands, reproducible exports, and source-linked examples.

The paper is deliberately scoped. Residence windows are declared analysis choices, not automatically discovered biological states. A bounded-coupling result means equivalence within a stated margin and context, not absence of all coupling. Reserve-like endpoint summaries remain tied to measured assays, and routed-output comparisons constrain tested alternatives without identifying direct biochemical edges. RhoDyn v0.1.0 is publicly available with GitHub and Zenodo release records, documented commands, public-derived example tables, tests, figure-ready outputs, and reviewable reproducibility surfaces.

[Author-confirmed related-manuscript, prior-editor-contact, dual-submission, double-blind-review, reviewer-suggestion, reviewer-exclusion, and declaration statements should be inserted here if required by the portal or journal instructions.]

Sincerely,

The authors
