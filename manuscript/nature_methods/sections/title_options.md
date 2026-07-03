# Stage 9.9 title and subtitle strategy

Generated UTC. 2026-07-03T12:43:22.114689Z

Strategy version. front-matter-strategy@2026-07-03@dbb6de87afff360b62b8bb5f48ccee76422b0a8d

Stage. 9.9 title, subtitle, and abstract strategy.

Scope. This file records title, short-title, and deck/subtitle options for a
future Nature Methods Article. It is not a submission title decision, not
Results prose, not figure legend prose, not citation resolution, and not a
submission package.

## Framing rule

The title should name the general RhoDyn method or residence-state inference
object while keeping the RhoA/microglia manuscript as an optional reference use
case rather than the source of the method claim. It should not promise universal
residence behavior, automatic biological-window discovery, therapeutic utility,
or direct molecular-edge identification.

## Option map

| option_id | title | short_title | status | claim_ids |
| --- | --- | --- | --- | --- |
| TITLE-001 | RhoDyn infers residence states in live-cell perturbation data | RhoDyn residence-state inference | preferred working option | CLM-0001;CLM-0005 |
| TITLE-002 | Residence-state inference for dynamic control in live-cell perturbation data | Residence-state inference | strong alternate | CLM-0001;CLM-0002;CLM-0004 |
| TITLE-003 | RhoDyn detects dynamic operating states beyond endpoint and amplitude summaries | RhoDyn dynamic operating states | higher-impact alternate | CLM-0001;CLM-0002;CLM-0003;CLM-0004;CLM-0005 |
| TITLE-004 | Residence-aware analysis of live-cell perturbation responses | Residence-aware perturbation analysis | conservative alternate | CLM-0001;CLM-0005 |

## Option details

### TITLE-001. RhoDyn infers residence states in live-cell perturbation data

- Status. preferred working option.
- Short title. RhoDyn residence-state inference.
- Deck or subtitle strategy. A reproducible Python, CLI, backend, and workbench method for dwell-time, bounded-coupling, reserve-like, and routed-output analysis.
- Claim mapping. CLM-0001;CLM-0005.
- Why this option exists. Most concise method-name option. It foregrounds the software and the residence-state object without claiming universal discovery.
- Claim boundary. Does not imply that every dataset contains a residence regime.

### TITLE-002. Residence-state inference for dynamic control in live-cell perturbation data

- Status. strong alternate.
- Short title. Residence-state inference.
- Deck or subtitle strategy. RhoDyn compares dwell-time structure, amplitude summaries, bounded-coupling decisions, and routed-output alternatives.
- Claim mapping. CLM-0001;CLM-0002;CLM-0004.
- Why this option exists. Best venue-facing methods title if the paper should read as a general method before the software name.
- Claim boundary. Keeps RhoDyn in the deck rather than using a software-first title.

### TITLE-003. RhoDyn detects dynamic operating states beyond endpoint and amplitude summaries

- Status. higher-impact alternate.
- Short title. RhoDyn dynamic operating states.
- Deck or subtitle strategy. A residence-aware method for live-cell trajectories, bounded coupling, reserve-like endpoints, and routed-output comparisons.
- Claim mapping. CLM-0001;CLM-0002;CLM-0003;CLM-0004;CLM-0005.
- Why this option exists. Highest conceptual punch, but stronger wording requires careful abstract and Results phrasing.
- Claim boundary. Use only if Results keep inconclusive cases visible and avoid universal language.

### TITLE-004. Residence-aware analysis of live-cell perturbation responses

- Status. conservative alternate.
- Short title. Residence-aware perturbation analysis.
- Deck or subtitle strategy. RhoDyn links trajectory dwell metrics with endpoint, coupling, reserve-like, routed-output, and reproducibility evidence.
- Claim mapping. CLM-0001;CLM-0005.
- Why this option exists. Safest restrained option. It is broad and accurate, though less memorable than the RhoDyn-first option.
- Claim boundary. Avoids overclaiming but may undersell the software and benchmark breadth.

## Preferred working route

Use `TITLE-001` as the current working option because it is short, software
specific, and claim-bounded. Retain `TITLE-002` as the strongest non-software
first fallback if editorial feedback prefers a method-object title over a
software-name title.
