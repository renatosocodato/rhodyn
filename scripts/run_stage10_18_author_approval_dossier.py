"""Assemble the Stage 10.18 corresponding-author approval dossier.

Stage 10.18 consolidates the polished presubmission query, one-page pitch,
route recommendation, author-only decisions, and no-send boundaries into a
single approval handoff. It does not approve, send, upload, add evidence, or
invent author metadata.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage10_author_approval_dossier"
DOC_PATH = ROOT / "docs" / "stage10_18_author_approval_dossier.md"
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"

STAGE10_15_GATE = ROOT / "case_studies" / "stage10_author_visual_review_packet" / "stage10_15_gate_report.json"
STAGE10_16_GATE = ROOT / "case_studies" / "stage10_route_decision_triage" / "stage10_16_gate_report.json"
STAGE10_17_GATE = ROOT / "case_studies" / "stage10_message_integrity" / "stage10_17_gate_report.json"
AUTHOR_VISUAL_PACKET = (
    ROOT / "case_studies" / "stage10_author_visual_review_packet" / "stage10_15_author_visual_review_packet.md"
)
ROUTE_RECOMMENDATION = (
    ROOT / "case_studies" / "stage10_route_decision_triage" / "stage10_16_route_recommendation.md"
)
POLISHED_QUERY = (
    ROOT
    / "case_studies"
    / "stage10_message_integrity"
    / "stage10_17_presubmission_query_polished_AUTHOR_REVIEW_REQUIRED.md"
)
POLISHED_PITCH = ROOT / "case_studies" / "stage10_message_integrity" / "stage10_17_one_page_pitch_polished.md"
FIGURE_CONTACT_SHEET = (
    ROOT
    / "case_studies"
    / "stage10_rendered_figure_visual_qc"
    / "stage10_14_review_render_contact_sheet.png"
)

DOSSIER = OUTPUT_DIR / "stage10_18_corresponding_author_approval_dossier_AUTHOR_ACTION_REQUIRED.md"
CHECKLIST = OUTPUT_DIR / "stage10_18_corresponding_author_approval_checklist.tsv"
ROUTE_LOCK = OUTPUT_DIR / "stage10_18_submission_route_lock.tsv"
MANIFEST = OUTPUT_DIR / "stage10_18_dossier_manifest.tsv"
BOUNDARY_SCAN = OUTPUT_DIR / "stage10_18_no_send_boundary_scan.tsv"
GATE_REPORT = OUTPUT_DIR / "stage10_18_gate_report.json"

CHECKLIST_FIELDS = ["item_id", "decision_item", "required", "current_status", "evidence", "author_action"]
ROUTE_FIELDS = ["route", "local_status", "risk_position", "author_action", "send_status"]
MANIFEST_FIELDS = ["surface", "path", "role", "exists", "bytes", "sha256", "author_action", "send_surface"]
BOUNDARY_FIELDS = ["boundary_id", "boundary", "status", "evidence", "action_if_failed"]

LOCAL_PATH_PATTERNS = ["/" + "Users/", "/" + "Volumes/", "Library/" + "LaunchAgents"]
TOKEN_PATTERNS = [
    r"\b" + "sk-" + r"[A-Za-z0-9_-]{10,}",
    r"\b" + "ghp" + r"_[A-Za-z0-9_]{10,}",
    r"\b" + "github" + r"_pat_[A-Za-z0-9_]{10,}",
    r"\b(API_KEY|TOKEN|SECRET|PASSWORD)\b",
    r"BEGIN (RSA|OPENSSH|PRIVATE)",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _write_tsv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _safe_text(paths: list[Path]) -> tuple[bool, list[str]]:
    hits: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            hits.append(f"missing::{_rel(path)}")
            continue
        body = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in LOCAL_PATH_PATTERNS:
            if pattern in body:
                hits.append(f"{_rel(path)}::{pattern}")
        for pattern in TOKEN_PATTERNS:
            if re.search(pattern, body):
                hits.append(f"{_rel(path)}::{pattern}")
    return not hits, hits


def checklist_rows() -> list[dict[str, str]]:
    return [
        {
            "item_id": "CAA-001",
            "decision_item": "Approve the presubmission route or choose an alternative",
            "required": "yes",
            "current_status": "author_required",
            "evidence": "Stage 10.16 recommends presubmission after author approval",
            "author_action": "Choose presubmission query, full submission, delay for new validation, or venue pivot.",
        },
        {
            "item_id": "CAA-002",
            "decision_item": "Approve exact query text",
            "required": "yes",
            "current_status": "author_required",
            "evidence": "Stage 10.17 polished query is concise and boundary-scanned",
            "author_action": "Edit or approve the polished query before any external message.",
        },
        {
            "item_id": "CAA-003",
            "decision_item": "Approve one-page pitch use",
            "required": "yes",
            "current_status": "author_required",
            "evidence": "Stage 10.17 polished pitch is candidate-only",
            "author_action": "Decide whether to attach, paste, shorten, or omit the pitch.",
        },
        {
            "item_id": "CAA-004",
            "decision_item": "Complete sender identity and signature",
            "required": "yes",
            "current_status": "author_required",
            "evidence": "Polished query retains the corresponding-author placeholder",
            "author_action": "Fill name, affiliation, account, address, and signature outside repository automation.",
        },
        {
            "item_id": "CAA-005",
            "decision_item": "Approve figure inclusion status",
            "required": "yes",
            "current_status": "author_required",
            "evidence": "Stage 10.14 readable figures and contact sheet exist",
            "author_action": "Decide whether figures are referenced only, attached, or held for full submission.",
        },
        {
            "item_id": "CAA-006",
            "decision_item": "Retain method-first framing",
            "required": "yes",
            "current_status": "ready_for_author_review",
            "evidence": "Query and pitch foreground residence-state inference before software surfaces",
            "author_action": "Do not weaken the method object into a software-wrapper story.",
        },
        {
            "item_id": "CAA-007",
            "decision_item": "Retain boundaries against overclaiming",
            "required": "yes",
            "current_status": "ready_for_author_review",
            "evidence": "Query and pitch preserve non-universal and non-mechanism language",
            "author_action": "Keep limits visible after any shortening.",
        },
        {
            "item_id": "CAA-008",
            "decision_item": "Decide whether to delay for prospective collaborator-blind validation",
            "required": "no",
            "current_status": "optional_new_evidence",
            "evidence": "Stage 10.12 and 10.16 retain this as optional new evidence",
            "author_action": "Delay only if prioritizing a stronger direct-submission posture.",
        },
        {
            "item_id": "CAA-009",
            "decision_item": "Confirm external contact remains manual",
            "required": "yes",
            "current_status": "not_sent",
            "evidence": "Stage 10.15, 10.16, 10.17, and 10.18 retain no-send state",
            "author_action": "Send only manually after all required approvals are complete.",
        },
    ]


def route_lock_rows() -> list[dict[str, str]]:
    return [
        {
            "route": "presubmission_query",
            "local_status": "recommended_after_author_approval",
            "risk_position": "lowest local editorial-risk route from Stage 10.16",
            "author_action": "Approve exact text and sender identity before manual send.",
            "send_status": "not_sent",
        },
        {
            "route": "full_submission",
            "local_status": "author_override_only",
            "risk_position": "medium residual risk remains without prospective collaborator-blind validation",
            "author_action": "Use only if PI accepts recorded risk and bypasses presubmission.",
            "send_status": "not_sent",
        },
        {
            "route": "delay_for_new_external_validation",
            "local_status": "optional_new_evidence",
            "risk_position": "would strengthen direct-submission posture but is not locally closable",
            "author_action": "Choose separately if delaying for collaborator-blind evidence.",
            "send_status": "not_sent",
        },
        {
            "route": "venue_pivot",
            "local_status": "fallback_not_current_route",
            "risk_position": "kept for editor feedback or PI venue decision",
            "author_action": "Use only after explicit venue decision.",
            "send_status": "not_sent",
        },
    ]


def dossier_text() -> str:
    return """# Stage 10.18 corresponding-author approval dossier. Author action required. Do not send from repository.

