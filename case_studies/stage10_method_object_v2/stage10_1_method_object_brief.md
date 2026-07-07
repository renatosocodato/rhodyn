# Stage 10.1 method-object v2 fixture brief

Stage 10.1 converts RhoDyn from a collection of compatible analysis components into an explicit decision object. The object reports when a declared residence window changes interpretation relative to a declared comparator, when bounded coupling is supported only within a margin, when reserve-like endpoints are buffered or fragile under their own measurement scale, and when routed-output alternatives are selected or withheld.

Status. `pass`.
Decision rows. `12`.

## Component calls

| component | required decision types represented |
| --- | --- |
| Trajectory residence versus comparator | residence-added, amplitude-sufficient, inconclusive |
| Bounded coupling | inside margin, exceeds margin, inconclusive |
| Reserve-like endpoint | buffered, fragile, inconclusive |
| Routed-output comparison | routed selected, reduced selected, inconclusive |

## Biological interpretation boundary

These fixtures demonstrate method behavior, not new biology. Decision divergence is a reporting object for comparing residence and baseline interpretations under declared rules. It is not a molecular mechanism, and it does not imply that every live-cell reporter contains a residence regime.
