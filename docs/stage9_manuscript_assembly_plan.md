# Stage 9 Nature Methods manuscript assembly plan

Stage 9 converts the completed Stage 7 methods-program evidence package into a Nature Methods-oriented manuscript package. This repository state serializes the entire Stage 9 v2.1 plan, completes the contract/schema scaffold, completes the Stage 9.0 evidence lock, registers official Nature Methods venue guidance in Stage 9.1, registers the representative methods-paper corpus in Stage 9.2, registers the Nature Methods Article narrative spine in Stage 9.3, and freezes the claim hierarchy in Stage 9.4. It does not begin paragraph-level planning, citation resolution, manuscript drafting, editorial polishing, PanelForge rendering, or package assembly.

## Project binding

- Method. RhoDyn.
- Method object. residence-aware interpretation of biological trajectories.
- Software. RhoDyn v0.1.0.
- Repository. https://github.com/renatosocodato/rhodyn.
- Software archive DOI. 10.5281/zenodo.21036616.
- Venue target. Nature Methods Article, verified against cached official guidance in Stage 9.1.

## Current non-execution boundary

Stage 9.-1 created the workspace, ID namespace, ledger schemas, gate convention, atomic-write protocol, substage registry, figure-engine binding, and execution memory. Stage 9.0 then locked the completed Stage 7.8 evidence package into `ledgers/stage9_evidence_manifest.csv`, `ledgers/stage9_evidence_lock.md`, `ledgers/stage7_output_contract.md`, and `gate_verdicts/9.0.json`. Stage 9.1 registers official Nature Methods, Nature Portfolio, and Springer Nature guidance in `refs/nature_methods_guidance_register.md`, `refs/_cache/`, `audits/venue_policy_constraints.md`, and `gate_verdicts/9.1.json`. Stage 9.2 registers the representative computational methods-paper corpus in `refs/representative_methods_papers.md`, `refs/_cache/methods_corpus/`, `audits/methods_paper_archetype_analysis.md`, and `gate_verdicts/9.2.json`. Stage 9.3 registers the Nature Methods Article narrative spine in `stage9_narrative_spine.md`, `audits/venue_fit_rationale.md`, and `gate_verdicts/9.3.json`. Stage 9.4 freezes the claim hierarchy and non-claims in `ledgers/claim_hierarchy.md`, `ledgers/claim_hierarchy.csv`, `ledgers/non_claims_and_scope_boundaries.md`, and `gate_verdicts/9.4.json`. The current state intentionally does not create `sections/results.md`, `sections/introduction.md`, `sections/discussion.md`, `sections/methods.md`, `refs/references.bib`, or submission-package files. It also does not clone PanelForge, create `.venv-panelforge`, validate a real figure manifest, or render panels.

## Patch ledger serialized from v2.1

| ID | Patch | Scaffold implication |
|---|---|---|
| P1 | Machine-checkable gates | Every substage emits a falsifiable gate verdict JSON. |
| P2 | Stable IDs and pinned ledger schemas | Claims, paragraphs, figures, artifacts, references, and statistics use immutable IDs. |
| P3 | Atomic idempotent writes | Substages stage, gate, promote, or quarantine without partially writing canonical outputs. |
| P4 | Citation anti-fabrication routing | References are resolved through the future reference-management route before manuscript use. |
| P5 | Numbers-are-live provenance | Reported statistics are recomputed from frozen artifacts before promotion. |
| P6 | Entry-gate ordering-loop fix | Stage 9.0 checks Stage 7 headline-result coverage before claim freeze. |
| P7 | Reader-surface hygiene | Publication-surface hygiene blocks internal scaffold leakage before package assembly. |
| P8 | Nature Methods venue corrections | Content type, Reporting Summary, code review, subheading, reference, and discovery-fit rules are pinned downstream. |
| P9 | Scope-fork resolution | Project-specific method nouns and venue choices live in the project binding block. |
| P10 | Figure-engine integration | PanelForge is version-bound for future deterministic figure rendering through Stage 9.6b. |

## Figure-engine binding

- Engine. panelforge-figures.
- Repository. https://github.com/renatosocodato/panelforge-figures.
- Pinned ref. v3.14.1.
- Version DOI. 10.5281/zenodo.20811171.
- Future clone path. `tools/panelforge-figures`.
- Future isolated environment. `.venv-panelforge`.
- Future manifest. `manuscript/nature_methods/figures/figures.manifest.yaml`.
- Scaffold status. `not_cloned_not_installed_not_rendered`.

## Serialized substages