## Local recommendation

Use the presubmission query route only after corresponding-author approval. The current local route remains presubmission inquiry, not direct full submission, not venue pivot, and not a request to send from repository automation.

## Materials for author review

- Polished query. `case_studies/stage10_message_integrity/stage10_17_presubmission_query_polished_AUTHOR_REVIEW_REQUIRED.md`
- Polished one-page pitch. `case_studies/stage10_message_integrity/stage10_17_one_page_pitch_polished.md`
- Route recommendation. `case_studies/stage10_route_decision_triage/stage10_16_route_recommendation.md`
- Visual-review packet. `case_studies/stage10_author_visual_review_packet/stage10_15_author_visual_review_packet.md`
- Figure contact sheet. `case_studies/stage10_rendered_figure_visual_qc/stage10_14_review_render_contact_sheet.png`
- Approval checklist. `case_studies/stage10_author_approval_dossier/stage10_18_corresponding_author_approval_checklist.tsv`
- Route lock. `case_studies/stage10_author_approval_dossier/stage10_18_submission_route_lock.tsv`

## Approval boundary

The repository can prepare a decision-safe dossier, but it cannot approve the sender identity, choose the route, submit a presubmission inquiry, complete journal metadata, or represent corresponding-author consent. Those decisions remain outside the code and must be made by the author team.

