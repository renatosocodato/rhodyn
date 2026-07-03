# Stage 9.8 section contract blueprint

Generated UTC. 2026-07-03T11:04:21.630557Z

Section-contract version. section-contracts@2026-07-03@7bdbc4d0f43e92ada9f5367e673c08362e7e9c46

Stage. 9.8 section contract blueprint.

Scope. This file defines manuscript section contracts for a future Nature
Methods Article. It is not a title draft, not an abstract draft, not
Introduction prose, not Results prose, not Discussion prose, not Methods prose,
not a reference library, and not a submission package.

## Contract rule

Each section contract states the surface, venue rule, planned role, required
content, prohibited content, claim links, display-item links, supplementary
support, subheading rule, word-budget target, and downstream stage. The
contracts are planning objects only. They prevent premature drafting and make
the future manuscript structure checkable before scientific prose is written.

## Section map

| section_id | surface | downstream_stage | word_budget | subheading_rule | source_constraints |
| --- | --- | --- | --- | --- | --- |
| SEC-001 | Title and short title | 9.9 | deferred to Stage 9.9 | prohibited/none | VENUE-001; VENUE-002 |
| SEC-002 | Abstract | 9.9 | maximum 150 words; unreferenced | prohibited/none | VENUE-003 |
| SEC-003 | Introduction | 9.12 | main-text budget share; target 450-650 words before editorial compression | prohibited/none | VENUE-004; VENUE-006; VENUE-007 |
| SEC-004 | Results | 9.10 | main-text budget share; target 1,600-2,100 words before editorial compression | required | VENUE-004; VENUE-005; VENUE-006; VENUE-008 |
| SEC-005 | Discussion | 9.13 | main-text budget share; target 650-900 words before editorial compression | prohibited/none | VENUE-004; VENUE-006 |
| SEC-006 | Online Methods | 9.15 | Methods budget target up to 3,000 words unless technical detail requires supplement | required | VENUE-006; VENUE-015; VENUE-016 |
| SEC-007 | Data availability | 9.17 | availability statement; concise and complete | prohibited/none | VENUE-010; VENUE-011 |
| SEC-008 | Code availability | 9.17 | availability statement; concise and complete | prohibited/none | VENUE-012; VENUE-013; VENUE-014 |
| SEC-009 | Acknowledgements and funding | 9.27 | back matter | prohibited/none | VENUE-018 |
| SEC-010 | Author contributions | 9.27 | back matter | prohibited/none | VENUE-018 |
| SEC-011 | Competing interests | 9.27 | back matter | prohibited/none | VENUE-018 |
| SEC-012 | References | 9.20 | typically up to 50 references | prohibited/none | VENUE-007 |
| SEC-013 | Figure legends | 9.23 | legend-specific budget handled in Stage 9.23 | prohibited/none | VENUE-016; VENUE-017 |
| SEC-014 | Supplementary Information | 9.18 | SI depth handled after main section contracts | prohibited/none | VENUE-008; VENUE-015; VENUE-016 |
| SEC-015 | Reporting Summary and software checklist | 9.17 | submission support; handled outside main text | prohibited/none | VENUE-009; VENUE-012; VENUE-018 |

## Section contracts

### SEC-001. Title and short title

- Nature Methods rule. Front matter only; title strategy is deferred to Stage 9.9.
- Planned role. Name the general RhoDyn method without implying the software generated the RhoA/microglia manuscript.
- Required content. method name; general method object; no unresolved venue claim.
- Prohibited content. draft title options; citation claims; marketing language.
- Claim IDs. CLM-0001; CLM-0005.
- Main figure IDs. none.
- Supplementary item IDs. none.
- Topical subheadings. none.
- Word budget. deferred to Stage 9.9.
- Source constraints. VENUE-001; VENUE-002.
- Downstream drafting or assembly stage. 9.9.

### SEC-002. Abstract

