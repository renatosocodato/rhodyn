# Stage 9.3 narrative spine

Generated UTC. 2026-07-02T10:43:28.325609Z

Narrative-spine version. narrative-spine@2026-07-02@3d01c5f009828471aa9ed3268cb7ce1557ebafa4

Stage. 9.3 archetype, content type, and narrative spine.

Scope. This document pins the manuscript archetype and narrative route for a
future Nature Methods Article. It is not a Results draft, not an Introduction
draft, not a reference library, and not a figure plan.

## Content type decision

RhoDyn should be prepared as a Nature Methods Article. Stage 9.1 sourced the
Article budget and structure from official venue guidance, including an
unreferenced abstract budget, a main-text budget, up to six display items, a
Results section with topical subheadings, and a Discussion without subheadings.

## Method object decision

The manuscript should introduce RhoDyn as a computational method for
residence-state inference and dynamic operating-state interpretation in
live-cell perturbation biology. The method object is not a reproduction route
for the RhoA/microglia manuscript. The manuscript reference case can provide
biological depth only after the method and independent public evidence are
defined.

## Discovery-versus-demonstration decision

The manuscript should make a methods claim, not a new primary biological
discovery claim. The evidence supports RhoDyn as a way to detect and interpret
dynamic control regimes where dwell time, buffering, bounded coupling, or routed
outputs can change biological interpretation relative to simpler summaries.
Biological examples demonstrate method behavior and scope. They do not imply
that RhoDyn generated the original RhoA/microglia manuscript results.

## Narrative spine

| spine_step | role | evidence_source |
| --- | --- | --- |
| 1. Problem | Show why endpoint amplitude, threshold crossing, and static endpoint summaries miss dwell-time structure in live-cell perturbation data. | Stage 7.1 method definitions and Stage 7.2 synthetic truth benchmarks. |
| 2. Method object | Define RhoDyn as residence-state inference for dynamic operating-state analysis, with tidy trajectory and endpoint inputs. | Stage 7.1 formal specification and stable API notes. |
| 3. Benchmark contrast | Compare residence windows, dwell metrics, bounded coupling, reserve-like summaries, and routed-output alternatives against simpler summaries on shared inputs. | Stage 7.2 benchmark harness and Stage 7.4 endpoint/reserve/routing outputs. |
| 4. Biological breadth | Use independent public live-cell signaling systems and endpoint demonstrations to show when RhoDyn changes interpretation beyond amplitude-only summaries. | Stage 7.3 public signaling, Stage 7.4 endpoint/reserve/routing, and Stage 7.5 held-out validation. |
| 5. Software adoption | Make CLI, Python, backend, workbench, export bundles, documentation, versioning, and archive DOI part of the methods evidence. | Stage 6 public release and Stage 7.6 to Stage 7.8 reproducibility/adoption evidence. |
| 6. Boundary conditions | State when residence, reserve-like, bounded-coupling, or routed-output claims cannot be identified from the input data. | Stage 7 limitations matrix, benchmark failure behavior, and held-out inconclusive cases. |

## Drafting boundary

Stage 9.3 stops at the narrative-spine decision. Stage 9.4 must freeze the
claim hierarchy before any paragraph-level ledger, figure-first spine,
citation-resolution surface, manuscript section, PanelForge rendering, or
submission package can begin.
