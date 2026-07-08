"""Run Stage 10.11 author-review readiness for the presubmission route.

Stage 10.11 packages the Stage 10.9 presubmission route and Stage 10.10
recursive-hardening result into a send-safe author-review surface. It does not
send external contact and does not add data, benchmarks, figures, manuscript
claims, or editor-response claims.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage10_author_review_readiness"
DOC_PATH = ROOT / "docs" / "stage10_11_author_review_readiness.md"
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"

STAGE10_9_DIR = ROOT / "case_studies" / "stage10_eic_contact_decision"
STAGE10_10_DIR = ROOT / "case_studies" / "stage10_recursive_hardening"
STAGE10_9_GATE = STAGE10_9_DIR / "stage10_9_gate_report.json"
STAGE10_10_GATE = STAGE10_10_DIR / "stage10_10_gate_report.json"
STAGE10_10_PATCHES = STAGE10_10_DIR / "stage10_10_patch_recommendations.tsv"
STAGE10_9_EMAIL = STAGE10_9_DIR / "stage10_9_presubmission_email_draft_AUTHOR_REVIEW_REQUIRED.md"
STAGE10_9_PITCH = STAGE10_9_DIR / "stage10_9_one_page_pitch.md"
STAGE10_9_MEMO = STAGE10_9_DIR / "stage10_9_decision_memo.md"

AUTHOR_CHECKLIST = OUTPUT_DIR / "stage10_11_author_review_checklist.tsv"
PACKET_MANIFEST = OUTPUT_DIR / "stage10_11_editor_contact_packet_manifest.tsv"
CLEAN_QUERY = OUTPUT_DIR / "stage10_11_presubmission_query_clean_AUTHOR_REVIEW_REQUIRED.md"
DECISION_BRIEF = OUTPUT_DIR / "stage10_11_author_decision_brief.md"
BOUNDARY_SCAN = OUTPUT_DIR / "stage10_11_boundary_scan.tsv"
GATE_REPORT = OUTPUT_DIR / "stage10_11_gate_report.json"

CHECKLIST_FIELDS = [
    "item_id",
    "review_item",
    "required",
    "status",
    "current_evidence",
    "author_action",
]
PACKET_FIELDS = ["surface", "path", "role", "send_ready_status", "author_action_required"]
BOUNDARY_FIELDS = ["boundary", "required_signal", "status", "evidence", "unsafe_overread_blocked"]


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _stage10_10_passes() -> bool:
    if not STAGE10_10_GATE.exists():
        return False
    gate = _read_json(STAGE10_10_GATE)
    gates = gate.get("gates", {})
    return gate.get("status") == "pass" and isinstance(gates, dict) and all(gates.values())


def _stage10_9_passes() -> bool:
    if not STAGE10_9_GATE.exists():
        return False
    gate = _read_json(STAGE10_9_GATE)
    gates = gate.get("gates", {})
    return (
        gate.get("status") == "pass"
        and gate.get("selected_route") == "presubmission_query_author_review_required"
        and gate.get("external_contact_status") == "not_sent"
        and isinstance(gates, dict)
        and all(gates.values())
    )


def clean_query_text() -> str:
    return """# Stage 10.11 presubmission query. Author review required. Do not send from repository.

Subject. Presubmission inquiry for Nature Methods. Residence-state inference for live-cell perturbation data

Dear Nature Methods editorial team,

I am writing to ask whether the enclosed concept would be appropriate for a presubmission inquiry as a computational methods Article.

RhoDyn is a residence-state inference method for live-cell perturbation biology that asks when dwell inside a declared response regime changes interpretation relative to endpoint, amplitude, threshold, and generic time-series summaries. The package benchmarks this decision object against simple summaries, SciPy peak summaries, scikit-learn feature models, HMM state summaries, catch22-style, tsfresh-style, MiniROCKET-style, and ruptures-style comparator families, while preserving regimes where simpler summaries are sufficient. Public demonstrations span DRG calcium, GPCR-linked ERK, Cell Painting/MitoTox endpoints, and MLCI tracking, and a sealed no-retuning validation route preserves positive, comparator-sufficient, bounded-coupling, and inconclusive calls in held-out public-derived contexts. The software implementation is available through Python, command-line, API, workbench, checksum, and archive surfaces, but the proposed Article is framed around the method object rather than software availability alone. The main limitation is explicit. RhoDyn does not claim that every live-cell system contains a residence regime or that declared windows are mechanisms; it provides a reproducible decision route for determining when residence-state structure changes interpretation and when simpler summaries are adequate.

