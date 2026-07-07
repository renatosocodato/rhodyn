# Current Nature Methods policy preflight

This preflight is a collaborator-review aid tied to official Nature Methods and Nature Portfolio guidance checked on 2026-07-07. It does not add evidence, citations, analyses, figures, datasets, performance claims, or manuscript text. It asks whether the current RhoDyn submission package makes the Article fit, reporting requirements, data/code availability, and algorithm/software review surfaces visible before upload.

## Official sources used

- Nature Methods content types. https://www.nature.com/nmeth/content
- Nature Portfolio reporting standards and availability of data, materials, code and protocols. https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards
- Nature Methods guidelines for algorithms and software. https://communities.springernature.com/posts/guidelines-for-algorithms-and-software-in-nature-methods

## Policy-to-package check

| Policy item | Official expectation being checked | Current package evidence | Preflight verdict | Remaining author action |
| --- | --- | --- | --- | --- |
| Article content type | An Article is a report describing a novel method or tool, with full technical description and strong validation for performance, reproducibility, general applicability, and potential for discovering new biology. | Title, Abstract, Results, Online Methods, six-figure spine, Supplementary Information, software checklist, and code-for-review surface frame RhoDyn as a residence-state inference method rather than as a single biology case. | aligned | Preserve Article framing during cover-letter and portal entry. |
| Article format | Abstract up to 150 words, main text target 3,000 words with editorial discretion to 5,000, up to 6 display items, unheaded Introduction, Results and Online Methods subheadings, no Discussion subheadings, and approximately 50 references. | `article_fit_checklist.md` records the 150-word Abstract, six display items, reference count, section order, Results and Methods subheadings, and unheaded Discussion. | aligned | Final uploaded files should preserve the same structure. |
| Reporting Summary | Life-science research submissions must include a completed Reporting Summary for editors and reviewers. | `reporting_summary_REQUIRED.md` and `reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md` are present and mapped to current evidence. | registered | Complete the official Springer Nature Reporting Summary form by author confirmation. |
| Data availability | The minimum dataset needed to interpret, verify, and extend the article should be transparent, preferably through repositories, and restrictions must be disclosed at submission and in the manuscript. | Main text availability statements, code-for-review surface, source-data/statistics inventory, public URL report, Zenodo records, and controlled reference-case wording are present. | aligned | Confirm final portal metadata and any controlled-access language. |
| Code and algorithm availability | Previously unreported custom code or algorithms central to the paper must be available to editors and reviewers; best practice is release through a DOI-minting repository with access and restrictions described. | Public GitHub, Zenodo software DOI, method specification, API/CLI docs, command index, source-distribution checks, software checklist, and code-for-review surface are present. | aligned | Verify release tag and reviewer-access links immediately before upload. |
| Algorithm or software description | Nature Methods software guidance expects usable source code, pseudocode, mathematical description, or compiled software where appropriate, with documentation and dependencies. | RhoDyn provides source code, mathematical Methods, API/CLI documentation, examples, backend/workbench parity, tests, and reproducibility commands. | aligned | Do not replace the method description with software-marketing language. |
| General applicability | Validation should demonstrate that the method travels beyond one narrow setting while retaining limits. | Synthetic truth cases, public calcium and ERK trajectories, public-derived endpoint/reserve/routed demonstrations, held-out bounded-coupling contexts, and inconclusive cases are visible in the package. | aligned | Do not claim universal residence regimes or automatic state discovery. |

Reporting Summary remains a human submission action. The answer bank can guide completion, but the official form requires author-confirmed transfer into the Springer Nature portal materials.

## Desk-rejection risk if this preflight drifts

The strongest risk is not the absence of a required surface, but loss of focus during final portal preparation. If the uploaded cover letter, Abstract, or author responses describe RhoDyn mainly as software packaging, as a universal residence detector, or as a hidden extension of the RhoA/microglia reference use case, the package becomes easier to triage away from Nature Methods. Keep the upload language tied to the Article-level method object, validation breadth, reproducibility surface, and explicit interpretation limits.