- Nature Methods rule. Nature Methods Article abstract up to 150 words and unreferenced.
- Planned role. State the method object, validation breadth, and scoped biological utility without citation or result-list overload.
- Required content. RhoDyn method object; validation breadth; software availability boundary; no references.
- Prohibited content. citations; over-150-word abstract; claims beyond CLM strength caps.
- Claim IDs. CLM-0001; CLM-0002; CLM-0003; CLM-0004; CLM-0005.
- Main figure IDs. FIG-001; FIG-002; FIG-003; FIG-004; FIG-005; FIG-006.
- Supplementary item IDs. none.
- Topical subheadings. none.
- Word budget. maximum 150 words; unreferenced.
- Source constraints. VENUE-003.
- Downstream drafting or assembly stage. 9.9.

### SEC-003. Introduction

- Nature Methods rule. Introduction appears without a heading in the Article structure.
- Planned role. Establish why endpoint, amplitude, and generic time-series summaries miss residence-state decisions in live-cell perturbation biology.
- Required content. problem statement; method gap; RhoDyn premise; scope of public demonstrations.
- Prohibited content. topical subheadings; unresolved citations; RhoA paper as sole evidence.
- Claim IDs. CLM-0001; CLM-0002.
- Main figure IDs. none.
- Supplementary item IDs. none.
- Topical subheadings. none.
- Word budget. main-text budget share; target 450-650 words before editorial compression.
- Source constraints. VENUE-004; VENUE-006; VENUE-007.
- Downstream drafting or assembly stage. 9.12.

### SEC-004. Results

- Nature Methods rule. Results should be divided by topical subheadings.
- Planned role. Present the evidence-bearing display sequence in locked FIG-001 through FIG-006 order.
- Required content. topical subheadings; figure-locked order; claim IDs; visible inconclusive contexts.
- Prohibited content. narrative-only subsections; uncited supplementary-only central evidence; claims exceeding strength caps.
- Claim IDs. CLM-0001; CLM-0002; CLM-0003; CLM-0004; CLM-0005.
- Main figure IDs. FIG-001; FIG-002; FIG-003; FIG-004; FIG-005; FIG-006.
- Supplementary item IDs. SUPP-001; SUPP-002; SUPP-003; SUPP-004; SUPP-005; SUPP-006; SUPP-007; SUPP-008.
- Topical subheadings. Method object and executable truth cases; Residence-amplitude separation in public live-cell trajectories; Bounded coupling under declared margins; Reserve-like endpoint buffering; Routed-output architecture comparison; Held-out validation and software reproducibility.
- Word budget. main-text budget share; target 1,600-2,100 words before editorial compression.
- Source constraints. VENUE-004; VENUE-005; VENUE-006; VENUE-008.
- Downstream drafting or assembly stage. 9.10.

### SEC-005. Discussion

- Nature Methods rule. Discussion does not contain subheadings.
- Planned role. Synthesize method contribution, biological scope, non-claims, limitations, and future use without adding new evidence.
- Required content. main contribution; scope boundaries; biological interpretation limits; software maturity limits.
- Prohibited content. subheadings; new results; universal residence law; therapeutic claims.
- Claim IDs. CLM-0001; CLM-0005.
- Main figure IDs. FIG-001; FIG-006.
- Supplementary item IDs. SUPP-007; SUPP-009.
- Topical subheadings. none.
- Word budget. main-text budget share; target 650-900 words before editorial compression.
- Source constraints. VENUE-004; VENUE-006.
- Downstream drafting or assembly stage. 9.13.

### SEC-006. Online Methods