Would this scope fit Nature Methods for a presubmission evaluation?

Sincerely,

[Author name, affiliation, and contact details to be completed by the corresponding author]
"""


def checklist_rows() -> list[dict[str, str]]:
    return [
        {
            "item_id": "AR-001",
            "review_item": "Corresponding author identity, affiliation, and contact details",
            "required": "yes",
            "status": "author_required",
            "current_evidence": "query contains author placeholder",
            "author_action": "replace placeholder before any external message",
        },
        {
            "item_id": "AR-002",
            "review_item": "Presubmission route approval",
            "required": "yes",
            "status": "author_required",
            "current_evidence": "Stage 10.9 selected presubmission query with author review required",
            "author_action": "confirm presubmission query rather than full submission, delay, or venue pivot",
        },
        {
            "item_id": "AR-003",
            "review_item": "Subject line",
            "required": "yes",
            "status": "author_required",
            "current_evidence": "clean query includes proposed Nature Methods presubmission subject",
            "author_action": "approve or edit subject before sending",
        },
        {
            "item_id": "AR-004",
            "review_item": "Method-first framing",
            "required": "yes",
            "status": "ready_for_author_review",
            "current_evidence": "query and pitch lead with residence-state inference method",
            "author_action": "preserve method-object framing during edits",
        },
        {
            "item_id": "AR-005",
            "review_item": "Named comparator families",
            "required": "yes",
            "status": "ready_for_author_review",
            "current_evidence": "query names simple summaries, SciPy, scikit-learn, HMM, catch22-style, tsfresh-style, MiniROCKET-style, and ruptures-style comparators",
            "author_action": "do not remove comparator evidence unless pitch is intentionally shortened",
        },
        {
            "item_id": "AR-006",
            "review_item": "Public biological breadth",
            "required": "yes",
            "status": "ready_for_author_review",
            "current_evidence": "query names DRG calcium, GPCR-linked ERK, Cell Painting/MitoTox, and MLCI tracking",
            "author_action": "preserve breadth while avoiding universal-residence language",
        },
        {
            "item_id": "AR-007",
            "review_item": "Held-out validation scope",
            "required": "yes",
            "status": "ready_for_author_review",
            "current_evidence": "query states sealed no-retuning validation over public-derived contexts",
            "author_action": "do not call it prospective blinded validation",
        },
        {
            "item_id": "AR-008",
            "review_item": "Software reproducibility support",
            "required": "yes",
            "status": "ready_for_author_review",
            "current_evidence": "query names Python, command-line, API, workbench, checksum, and archive surfaces",
            "author_action": "keep software as support for the method, not the primary claim",
        },
        {
            "item_id": "AR-009",
            "review_item": "Limits and non-claims",
            "required": "yes",
            "status": "ready_for_author_review",
            "current_evidence": "query explicitly rejects universal residence and automatic mechanism readings",
            "author_action": "do not strengthen limits into unsupported claims during shortening",
        },
        {
            "item_id": "AR-010",
            "review_item": "Attachment decision",
            "required": "no",
            "status": "author_optional",
            "current_evidence": "one-page pitch is available as a concise attachment source",
            "author_action": "decide whether to attach, paste, or omit the one-page pitch",
        },
        {
            "item_id": "AR-011",
            "review_item": "Stage 9.29 package not used alone",
            "required": "yes",
            "status": "ready_for_author_review",
            "current_evidence": "Stage 10.10 forbids old-package reconsideration without the Stage 10 evidence pitch",
            "author_action": "do not ask for reconsideration of the Stage 9.29 package alone",
        },
        {
            "item_id": "AR-012",
            "review_item": "External contact send state",
            "required": "yes",
            "status": "not_sent",
            "current_evidence": "Stage 10.9 and 10.10 both record external_contact_status not_sent",
            "author_action": "send only after explicit corresponding-author approval",
        },
    ]


def boundary_rows() -> list[dict[str, str]]:
    query = clean_query_text()
    pitch = STAGE10_9_PITCH.read_text(encoding="utf-8") if STAGE10_9_PITCH.exists() else ""
    joined = query + "\n" + pitch

    def status(condition: bool) -> str:
        return "pass" if condition else "fail"

    return [
        {
            "boundary": "method_advance_present",
            "required_signal": "residence-state inference method",
            "status": status("residence-state inference method" in joined),
            "evidence": "query and one-page pitch",
            "unsafe_overread_blocked": "software-only reading",
        },
        {
            "boundary": "comparator_classes_present",
            "required_signal": "named baseline families appear",
            "status": status(all(term in joined for term in ["SciPy", "scikit-learn", "HMM", "catch22-style", "tsfresh-style", "MiniROCKET-style", "ruptures-style"])),
            "evidence": "query comparator sentence",
            "unsafe_overread_blocked": "self-comparison only",
        },
        {
            "boundary": "public_breadth_present",
            "required_signal": "four public systems appear",
            "status": status(all(term in joined for term in ["DRG calcium", "GPCR-linked ERK", "Cell Painting/MitoTox", "MLCI tracking"])),
            "evidence": "query public demonstrations sentence",
            "unsafe_overread_blocked": "single manuscript-specific example",
        },
        {
            "boundary": "heldout_validation_scoped",
            "required_signal": "sealed no-retuning public-derived validation",
            "status": status("sealed no-retuning" in joined and "public-derived" in joined and "prospective blinded" not in query),
            "evidence": "query and residual boundaries",
            "unsafe_overread_blocked": "prospective collaborator-blind validation claim",
        },
        {
            "boundary": "software_support_not_primary_claim",
            "required_signal": "software surfaces support method object",
            "status": status("method object rather than software availability alone" in joined and "not a software wrapper" in joined),
            "evidence": "query and one-page pitch",
            "unsafe_overread_blocked": "software maturity replaces method evidence",
        },
        {
            "boundary": "universal_residence_blocked",
            "required_signal": "query rejects every-system residence claim",
            "status": status("does not claim that every live-cell system contains a residence regime" in joined),
            "evidence": "query limitation sentence",
            "unsafe_overread_blocked": "universal residence-state biology",
        },
        {
            "boundary": "mechanism_discovery_blocked",
            "required_signal": "declared windows are not mechanisms",
            "status": status("declared windows are mechanisms" in joined and "does not claim" in joined),
            "evidence": "query limitation sentence",
            "unsafe_overread_blocked": "automatic mechanism discovery",
        },
        {
            "boundary": "old_package_not_contact_basis",
            "required_signal": "Stage 9.29 alone is forbidden",
            "status": status("Stage 9.29 package alone" in (STAGE10_9_MEMO.read_text(encoding="utf-8") if STAGE10_9_MEMO.exists() else "") and _stage10_10_passes()),
            "evidence": "Stage 10.9 decision memo and Stage 10.10 gate",
            "unsafe_overread_blocked": "old-package reconsideration route",
        },
        {
            "boundary": "external_contact_not_sent",
            "required_signal": "no send action occurred",
            "status": status("Do not send from repository" in query and _read_json(STAGE10_9_GATE).get("external_contact_status") == "not_sent" and _read_json(STAGE10_10_GATE).get("external_contact_status") == "not_sent"),
            "evidence": "clean query header plus Stage 10.9 and 10.10 gates",
            "unsafe_overread_blocked": "implicit editor contact",
        },
    ]


def packet_manifest_rows() -> list[dict[str, str]]:
    return [
        {
            "surface": "clean_presubmission_query",
            "path": _rel(CLEAN_QUERY),
            "role": "author-reviewed message source for optional Nature Methods presubmission inquiry",
            "send_ready_status": "author_review_required_not_sent",
            "author_action_required": "complete author identity and approve exact wording before any external message",
        },
        {
            "surface": "one_page_pitch",
            "path": _rel(STAGE10_9_PITCH),
            "role": "optional attachment or paste-in pitch source",
            "send_ready_status": "author_review_required",
            "author_action_required": "decide whether to attach or reuse",
        },
        {
            "surface": "route_decision_memo",
            "path": _rel(STAGE10_9_MEMO),
            "role": "records selected route and rejected alternatives",
            "send_ready_status": "internal_decision_support",
            "author_action_required": "review if overriding selected route",
        },
        {
            "surface": "author_review_checklist",
            "path": _rel(AUTHOR_CHECKLIST),
            "role": "pre-send checklist",
            "send_ready_status": "author_action_required",
            "author_action_required": "complete required author rows before contact",
        },
        {
            "surface": "boundary_scan",
            "path": _rel(BOUNDARY_SCAN),
            "role": "claim-boundary and overread screen",
            "send_ready_status": "ready_for_author_review",
            "author_action_required": "preserve pass boundaries during edits",
        },
        {
            "surface": "gate_report",
            "path": _rel(GATE_REPORT),
            "role": "machine-checkable readiness gate",
            "send_ready_status": "not_a_send_surface",
            "author_action_required": "none",
        },
    ]


def decision_brief_text(report: dict[str, Any]) -> str:
    return f"""# Stage 10.11 author-review readiness