| Substage | Title | Status | Objective |
|---|---|---|---|
| 9.-1 | Contract and schema layer | complete_scaffold_only | Make downstream gates machine-checkable and ledgers joinable before evidence intake. |
| 9.0 | Stage 7 evidence intake and lock | complete_evidence_locked | Confirm that manuscript assembly can begin from frozen, typed Stage 7 evidence. |
| 9.1 | Venue guidance source register | complete_guidance_registered | Bind manuscript process to official and cached Nature Methods guidance. |
| 9.2 | Representative methods-paper corpus | complete_methods_corpus_registered | Create a structural corpus of successful computational methods papers. |
| 9.3 | Archetype, content type, and narrative spine | complete_narrative_spine_registered | Pin paper type, content type, and venue-fit decision before drafting. |
| 9.4 | Manuscript claim freeze | complete_claim_freeze_registered | Freeze claim hierarchy with stable CLM IDs and strength caps. |
| 9.5 | Paragraph-level claim ledger | not_started | Plan manuscript paragraphs as auditable claim-bearing units. |
| 9.6 | Figure-first manuscript spine | not_started | Build the manuscript around evidence-bearing display items before prose. |
| 9.6b | Figure rendering via PanelForge | not_started | Prepare deterministic publication-grade figure rendering from the frozen figure-to-claim-to-artifact contract. |
| 9.7 | Supplementary display item plan | not_started | Plan supplementary material as cited support rather than a data dump. |
| 9.8 | Section contract blueprint | not_started | Define every manuscript section and venue structural rule before writing. |
| 9.9 | Title, subtitle, and abstract strategy | not_started | Create high-level framing without overselling. |
| 9.10 | Results subsection architecture | not_started | Break Results into evidence-locked drafting units. |
| 9.11 | Results drafting pass | not_started | Draft Results in figure-locked order. |
| 9.12 | Introduction literature binding | not_started | Draft citation-bound Introduction through resolved references. |
| 9.13 | Discussion interpretation map | not_started | Plan limitation-aware Discussion before drafting. |
| 9.14 | Discussion drafting pass | not_started | Draft balanced Discussion with no subheadings. |
| 9.15 | Methods architecture | not_started | Build Methods structure from repository implementation and Stage 7 artifacts. |
| 9.16 | Methods drafting pass | not_started | Draft reviewer-reconstructable Methods. |
| 9.17 | Software, data, and code availability assembly | not_started | Create precise availability statements and required Reporting Summary placeholder. |
| 9.18 | Supplementary Methods drafting | not_started | Move technical depth into structured Supplementary Methods. |
| 9.19 | Supplementary tables and source-data binding | not_started | Build supplementary tables as reviewable evidence objects. |
| 9.20 | Reference library and citation audit | not_started | Resolve and audit complete reference library. |
| 9.21 | Cross-document consistency audit | not_started | Check manuscript consistency by relational joins over keyed ledgers. |
| 9.22 | Statistical and quantitative language audit | not_started | Recompute reported numbers from frozen artifacts and diff manuscript text. |
| 9.23 | Figure legend and caption audit | not_started | Make display items self-contained and precise. |
| 9.24 | Editorial polish pass I | not_started | Improve scientific clarity without changing meaning. |
| 9.25 | Editorial polish pass II | not_started | Tune venue style and readability without broadening claims. |
| 9.25b | Reader-surface hygiene gate | not_started | Strip internal IDs and build-language from reader-facing surfaces before assembly. |
| 9.26 | Internal peer review simulation | not_started | Stress-test the manuscript with eight reviewer perspectives. |
| 9.27 | Submission package assembly | not_started | Assemble complete manuscript and submission package after hygiene gate. |
| 9.28 | Final human PI review packet | not_started | Prepare final human decision packet. |
| 9.29 | Roadmap closure and version binding | not_started | Close Stage 9 with package, evidence, release, and limitation versions bound. |

## Final deliverables at Stage 9 completion

1. Complete Nature Methods-aligned manuscript draft.
2. Complete Methods and Supplementary Information drafts.
3. Complete figure and table package plan with legends.
4. Data, code, and software availability statements.
5. Mandatory Reporting Summary registered for package assembly.
6. Resolved literature and citation ledger.
7. Claim-to-evidence, figure-to-artifact, methods-to-code, and statistic ledgers.
8. PanelForge manifest, rendered panels, pinned engine commit, and render report after Stage 9.6b executes.
9. Reproducibility command index.
10. Contract and schema layer with all gate verdict JSON files.
11. Cross-document consistency, statistical language, reader-surface hygiene, and internal peer-review reports.
12. PI review packet, submission-readiness checklist, Stage 9 completion report, and updated roadmap memory.

## Completion rule

Stage 9 must proceed substage by substage. A downstream substage may not promote outputs unless its `gate_verdicts/<substage>.json` reports `pass == true`. Polished prose, rendered figures, or package files may not substitute for missing evidence, failed predicates, unresolved identifiers, or an upstream scope problem.
