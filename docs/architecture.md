# RhoDyn architecture

RhoDyn separates reusable dynamic-state analysis from manuscript-specific
biological interpretation.

## Core layers

1. `rhodyn.schema`
   Validates tidy trajectory and endpoint tables.

2. `rhodyn.residence`
   Scores signal dwell time inside a declared window and compares residence
   summaries with amplitude summaries.

3. `rhodyn.reserve`
   Provides normalization helpers for reserve-like buffering readouts.

4. `rhodyn.coupling`
   Encodes bounded-coupling decisions from confidence intervals or posterior
   samples supplied by the user. It also provides one-sample and Welch
   two-sample TOST helpers from raw arrays, with optional SciPy-backed
   t-distribution calculations under `rhodyn[stats]` and a dependency-free
   normal approximation for lightweight use. A passing decision means
   equivalence inside the declared biological margin, not proof that the
   underlying coupling is exactly zero.

5. `rhodyn.models`
   Simulates a minimal residence-gated controller.

6. `rhodyn.sim`
   Provides stochastic timing helpers, including first-passage and simple
   Gillespie/tau-leap routines.

7. `rhodyn.compare`
   Compares reduced controller predictions against endpoint constraints.

8. `rhodyn.results`
   Wraps residence, reserve, coupling, uncertainty, sensitivity, and
   model-comparison outputs in typed, JSON-friendly result objects. Each result
   carries grouping metadata and provenance fields so condition, cell, replicate,
   well, donor, batch, input schema, analysis parameters, and software version
   remain visible beside the quantitative value.

9. `rhodyn.paper`
   Documents the manuscript repository and Zenodo data package as an optional
   case study without making them package dependencies.

## What stays outside the core

- raw microscopy reading;
- image segmentation;
- manuscript figure composition;
- disease-specific claims;
- private data adapters;
- dashboard or hosted analysis.
