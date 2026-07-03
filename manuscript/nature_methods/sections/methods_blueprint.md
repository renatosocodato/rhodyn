<!-- METHODS-BLUEPRINT stage=9.15 generated_utc=2026-07-03T14:39:07.653833Z architecture_version=methods-architecture@2026-07-03@2a73afd1fa91d5ce13b30b8662717e4b77c8c987 -->

# Stage 9.15 Methods architecture

Generated UTC. 2026-07-03T14:39:07.653833Z

Architecture version. methods-architecture@2026-07-03@2a73afd1fa91d5ce13b30b8662717e4b77c8c987

Scope. This file defines the Online Methods architecture for the future Nature Methods Article. It is not Methods prose, not a full reference library, not figure legends, not a Reporting Summary, and not a submission package.

Software version. RhoDyn v0.1.0.

Default locked evidence dataset reference. dataset_version=stage7.8-methods-readiness@242f06c49e8310b81ac1c06a270bb6810f3f4cfc; dataset_date=2026-06-30. Public-source derived demonstrations override this default in the statement map when a Zenodo DOI-specific source is used.

## Methods architecture rule

Every future Methods subsection must name its input object, executable implementation, data or benchmark version, uncertainty or decision rule, and interpretation boundary before prose is drafted. The Methods draft must remain reconstructable from the methods-to-code ledger and from the locked Stage 7 evidence artifacts.

## Planned Online Methods order

1. Input schemas and preprocessing. Methods statement IDs. MTH-0001.
2. Residence windows and amplitude comparators. Methods statement IDs. MTH-0002; MTH-0003; MTH-0008.
3. Bounded-coupling and uncertainty decisions. Methods statement IDs. MTH-0004; MTH-0007.
4. Reserve-like endpoint construction. Methods statement IDs. MTH-0005.
5. Routed-output model comparison. Methods statement IDs. MTH-0006.
6. Software surfaces, versioning, and reproducibility. Methods statement IDs. MTH-0009.

## Methods statement map

| methods_stmt_id | future_methods_subheading | claim_ids | evidence_artifact | repository_implementation | dataset_reference | interpretation_boundary |
| --- | --- | --- | --- | --- | --- | --- |
| MTH-0001 | Input schemas and preprocessing | CLM-0001; CLM-0002; CLM-0003; CLM-0004 | ART-0016 | src/rhodyn/schema.py | RhoDyn schema definitions and Stage 7 method specification locked on 2026-06-30. | Input validation identifies malformed tables but cannot rescue missing biological grouping, time units, or merged trace identities. |
| MTH-0002 | Residence windows and amplitude comparators | CLM-0001 | ART-0029 | src/rhodyn/residence.py | Synthetic residence benchmark tables generated from Stage 7.2 truth and baseline cases on 2026-06-30. | Residence windows are declared analysis choices and do not by themselves identify a causal biological state. |
| MTH-0003 | Residence windows and amplitude comparators | CLM-0001 | ART-0032 | scripts/run_stage7_3_public_signaling.py | DRG calcium Zenodo 10.5281/zenodo.14907827 and ERK GPCR Zenodo 10.5281/zenodo.5836623, converted to derived trajectory tables on 2026-06-30. | Public examples test portability of the analysis object and do not establish a universal residence regime. |
| MTH-0004 | Bounded-coupling and uncertainty decisions | CLM-0002 | ART-0037 | src/rhodyn/coupling.py | ERK/Akt bounded-coupling rows derived from Wan 2021 public Zenodo 10.5281/zenodo.5836623 and Stage 7.4 outputs. | A passing bounded-coupling decision means equivalence inside the declared margin and context, not proof that all coupling is absent. |
| MTH-0005 | Reserve-like endpoint construction | CLM-0003 | ART-0039 | src/rhodyn/reserve.py | Cell Painting mitotoxicity endpoint rows retained as public-derived Stage 7.4 demonstration tables on 2026-06-30. | Reserve-like coordinates remain tied to the measured endpoint and are not direct assays of unmeasured biological reserve capacity. |
| MTH-0006 | Routed-output model comparison | CLM-0004 | ART-0038 | src/rhodyn/compare.py | Cell Painting routed-output comparison rows and reduced-alternative decisions retained from Stage 7.4. | Model comparison can reject reduced alternatives in the tested endpoint setting but does not identify direct biochemical interactions. |
| MTH-0007 | Bounded-coupling and uncertainty decisions | CLM-0002 | ART-0042 | scripts/run_stage7_5_heldout_validation.py | Held-out inhibitor contexts derived from Wan 2021 public Zenodo 10.5281/zenodo.5836623 on 2026-06-30. | Held-out pass and inconclusive contexts are both method outputs; margin-boundary cases cannot be promoted to equivalence. |
| MTH-0008 | Residence windows and amplitude comparators | CLM-0001 | ART-0025 | src/rhodyn/sim.py | Stage 7.1 synthetic truth cases and simulation utilities locked on 2026-06-30. | Stochastic timing summaries are not measured cell death, hazard, or injury unless the input endpoint directly supports that interpretation. |
| MTH-0009 | Software surfaces, versioning, and reproducibility | CLM-0005 | ART-0022 | src/rhodyn/backend_core.py | RhoDyn v0.1.0 source-distribution reproduction and export-surface parity checked through Stage 7.6 and Stage 7.7. | Software reproducibility supports inspection of demonstrated analyses, not a new biological result or private-data reproduction claim. |

## Drafting instructions

- MTH-0001. Describe accepted columns, optional replicate fields, and failure behavior before any analysis-specific method.
- MTH-0002. State the window definition, dwell metrics, amplitude comparators, and required sensitivity reporting.
- MTH-0003. Report public-source DOI, derived-table policy, grouping variables, declared windows, and uncertainty summaries.
- MTH-0004. Define margin, interval decision, TOST/ROPE threshold when used, grouping level, and inconclusive handling.
- MTH-0005. Use reserve-like language, define scaling bounds, and state the measured endpoint that anchors the coordinate.
- MTH-0006. Describe candidate alternatives, residual objective, ranking rule, and near-tie reporting.
- MTH-0007. State fixed thresholds, held-out contexts, bootstrap level, pass/inconclusive reporting, and controlled-access note policy.
- MTH-0008. Define first-passage, Gillespie, and tau-leap utilities as method support, with clear model-derived language.
- MTH-0009. Describe API, CLI, backend, workbench, export bundle, checksum, and version surfaces without claiming PyPI publication.

## Boundaries that must survive Methods drafting

- Residence windows are declared and sensitivity-tested analysis choices, not automatically discovered causal mechanisms.
- Bounded-coupling claims require declared margins, uncertainty support, and visible inconclusive cases, and do not exclude all slower or context-specific coupling.
- Reserve-like coordinates must remain scoped to measured endpoint behavior unless a direct reserve assay is supplied.
- Routed-output comparisons constrain reduced alternatives in tested endpoint demonstrations but do not identify direct biochemical interactions.
- Software reproducibility demonstrates inspectable reruns of retained Stage 7 evidence, not new biological evidence or private-data reproduction.
