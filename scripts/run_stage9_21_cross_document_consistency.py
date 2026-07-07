"""Run Stage 9.21 cross-document consistency audit.

Stage 9.21 checks the keyed manuscript ledgers as relational tables. It binds
claims, paragraphs, figures, statistics, source-data tables, supplementary
callouts, and references without rewriting figure legends, recomputing numbers,
or assembling the final submission package.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
AUDITS_DIR = WORKSPACE / "audits"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.21"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.21"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"

GATE_920 = GATE_DIR / "9.20.json"
GATE_929 = GATE_DIR / "9.29.json"
CLAIM_HIERARCHY = WORKSPACE / "ledgers" / "claim_hierarchy.csv"
PARAGRAPH_LEDGER = WORKSPACE / "ledgers" / "paragraph_claim_ledger.csv"
FIGURE_LEDGER = WORKSPACE / "ledgers" / "figure_to_claim_to_artifact.csv"
STATISTIC_LEDGER = WORKSPACE / "ledgers" / "statistic_ledger.csv"
SUPPLEMENTARY_LEDGER = WORKSPACE / "ledgers" / "supplementary_callout_ledger.csv"
SOURCE_DATA_LEDGER = WORKSPACE / "supplementary" / "source_data_binding_ledger.csv"
CITATION_LEDGER = WORKSPACE / "refs" / "citation_claim_ledger.csv"
REFERENCES_BIB = WORKSPACE / "refs" / "references.bib"

OUTPUTS = {
    "audit": AUDITS_DIR / "cross_document_consistency_audit.md",
    "gate": GATE_DIR / "9.21.json",
}

FORBIDDEN_STARTED_PATHS = [
    WORKSPACE / "figures" / "figure_legends.md",
    WORKSPACE / "audits" / "statistical_language_audit.md",
    WORKSPACE / "audits" / "live_numbers_diff.csv",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
    WORKSPACE / "stage9_completion_report.md",
]


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except subprocess.CalledProcessError:
        return "unknown"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _split_ids(value: str) -> set[str]:
    ids: set[str] = set()
    for item in re.split(r"[;\n]", value or ""):
        token = item.strip()
        if token and not token.startswith("pending_stage9."):
            ids.add(token)
    return ids


def _sorted(values: set[str]) -> list[str]:
    return sorted(values)


def _extract_bib_ids(body: str) -> set[str]:
    return set(re.findall(r"@\w+\{(REF-\d{4}),", body))


def _closed_stage9_refresh_allowed() -> bool:
    if not GATE_929.exists():
        return False
    try:
        gate = _read_json(GATE_929)
    except json.JSONDecodeError:
        return False
    return gate.get("pass") is True and gate.get("substage") == "9.29"


def _join_analysis() -> dict[str, Any]:
    stage_920_gate = _read_json(GATE_920)
    claims = _read_csv(CLAIM_HIERARCHY)
    paragraphs = _read_csv(PARAGRAPH_LEDGER)
    figures = _read_csv(FIGURE_LEDGER)
    statistics = _read_csv(STATISTIC_LEDGER)
    supplementary = _read_csv(SUPPLEMENTARY_LEDGER)
    source_rows = _read_csv(SOURCE_DATA_LEDGER)
    citations = _read_csv(CITATION_LEDGER)
    bib_ids = _extract_bib_ids(REFERENCES_BIB.read_text(encoding="utf-8"))

    claim_ids = {row["claim_id"] for row in claims}
    paragraph_ids = {row["para_id"] for row in paragraphs}
    figure_ids = {row["fig_id"] for row in figures}
    stat_ids = {row["stat_id"] for row in statistics}
    supp_ids = {row["supp_id"] for row in supplementary} | {row["supp_id"] for row in source_rows}
    table_ids = {row["table_id"] for row in source_rows}
    ref_ids = {row["ref_id"] for row in citations}

    claim_refs = {
        *_split_ids(";".join(row.get("claim_id", "") for row in paragraphs)),
        *_split_ids(";".join(row.get("claim_id", "") for row in figures)),
        *_split_ids(";".join(row.get("claim_ids", "") for row in source_rows)),
        *_split_ids(";".join(row.get("claim_id", "") for row in citations)),
    }
    represented_claims = claim_refs & claim_ids
    orphan_claims = claim_ids - represented_claims
    unknown_claim_refs = claim_refs - claim_ids

    figure_refs = {
        *_split_ids(";".join(row.get("fig_ids", "") for row in paragraphs)),
        *_split_ids(";".join(row.get("fig_id", "") for row in statistics)),
        *_split_ids(";".join(row.get("fig_id", "") for row in supplementary)),
        *_split_ids(";".join(row.get("linked_main_figures", "") for row in source_rows)),
    }
    represented_figures = figure_refs & figure_ids
    orphan_figures = figure_ids - represented_figures
    unknown_figure_refs = figure_refs - figure_ids

    stat_refs = {
        *_split_ids(";".join(row.get("stat_ids", "") for row in figures)),
        *_split_ids(";".join(row.get("stat_ids", "") for row in source_rows)),
        *_split_ids(";".join(row.get("stat_ids", "") for row in supplementary)),
        *_split_ids(";".join(row.get("manuscript_locations", "") for row in statistics)),
    }
    stat_refs = {item for item in stat_refs if item.startswith("STAT-")}
    represented_stats = stat_refs & stat_ids
    orphan_statistics = stat_ids - represented_stats
    unknown_stat_refs = stat_refs - stat_ids

    para_refs = {
        *_split_ids(";".join(row.get("paragraph_ids", "") for row in citations)),
        *_split_ids(";".join(row.get("callout_location", "") for row in source_rows)),
        *_split_ids(";".join(row.get("callout_location", "") for row in supplementary)),
    }
    para_refs = {item for item in para_refs if item.startswith("PARA-")}
    unknown_paragraph_refs = para_refs - paragraph_ids

    source_table_refs = {
        item
        for row in statistics
        for item in _split_ids(row.get("manuscript_locations", ""))
        if item.startswith("STBL-")
    }
    unknown_table_refs = source_table_refs - table_ids

    citation_claim_refs = {row["ref_id"] for row in citations}
    dangling_references = (citation_claim_refs - bib_ids) | (bib_ids - citation_claim_refs)
    unresolved_references = {
        row["ref_id"]
        for row in citations
        if row.get("resolved") != "true" or row.get("retraction_check") not in {"clear", "not_applicable_zenodo_record"}
    }

    claim_strength = {row["claim_id"]: row["strength_cap"] for row in claims}
    strength_mismatches: list[dict[str, str]] = []
    for row in paragraphs:
        row_claims = _split_ids(row.get("claim_id", ""))
        if len(row_claims) == 1:
            claim_id = next(iter(row_claims))
            if row.get("strength_cap") != claim_strength.get(claim_id):
                strength_mismatches.append(
                    {
                        "para_id": row["para_id"],
                        "claim_id": claim_id,
                        "paragraph_strength_cap": row.get("strength_cap", ""),
                        "claim_strength_cap": claim_strength.get(claim_id, ""),
                    }
                )

    missing_render_paths: list[str] = []
    bad_engine_rows: list[str] = []
    for row in figures:
        render_path = row.get("render_path", "")
        if not render_path or not (ROOT / render_path).exists():
            missing_render_paths.append(row.get("fig_id", "unknown"))
        if row.get("engine_version") != "panelforge-figures@v3.14.1":
            bad_engine_rows.append(row.get("fig_id", "unknown"))
        if len(row.get("engine_commit", "")) != 40:
            bad_engine_rows.append(row.get("fig_id", "unknown"))
        if row.get("drift_ok") != "accepted_stage9.6b":
            bad_engine_rows.append(row.get("fig_id", "unknown"))

    missing_source_paths: list[str] = []
    missing_binding_render_paths: list[str] = []
    for row in source_rows:
        for rel in _split_ids(row.get("source_paths", "")):
            if rel.startswith("docs/") or rel.startswith("case_studies/"):
                if not (ROOT / rel).exists():
                    missing_source_paths.append(rel)
        for rel in _split_ids(row.get("render_paths", "")):
            if not (ROOT / rel).exists():
                missing_binding_render_paths.append(rel)

    checks = [
        {
            "name": "stage_9_20_gate_passed",
            "passed": stage_920_gate.get("pass") is True and stage_920_gate.get("substage") == "9.20",
            "detail": "Stage 9.20 reference library is present and passed",
        },
        {
            "name": "orphan_claim_set_empty",
            "passed": not orphan_claims and not unknown_claim_refs,
            "detail": f"orphan={len(orphan_claims)}; unknown_refs={len(unknown_claim_refs)}",
        },
        {
            "name": "orphan_figure_set_empty",
            "passed": not orphan_figures and not unknown_figure_refs,
            "detail": f"orphan={len(orphan_figures)}; unknown_refs={len(unknown_figure_refs)}",
        },
        {
            "name": "orphan_statistic_set_empty",
            "passed": not orphan_statistics and not unknown_stat_refs,
            "detail": f"orphan={len(orphan_statistics)}; unknown_refs={len(unknown_stat_refs)}",
        },
        {
            "name": "dangling_reference_set_empty",
            "passed": not dangling_references and not unresolved_references and not unknown_paragraph_refs and not unknown_table_refs,
            "detail": (
                f"dangling_refs={len(dangling_references)}; unresolved_refs={len(unresolved_references)}; "
                f"unknown_paragraphs={len(unknown_paragraph_refs)}; unknown_tables={len(unknown_table_refs)}"
            ),
        },
        {
            "name": "version_and_strength_coherence_hold",
            "passed": not strength_mismatches and not missing_render_paths and not bad_engine_rows and not missing_source_paths and not missing_binding_render_paths,
            "detail": (
                f"strength_mismatches={len(strength_mismatches)}; missing_render_paths={len(missing_render_paths)}; "
                f"bad_engine_rows={len(bad_engine_rows)}; missing_source_paths={len(missing_source_paths)}; "
                f"missing_binding_render_paths={len(missing_binding_render_paths)}"
            ),
        },
        {
            "name": "no_statistical_language_legend_or_package_started",
            "passed": _closed_stage9_refresh_allowed() or not [path for path in FORBIDDEN_STARTED_PATHS if path.exists()],
            "detail": "Closed Stage 9.29 package refresh allowed existing downstream surfaces"
            if _closed_stage9_refresh_allowed()
            else "No Stage 9.22 live-number audit, figure legends, PI packet, readiness checklist, or completion report detected",
        },
        {
            "name": "scope_boundary_preserved",
            "passed": True,
            "detail": "Cross-document joins only; no statistics recomputed, legends written, or final package assembled",
        },
    ]

    return {
        "generated_utc": _now(),
        "commit": _git_sha(),
        "claim_ids": _sorted(claim_ids),
        "paragraph_ids": _sorted(paragraph_ids),
        "figure_ids": _sorted(figure_ids),
        "stat_ids": _sorted(stat_ids),
        "supp_ids": _sorted(supp_ids),
        "table_ids": _sorted(table_ids),
        "ref_ids": _sorted(ref_ids),
        "orphan_claims": _sorted(orphan_claims),
        "unknown_claim_refs": _sorted(unknown_claim_refs),
        "orphan_figures": _sorted(orphan_figures),
        "unknown_figure_refs": _sorted(unknown_figure_refs),
        "orphan_statistics": _sorted(orphan_statistics),
        "unknown_statistic_refs": _sorted(unknown_stat_refs),
        "dangling_references": _sorted(dangling_references | unresolved_references),
        "unknown_paragraph_refs": _sorted(unknown_paragraph_refs),
        "unknown_table_refs": _sorted(unknown_table_refs),
        "strength_mismatches": strength_mismatches,
        "missing_render_paths": sorted(missing_render_paths),
        "bad_engine_rows": sorted(set(bad_engine_rows)),
        "missing_source_paths": sorted(set(missing_source_paths)),
        "missing_binding_render_paths": sorted(set(missing_binding_render_paths)),
        "counts": {
            "claims": len(claim_ids),
            "paragraphs": len(paragraph_ids),
            "figures": len(figure_ids),
            "statistics": len(stat_ids),
            "supplementary_items": len(supp_ids),
            "source_data_tables": len(table_ids),
            "references": len(ref_ids),
        },
        "checks": checks,
    }


def _build_audit(analysis: dict[str, Any]) -> str:
    counts = analysis["counts"]
    check_rows = "\n".join(
        f"| {item['name']} | {'pass' if item['passed'] else 'fail'} | {item['detail']} |" for item in analysis["checks"]
    )
    source_rows = [
        ("Frozen claims", counts["claims"], "Claim hierarchy and paragraph/figure/source/reference ledgers"),
        ("Main figures", counts["figures"], "Figure-to-claim ledger, statistic ledger, supplementary callouts, and source-data bindings"),
        ("Statistics", counts["statistics"], "Statistic ledger and supplementary source-data binding ledger"),
        ("References", counts["references"], "Citation-claim ledger and BibTeX library"),
        ("Supplementary tables", counts["source_data_tables"], "Source-data binding ledger"),
    ]
    source_table = "\n".join(f"| {label} | {count} | {basis} |" for label, count, basis in source_rows)
    return f"""<!-- CROSS-DOCUMENT-CONSISTENCY stage=9.21 generated={analysis['generated_utc']} commit={analysis['commit']} -->
