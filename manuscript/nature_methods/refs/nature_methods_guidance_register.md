# Nature Methods guidance register

Generated UTC. 2026-07-02T10:09:14.214615Z

Stage. 9.1 venue guidance source register.

Scope. This file binds the RhoDyn Nature Methods manuscript process to official
Nature Methods, Nature Portfolio, and Springer Nature guidance available at the
listed URLs on the access date. It does not start literature lookup, reference
library construction, manuscript drafting, figure rendering, or submission
package assembly.

## Cached official sources

| source_id | title | url | accessed_utc | cache_file | sha256 | status |
| --- | --- | --- | --- | --- | --- | --- |
| NMETH-AIMS | Nature Methods aims and scope | https://www.nature.com/nmeth/aims | 2026-07-02T10:09:14.214615Z | manuscript/nature_methods/refs/_cache/nmeth_aims_scope.txt | 06746ff2ecfb1a5e | fetched |
| NMETH-CONTENT | Nature Methods content types | https://www.nature.com/nmeth/content | 2026-07-02T10:09:14.214615Z | manuscript/nature_methods/refs/_cache/nmeth_content_types.txt | 8357c6f52548c655 | fetched |
| NMETH-SUBMISSION | Nature Methods submission guidelines | https://www.nature.com/nmeth/submission-guidelines | 2026-07-02T10:09:14.214615Z | manuscript/nature_methods/refs/_cache/nmeth_submission_guidelines.txt | 434fd5341c5de194 | fetched |
| NMETH-EDITORIAL | Nature Methods editorial policies | https://www.nature.com/nmeth/editorial-policies | 2026-07-02T10:09:14.214615Z | manuscript/nature_methods/refs/_cache/nmeth_editorial_policies.txt | 7c22463ce069db3d | fetched |
| NPORT-REPORTING | Nature Portfolio reporting standards | https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards | 2026-07-02T10:09:14.214615Z | manuscript/nature_methods/refs/_cache/nature_portfolio_reporting_standards.txt | 5422b5048652dcdd | fetched |
| NATURE-INITIAL | Nature initial-submission format guidance | https://www.nature.com/nature/for-authors/initial-submission | 2026-07-02T10:09:14.214615Z | manuscript/nature_methods/refs/_cache/nature_initial_submission.txt | efdbeb227641b4b3 | fetched |
| SN-CODE | Springer Nature research-code policy | https://www.springernature.com/gp/open-science/code-policy | 2026-07-02T10:09:14.214615Z | manuscript/nature_methods/refs/_cache/springer_nature_code_policy.txt | 0b428dd025a86bc5 | fetched |

## Venue constraints for downstream Stage 9 work

