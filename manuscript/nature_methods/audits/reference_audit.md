<!-- REFERENCE-AUDIT stage=9.20 generated_utc=2026-07-04T09:33:26.476578Z reference_version=reference-library@2026-07-04@42be37d69bc6b0229aa611f260215454db4e3f12 -->

# Reference library and citation audit

Stage 9.20 resolves the current manuscript reference set as claim-linked sources. The audit binds each reference to a DOI, claim ID, paragraph route, support role, and retraction-check status. This is a citation-support surface only. It does not write figure legends, run cross-document consistency checks, or assemble a submission package.

## Summary

- Reference count. 13 of 50 typical Nature Methods Article references.
- DOI-resolved references. 13 of 13.
- Retraction-check clear or not applicable. 13 of 13.
- Source-type counts. dataset=3; methods=8; software=2.

## Citation support map

| ref | source type | claim IDs | paragraph routes | support role | DOI | status |
| --- | --- | --- | --- | --- | --- | --- |
| REF-0001 | methods | CLM-0001 | PARA-INTRO-001;PARA-DISCUSSION-001 | trajectory-inference benchmark context | 10.1038/s41587-019-0071-9 | true; clear |
| REF-0002 | methods | CLM-0001 | PARA-INTRO-001;PARA-DISCUSSION-001 | dynamical transient-state modeling context | 10.1038/s41587-020-0591-3 | true; clear |
| REF-0003 | methods | CLM-0001 | PARA-INTRO-001;PARA-DISCUSSION-001 | state-space visualization context | 10.1038/s41587-019-0336-3 | true; clear |
| REF-0004 | methods | CLM-0001 | PARA-INTRO-001;PARA-METHODS-001 | formal dynamic-state inference object context | 10.1038/s41592-021-01346-6 | true; clear |
| REF-0005 | methods | CLM-0002 | PARA-INTRO-002;PARA-DISCUSSION-002 | generalist software-method validation context | 10.1038/s41592-020-01018-x | true; clear |
| REF-0006 | methods | CLM-0002 | PARA-INTRO-002;PARA-DISCUSSION-002 | spatial-omics workbench and reproducibility context | 10.1038/s41592-021-01358-2 | true; clear |
| REF-0007 | methods | CLM-0002;CLM-0005 | PARA-INTRO-002;PARA-METHODS-005 | probabilistic software architecture and uncertainty context | 10.1038/s41587-021-01206-w | true; clear |
| REF-0008 | methods | CLM-0002;CLM-0005 | PARA-INTRO-002;PARA-DISCUSSION-002 | adoption-facing computational method context | 10.1038/s41593-018-0209-y | true; clear |
| REF-0009 | dataset | CLM-0001 | PARA-INTRO-001;PARA-METHODS-001;PARA-RESULTS-002 | public DRG calcium live-cell trajectory source | 10.5281/zenodo.14907827 | true; not_applicable_zenodo_record |
| REF-0010 | dataset | CLM-0001;CLM-0002 | PARA-INTRO-001;PARA-INTRO-002;PARA-METHODS-001;PARA-METHODS-002;PARA-RESULTS-002;PARA-RESULTS-003 | public ERK GPCR and paired ERK/Akt reporter source | 10.5281/zenodo.5836623 | true; not_applicable_zenodo_record |
| REF-0011 | dataset | CLM-0002;CLM-0003;CLM-0004 | PARA-INTRO-002;PARA-METHODS-003;PARA-METHODS-004;PARA-RESULTS-004;PARA-RESULTS-005 | public Cell Painting and MitoTox endpoint source | 10.5281/zenodo.10011861 | true; not_applicable_zenodo_record |
| REF-0012 | software | CLM-0005 | PARA-METHODS-005;PARA-RESULTS-006 | citable RhoDyn v0.1.0 software archive | 10.5281/zenodo.21036616 | true; not_applicable_zenodo_record |
| REF-0013 | software | CLM-0005 | PARA-METHODS-005;PARA-RESULTS-006 | citable figure-rendering software archive | 10.5281/zenodo.20811171 | true; not_applicable_zenodo_record |

## Gate checks

| check | status | detail |
| --- | --- | --- |
| stage_9_19_gate_passed | pass | Stage 9.19 supplementary table/source-data binding exists and passes |
| reference_set_complete_and_under_cap | pass | reference_count=13; cap=50; ref_ids=REF-0001;REF-0002;REF-0003;REF-0004;REF-0005;REF-0006;REF-0007;REF-0008;REF-0009;REF-0010;REF-0011;REF-0012;REF-0013 |
| references_resolve_with_doi | pass | All references have DOI-form identifiers and resolved DOI metadata |
| retraction_checks_clear_or_justified | pass | Crossref relation checks are clear for papers; Zenodo dataset/software records are marked not applicable |
| references_map_to_claims_and_paragraphs | pass | All citation rows resolve to frozen CLM IDs and paragraph routes; Stage 9.12 Introduction refs are included |
| software_and_dataset_records_included | pass | Public datasets, RhoDyn software DOI, and PanelForge software DOI are present |
| bibtex_contains_one_entry_per_reference | pass | BibTeX library contains exactly the expected REF keys |
| no_legend_consistency_or_package_started | pass | No figure legends, cross-document consistency audit, PI packet, or readiness checklist detected |
| scope_boundary_preserved | pass | Reference audit preserves citation-support scope without new biological claims |

## Scope boundary

The reference library supports the existing manuscript claims and availability statements. It does not add a new biological demonstration, does not change any model decision, and does not replace the later cross-document consistency audit.
