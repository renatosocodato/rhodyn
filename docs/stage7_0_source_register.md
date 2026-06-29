# Stage 7.0 source register

Stage 7.0 freezes the evidence source register for the future RhoDyn methods program. This is a planning artifact only. It records editorial guidance, representative methods papers, current RhoDyn state, candidate dataset classes, and the boundary that the RhoA/microglia manuscript remains a reference use case rather than the source of the software generality claim.

## Planning status

- Stage 7.0 status. Complete as a planning-freeze surface.
- Scientific implementation status. Not started.
- Software implementation status. Not started.
- Manuscript drafting status. Not started.
- Next authorized phase. Stage 7.1, formal method definition and assumption ledger, only after explicit authorization.

## Official and community guidance sources

| id | source | URL | signal extracted for RhoDyn |
| --- | --- | --- | --- |
| G1 | Nature Portfolio reporting standards and availability of data, materials, code and protocols | https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards | Strong methods work must make the minimum dataset, code, algorithms, protocols, and restrictions visible enough for readers, editors, and reviewers to verify and extend the claims. This directly supports a Stage 7 requirement for code/data availability, archived releases, analysis scripts, and clear limitations. |
| G2 | PLOS Computational Biology submission guidelines | https://journals.plos.org/ploscompbiol/s/submission-guidelines | Data and code supporting computational findings should be openly shared in repositories with persistent identifiers, licenses, documentation, and clear availability statements. This supports DOI-backed examples, public-data adapters, and public benchmark outputs. |
| G3 | JOSS review criteria | https://joss.readthedocs.io/en/latest/review_criteria.html | Sustainable scientific software needs a statement of need, installation instructions, usage examples, API documentation, tests or objective verification, releases, license, and contribution/support pathways. This defines a software-maturity floor, not the high-impact methods-paper ceiling. |
| G4 | Nature Portfolio code availability policy component | https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards | Custom code and algorithms central to claims should be available for peer review and ideally released through DOI-minting repositories. This supports a versioned RhoDyn release candidate for any future methods manuscript. |
| G5 | PLOS code reporting component | https://journals.plos.org/ploscompbiol/s/submission-guidelines | Author-generated code directly related to findings should be public without access restriction unless restrictions are justified. This supports public scripts, notebooks, and reproducible examples for Stage 7 demonstrations. |

## Representative methods papers

These papers are not templates to copy. They are reference examples for patterns that recur in strong computational methods publications.

| id | paper | URL | pattern relevant to RhoDyn |
| --- | --- | --- | --- |
| M1 | Cellpose. Stringer et al., Nature Methods 2021 | https://www.nature.com/articles/s41592-020-01018-x | Broad biological bottleneck, general method, diverse training and test images, benchmarking against specialist methods, GUI/web/software access, public dataset, and code availability. |
| M2 | Squidpy. Palla et al., Nature Methods 2022 | https://www.nature.com/articles/s41592-021-01358-2 | Scalable platform, multiple spatial-omics modalities, preprocessed datasets, package documentation, and reproducibility repository. |
| M3 | CellRank. Lange et al., Nature Methods 2022 | https://www.nature.com/articles/s41592-021-01346-6 | Formal inference object, biological demonstrations across systems, processed data availability, software, documentation, tutorials, examples, and reproducibility notebooks. |
| M4 | Trajectory inference benchmark. Saelens et al., Nature Biotechnology 2019 | https://www.nature.com/articles/s41587-019-0071-9 | Method benchmarking across many real and synthetic datasets, evaluation of accuracy, scalability, stability, usability, common output wrappers, and user-selection guidance. |
| M5 | scvi-tools. Gayoso et al., Nature Biotechnology 2022 | https://www.nature.com/articles/s41587-021-01206-w | Software platform framing, probabilistic model family, user and developer API surfaces, uncertainty-aware modeling, and community-oriented software architecture. |

## Current RhoDyn state snapshot

| surface | current evidence | Stage 7.0 interpretation |
| --- | --- | --- |
| Public release | `v0.1.0` GitHub release and Zenodo DOI are recorded in `docs/zenodo_publication_report.json` and `docs/public_release_integrity_report.json`. | RhoDyn has a citable software base, but Stage 7 evidence must be built on future method-specific release candidates. |
| Stage 3 evidence bank | `case_studies/stage3_case_study_bank_gate_report.json` passes. | Stage 3 is sufficient for the current gate, but Stage 7 needs broader and more formal demonstrations. |
| Stage 4 backend | `api/stage4/openapi.json`, `api/stage4/frontend_contract.json`, and `docs/stage4_closeout.md` exist. | Backend routes can support future evidence, but Stage 7 should not add routes until a subphase requires them. |
| Stage 5 workbench | `docs/stage5_closeout.md` records completion. | The workbench can support usability rehearsal later, but Stage 7.0 does not change the interface. |
| Stage 6 release checks | `scripts/check_release.py`, docs link scans, checksums, and public release reports pass. | The release posture is strong enough to start Stage 7 planning. |

## Candidate dataset classes

| class | biological stress test | preferred public data properties | Stage 7 role |
| --- | --- | --- | --- |
| Live-cell kinase reporter trajectories | Tests residence versus amplitude in signaling dynamics. | Single-cell ERK, Akt, Src, PKA, JNK, or MAPK reporter traces with time units, condition labels, and replicate structure. | Primary Stage 7.3 demonstration class. |
| NF-kB or transcription-factor nuclear translocation | Tests dwell-time and pulse-duration control outside kinase reporters. | Single-cell nuclear/cytoplasmic trajectories, perturbations, stimulation dose or ligand metadata, and cell/field/well grouping. | Independent live-cell signaling demonstration class. |
| Calcium or excitable-cell activity traces | Tests reserve-like or buffering logic and amplitude/residence divergence. | GCaMP or calcium-intensity time series with episode timing, perturbation context, and biological replicates. | Residence, reserve-like, and sensitivity demonstration class. |
| Paired live-cell reporters | Tests bounded coupling and context-dependent reporter relationships. | Same-cell paired reporters, synchronized time bases, condition labels, and replicate structure. | Stage 7.4 bounded-coupling class. |
| Perturbation endpoint phenotyping | Tests reduced-architecture comparison when only endpoint features are available. | Cell Painting, cytometry, morphology, or screening endpoint tables with perturbation labels and replicate structure. | Stage 7.4 routed-output and model-comparison class. |
| Reserve or stress-buffering readouts | Tests whether a buffer variable changes how stimulus drive maps to vulnerability. | Mitochondrial, calcium, viability, stress-response, or recovery trajectories with matched stimulation conditions. | Stage 7.4 reserve-like demonstration class. |
| Collaborator or held-out dataset | Tests whether the method works outside author-selected examples. | Reviewable access, predeclared analysis plan, clear grouping, and permission for controlled or public reporting. | Stage 7.5 external validation class. |
| RhoA/microglia reference case | Biological-depth reference only. | Existing manuscript-linked tables and release package metadata. | Reference use case, not a generality claim and not a Stage 7 independent demonstration by itself. |

## Source-register completion decision

The source register contains official guidance, representative methods papers, current RhoDyn state, candidate dataset classes, and the RhoA/microglia reference-use boundary. It is sufficient to close the Stage 7.0 source-register requirement.