## Decision state

The Stage 10 presubmission route is ready for author review, not for automatic sending.

## What is ready

- A clean presubmission query is available at `{_rel(CLEAN_QUERY)}`.
- The Stage 10.9 one-page pitch remains available at `{_rel(STAGE10_9_PITCH)}`.
- The author checklist records which items require corresponding-author action before contact.
- The boundary scan confirms that the query keeps the method-first reading, named comparator evidence, public breadth, no-retuning held-out scope, software support, and explicit limits.

## What remains author-only

1. Confirm that a presubmission query is the intended route.
2. Complete author name, affiliation, and contact details.
3. Approve the exact subject line and message body.
4. Decide whether to attach or paste the one-page pitch.
5. Send only from the corresponding author's chosen account after explicit approval.

## Boundary

Stage 10.11 does not contact Nature Methods, does not add data, does not render figures, and does not change the manuscript evidence. It converts the existing Stage 10 evidence ladder into a safer author-review packet.

Gate status. `{report['status']}`.
"""


def doc_text(report: dict[str, Any]) -> str:
    return f"""# Stage 10.11 author-review readiness

Stage 10.11 packages the Stage 10.9 presubmission route and Stage 10.10 recursive-hardening result into a clean author-review surface. It is a send-safety and claim-boundary step, not a new analysis.

