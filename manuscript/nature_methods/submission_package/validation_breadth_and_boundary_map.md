# Validation breadth and boundary map

This map is a collaborator-review aid for the Nature Methods validation argument. It does not add data, analyses, citations, figures, datasets, performance claims, or manuscript text. It condenses where the current package tests RhoDyn, what each validation layer can support, and what each layer must not be used to claim.

## Core editorial question

The relevant validation question is whether RhoDyn behaves as a reusable residence-state decision framework beyond one motivating biological example. The current package answers that question through a ladder of known-truth, public trajectory, endpoint, held-out, and software-reproducibility tests. The ladder supports portability of the method object and its decision boundaries. It does not claim that every biological system contains a residence regime.

## Validation ladder

| Layer | Package evidence | What it tests | Decision value | Boundary |
| --- | --- | --- | --- | --- |
| Known-truth synthetic regimes | Main Fig. 2, Supplementary Methods, Stage 7.2 benchmark outputs | Whether residence, amplitude, bounded-coupling, reserve-like, and routed-output decisions behave correctly when truth is known | Establishes that the declared decision rules can recover positive, negative, and ambiguous cases | Synthetic truth is method validation, not biological generality |
| Public live-cell trajectory examples | Main Fig. 3, public DRG calcium and ERK reporter examples, source-data/statistics inventory | Whether tidy public time-lapse reporter tables can be analyzed without private manuscript data | Shows that residence and amplitude summaries can separate or agree depending on the reporter and window | Public examples are portability tests, not proof that residence is always superior |
| Public-derived endpoint and paired-reporter demonstrations | Main Fig. 4, endpoint/reserve/routed-output case-study tables | Whether RhoDyn can handle non-trajectory endpoints, bounded coupling, reserve-like coordinates, and reduced alternatives | Extends the method beyond single-reporter trajectories | Reserve-like labels remain tied to measured endpoints and do not directly measure unobserved biological reserve |
| Held-out contexts and margin sensitivity | Main Fig. 5, held-out bounded-coupling decisions, margin-sensitivity outputs | Whether declared decisions remain inspectable when contexts, margins, or evidence strength change | Keeps pass, fail, and inconclusive outcomes visible | Held-out success is scoped transfer, not universal coupling or residence biology |
| Software and reproducibility parity | Main Fig. 6, code-for-review file, release checks, source distribution, workbench/backend parity, GitHub, Zenodo, checksums | Whether a reviewer can run the method, inspect parameters, and reproduce representative outputs | Makes the method reviewable as software and algorithm, not only as manuscript prose | Reproducibility surfaces support reviewability but do not create new biological evidence |
| RhoA/microglia reference use case | Optional reviewer-access reference-use-case surfaces and controlled-access boundary notes | Whether the method language remains biologically interpretable in a deep motivating application | Provides biological depth without carrying every method claim | The reference use case should not dominate validation breadth or reviewer assignment |

## What the validation ladder supports

- RhoDyn can report residence-supported, amplitude-sufficient, bounded-coupling, reserve-like, routed-output, and withheld decisions from declared inputs.
- The package tests the same method object across synthetic, public trajectory, public-derived endpoint, held-out, and software-reproducibility settings.
- The manuscript is strongest when the validation ladder is described as method portability plus decision-boundary behavior, not as a universal biological law.

## Claims to avoid during upload

- Do not say that RhoDyn discovers biological states automatically.
- Do not say that residence is always more informative than amplitude.
- Do not say that every live-cell reporter contains a residence regime.
- Do not say that bounded coupling proves absence of all coupling.
- Do not say that reserve-like endpoint summaries directly measure unobserved biological reserve.
- Do not let the RhoA/microglia reference use case replace the synthetic, public, endpoint, held-out, and software-validation evidence.

## Cover-letter use

If validation breadth is challenged, the safest response is that the manuscript tests decision behavior across known-truth regimes, public live-cell reporters, endpoint and paired-reporter demonstrations, held-out contexts, and software parity. The response should also state that RhoDyn deliberately returns amplitude-sufficient and inconclusive outcomes where the evidence does not support a residence-state interpretation.