| constraint_id | topic | requirement | source_id | stage9_implication |
| --- | --- | --- | --- | --- |
| VENUE-001 | Nature Methods Article fit | Article submissions should report a novel method or tool with full technical description and strong validation showing performance, reproducibility, broad applicability, and potential for discovering new biology. | NMETH-CONTENT | RhoDyn must be presented as a general computational method, with the RhoA/microglia use case framed as one biological demonstration rather than as the method's only source of value. |
| VENUE-002 | Aims and scope | Nature Methods prioritizes methodological advances for life-science research, including computational, statistical, machine-learning, analysis, modeling, and visualization methods. | NMETH-AIMS | The manuscript should emphasize the method object, executable workflow, benchmarking, uncertainty, and biological demonstrations, not a software marketing narrative. |
| VENUE-003 | Abstract budget | Article abstract up to 150 words and unreferenced. | NMETH-CONTENT | Stage 9.9 must draft a concise, unreferenced method abstract and block citation-heavy or result-list abstracts. |
| VENUE-004 | Main text budget | Article main text target is 3,000 words, with up to 5,000 words at editorial discretion, excluding abstract, Methods, references, and figure legends. | NMETH-CONTENT | Stage 9 section contracts must track word budgets and reserve extra length for method definition, benchmarks, and biological applications only where justified. |
| VENUE-005 | Display-item budget | Article display items are limited to up to six figures and/or tables. | NMETH-CONTENT | Stage 9.6 must keep the main display spine at six or fewer total main figures/tables and move technical detail into supplementary material. |
| VENUE-006 | Article section structure | Article structure is Introduction without heading, Results, Discussion, and Online Methods. Results and Methods can use topical subheadings, while Discussion has no subheadings. | NMETH-CONTENT | Stage 9.8 must block Discussion subheadings and preserve Results/Methods subheading logic. |
| VENUE-007 | Reference scope | Article references are typically recommended up to 50. | NMETH-CONTENT | Stage 9.20 must keep reference selection tight and citation-bearing claims explicit. |
| VENUE-008 | Supplementary information | Articles may be accompanied by supplementary information. | NMETH-CONTENT | Stage 9.7 and 9.18 should move technical derivations, extended benchmarks, and implementation checks to cited supplementary material rather than overloading the main text. |
| VENUE-009 | Reporting Summary | Life-science manuscripts require a Reporting Summary for editors and reviewers, with accepted summaries published alongside the paper. | NPORT-REPORTING | Stage 9.17 must include a Reporting Summary placeholder and route quantitative design details to the appropriate form. |
| VENUE-010 | Data availability | Data availability statements are required and must make the minimum dataset needed to interpret, verify, and extend the research transparent. | NPORT-REPORTING | Stage 9.17 must map every public and controlled input, derived table, benchmark output, and RhoA/microglia reference-use artifact to a clear availability statement. |
| VENUE-011 | Material, code, and protocol sharing | Materials, data, code, and associated protocols should be made promptly available, with restrictions disclosed to editors and in the manuscript. | NPORT-REPORTING | Stage 9.17 must distinguish open software, public examples, restricted or controlled-access data, and optional biological reference-case inputs. |
| VENUE-012 | Software submission checklist | Manuscripts with new code central to the paper require software details sufficient for peer-review evaluation. | NMETH-EDITORIAL | RhoDyn code, versioning, installation route, command index, tests, and example outputs must remain reviewable before submission package assembly. |
| VENUE-013 | Code availability statement | Original research articles containing new code necessary to interpret and replicate the conclusions require a Code Availability Statement. | SN-CODE | Stage 9.17 must include repository, release, archive DOI, license, and reproducibility details for RhoDyn. |
| VENUE-014 | Permanent code identifier | A GitHub link alone is not sufficient for code archiving. A permanent identifier such as a Zenodo DOI is recommended. | SN-CODE | The manuscript should cite the RhoDyn release archive DOI alongside the GitHub repository, not only a mutable repository URL. |
| VENUE-015 | Methods reproducibility | Methods should contain the elements necessary for interpretation and replication. | NATURE-INITIAL | Stage 9.15 and 9.16 must bind method definitions, assumptions, parameters, grouping rules, and execution commands to Stage 7 outputs. |
| VENUE-016 | Statistics reporting | Statistical reporting should name tests, one- or two-tailed design where relevant, error-bar definitions, and exact sample sizes. | NATURE-INITIAL | Stage 9.22 must diff every numeric claim against locked outputs and require exact n, uncertainty, and decision rules where reported. |
| VENUE-017 | Figure legends | Figure legends should remain concise, include a title sentence, describe the figure, and be understandable in isolation. | NATURE-INITIAL | Stage 9.23 must keep legends self-contained while preventing legends from becoming Methods or Results prose. |
| VENUE-018 | Initial submission hygiene | Initial submissions should be complete, readable, and aligned with editorial policies before review. | NMETH-SUBMISSION | Stage 9.27 cannot assemble the submission package until cross-document consistency, citation, statistical language, and reader-surface hygiene gates pass. |

## Article budget now bound for future stages

- Content type. Nature Methods Article.
- Abstract. Up to 150 words, unreferenced.
- Main text. 3,000 words, with up to 5,000 words at editorial discretion,
  excluding abstract, Methods, references, and figure legends.
- Display items. Up to six figures and/or tables.
- Structure. Introduction without heading, Results, Discussion, and Online
  Methods.
- Subheadings. Results and Methods can use topical subheadings. Discussion does
  not contain subheadings.
- References. Typically up to 50.
- Methods, data, code, software, statistics, figure legends, and Reporting
  Summary obligations are captured in the constraints table above.