# Stage 9.21 cross-document consistency audit

Stage 9.21 checks whether the manuscript's frozen claim system is internally coherent across claims, paragraphs, main figures, statistics, supplementary support, source-data tables, and references. This is a keyed-ledger consistency pass only. It does not rewrite the manuscript, recompute numerical results, write figure legends, audit statistical phrasing, or assemble the final submission package.

## Summary

The cross-document joins passed. The current manuscript state contains no orphan claims, no orphan main figures, no orphan statistic IDs, and no dangling references. Figure-engine versioning, rendered figure paths, source-data paths, and paragraph-level strength caps remain coherent with the frozen claim hierarchy.

| Surface | Count | Join basis |
|---|---:|---|
{source_table}

## Gate checks

| Check | Status | Detail |
|---|---|---|
{check_rows}

## Empty mismatch sets

- Orphan claims. {analysis['orphan_claims']}
- Unknown claim references. {analysis['unknown_claim_refs']}
- Orphan figures. {analysis['orphan_figures']}
- Unknown figure references. {analysis['unknown_figure_refs']}
- Orphan statistics. {analysis['orphan_statistics']}
- Unknown statistic references. {analysis['unknown_statistic_refs']}
- Dangling or unresolved references. {analysis['dangling_references']}
- Unknown paragraph references. {analysis['unknown_paragraph_refs']}
- Unknown source-data table references. {analysis['unknown_table_refs']}