## Status

`{report['status']}`

## Selected route

`{report['selected_route']}`

## External contact status

`{report['external_contact_status']}`

## Outputs

- `{_rel(CLEAN_QUERY)}`
- `{_rel(AUTHOR_CHECKLIST)}`
- `{_rel(PACKET_MANIFEST)}`
- `{_rel(BOUNDARY_SCAN)}`
- `{_rel(DECISION_BRIEF)}`
- `{_rel(GATE_REPORT)}`

## Interpretation boundary

{report['interpretation_boundary']}
"""


def _safe_query_checks(query: str) -> dict[str, bool]:
    forbidden = [
        r"\bprospective blinded\b",
        r"\buniversal\b",
        r"all live-cell systems contain",
        r"automatic mechanism",
        r"take another look",
    ]
    return {
        "author_review_header_present": "Author review required. Do not send from repository." in query,
        "author_placeholder_present": "[Author name, affiliation, and contact details" in query,
        "forbidden_overreads_absent": not any(re.search(pattern, query, flags=re.I) for pattern in forbidden),
        "no_local_paths_or_tokens": not any(
            term in query
            for term in [
                "/" + "Users/",
                "/" + "Volumes/",
                "Library/" + "LaunchAgents",
                "sk" + "-",
                "github" + "_pat_",
                "ghp" + "_",
            ]
        ),
    }


def _update_memory(report: dict[str, Any]) -> None:
    memory = _read_json(MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 10.11 author-review readiness complete; external contact remains not sent"
    current["stage10_active_gate"] = "Stage 10.11 author-review readiness complete; external contact remains not sent"
    current["current_gate"] = "Stage 10.11 author-review readiness complete; external contact remains not sent"
    current["next_stage"] = "Author review and optional EIC presubmission contact, not sent"
    current["after_stage10_11_author_review_readiness"] = (
        "Stage 10.11 produced an author-review-ready presubmission query packet with checklist, boundary scan, "
        "packet manifest, decision brief, and gate report. It preserved the selected presubmission route and did not "
        "send external contact."
    )
    stages = memory.get("stage_lock", [])
    for stage in stages:
        if stage.get("stage") != 10:
            continue
        stage["status"] = "stage10_11_complete_author_review_readiness"
        stage["current_gate"] = "Stage 10.11 author-review readiness complete; external contact remains not sent"
        artifacts = set(stage.get("artifacts", []))
        artifacts.update(
            [
                _rel(DOC_PATH),
                "scripts/run_stage10_11_author_review_readiness.py",
                "tests/test_stage10_11_author_review_readiness.py",
                _rel(AUTHOR_CHECKLIST),
                _rel(PACKET_MANIFEST),
                _rel(CLEAN_QUERY),
                _rel(DECISION_BRIEF),
                _rel(BOUNDARY_SCAN),
                _rel(GATE_REPORT),
            ]
        )
        stage["artifacts"] = sorted(artifacts)
        subphases = stage.setdefault("subphases", [])
        if not any(item.get("id") == "10.11" for item in subphases if isinstance(item, dict)):
            subphases.append(
                {
                    "id": "10.11",
                    "name": "Author-review readiness",
                    "goal": "Package the selected presubmission route as an author-review-ready no-send surface.",
                    "gate": "Stage 10.10 passes; presubmission route remains selected; boundary scan passes; external contact remains not sent.",
                    "status": "complete_author_review_readiness",
                    "evidence": _rel(GATE_REPORT),
                }
            )
    _write_json(MEMORY_PATH, memory)


def validate_stage10_11() -> dict[str, Any]:
    query = clean_query_text()
    boundary = boundary_rows()
    checklist = checklist_rows()
    safe_query = _safe_query_checks(query)
    required_checklist = [row for row in checklist if row["required"] == "yes"]
    author_required = [row for row in checklist if "author" in row["status"]]
    patch_rows = _read_tsv(STAGE10_10_PATCHES) if STAGE10_10_PATCHES.exists() else []
    patch_decisions = {row.get("item"): row for row in patch_rows}
    gates = {
        "stage10_9_route_passed": _stage10_9_passes(),
        "stage10_10_hardening_passed": _stage10_10_passes(),
        "selected_route_preserved": _read_json(STAGE10_9_GATE).get("selected_route") == "presubmission_query_author_review_required",
        "external_contact_not_sent": _read_json(STAGE10_9_GATE).get("external_contact_status") == "not_sent"
        and _read_json(STAGE10_10_GATE).get("external_contact_status") == "not_sent",
        "author_review_required": bool(required_checklist) and any(row["status"] == "author_required" for row in checklist),
        "boundary_scan_passes": all(row["status"] == "pass" for row in boundary),
        "safe_query_checks_pass": all(safe_query.values()),
        "old_package_contact_forbidden": patch_decisions.get("Stage 9.29 package alone as EIC basis", {}).get("decision") == "forbid",
        "optional_strengthening_not_blocking": all(
            row.get("status") == "not_blocking"
            for row in patch_rows
            if row.get("priority") == "optional_strengthening"
        ),
    }
    return {
        "stage": "10.11",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "selected_route": "presubmission_query_author_review_required",
        "external_contact_status": "not_sent",
        "gates": gates,
        "safe_query_checks": safe_query,
        "summary_metrics": {
            "author_review_item_count": len(checklist),
            "required_author_review_item_count": len(required_checklist),
            "author_action_item_count": len(author_required),
            "boundary_count": len(boundary),
            "boundary_pass_count": sum(row["status"] == "pass" for row in boundary),
            "packet_surface_count": len(packet_manifest_rows()),
        },
        "outputs": {
            "author_review_checklist": _rel(AUTHOR_CHECKLIST),
            "packet_manifest": _rel(PACKET_MANIFEST),
            "clean_query": _rel(CLEAN_QUERY),
            "author_decision_brief": _rel(DECISION_BRIEF),
            "boundary_scan": _rel(BOUNDARY_SCAN),
            "gate_report": _rel(GATE_REPORT),
        },
        "interpretation_boundary": (
            "Stage 10.11 is an author-review readiness step only. It does not send any external message, "
            "does not create new evidence, and does not alter the Stage 10 method claims."
        ),
        "next_phase": "Author review and optional EIC presubmission contact",
    }


def run_stage10_11() -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report = validate_stage10_11()
    _write_text(CLEAN_QUERY, clean_query_text())
    _write_tsv(AUTHOR_CHECKLIST, checklist_rows(), CHECKLIST_FIELDS)
    _write_tsv(PACKET_MANIFEST, packet_manifest_rows(), PACKET_FIELDS)
    _write_tsv(BOUNDARY_SCAN, boundary_rows(), BOUNDARY_FIELDS)
    _write_text(DECISION_BRIEF, decision_brief_text(report))
    _write_json(GATE_REPORT, report)
    _write_text(DOC_PATH, doc_text(report))
    _update_memory(report)
    return report


if __name__ == "__main__":
    print(json.dumps(run_stage10_11(), indent=2, sort_keys=True))