- Nature Methods rule. Methods should be divided by topical subheadings and contain details needed for interpretation and replication.
- Planned role. Make RhoDyn inputs, algorithms, uncertainty decisions, benchmarks, and software surfaces reconstructable.
- Required content. topical subheadings; input schemas; decision rules; uncertainty; software versioning.
- Prohibited content. unscoped biological mechanisms; hidden parameter choices; reader-facing internal IDs.
- Claim IDs. CLM-0001; CLM-0002; CLM-0003; CLM-0004; CLM-0005.
- Main figure IDs. FIG-001; FIG-002; FIG-003; FIG-004; FIG-005; FIG-006.
- Supplementary item IDs. SUPP-001; SUPP-002; SUPP-003; SUPP-004; SUPP-005; SUPP-006; SUPP-008.
- Topical subheadings. Input schemas and preprocessing; Residence windows and amplitude comparators; Bounded-coupling and uncertainty decisions; Reserve-like endpoint construction; Routed-output model comparison; Software surfaces, versioning, and reproducibility.
- Word budget. Methods budget target up to 3,000 words unless technical detail requires supplement.
- Source constraints. VENUE-006; VENUE-015; VENUE-016.
- Downstream drafting or assembly stage. 9.15.

### SEC-007. Data availability

- Nature Methods rule. Data availability statement is required for datasets needed to interpret, verify, and extend the research.
- Planned role. Separate public examples, controlled-access inputs, derived tables, and optional RhoA/microglia reference-use artifacts.
- Required content. public datasets; derived tables; controlled-access boundaries; archive links.
- Prohibited content. private data promises; local paths; unavailable raw-data claims.
- Claim IDs. CLM-0005.
- Main figure IDs. FIG-006.
- Supplementary item IDs. SUPP-008.
- Topical subheadings. none.
- Word budget. availability statement; concise and complete.
- Source constraints. VENUE-010; VENUE-011.
- Downstream drafting or assembly stage. 9.17.

### SEC-008. Code availability

- Nature Methods rule. Original code necessary to interpret and replicate conclusions requires a code availability statement and permanent identifier.
- Planned role. State repository, release version, Zenodo DOI, license, command index, and archive boundary.
- Required content. GitHub release; Zenodo DOI; license; version; reproducibility commands.
- Prohibited content. GitHub-only archive claim; PyPI publication claim; private-data reproduction claim.
- Claim IDs. CLM-0005.
- Main figure IDs. FIG-006.
- Supplementary item IDs. SUPP-008.
- Topical subheadings. none.
- Word budget. availability statement; concise and complete.
- Source constraints. VENUE-012; VENUE-013; VENUE-014.
- Downstream drafting or assembly stage. 9.17.

### SEC-009. Acknowledgements and funding

- Nature Methods rule. Back matter; no Stage 9.8 prose drafting.
- Planned role. Reserve a back-matter slot without inventing funding or contribution details.
- Required content. funding placeholder policy; human-authored confirmation requirement.
- Prohibited content. invented funders; unconfirmed contribution claims.
- Claim IDs. none.
- Main figure IDs. none.
- Supplementary item IDs. none.
- Topical subheadings. none.
- Word budget. back matter.
- Source constraints. VENUE-018.
- Downstream drafting or assembly stage. 9.27.

### SEC-010. Author contributions

- Nature Methods rule. Back matter; no Stage 9.8 prose drafting.
- Planned role. Reserve contribution taxonomy for later human-confirmed authorship input.
- Required content. author-role confirmation requirement.
- Prohibited content. invented author roles.
- Claim IDs. none.
- Main figure IDs. none.
- Supplementary item IDs. none.
- Topical subheadings. none.
- Word budget. back matter.
- Source constraints. VENUE-018.
- Downstream drafting or assembly stage. 9.27.

### SEC-011. Competing interests

- Nature Methods rule. Back matter; no Stage 9.8 prose drafting.
- Planned role. Reserve competing-interest statement for later human-confirmed input.
- Required content. competing-interest confirmation requirement.
- Prohibited content. invented declarations.
- Claim IDs. none.
- Main figure IDs. none.
- Supplementary item IDs. none.
- Topical subheadings. none.
- Word budget. back matter.
- Source constraints. VENUE-018.
- Downstream drafting or assembly stage. 9.27.

### SEC-012. References

