# Stage 10.6 title and abstract route

## Preferred title

Residence-state inference for live-cell perturbation data

## Deck

RhoDyn formalizes dwell, coupling, reserve-like endpoint, and routed-output decisions against named baselines across public systems and held-out contexts.

## Abstract

Live-cell perturbation datasets are often interpreted through endpoints, peaks, amplitudes, thresholds, or generic time-series features, leaving unclear when time spent inside a biologically declared response regime changes the state assignment. We introduce RhoDyn, a residence-state inference method that represents trajectories and endpoint perturbation tables as explicit decision objects. RhoDyn compares dwell fraction, dwell time, segment count, and amplitude summaries, evaluates bounded reporter coupling under declared margins, constructs measurement-scoped reserve-like endpoint coordinates, tests routed-output alternatives against reduced architectures, and withholds calls when uncertainty or input structure is insufficient. In known-truth synthetic regimes, RhoDyn separates residence-positive, amplitude-sufficient, and ambiguous cases while named baseline families, including simple summaries, SciPy peak summaries, scikit-learn feature models, HMM state summaries, catch22-style, tsfresh-style, MiniROCKET-style, and ruptures-style comparators, define where simpler methods succeed. Public demonstrations span DRG calcium, GPCR-linked ERK, Cell Painting/MitoTox endpoints, and MLCI tracking, with sealed held-out contexts preserving positive, comparator-sufficient, and inconclusive decisions. RhoDyn is implemented across Python, command-line, API, workbench, and archived release surfaces with reproducible exports. The method therefore provides a reviewable route for deciding when residence, bounded coupling, reserve-like preservation, or routed-output structure changes interpretation relative to endpoint and amplitude summaries, without treating every declared window or fitted parameter as mechanism.

## Why this changes the first read

The Stage 9 title was accurate but still software-name first. The Stage 10.6 title is method-object first. It names residence-state inference and the live-cell perturbation data class directly, while the deck keeps RhoDyn visible as the implementation.
