# Interpretation guide

RhoDyn is designed for dynamic operating-state analysis. It helps ask whether
a live-cell or perturbation table is more informative when summarized by
residence time, amplitude, bounded coupling, reserve-like buffering, routed
outputs, or reduced-architecture compatibility.

## Residence is not amplitude

A trajectory can have a high peak but short dwell time inside a declared
window, or a moderate peak with long residence. RhoDyn reports both amplitude
and residence summaries so those cases are not collapsed. The user declares the
window and should test window sensitivity when the biological threshold is not
fixed in advance.

## Bounded coupling is not proof of zero effect

A bounded-coupling decision asks whether an interval sits inside a declared
biological margin. If the decision passes, the supported statement is narrow.
The contrast is bounded within that margin in the submitted context. The result
does not show that two pathways never communicate, that slower coupling is
absent, or that every molecular edge has been excluded.

## Reserve summaries are model-facing variables

Reserve-style coordinates map response traces to a bounded scale that can be
used beside signaling and endpoint summaries. A high reserve value means the
submitted response stayed closer to the declared buffered range. It should not
be described as a direct injury, death, or fate endpoint unless the input table
measures that endpoint directly.

## Reduced-architecture comparison is a constraint test

Endpoint model comparison ranks candidate architectures by compatibility with
observed endpoints. A better-ranked architecture narrows the set of plausible
explanations under the supplied rows and weights. It does not prove that each
fitted or effective parameter is a literal molecular interaction.

## Uncertainty depends on the declared unit

Bootstrap and permutation helpers can operate at observation or group level.
When a table contains cells nested within wells, donors, fields, plates, or
sequences, the group label should match the biological or experimental unit
that can be resampled or exchanged. This protects against turning repeated
measurements into independent biological replicates.

## Public examples and manuscript independence

The synthetic examples and public case studies teach the method. The
RhoA/microglia manuscript repository and Zenodo data package remain optional
reference inputs. RhoDyn did not generate that manuscript, and normal RhoDyn
use does not require manuscript-private data.

## Recommended reporting language

Use precise statements tied to the submitted table and parameters.

- Prefer "residence and amplitude separate under this declared window" over
  "the pathway is controlled by residence in all contexts."
- Prefer "the contrast is bounded inside the declared margin" over "there is
  no coupling."
- Prefer "the reserve-like coordinate decreases under this response scale" over
  "cells are injured" unless injury is directly measured.
- Prefer "this architecture better satisfies the endpoint constraints" over
  "this model proves the molecular mechanism."
