# Stage 3 case-study evidence bank

This document binds the Stage 3 evidence bank to the original RhoDyn roadmap.
Its purpose is to keep the software method separate from the RhoA/microglia
manuscript while showing that the same residence-state logic can be exercised
on independent public data.

## Stage 3 role

Stage 3 is the generality gate. It asks whether RhoDyn can show useful
residence, bounded-coupling, reserve-like, or reduced-architecture behavior
outside the original manuscript setting. It is not a branding step and it is
not a claim that RhoDyn generated the manuscript results.

## Current case-study bank

| role | retained surface | biological system | narrow result |
| --- | --- | --- | --- |
| Synthetic primer | `examples/residence_reserve_workflow.py` and `examples/*.csv` | declared toy traces and endpoints | residence, reserve-like summaries, bounded coupling, uncertainty, sensitivity, and reduced-model comparison can be taught without private data |
| Manuscript reference case | `rhodyn paper-case-study` and `docs/paper_case_study_adapter.md` | RhoA/microglia release metadata | the paper remains an optional reference use case, not a dependency or output of RhoDyn |
| Public live-cell signaling A | `case_studies/drg_calcium_residence_amplitude_benchmark.csv` | DRG neuron calcium traces | maximum calcium amplitude and high-calcium residence separate in a public live-cell dataset |
| Public live-cell signaling B | `case_studies/erk_gpcr_residence_amplitude_benchmark.csv` | GPCR-stimulated ERK KTR dynamics | peak ERK signal and high-ERK residence separate in a second public signaling system |
| Public endpoint model comparison | `case_studies/cell_painting_mitotox_model_ranking.csv` | Cell Painting morphology and MitoTox endpoints | a routed compartment architecture fits the endpoint table better than reduced endpoint or morphology-only alternatives |
| Public bounded-coupling example | `case_studies/erk_gpcr_erk_akt_bounded_coupling.csv` | paired ERK and Akt KTR dynamics | one GPCR context satisfies the declared ERK/Akt residence-margin rule, while other contexts remain outside that bounded claim |

## Machine-checkable gate

Run the Stage 3 gate audit from the repository root.

```bash
python scripts/audit_stage3_case_study_bank.py \
  --write case_studies/stage3_case_study_bank_gate_report.json
```

The report checks the retained derived tables, public-source provenance, public
adapters, tutorial notebooks, and the manuscript-independence boundary. The
current gate is satisfied only when all of the following remain true.

- At least two public biological systems show amplitude-only and
  residence-only top-quartile cases.
- At least one public endpoint dataset supports model comparison among reduced
  architectures.
- At least one public case supports bounded-coupling or reserve-like logic.
- The public examples do not imply that RhoDyn produced the original
  RhoA/microglia manuscript analysis.

## Interpretation boundary

The Stage 3 public examples are software-methods evidence. They show that
RhoDyn can expose residence/amplitude separations, bounded-coupling decisions,
and reduced-architecture behavior in retained public tables. They do not prove
new mechanism in the source publications, do not replace the original analyses
from those studies, and do not make the RhoA/microglia manuscript a RhoDyn
output.

## Relationship to later stages

Stage 4 may expose these frozen operations through a backend only if backend
results remain identical to Python-library outputs. Stage 7 may add more public
systems for a Nature Methods campaign, but those expansions should be treated
as new method evidence rather than changes to the Stage 3 closure gate.