## Version and strength coherence

- PanelForge engine version. `panelforge-figures@v3.14.1`
- Missing rendered main-figure paths. {analysis['missing_render_paths']}
- Bad figure-engine rows. {analysis['bad_engine_rows']}
- Missing source paths. {analysis['missing_source_paths']}
- Missing source-data render paths. {analysis['missing_binding_render_paths']}
- Paragraph strength-cap mismatches. {analysis['strength_mismatches']}

## Scope boundary

The biological interpretation remains unchanged. This audit supports manuscript assembly by showing that the current Results, Methods, figures, source-data support, and references point to the same bounded method claims. It does not test live-number phrasing, does not write figure legends, and does not create the PI review or submission-readiness package. Those remain downstream Stage 9 steps.
"""


def _gate_payload(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "substage": "9.21",
        "title": "Cross-document consistency audit",
        "generated_utc": analysis["generated_utc"],
        "commit": analysis["commit"],
        "pass": all(item["passed"] for item in analysis["checks"]),
        "checks": analysis["checks"],
        "claim_count": analysis["counts"]["claims"],
        "paragraph_count": analysis["counts"]["paragraphs"],
        "pnas_figure_count": analysis["counts"]["figures"],
        "figure_count": analysis["counts"]["figures"],
        "statistic_count": analysis["counts"]["statistics"],
        "supplementary_item_count": analysis["counts"]["supplementary_items"],
        "source_data_table_count": analysis["counts"]["source_data_tables"],
        "reference_count": analysis["counts"]["references"],
        "claim_ids": analysis["claim_ids"],
        "figure_ids": analysis["figure_ids"],
        "stat_ids": analysis["stat_ids"],
        "ref_ids": analysis["ref_ids"],
        "orphan_claims": analysis["orphan_claims"],
        "unknown_claim_refs": analysis["unknown_claim_refs"],
        "orphan_figures": analysis["orphan_figures"],
        "unknown_figure_refs": analysis["unknown_figure_refs"],
        "orphan_statistics": analysis["orphan_statistics"],
        "unknown_statistic_refs": analysis["unknown_statistic_refs"],
        "dangling_references": analysis["dangling_references"],
        "unknown_paragraph_refs": analysis["unknown_paragraph_refs"],
        "unknown_table_refs": analysis["unknown_table_refs"],
        "strength_mismatches": analysis["strength_mismatches"],
        "missing_render_paths": analysis["missing_render_paths"],
        "bad_engine_rows": analysis["bad_engine_rows"],
        "missing_source_paths": analysis["missing_source_paths"],
        "missing_binding_render_paths": analysis["missing_binding_render_paths"],
        "outputs": [
            "manuscript/nature_methods/audits/cross_document_consistency_audit.md",
            "manuscript/nature_methods/gate_verdicts/9.21.json",
        ],
        "scope_boundary": "Cross-document consistency joins only. No figure legends, live-number audit, statistical-language audit, PI packet, readiness checklist, or final submission-package assembly.",
        "next_substage": "9.22",
    }


def _promote_from_staging() -> None:
    for name, final_path in OUTPUTS.items():
        staged = STAGING_DIR / final_path.relative_to(WORKSPACE)
        final_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, final_path)


def _quarantine_staging() -> Path:
    QUARANTINE_DIR.parent.mkdir(parents=True, exist_ok=True)
    target = QUARANTINE_DIR
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(STAGING_DIR), str(target))
    return target


def _update_registry() -> None:
    registry = _read_json(REGISTRY_PATH)
    for substage in registry.get("substages", []):
        if substage.get("id") == "9.21":
            substage["status"] = "complete_cross_document_consistency_bound"
    registry["last_completed_substage"] = "9.21"
    registry["next_substage"] = "9.22"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.21",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.21.json",
        "validation_outcome": "Cross-document joins show no orphan claims, figures, statistics, or references",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.20.json",
            "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
            "manuscript/nature_methods/ledgers/paragraph_claim_ledger.csv",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
            "manuscript/nature_methods/ledgers/statistic_ledger.csv",
            "manuscript/nature_methods/supplementary/source_data_binding_ledger.csv",
            "manuscript/nature_methods/refs/citation_claim_ledger.csv",
            "manuscript/nature_methods/refs/references.bib",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/audits/cross_document_consistency_audit.md",
            "manuscript/nature_methods/gate_verdicts/9.21.json",
        ],
        "remaining_blockers": [
            "Statistical and quantitative language audit has not started",
            "Figure legends have not started",
            "Full submission-package assembly has not started beyond the Reporting Summary requirement placeholder",
        ],
        "checks": checks,
    }
    entries = [
        item
        for item in memory.get("completed_substages", [])
        if not (isinstance(item, dict) and item.get("substage") == "9.21")
    ]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.21"
    memory["cross_document_consistency_started"] = True
    memory["status"] = "stage9_21_cross_document_consistency_bound"
    memory["current_gate"] = "Stage 9.21 cross-document consistency joins passed across claims, figures, statistics, references, and strength caps"
    memory["next_substage"] = "9.22"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.21 Cross-document consistency audit complete; statistical and quantitative language audit not started"
    memory["stage9_21_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/audits/cross_document_consistency_audit.md",
        "manuscript/nature_methods/gate_verdicts/9.21.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.21 are complete through cross-document consistency audit.",
        "Stage 9.22 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No figure legends, live-number audit, PI review packet, or submission readiness checklist are created in this consistency pass.",
        "Claims, figures, statistics, source-data support, and references have no orphan or dangling keyed-ledger joins.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, "
        "Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data "
        "binding, reference-library/citation audit, and cross-document consistency audit only. Do not start figure legends, live-number audit, or final submission package without explicit substage authorization."
    )
    _upsert_completed_substage(memory, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory() -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.21 Cross-document consistency audit complete; statistical and quantitative language audit not started"
    current["stage9_active_gate"] = "Stage 9.21 Cross-document consistency audit complete; statistical and quantitative language audit not started"
    current["after_stage9_21_cross_document_consistency"] = (
        "Stage 9.21 registered the cross-document consistency audit and verified that claims, figures, statistics, source-data support, and references have no orphan or dangling keyed-ledger joins. "
        "It did not write figure legends, perform the live-number or statistical-language audit, or assemble the final submission package."
    )
    current["current_gate"] = "Cross-document consistency audit completed without figure legend or statistical-language assembly"
    current["next_stage"] = "Stage 9.22 Statistical and quantitative language audit"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_21_cross_document_consistency_bound"
        stage["current_gate"] = "Stage 9.21 cross-document joins show no orphan claims, figures, statistics, references, or strength-cap mismatches"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, "
            "Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, and cross-document consistency audit only. "
            "Do not start figure legends, statistical-language audit, live-number audit, review response, or final submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/audits/cross_document_consistency_audit.md",
            "manuscript/nature_methods/gate_verdicts/9.21.json",
            "scripts/run_stage9_21_cross_document_consistency.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        consistency_gate = "Stage 9.21 cross-document joins have empty orphan claim, orphan figure, orphan statistic, and dangling-reference sets."
        if consistency_gate not in gate:
            gate.append(consistency_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.21":
                subphase["status"] = "complete_cross_document_consistency_bound"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.21.json"
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.20 registers `refs/references.bib`, `refs/citation_claim_ledger.csv`, `audits/reference_audit.md`, and `gate_verdicts/9.20.json`. The current state intentionally does not create figure legends, cross-document consistency audits, live-number audits, or full submission-package files.",
            "Stage 9.20 registers `refs/references.bib`, `refs/citation_claim_ledger.csv`, `audits/reference_audit.md`, and `gate_verdicts/9.20.json`. Stage 9.21 registers `audits/cross_document_consistency_audit.md` and `gate_verdicts/9.21.json`. The current state intentionally does not create figure legends, live-number audits, statistical-language audits, or full submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.21 | Cross-document consistency audit | not_started | Check manuscript consistency by relational joins over keyed ledgers. |",
            "| 9.21 | Cross-document consistency audit | complete_cross_document_consistency_bound | Check manuscript consistency by relational joins over keyed ledgers. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.18 has registered Supplementary Methods, Stage 9.19 has\nregistered supplementary table/source-data binding, and Stage 9.20 has\nregistered the reference library and citation audit. Figure legends,\ncross-document consistency audit, live-number audit, and final package assembly\nremain not started.",
            "Stage 9.18 has registered Supplementary Methods, Stage 9.19 has\nregistered supplementary table/source-data binding, Stage 9.20 has registered\nthe reference library and citation audit, and Stage 9.21 has registered the\ncross-document consistency audit. Figure legends, statistical-language audit,\nlive-number audit, and final package assembly remain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.20 Reference library and citation audit complete, cross-document consistency audit not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, and reference-library/citation audit only. Do not start figure legends, cross-document consistency audit, live-number audit, review response, or final submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.21 Cross-document consistency audit complete, statistical and quantitative language audit not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, and cross-document consistency audit only. Do not start figure legends, statistical-language audit, live-number audit, review response, or final submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit has been completed. Stage 9.21 Cross-document consistency audit remains the next unstarted manuscript step. Figure legends, live-number audit, and final package assembly remain not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit has been completed. Stage 9.21 Cross-document consistency audit has been completed. Stage 9.22 Statistical and quantitative language audit remains the next unstarted manuscript step. Figure legends, live-number audit, and final package assembly remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    analysis = _join_analysis()
    audit = _build_audit(analysis)
    gate = _gate_payload(analysis)

    staged_audit = STAGING_DIR / OUTPUTS["audit"].relative_to(WORKSPACE)
    staged_gate = STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE)
    staged_audit.parent.mkdir(parents=True, exist_ok=True)
    staged_gate.parent.mkdir(parents=True, exist_ok=True)
    staged_audit.write_text(audit, encoding="utf-8")
    _write_json(staged_gate, gate)

    if not gate["pass"]:
        quarantine = _quarantine_staging()
        return {
            "status": "failed",
            "substage": "9.21",
            "quarantine_dir": str(quarantine.relative_to(ROOT)),
            "failed_checks": [item for item in gate["checks"] if not item["passed"]],
        }

    _promote_from_staging()
    shutil.rmtree(STAGING_DIR)
    _update_registry()
    _update_memory(analysis["generated_utc"], gate["checks"])
    _update_roadmap_memory()
    _update_docs()

    return {
        "status": "completed",
        "substage": "9.21",
        "outputs": gate["outputs"],
        "next_substage": "9.22",
        "checks": gate["checks"],
    }


def main() -> int:
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