- Nature Methods rule. Article references are typically recommended up to 50.
- Planned role. Reserve citation library scope for Stage 9.20 without creating references.bib now.
- Required content. resolved reference IDs; claim-linked citation support; methods-paper and venue-policy support.
- Prohibited content. unresolved citation placeholders; uncited bibliography padding; references.bib before Stage 9.20.
- Claim IDs. CLM-0001; CLM-0002; CLM-0003; CLM-0004; CLM-0005.
- Main figure IDs. none.
- Supplementary item IDs. none.
- Topical subheadings. none.
- Word budget. typically up to 50 references.
- Source constraints. VENUE-007.
- Downstream drafting or assembly stage. 9.20.

### SEC-013. Figure legends

- Nature Methods rule. Legends should begin with a brief title sentence and describe what is depicted.
- Planned role. Reserve concise legends for the six main figures and future supplementary displays.
- Required content. title sentence; what is depicted; sample-size/statistical definitions where reported.
- Prohibited content. Results prose; Methods overload; internal IDs in reader-facing legends.
- Claim IDs. CLM-0001; CLM-0002; CLM-0003; CLM-0004; CLM-0005.
- Main figure IDs. FIG-001; FIG-002; FIG-003; FIG-004; FIG-005; FIG-006.
- Supplementary item IDs. SUPP-001; SUPP-002; SUPP-003; SUPP-004; SUPP-005; SUPP-006; SUPP-007; SUPP-008; SUPP-009.
- Topical subheadings. none.
- Word budget. legend-specific budget handled in Stage 9.23.
- Source constraints. VENUE-016; VENUE-017.
- Downstream drafting or assembly stage. 9.23.

### SEC-014. Supplementary Information

- Nature Methods rule. Articles may be accompanied by supplementary information.
- Planned role. Bind supplementary items to cited support roles without replacing main evidence.
- Required content. planned SUPP items; methods depth; extended benchmark tables; interpretation boundaries.
- Prohibited content. uncited data dump; central evidence moved out of main figures; unrendered legend prose at Stage 9.8.
- Claim IDs. CLM-0001; CLM-0002; CLM-0003; CLM-0004; CLM-0005.
- Main figure IDs. FIG-001; FIG-002; FIG-003; FIG-004; FIG-005; FIG-006.
- Supplementary item IDs. SUPP-001; SUPP-002; SUPP-003; SUPP-004; SUPP-005; SUPP-006; SUPP-007; SUPP-008; SUPP-009.
- Topical subheadings. none.
- Word budget. SI depth handled after main section contracts.
- Source constraints. VENUE-008; VENUE-015; VENUE-016.
- Downstream drafting or assembly stage. 9.18.

### SEC-015. Reporting Summary and software checklist

- Nature Methods rule. Life-science manuscripts and new central code require reporting and software-review details.
- Planned role. Reserve submission-support forms without assembling the submission package now.
- Required content. Reporting Summary placeholder; software submission checklist; reviewable code details.
- Prohibited content. completed submission package; unchecked claims; unverified checklist assertions.
- Claim IDs. CLM-0005.
- Main figure IDs. FIG-006.
- Supplementary item IDs. SUPP-008.
- Topical subheadings. none.
- Word budget. submission support; handled outside main text.
- Source constraints. VENUE-009; VENUE-012; VENUE-018.
- Downstream drafting or assembly stage. 9.17.

## Venue-bound structure rules

- Abstract. Maximum 150 words and unreferenced.
- Introduction. No heading in the Nature Methods Article structure.
- Results. Topical subheadings are required.
- Discussion. Subheadings are prohibited.
- Online Methods. Topical subheadings are required and must support interpretation and replication.
- References. Citation resolution is deferred to Stage 9.20 and no `references.bib` is created here.
- Availability and reporting surfaces. Data, code, Reporting Summary, and software-checklist content is deferred to Stage 9.17.

## Non-drafting boundary

Stage 9.8 creates only this contract file and its gate verdict. It does not
create reader-facing manuscript prose or a reference bibliography.