## Scientific boundary

The query and pitch should preserve the method-first claim. RhoDyn is presented as a residence-state inference method for live-cell perturbation data, supported by named baselines, public biological breadth, no-retuning held-out validation, readable method figures, and reproducible software surfaces. It does not claim that every live-cell system contains a residence regime, that declared windows are mechanisms, or that prospective blinded collaborator validation has already been completed.
"""


def manifest_rows() -> list[dict[str, Any]]:
    surfaces = [
        (
            "polished_query",
            POLISHED_QUERY,
            "candidate presubmission query",
            "approve exact wording and sender identity",
            "candidate_after_author_approval",
        ),
        (
            "polished_pitch",
            POLISHED_PITCH,
            "candidate one-page pitch",
            "decide whether to attach, paste, shorten, or omit",
            "candidate_after_author_approval",
        ),
        ("route_recommendation", ROUTE_RECOMMENDATION, "Stage 10.16 route recommendation", "approve or override route", "no"),
        ("author_visual_packet", AUTHOR_VISUAL_PACKET, "Stage 10.15 visual-review packet", "review support surfaces", "no"),
        ("figure_contact_sheet", FIGURE_CONTACT_SHEET, "readable Stage 10 figure contact sheet", "review figures visually", "no"),
        ("approval_dossier", DOSSIER, "Stage 10.18 approval dossier", "read before author decision", "no"),
        ("approval_checklist", CHECKLIST, "corresponding-author approval checklist", "complete required rows", "no"),
        ("route_lock", ROUTE_LOCK, "route status and alternatives", "select or override route", "no"),
        ("boundary_scan", BOUNDARY_SCAN, "no-send and claim-boundary scan", "review pass/fail state", "no"),
        ("stage10_17_gate", STAGE10_17_GATE, "message-integrity parent gate", "verify parent state", "no"),
    ]
    rows: list[dict[str, Any]] = []
    for surface, path, role, author_action, send_surface in surfaces:
        exists = path.exists() and path.is_file()
        rows.append(
            {
                "surface": surface,
                "path": _rel(path),
                "role": role,
                "exists": "yes" if exists else "no",
                "bytes": path.stat().st_size if exists else 0,
                "sha256": _sha256(path) if exists else "",
                "author_action": author_action,
                "send_surface": send_surface,
            }
        )
    return rows


def boundary_rows(
    stage10_15: dict[str, Any],
    stage10_16: dict[str, Any],
    stage10_17: dict[str, Any],
    checklist: list[dict[str, str]],
    routes: list[dict[str, str]],
    manifest: list[dict[str, Any]],
) -> list[dict[str, str]]:
    query = POLISHED_QUERY.read_text(encoding="utf-8") if POLISHED_QUERY.exists() else ""
    pitch = POLISHED_PITCH.read_text(encoding="utf-8") if POLISHED_PITCH.exists() else ""
    dossier = DOSSIER.read_text(encoding="utf-8") if DOSSIER.exists() else ""
    safe, hits = _safe_text([POLISHED_QUERY, POLISHED_PITCH, DOSSIER])
    required_author_rows = [row for row in checklist if row["required"] == "yes" and row["current_status"] == "author_required"]
    routes_not_sent = all(row["send_status"] == "not_sent" for row in routes)
    return [
        {
            "boundary_id": "B-001",
            "boundary": "Parent Stage 10.15, 10.16, and 10.17 gates pass",
            "status": "pass"
            if stage10_15.get("status") == stage10_16.get("status") == stage10_17.get("status") == "pass"
            else "fail",
            "evidence": "parent gate reports",
            "action_if_failed": "Regenerate or repair the failing parent stage before author approval.",
        },
        {
            "boundary_id": "B-002",
            "boundary": "External contact remains unsent across the handoff",
            "status": "pass"
            if stage10_15.get("external_contact_status")
            == stage10_16.get("external_contact_status")
            == stage10_17.get("external_contact_status")
            == "not_sent"
            and routes_not_sent
            else "fail",
            "evidence": "parent gates and route lock",
            "action_if_failed": "Stop and restore no-send status.",
        },
        {
            "boundary_id": "B-003",
            "boundary": "Presubmission remains recommended only after author approval",
            "status": "pass"
            if stage10_16.get("recommendation") == "presubmission_query_after_author_approval"
            and any(row["route"] == "presubmission_query" and row["local_status"] == "recommended_after_author_approval" for row in routes)
            else "fail",
            "evidence": "Stage 10.16 recommendation and Stage 10.18 route lock",
            "action_if_failed": "Restore route lock before approval review.",
        },
        {
            "boundary_id": "B-004",
            "boundary": "Corresponding-author identity and send decisions remain explicit author actions",
            "status": "pass" if len(required_author_rows) >= 5 and "corresponding-author approval" in dossier else "fail",
            "evidence": "approval checklist and dossier",
            "action_if_failed": "Restore required author-action rows.",
        },
        {
            "boundary_id": "B-005",
            "boundary": "Polished query retains the author placeholder",
            "status": "pass"
            if "[Author name, affiliation, and contact details to be completed by the corresponding author]" in query
            else "fail",
            "evidence": "polished query",
            "action_if_failed": "Restore the author placeholder and remove invented metadata.",
        },
        {
            "boundary_id": "B-006",
            "boundary": "Overclaim boundaries remain visible",
            "status": "pass"
            if "does not claim that every live-cell system contains a residence regime" in query
            and "declared windows are mechanisms" in query
            and "not a prospective blinded collaborator study" in pitch
            else "fail",
            "evidence": "polished query and pitch",
            "action_if_failed": "Restore non-universal, non-mechanism, and prospective-validation boundaries.",
        },
        {
            "boundary_id": "B-007",
            "boundary": "No local path or credential-like pattern appears in outgoing candidate text",
            "status": "pass" if safe else "fail",
            "evidence": "hits=" + json.dumps(hits),
            "action_if_failed": "Remove local path or credential-like text before author review.",
        },
        {
            "boundary_id": "B-008",
            "boundary": "All dossier surfaces exist and are checksum-backed",
            "status": "pass" if all(row["exists"] == "yes" and row["sha256"] for row in manifest) else "fail",
            "evidence": "Stage 10.18 manifest",
            "action_if_failed": "Regenerate missing surfaces.",
        },
        {
            "boundary_id": "B-009",
            "boundary": "Stage 10.18 adds no data, figures, benchmarks, manuscript claims, upload, or external contact",
            "status": "pass",
            "evidence": "dossier-only assembly from existing Stage 10 surfaces",
            "action_if_failed": "Move new evidence into a separate authorized phase.",
        },
    ]


def _write_doc(gate: dict[str, Any]) -> None:
    body = f"""# Stage 10.18 corresponding-author approval dossier

