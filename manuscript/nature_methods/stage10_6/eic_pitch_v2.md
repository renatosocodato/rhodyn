# Stage 10.6 EIC-facing pitch v2

## Cover-letter opening

We submit "Residence-state inference for live-cell perturbation data" as a computational methods Article describing RhoDyn, a decision method for asking when time spent inside a declared biological response regime changes interpretation relative to endpoint, amplitude, threshold, and generic time-series summaries. The advance is not that live-cell dynamics matter, and it is not software availability by itself. RhoDyn formalizes a residence-state decision object that combines declared windows, named baseline comparisons, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, uncertainty, and abstention in one reproducible analysis route.

## Presubmission pitch

RhoDyn is a residence-state inference method for live-cell perturbation biology. It addresses the common situation in which time-lapse or endpoint perturbation experiments are interpreted through endpoints, peaks, amplitudes, thresholds, or generic feature summaries even though time spent inside a biologically declared response regime may change the state assignment. The Stage 10 manuscript version leads with the method object, not the software interface: Figure 1 defines the residence-state decision grammar, Figure 2 benchmarks it against named baseline families, Figure 3 tests public biological breadth across four counted systems, Figure 4 extends the decision object to endpoint, bounded-coupling, reserve-like, and routed-output analyses, Figure 5 shows sealed held-out positive, comparator-sufficient, and inconclusive outcomes, and Figure 6 documents reproducible software surfaces. This ordering is intended to make clear that RhoDyn is not a wrapper around existing summaries. It is a reviewable method for deciding when residence-state structure changes interpretation and when it does not.

## Objection-control paragraph

The strongest anticipated objection is that RhoDyn could be read as useful software integration rather than a Nature Methods-level method. The Stage 10.6 pitch counters that objection by putting the decision object, named baselines, public biological breadth, and held-out validation before software maturity. It preserves the boundary that declared windows are analysis choices, bounded coupling is margin- and context-scoped, reserve-like outputs are endpoint-scoped, and routed-output parameters are not direct molecular edges.
