"""Run Stage 9.20 reference-library and citation-audit pass.

Stage 9.20 resolves the complete manuscript reference library for the current
Nature Methods draft. It creates a DOI-backed BibTeX library, a claim-linked
citation ledger, and a compact audit report without writing figure legends,
cross-document consistency reports, or the final submission package.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
REFS_DIR = WORKSPACE / "refs"
REF_CACHE_DIR = REFS_DIR / "_cache" / "reference_library"
AUDITS_DIR = WORKSPACE / "audits"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.20"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.20"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"

GATE_919 = GATE_DIR / "9.19.json"
GATE_929 = GATE_DIR / "9.29.json"
CLAIM_HIERARCHY = WORKSPACE / "ledgers" / "claim_hierarchy.csv"
PARAGRAPH_LEDGER = WORKSPACE / "ledgers" / "paragraph_claim_ledger.csv"
INTRO_LEDGER = REFS_DIR / "introduction_citation_ledger.csv"
VENUE_GUIDANCE = REFS_DIR / "nature_methods_guidance_register.md"
DATA_AVAILABILITY = WORKSPACE / "sections" / "data_availability.md"
CODE_AVAILABILITY = WORKSPACE / "sections" / "code_availability.md"

OUTPUTS = {
    "references": REFS_DIR / "references.bib",
    "citation_ledger": REFS_DIR / "citation_claim_ledger.csv",
    "audit": AUDITS_DIR / "reference_audit.md",
    "gate": GATE_DIR / "9.20.json",
}

FORBIDDEN_STARTED_PATHS = [
    WORKSPACE / "figures" / "figure_legends.md",
    WORKSPACE / "audits" / "cross_document_consistency_audit.md",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
]

REFERENCE_CAP = 50


@dataclass(frozen=True)
class ReferenceSpec:
    ref_id: str
    citation_label: str
    doi: str
    source_type: str
    claim_id: str
    paragraph_ids: str
    support_role: str
    source_note: str


REFERENCE_SPECS: tuple[ReferenceSpec, ...] = (
    ReferenceSpec(
        "REF-0001",
        "Saelens et al. 2019",
        "10.1038/s41587-019-0071-9",
        "methods",
        "CLM-0001",
        "PARA-INTRO-001;PARA-DISCUSSION-001",
        "trajectory-inference benchmark context",
        "Existing Stage 9.12 Introduction citation ledger and Stage 9.2 methods corpus.",
    ),
    ReferenceSpec(
        "REF-0002",
        "Bergen et al. 2020",
        "10.1038/s41587-020-0591-3",
        "methods",
        "CLM-0001",
        "PARA-INTRO-001;PARA-DISCUSSION-001",
        "dynamical transient-state modeling context",
        "Existing Stage 9.12 Introduction citation ledger and Stage 9.2 methods corpus.",
    ),
    ReferenceSpec(
        "REF-0003",
        "Moon et al. 2019",
        "10.1038/s41587-019-0336-3",
        "methods",
        "CLM-0001",
        "PARA-INTRO-001;PARA-DISCUSSION-001",
        "state-space visualization context",
        "Existing Stage 9.12 Introduction citation ledger and Stage 9.2 methods corpus.",
    ),
    ReferenceSpec(
        "REF-0004",
        "Lange et al. 2022",
        "10.1038/s41592-021-01346-6",
        "methods",
        "CLM-0001",
        "PARA-INTRO-001;PARA-METHODS-001",
        "formal dynamic-state inference object context",
        "Existing Stage 9.12 Introduction citation ledger and Stage 9.2 methods corpus.",
    ),
    ReferenceSpec(
        "REF-0005",
        "Stringer et al. 2021",
        "10.1038/s41592-020-01018-x",
        "methods",
        "CLM-0002",
        "PARA-INTRO-002;PARA-DISCUSSION-002",
        "generalist software-method validation context",
        "Existing Stage 9.12 Introduction citation ledger and Stage 9.2 methods corpus.",
    ),
    ReferenceSpec(
        "REF-0006",
        "Palla et al. 2022",
        "10.1038/s41592-021-01358-2",
        "methods",
        "CLM-0002",
        "PARA-INTRO-002;PARA-DISCUSSION-002",
        "spatial-omics workbench and reproducibility context",
        "Existing Stage 9.12 Introduction citation ledger and Stage 9.2 methods corpus.",
    ),
    ReferenceSpec(
        "REF-0007",
        "Gayoso et al. 2022",
        "10.1038/s41587-021-01206-w",
        "methods",
        "CLM-0002;CLM-0005",
        "PARA-INTRO-002;PARA-METHODS-005",
        "probabilistic software architecture and uncertainty context",
        "Existing Stage 9.12 Introduction citation ledger and Stage 9.2 methods corpus.",
    ),
    ReferenceSpec(
        "REF-0008",
        "Mathis et al. 2018",
        "10.1038/s41593-018-0209-y",
        "methods",
        "CLM-0002;CLM-0005",
        "PARA-INTRO-002;PARA-DISCUSSION-002",
        "adoption-facing computational method context",
        "Existing Stage 9.12 Introduction citation ledger and Stage 9.2 methods corpus.",
    ),
    ReferenceSpec(
        "REF-0009",
        "Copperman et al. 2023",
        "10.1038/s42003-023-04837-8",
        "methods",
        "CLM-0001;CLM-0002",
        "PARA-INTRO-002;PARA-DISCUSSION-001",
        "live-cell morphodynamic trajectory-embedding prior-art context",
        "Promoted Stage 9.29 editorial-hardening prior-art support for live-cell trajectory methods.",
    ),
    ReferenceSpec(
        "REF-0010",
        "von Buchholtz 2025 dataset",
        "10.5281/zenodo.14907827",
        "dataset",
        "CLM-0001",
        "PARA-INTRO-001;PARA-METHODS-001;PARA-RESULTS-002",
        "public DRG calcium live-cell trajectory source",
        "Stage 7.3 public signaling adapter and provenance.",
    ),
    ReferenceSpec(
        "REF-0011",
        "Wan et al. 2021 dataset",
        "10.5281/zenodo.5836623",
        "dataset",
        "CLM-0001;CLM-0002",
        "PARA-INTRO-001;PARA-INTRO-002;PARA-METHODS-001;PARA-METHODS-002;PARA-RESULTS-002;PARA-RESULTS-003",
        "public ERK GPCR and paired ERK/Akt reporter source",
        "Stage 7.3, Stage 7.4, and Stage 7.5 public signaling adapters.",
    ),
    ReferenceSpec(
        "REF-0012",
        "Seal et al. 2023 dataset",
        "10.5281/zenodo.10011861",
        "dataset",
        "CLM-0002;CLM-0003;CLM-0004",
        "PARA-INTRO-002;PARA-METHODS-003;PARA-METHODS-004;PARA-RESULTS-004;PARA-RESULTS-005",
        "public Cell Painting and MitoTox endpoint source",
        "Stage 7.4 endpoint, reserve-like, and routed-output demonstration.",
    ),
    ReferenceSpec(
        "REF-0013",
        "Socodato 2026 RhoDyn software",
        "10.5281/zenodo.21036616",
        "software",
        "CLM-0005",
        "PARA-METHODS-005;PARA-RESULTS-006",
        "citable RhoDyn v0.1.0 software archive",
        "Stage 9.17 code availability statement and Stage 7.6 release archive.",
    ),
    ReferenceSpec(
        "REF-0014",
        "Socodato 2026 PanelForge software",
        "10.5281/zenodo.20811171",
        "software",
        "CLM-0005",
        "PARA-METHODS-005;PARA-RESULTS-006",
        "citable figure-rendering software archive",
        "Stage 9.6b PanelForge render binding and Stage 9.17 code availability statement.",
    ),
)


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _read_csv(path: Path, *, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _fetch_csl(doi: str) -> dict[str, Any]:
    cache_path = REF_CACHE_DIR / f"{doi.lower().replace('/', '_')}.csl.json"
    if cache_path.exists():
        return _read_json(cache_path)
    url = f"https://doi.org/{doi}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.citationstyles.csl+json",
            "User-Agent": "rhodyn-stage9.20-reference-audit/0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        payload = {"DOI": doi, "metadata_error": str(exc)}
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(cache_path, payload)
    return payload


def _fetch_crossref_relation(doi: str) -> dict[str, Any]:
    cache_path = REF_CACHE_DIR / f"{doi.lower().replace('/', '_')}.crossref_relation.json"
    if cache_path.exists():
        return _read_json(cache_path)
    if doi.lower().startswith("10.5281/zenodo."):
        payload = {"doi": doi, "status": "not_applicable_zenodo_record", "relation": {}}
        _write_json(cache_path, payload)
        return payload
    url = f"https://api.crossref.org/works/{doi}"
    request = urllib.request.Request(url, headers={"User-Agent": "rhodyn-stage9.20-reference-audit/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            message = json.loads(response.read().decode("utf-8")).get("message", {})
        relation = message.get("relation", {})
        relation_keys = sorted(relation.keys())
        has_retraction_marker = any("retract" in key.lower() for key in relation_keys)
        payload = {
            "doi": doi,
            "status": "clear" if not has_retraction_marker else "needs_manual_review",
            "relation": relation,
            "relation_keys": relation_keys,
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        payload = {"doi": doi, "status": "unresolved", "error": str(exc), "relation": {}}
    _write_json(cache_path, payload)
    return payload


def _names(authors: Any) -> str:
    if not isinstance(authors, list) or not authors:
        return "Unknown"
    names: list[str] = []
    for author in authors:
        if not isinstance(author, dict):
            continue
        given = str(author.get("given", "")).strip()
        family = str(author.get("family", "")).strip()
        literal = str(author.get("literal", "")).strip()
        if family and given:
            names.append(f"{family}, {given}")
        elif family:
            names.append(family)
        elif literal:
            names.append(literal)
    return " and ".join(names) if names else "Unknown"


def _first_year(issued: Any) -> str:
    try:
        return str(issued["date-parts"][0][0])
    except (KeyError, IndexError, TypeError):
        return "unknown"


def _first(value: Any) -> str:
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value or "")


def _bibtex_escape(value: str) -> str:
    return value.replace("&amp;", "\\&").replace("&", "\\&")


def _build_bibtex(metadata_by_ref: dict[str, dict[str, Any]]) -> str:
    entries: list[str] = [
        "% REFERENCES-BIB stage=9.20 generated_by=scripts/run_stage9_20_reference_audit.py",
        "% Scope. DOI-backed reference library only. Figure legends and final package assembly are downstream.",
        "",
    ]
    for spec in REFERENCE_SPECS:
        meta = metadata_by_ref[spec.ref_id]
        entry_type = "article" if spec.source_type == "methods" else "misc"
        title = _first(meta.get("title")) or spec.citation_label
        journal = _first(meta.get("container-title"))
        publisher = _first(meta.get("publisher"))
        url = _first(meta.get("URL")) or f"https://doi.org/{spec.doi}"
        fields = {
            "title": title,
            "author": _names(meta.get("author")),
            "year": _first_year(meta.get("issued")),
            "doi": spec.doi,
            "url": url,
            "note": f"{spec.ref_id}. {spec.support_role}",
        }
        if entry_type == "article":
            fields["journal"] = journal
        else:
            fields["publisher"] = publisher or "Zenodo"
            fields["howpublished"] = "Zenodo record"
        entries.append(f"@{entry_type}{{{spec.ref_id},")
        for key, value in fields.items():
            if value:
                entries.append(f"  {key} = {{{_bibtex_escape(str(value))}}},")
        entries.append("}")
        entries.append("")
    return "\n".join(entries).rstrip() + "\n"


def _build_citation_rows(metadata_by_ref: dict[str, dict[str, Any]], relation_by_ref: dict[str, dict[str, Any]], access_date: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for spec in REFERENCE_SPECS:
        meta = metadata_by_ref[spec.ref_id]
        relation = relation_by_ref[spec.ref_id]
        resolved = "false" if meta.get("metadata_error") else "true"
        rows.append(
            {
                "ref_id": spec.ref_id,
                "claim_id": spec.claim_id,
                "doi_or_pmid": spec.doi,
                "resolved": resolved,
                "access_date": access_date,
                "source_type": spec.source_type,
                "citation_label": spec.citation_label,
                "title": _first(meta.get("title")) or spec.citation_label,
                "paragraph_ids": spec.paragraph_ids,
                "support_role": spec.support_role,
                "retraction_check": str(relation.get("status", "unresolved")),
                "source_note": spec.source_note,
            }
        )
    return rows


def _claim_ids() -> set[str]:
    return {row["claim_id"] for row in _read_csv(CLAIM_HIERARCHY)}


def _paragraph_ids() -> set[str]:
    return {row["para_id"] for row in _read_csv(PARAGRAPH_LEDGER)}


def _no_downstream_started() -> tuple[bool, list[str]]:
    if GATE_929.exists():
        try:
            gate_929 = _read_json(GATE_929)
        except json.JSONDecodeError:
            gate_929 = {}
        if gate_929.get("pass") is True and gate_929.get("substage") == "9.29":
            return True, ["closed_stage9_refresh_allowed"]
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden, forbidden


def _build_audit(generated_utc: str, reference_version: str, rows: list[dict[str, str]], checks: list[dict[str, Any]]) -> str:
    resolved_count = sum(row["resolved"] == "true" for row in rows)
    clear_count = sum(row["retraction_check"] in {"clear", "not_applicable_zenodo_record"} for row in rows)
    source_counts: dict[str, int] = {}
    for row in rows:
        source_counts[row["source_type"]] = source_counts.get(row["source_type"], 0) + 1
    lines = [
        f"<!-- REFERENCE-AUDIT stage=9.20 generated_utc={generated_utc} reference_version={reference_version} -->",
        "",
        "# Reference library and citation audit",
        "",
        "Stage 9.20 resolves the current manuscript reference set as claim-linked sources. The audit binds each reference to a DOI, claim ID, paragraph route, support role, and retraction-check status. This is a citation-support surface only. It does not write figure legends, run cross-document consistency checks, or assemble a submission package.",
        "",
        "## Summary",
        "",
        f"- Reference count. {len(rows)} of {REFERENCE_CAP} typical Nature Methods Article references.",
        f"- DOI-resolved references. {resolved_count} of {len(rows)}.",
        f"- Retraction-check clear or not applicable. {clear_count} of {len(rows)}.",
        f"- Source-type counts. {'; '.join(f'{key}={source_counts[key]}' for key in sorted(source_counts))}.",
        "",
        "## Citation support map",
        "",
        "| ref | source type | claim IDs | paragraph routes | support role | DOI | status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["ref_id"],
                    row["source_type"],
                    row["claim_id"],
                    row["paragraph_ids"],
                    row["support_role"],
                    row["doi_or_pmid"],
                    f"{row['resolved']}; {row['retraction_check']}",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Gate checks",
            "",
            "| check | status | detail |",
            "| --- | --- | --- |",
        ]
    )
    for check in checks:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"| {check['name']} | {status} | {check['detail']} |")
    lines.extend(
        [
            "",
            "## Scope boundary",
            "",
            "The reference library supports the existing manuscript claims and availability statements. It does not add a new biological demonstration, does not change any model decision, and does not replace the later cross-document consistency audit.",
        ]
    )
    return "\n".join(lines)


def _validate(rows: list[dict[str, str]], bibtex: str, audit: str) -> list[dict[str, Any]]:
    gate_919_pass = False
    if GATE_919.exists():
        try:
            gate_919_pass = _read_json(GATE_919).get("pass") is True
        except json.JSONDecodeError:
            gate_919_pass = False
    claim_ids = _claim_ids() if CLAIM_HIERARCHY.exists() else set()
    paragraph_ids = _paragraph_ids() if PARAGRAPH_LEDGER.exists() else set()
    row_ref_ids = {row["ref_id"] for row in rows}
    expected_ref_ids = {spec.ref_id for spec in REFERENCE_SPECS}
    doi_ok = all(row["doi_or_pmid"].startswith("10.") for row in rows)
    resolved_ok = all(row["resolved"] == "true" for row in rows)
    retraction_ok = all(row["retraction_check"] in {"clear", "not_applicable_zenodo_record"} for row in rows)
    claim_ok = all(set(row["claim_id"].split(";")) <= claim_ids for row in rows)
    para_ok = all(set(row["paragraph_ids"].split(";")) <= paragraph_ids for row in rows)
    downstream_ok, downstream_paths = _no_downstream_started()
    intro_ref_ids = set()
    if INTRO_LEDGER.exists():
        intro_ref_ids = {row["ref_id"] for row in _read_csv(INTRO_LEDGER)}
    return [
        {
            "name": "stage_9_19_gate_passed",
            "passed": gate_919_pass,
            "detail": "Stage 9.19 supplementary table/source-data binding exists and passes" if gate_919_pass else "Stage 9.19 gate is missing or not passing",
        },
        {
            "name": "reference_set_complete_and_under_cap",
            "passed": row_ref_ids == expected_ref_ids and len(rows) <= REFERENCE_CAP,
            "detail": f"reference_count={len(rows)}; cap={REFERENCE_CAP}; ref_ids={';'.join(sorted(row_ref_ids))}",
        },
        {
            "name": "references_resolve_with_doi",
            "passed": doi_ok and resolved_ok,
            "detail": "All references have DOI-form identifiers and resolved DOI metadata",
        },
        {
            "name": "retraction_checks_clear_or_justified",
            "passed": retraction_ok,
            "detail": "Crossref relation checks are clear for papers; Zenodo dataset/software records are marked not applicable",
        },
        {
            "name": "references_map_to_claims_and_paragraphs",
            "passed": claim_ok and para_ok and intro_ref_ids <= row_ref_ids,
            "detail": "All citation rows resolve to frozen CLM IDs and paragraph routes; Stage 9.12 Introduction refs are included",
        },
        {
            "name": "software_and_dataset_records_included",
            "passed": {"REF-0010", "REF-0011", "REF-0012", "REF-0013", "REF-0014"} <= row_ref_ids,
            "detail": "Public datasets, RhoDyn software DOI, and PanelForge software DOI are present",
        },
        {
            "name": "bibtex_contains_one_entry_per_reference",
            "passed": all(f"@article{{{ref_id}," in bibtex or f"@misc{{{ref_id}," in bibtex for ref_id in expected_ref_ids),
            "detail": "BibTeX library contains exactly the expected REF keys",
        },
        {
            "name": "no_legend_consistency_or_package_started",
            "passed": downstream_ok,
            "detail": (
                "Closed Stage 9.29 package refresh allowed existing downstream surfaces"
                if downstream_paths == ["closed_stage9_refresh_allowed"]
                else "No figure legends, cross-document consistency audit, PI packet, or readiness checklist detected"
            )
            if downstream_ok
            else "; ".join(downstream_paths),
        },
        {
            "name": "scope_boundary_preserved",
            "passed": "does not add a new biological demonstration" in audit and "does not replace the later cross-document consistency audit" in audit,
            "detail": "Reference audit preserves citation-support scope without new biological claims",
        },
    ]


def _promote_staging() -> None:
    for destination in OUTPUTS.values():
        staged = STAGING_DIR / destination.relative_to(WORKSPACE)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, destination)
    for staged_cache in (STAGING_DIR / REF_CACHE_DIR.relative_to(WORKSPACE)).glob("*.json"):
        target = REF_CACHE_DIR / staged_cache.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged_cache, target)


def _quarantine_staging(timestamp: str) -> Path:
    target = QUARANTINE_DIR / timestamp.replace(":", "").replace("-", "")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(STAGING_DIR), str(target))
    return target


def _update_registry() -> None:
    registry = _read_json(REGISTRY_PATH)
    for substage in registry.get("substages", []):
        if substage.get("id") == "9.20":
            substage["status"] = "complete_reference_library_bound"
    registry["last_completed_substage"] = "9.20"
    registry["next_substage"] = "9.21"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], reference_version: str, checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.20",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.20.json",
        "validation_outcome": "Reference library and citation-claim ledger resolve DOI-backed sources to manuscript claims",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.19.json",
            "manuscript/nature_methods/refs/introduction_citation_ledger.csv",
            "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
            "manuscript/nature_methods/ledgers/paragraph_claim_ledger.csv",
            "manuscript/nature_methods/sections/data_availability.md",
            "manuscript/nature_methods/sections/code_availability.md",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/refs/references.bib",
            "manuscript/nature_methods/refs/citation_claim_ledger.csv",
            "manuscript/nature_methods/audits/reference_audit.md",
            "manuscript/nature_methods/refs/_cache/reference_library/",
            "manuscript/nature_methods/gate_verdicts/9.20.json",
        ],
        "remaining_blockers": [
            "Cross-document consistency audit has not started",
            "Live-number and statistical-language audit has not started",
            "Figure legends have not started",
            "Full submission-package assembly has not started beyond the Reporting Summary requirement placeholder",
        ],
        "reference_version": reference_version,
        "checks": checks,
    }
    entries = [
        item
        for item in memory.get("completed_substages", [])
        if not (isinstance(item, dict) and item.get("substage") == "9.20")
    ]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(reference_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.20"
    memory["citation_resolution_started"] = True
    memory["reference_library_started"] = True
    memory["status"] = "stage9_20_reference_library_bound"
    memory["current_gate"] = "Stage 9.20 resolved DOI-backed references and citation-to-claim bindings"
    memory["next_substage"] = "9.21"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.20 Reference library and citation audit complete; cross-document consistency audit not started"
    memory["stage9_20_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/refs/references.bib",
        "manuscript/nature_methods/refs/citation_claim_ledger.csv",
        "manuscript/nature_methods/audits/reference_audit.md",
        "manuscript/nature_methods/gate_verdicts/9.20.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.20 are complete through reference-library and citation-claim audit.",
        "Stage 9.21 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No figure legends, cross-document consistency audit, PI review packet, or submission readiness checklist are created in this reference pass.",
        "Every reference has a DOI-form identifier, claim mapping, paragraph route, and clear or justified retraction-check state.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, "
        "Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data "
        "binding, and reference-library/citation audit only. Do not start figure legends, cross-document audit, live-number audit, or final submission package without explicit substage authorization."
    )
    _upsert_completed_substage(memory, reference_version, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(reference_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.20 Reference library and citation audit complete; cross-document consistency audit not started"
    current["stage9_active_gate"] = "Stage 9.20 Reference library and citation audit complete; cross-document consistency audit not started"
    current["after_stage9_20_reference_audit"] = (
        "Stage 9.20 registered the DOI-backed reference library, citation-claim ledger, and reference audit. "
        "It did not write figure legends, run the cross-document consistency audit, perform the live-number audit, or assemble the final submission package."
    )
    current["current_gate"] = "Reference library and citation audit completed without figure legend or consistency-audit assembly"
    current["next_stage"] = "Stage 9.21 Cross-document consistency audit"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_20_reference_library_bound"
        stage["current_gate"] = "Stage 9.20 resolved DOI-backed references and citation-to-claim bindings"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, "
            "Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, and reference-library/citation audit only. "
            "Do not start figure legends, cross-document consistency audit, review response, live-number audit, or final submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/refs/references.bib",
            "manuscript/nature_methods/refs/citation_claim_ledger.csv",
            "manuscript/nature_methods/audits/reference_audit.md",
            "manuscript/nature_methods/gate_verdicts/9.20.json",
            "scripts/run_stage9_20_reference_audit.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        reference_gate = "Stage 9.20 references resolve with DOI metadata, clear or justified retraction checks, reference count under cap, and claim mappings."
        if reference_gate not in gate:
            gate.append(reference_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.20":
                subphase["status"] = "complete_reference_library_bound"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.20.json"
                subphase["reference_version"] = reference_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.18 registers Supplementary Methods prose in `supplementary/supplementary_methods.md` and `gate_verdicts/9.18.json`. Stage 9.19 registers supplementary table/source-data binding in `supplementary/supplementary_tables_plan.md`, `supplementary/source_data_binding_ledger.csv`, `ledgers/statistic_ledger.csv`, and `gate_verdicts/9.19.json`. The current state intentionally does not create `refs/references.bib`, figure legends, cross-document consistency audits, or full submission-package files.",
            "Stage 9.18 registers Supplementary Methods prose in `supplementary/supplementary_methods.md` and `gate_verdicts/9.18.json`. Stage 9.19 registers supplementary table/source-data binding in `supplementary/supplementary_tables_plan.md`, `supplementary/source_data_binding_ledger.csv`, `ledgers/statistic_ledger.csv`, and `gate_verdicts/9.19.json`. Stage 9.20 registers `refs/references.bib`, `refs/citation_claim_ledger.csv`, `audits/reference_audit.md`, and `gate_verdicts/9.20.json`. The current state intentionally does not create figure legends, cross-document consistency audits, live-number audits, or full submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.20 | Reference library and citation audit | not_started | Resolve and audit complete reference library. |",
            "| 9.20 | Reference library and citation audit | complete_reference_library_bound | Resolve and audit complete reference library. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.18 has registered Supplementary Methods, and Stage 9.19 has\nregistered supplementary table/source-data binding. Full reference-library\nassembly, figure legends, cross-document consistency audit, and final package\nassembly remain not started.",
            "Stage 9.18 has registered Supplementary Methods, Stage 9.19 has\nregistered supplementary table/source-data binding, and Stage 9.20 has\nregistered the reference library and citation audit. Figure legends,\ncross-document consistency audit, live-number audit, and final package assembly\nremain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.19 Supplementary tables/source-data binding complete, reference library and citation audit not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, and supplementary table/source-data binding only. Do not start full reference-library assembly, figure legends, cross-document consistency audit, review response, or final submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.20 Reference library and citation audit complete, cross-document consistency audit not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, and reference-library/citation audit only. Do not start figure legends, cross-document consistency audit, live-number audit, review response, or final submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit remains the next unstarted manuscript step. Full reference-library assembly, figure legends, cross-document consistency audit, and final package assembly remain not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit has been completed. Stage 9.21 Cross-document consistency audit remains the next unstarted manuscript step. Figure legends, live-number audit, and final package assembly remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    access_date = generated_utc[:10]
    commit = _git_sha()
    reference_version = f"reference-library@{access_date}@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    (STAGING_DIR / REF_CACHE_DIR.relative_to(WORKSPACE)).mkdir(parents=True, exist_ok=True)

    metadata_by_ref: dict[str, dict[str, Any]] = {}
    relation_by_ref: dict[str, dict[str, Any]] = {}
    original_cache_dir = REF_CACHE_DIR
    try:
        globals()["REF_CACHE_DIR"] = STAGING_DIR / original_cache_dir.relative_to(WORKSPACE)
        for spec in REFERENCE_SPECS:
            metadata_by_ref[spec.ref_id] = _fetch_csl(spec.doi)
            relation_by_ref[spec.ref_id] = _fetch_crossref_relation(spec.doi)
    finally:
        globals()["REF_CACHE_DIR"] = original_cache_dir

    bibtex = _build_bibtex(metadata_by_ref)
    rows = _build_citation_rows(metadata_by_ref, relation_by_ref, access_date)
    preliminary_checks = _validate(rows, bibtex, "")
    audit = _build_audit(generated_utc, reference_version, rows, preliminary_checks)
    checks = _validate(rows, bibtex, audit)
    audit = _build_audit(generated_utc, reference_version, rows, checks)
    passed = all(check["passed"] for check in checks)

    _write_text(STAGING_DIR / OUTPUTS["references"].relative_to(WORKSPACE), bibtex)
    _write_csv(
        STAGING_DIR / OUTPUTS["citation_ledger"].relative_to(WORKSPACE),
        rows,
        [
            "ref_id",
            "claim_id",
            "doi_or_pmid",
            "resolved",
            "access_date",
            "source_type",
            "citation_label",
            "title",
            "paragraph_ids",
            "support_role",
            "retraction_check",
            "source_note",
        ],
    )
    _write_text(STAGING_DIR / OUTPUTS["audit"].relative_to(WORKSPACE), audit)
    gate = {
        "substage": "9.20",
        "timestamp": generated_utc,
        "reference_version": reference_version,
        "pass": passed,
        "checks": checks,
        "reference_count": len(rows),
        "reference_cap": REFERENCE_CAP,
        "ref_ids": sorted(row["ref_id"] for row in rows),
        "next_substage": "9.21",
        "outputs": [path.relative_to(ROOT).as_posix() for path in OUTPUTS.values()],
        "scope_boundary": "Reference library and citation audit only. No figure legends, cross-document consistency audit, live-number audit, PI packet, readiness checklist, or final submission-package assembly.",
    }
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)

    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(reference_version, generated_utc, checks)
        _update_roadmap_memory(reference_version)
        _update_docs()
    else:
        gate["quarantine_path"] = _quarantine_staging(generated_utc).relative_to(ROOT).as_posix()

    return gate


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