Stage 10.18 assembles a no-send approval dossier for the selected presubmission route. It consolidates the polished query, one-page pitch, route lock, approval checklist, manifest, boundary scan, and parent gate state so the corresponding author can make the final route and sender decision outside repository automation.

## Status

`{gate["status"]}`

## Outputs

- Approval dossier. `{gate["outputs"]["dossier"]}`
- Approval checklist. `{gate["outputs"]["checklist"]}`
- Route lock. `{gate["outputs"]["route_lock"]}`
- Dossier manifest. `{gate["outputs"]["manifest"]}`
- Boundary scan. `{gate["outputs"]["boundary_scan"]}`
- Gate report. `{gate["outputs"]["gate_report"]}`

## Boundary

External contact remains `{gate["external_contact_status"]}`. The current local recommendation is a presubmission query after author approval, but route selection, sender identity, and actual sending remain corresponding-author actions.
"""
    _write_text(DOC_PATH, body)


def _update_memory(gate: dict[str, Any]) -> None:
    memory = _read_json(MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 10.18 author approval dossier complete; external contact remains not sent"
    current["current_gate"] = "Stage 10.18 author approval dossier complete; external contact remains not sent"
    current["stage10_active_gate"] = "Stage 10.18 author approval dossier complete; external contact remains not sent"
    current["next_stage"] = "Corresponding-author signoff and manual external action outside repository, or a new-evidence delay decision"
    current["after_stage10_18_author_approval_dossier"] = (
        "Stage 10.18 assembled the no-send corresponding-author approval dossier, route lock, checklist, manifest, "
        "and boundary scan. It preserves the presubmission recommendation after author approval and keeps all external "
        "contact outside repository automation."
    )

    stage10 = next((stage for stage in memory.get("stage_lock", []) if stage.get("stage") == 10), None)
    if not isinstance(stage10, dict):
        _write_json(MEMORY_PATH, memory)
        return
    artifacts = set(stage10.get("artifacts", []))
    artifacts.update(
        [
            _rel(DOC_PATH),
            "scripts/run_stage10_18_author_approval_dossier.py",
            "tests/test_stage10_18_author_approval_dossier.py",
            _rel(DOSSIER),
            _rel(CHECKLIST),
            _rel(ROUTE_LOCK),
            _rel(MANIFEST),
            _rel(BOUNDARY_SCAN),
            _rel(GATE_REPORT),
        ]
    )
    stage10["artifacts"] = sorted(artifacts)
    stage10["status"] = "stage10_18_complete_author_approval_dossier"
    stage10["current_gate"] = "Stage 10.18 author approval dossier complete; external contact remains not sent"
    subphases = stage10.setdefault("subphases", [])
    by_id = {entry.get("id"): entry for entry in subphases if isinstance(entry, dict)}
    by_id["10.18"] = {
        "id": "10.18",
        "name": "No-send corresponding-author approval dossier",
        "status": "complete_author_approval_dossier",
        "goal": "Consolidate the selected route, polished text, author-only decisions, and no-send boundaries for corresponding-author signoff.",
        "gate": "Approval dossier, route lock, checklist, manifest, and boundary scan pass without sending or adding new evidence.",
        "evidence": _rel(GATE_REPORT),
    }
    stage10["subphases"] = [by_id[key] for key in sorted(by_id, key=lambda value: tuple(int(part) for part in value.split(".")))]
    _write_json(MEMORY_PATH, memory)


def run_stage10_18() -> dict[str, Any]:
    stage10_15 = _read_json(STAGE10_15_GATE)
    stage10_16 = _read_json(STAGE10_16_GATE)
    stage10_17 = _read_json(STAGE10_17_GATE)

    _write_text(DOSSIER, dossier_text())
    checklist = checklist_rows()
    routes = route_lock_rows()
    _write_tsv(CHECKLIST, checklist, CHECKLIST_FIELDS)
    _write_tsv(ROUTE_LOCK, routes, ROUTE_FIELDS)

    preliminary_manifest = manifest_rows()
    preliminary_boundary = boundary_rows(stage10_15, stage10_16, stage10_17, checklist, routes, preliminary_manifest)
    _write_tsv(BOUNDARY_SCAN, preliminary_boundary, BOUNDARY_FIELDS)
    manifest = manifest_rows()
    boundary = boundary_rows(stage10_15, stage10_16, stage10_17, checklist, routes, manifest)
    _write_tsv(BOUNDARY_SCAN, boundary, BOUNDARY_FIELDS)
    manifest = manifest_rows()
    _write_tsv(MANIFEST, manifest, MANIFEST_FIELDS)

    required_author_count = sum(row["required"] == "yes" and row["current_status"] == "author_required" for row in checklist)
    gates = {
        "parent_gates_pass": stage10_15.get("status") == stage10_16.get("status") == stage10_17.get("status") == "pass",
        "external_contact_not_sent": all(
            gate.get("external_contact_status") == "not_sent" for gate in [stage10_15, stage10_16, stage10_17]
        ),
        "presubmission_route_locked_for_author_approval": stage10_16.get("recommendation")
        == "presubmission_query_after_author_approval",
        "approval_dossier_exists": DOSSIER.exists(),
        "manifest_all_exists": all(row["exists"] == "yes" and row["sha256"] for row in manifest),
        "boundary_scan_all_pass": all(row["status"] == "pass" for row in boundary),
        "author_actions_retained": required_author_count >= 5,
        "route_lock_not_sent": all(row["send_status"] == "not_sent" for row in routes),
        "no_new_science_claims_or_contact": True,
    }
    gate = {
        "stage": "10.18",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "gates": gates,
        "external_contact_status": "not_sent",
        "recommendation": "presubmission_query_after_corresponding_author_approval",
        "summary_metrics": {
            "checklist_count": len(checklist),
            "required_author_action_count": required_author_count,
            "route_count": len(routes),
            "manifest_row_count": len(manifest),
            "boundary_count": len(boundary),
            "boundary_pass_count": sum(row["status"] == "pass" for row in boundary),
        },
        "outputs": {
            "dossier": _rel(DOSSIER),
            "checklist": _rel(CHECKLIST),
            "route_lock": _rel(ROUTE_LOCK),
            "manifest": _rel(MANIFEST),
            "boundary_scan": _rel(BOUNDARY_SCAN),
            "gate_report": _rel(GATE_REPORT),
            "doc": _rel(DOC_PATH),
        },
        "interpretation_boundary": (
            "Stage 10.18 is a no-send author-approval dossier. It consolidates existing Stage 10 route, message, "
            "figure-review, and boundary surfaces for corresponding-author signoff, but does not approve, send, upload, "
            "add evidence, or create new manuscript claims."
        ),
    }
    _write_json(GATE_REPORT, gate)
    _write_doc(gate)
    _update_memory(gate)
    return gate


def main() -> int:
    gate = run_stage10_18()
    print(json.dumps(gate, indent=2))
    return 0 if gate["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
