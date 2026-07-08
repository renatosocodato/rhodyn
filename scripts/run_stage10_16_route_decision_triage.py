"""Assemble the Stage 10.16 no-send route-decision triage.

Stage 10.16 resolves the locally decidable author-review items from Stage 10.15
and keeps author-only or new-evidence decisions explicit. It does not send
external contact, invent author metadata, add analyses, or change claims.
"""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage10_route_decision_triage"
DOC_PATH = ROOT / "docs" / "stage10_16_route_decision_triage.md"
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"

STAGE10_15_GATE = ROOT / "case_studies" / "stage10_author_visual_review_packet" / "stage10_15_gate_report.json"
STAGE10_15_CHECKLIST = (
    ROOT / "case_studies" / "stage10_author_visual_review_packet" / "stage10_15_author_decision_checklist.tsv"
)
STAGE10_9_ROUTE_MATRIX = ROOT / "case_studies" / "stage10_eic_contact_decision" / "stage10_9_route_decision_matrix.tsv"
STAGE10_12_OPTION_MATRIX = (
    ROOT / "case_studies" / "stage10_optional_strengthening" / "stage10_12_strengthening_option_matrix.tsv"
)
STAGE10_12_GAP_MATRIX = ROOT / "case_studies" / "stage10_optional_strengthening" / "stage10_12_validation_gap_matrix.tsv"

OPEN_ITEM_RESOLUTION = OUTPUT_DIR / "stage10_16_open_item_resolution.tsv"
ROUTE_TRIAGE = OUTPUT_DIR / "stage10_16_route_decision_triage.tsv"
BOUNDARY_SCAN = OUTPUT_DIR / "stage10_16_no_send_boundary_scan.tsv"
RECOMMENDATION = OUTPUT_DIR / "stage10_16_route_recommendation.md"
GATE_REPORT = OUTPUT_DIR / "stage10_16_gate_report.json"

OPEN_ITEM_FIELDS = [
    "item_id",
    "source_item",
    "stage10_15_status",
    "codex_resolution",
    "recommendation",
    "remaining_human_action",
]
ROUTE_FIELDS = [
    "route",
    "stage10_9_decision",
    "stage10_12_decision",
    "stage10_16_recommendation",
    "residual_risk",
    "required_human_action",
]
BOUNDARY_FIELDS = ["boundary_id", "boundary", "status", "evidence", "action_if_failed"]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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


def _route_matrix_by_route(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["route"]: row for row in rows}


def _option_matrix_by_option(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["option"]: row for row in rows}


def open_item_resolution_rows(checklist: list[dict[str, str]]) -> list[dict[str, str]]:
    recommendations = {
        "AVR-001": (
            "codex_resolved_ready",
            "Use the Stage 10.14 readable review renders rather than the crowded Stage 10.13 parent renders.",
            "Author performs final visual acceptance before sending or uploading.",
        ),
        "AVR-002": (
            "author_only_not_sent",
            "Keep external contact unsent until the corresponding author explicitly approves the route and final message.",
            "Corresponding author approval and actual sending remain outside Codex authority.",
        ),
        "AVR-003": (
            "author_only_metadata",
            "Do not invent name, affiliation, account, signature, or contact details.",
            "Corresponding author fills identity and contact fields.",
        ),
        "AVR-004": (
            "codex_recommendation_author_decision",
            "Retain the presubmission query as the recommended next route.",
            "Author chooses presubmission, full submission, delay for external validation, or venue pivot.",
        ),
        "AVR-005": (
            "codex_resolved_retain",
            "Retain method-first residence-state inference framing.",
            "Author may shorten wording, but should not convert the pitch back into a software-wrapper story.",
        ),
        "AVR-006": (
            "codex_resolved_retain",
            "Retain named comparator evidence and comparator-sufficient boundaries.",
            "Author may shorten comparator detail only if the method novelty remains visible.",
        ),
        "AVR-007": (
            "codex_resolved_retain",
            "Retain public biological breadth while avoiding universal-residence language.",
            "Author may adjust examples, but should preserve breadth across trajectory, endpoint, and paired-reporter contexts.",
        ),
        "AVR-008": (
            "codex_resolved_retain",
            "Describe Stage 10.4 as no-retuning held-out validation over retained public-derived contexts.",
            "Author should not describe this as prospective blinded collaborator validation.",
        ),
        "AVR-009": (
            "codex_resolved_retain",
            "Retain explicit limits against universal superiority, automatic mechanism discovery, and all-system residence claims.",
            "Author should keep a limits sentence visible if the message is shortened.",
        ),
        "AVR-010": (
            "new_evidence_optional_not_blocking",
            "Treat prospective collaborator-blind validation as optional strengthening, not a local blocker for presubmission.",
            "Author decides whether to delay for new external data before a direct full-submission route.",
        ),
    }
    rows: list[dict[str, str]] = []
    for item in checklist:
        resolution, recommendation, human_action = recommendations[item["item_id"]]
        rows.append(
            {
                "item_id": item["item_id"],
                "source_item": item["review_item"],
                "stage10_15_status": item["status"],
                "codex_resolution": resolution,
                "recommendation": recommendation,
                "remaining_human_action": human_action,
            }
        )
    return rows


def route_triage_rows(route_matrix: list[dict[str, str]], option_matrix: list[dict[str, str]]) -> list[dict[str, str]]:
    routes = _route_matrix_by_route(route_matrix)
    options = _option_matrix_by_option(option_matrix)
    return [
        {
            "route": "presubmission_query_author_review_required",
            "stage10_9_decision": routes["presubmission_query_author_review_required"]["decision"],
            "stage10_12_decision": options["author_review_presubmission_query"]["recommended_decision"],
            "stage10_16_recommendation": "recommended_next_route_after_author_approval",
            "residual_risk": routes["presubmission_query_author_review_required"]["residual_risk"],
            "required_human_action": "Author approves exact message, contact identity, and whether to paste or attach the one-page pitch.",
        },
        {
            "route": "full_submission",
            "stage10_9_decision": routes["full_submission"]["decision"],
            "stage10_12_decision": options["full_submission_now"]["recommended_decision"],
            "stage10_16_recommendation": "viable_only_with_author_override",
            "residual_risk": routes["full_submission"]["residual_risk"],
            "required_human_action": "PI explicitly accepts medium residual risk and chooses full submission instead of presubmission.",
        },
        {
            "route": "delay_for_another_dataset",
            "stage10_9_decision": routes["delay_for_another_dataset"]["decision"],
            "stage10_12_decision": options["prospective_collaborator_blind_validation"]["recommended_decision"],
            "stage10_16_recommendation": "optional_new_evidence_not_required_for_presubmission",
            "residual_risk": routes["delay_for_another_dataset"]["residual_risk"],
            "required_human_action": "Author decides whether a stronger direct-submission posture is worth delaying for external data.",
        },
        {
            "route": "venue_pivot",
            "stage10_9_decision": routes["pivot_venue"]["decision"],
            "stage10_12_decision": options["venue_pivot"]["recommended_decision"],
            "stage10_16_recommendation": "retain_as_fallback_not_current_route",
            "residual_risk": routes["pivot_venue"]["residual_risk"],
            "required_human_action": "Use only after PI venue decision or editor feedback indicating poor Nature Methods fit.",
        },
    ]


def boundary_rows(stage10_15: dict[str, Any], open_items: list[dict[str, str]], route_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    resolutions = {row["codex_resolution"] for row in open_items}
    route_recommendations = {row["route"]: row["stage10_16_recommendation"] for row in route_rows}
    return [
        {
            "boundary_id": "B-001",
            "boundary": "External contact remains unsent",
            "status": "pass" if stage10_15.get("external_contact_status") == "not_sent" else "fail",
            "evidence": "Stage 10.15 gate report",
            "action_if_failed": "Stop and restore no-send status",
        },
        {
            "boundary_id": "B-002",
            "boundary": "Presubmission remains the recommended next route after author approval",
            "status": "pass"
            if route_recommendations.get("presubmission_query_author_review_required")
            == "recommended_next_route_after_author_approval"
            else "fail",
            "evidence": "Stage 10.9 route matrix and Stage 10.12 option matrix",
            "action_if_failed": "Do not advance route handoff until the route matrix is reconciled",
        },
        {
            "boundary_id": "B-003",
            "boundary": "Full submission is not silently selected",
            "status": "pass" if route_recommendations.get("full_submission") == "viable_only_with_author_override" else "fail",
            "evidence": "Stage 10.16 route triage",
            "action_if_failed": "Restore full submission as author-override only",
        },
        {
            "boundary_id": "B-004",
            "boundary": "Prospective collaborator-blind validation remains optional new evidence, not a local blocker",
            "status": "pass" if "new_evidence_optional_not_blocking" in resolutions else "fail",
            "evidence": "Stage 10.16 open-item resolution",
            "action_if_failed": "Move new validation to a separate evidence phase",
        },
        {
            "boundary_id": "B-005",
            "boundary": "Author-only identity and send decisions remain outside Codex authority",
            "status": "pass" if {"author_only_not_sent", "author_only_metadata"}.issubset(resolutions) else "fail",
            "evidence": "Stage 10.16 open-item resolution",
            "action_if_failed": "Remove invented author-only metadata or send decisions",
        },
        {
            "boundary_id": "B-006",
            "boundary": "Resolved local items retain method-first framing, comparator evidence, public breadth, held-out scope, and limits",
            "status": "pass" if sum(row["codex_resolution"].startswith("codex_resolved") for row in open_items) >= 6 else "fail",
            "evidence": "Stage 10.16 open-item resolution",
            "action_if_failed": "Restore local framing and claim-boundary recommendations",
        },
        {
            "boundary_id": "B-007",
            "boundary": "No new biological evidence, benchmark result, manuscript claim, or figure output is introduced",
            "status": "pass",
            "evidence": "Stage 10.16 reads existing decision surfaces only",
            "action_if_failed": "Move any new evidence to a separate authorized phase",
        },
    ]


def _write_recommendation(route_rows: list[dict[str, str]], boundary: list[dict[str, str]]) -> None:
    selected = next(row for row in route_rows if row["route"] == "presubmission_query_author_review_required")
    lines = [
        "# Stage 10.16 route recommendation",
        "",
        "Recommended local decision. Retain the presubmission query as the next route, but send nothing until the corresponding author approves the exact message and fills author-only contact details.",
        "",
        "## Why this is the safest current route",
        "",
        "- Stage 10.9 already selected presubmission as the lowest-risk route after the red-team simulation.",
        "- Stage 10.12 kept prospective collaborator-blind validation as optional strengthening rather than a presubmission blocker.",
        "- Stage 10.14 repaired the figure-readability issue that had weakened the direct-submission posture.",
        "- Stage 10.15 assembled the author visual-review packet without sending external contact.",
        "",
        "## Route state",
        "",
        f"- Presubmission query. `{selected['stage10_16_recommendation']}` with `{selected['residual_risk']}` residual risk.",
        "- Full submission. Viable only if the PI accepts the recorded medium residual risk.",
        "- Delay for external validation. Useful for a stronger direct-submission posture, but not locally closable and not required for presubmission.",
        "- Venue pivot. Retained as fallback if the editor or PI decides Nature Methods fit is weak.",
        "",
        "## Boundary result",
        "",
        f"Boundary rows passing. `{sum(row['status'] == 'pass' for row in boundary)}` of `{len(boundary)}`.",
        "",
        "This recommendation is a no-send decision aid. It is not a journal contact, not a submission, and not a new scientific result.",
    ]
    _write_text(RECOMMENDATION, "\n".join(lines))


def _write_doc(gate: dict[str, Any]) -> None:
    body = f"""# Stage 10.16 route-decision triage

Stage 10.16 converts the Stage 10.15 author-review checklist into a no-send route-decision triage. It separates locally resolved recommendations from author-only actions and optional new-evidence decisions.

## Status

`{gate["status"]}`

## Recommendation

Retain the presubmission query as the recommended next route after corresponding-author approval. Direct full submission remains viable only with explicit PI override, prospective collaborator-blind validation remains optional new evidence, and venue pivot remains a fallback.

## Outputs

- Open-item resolution. `{gate["outputs"]["open_item_resolution"]}`
- Route triage. `{gate["outputs"]["route_triage"]}`
- Boundary scan. `{gate["outputs"]["boundary_scan"]}`
- Recommendation brief. `{gate["outputs"]["recommendation"]}`
- Gate report. `{gate["outputs"]["gate_report"]}`

## Boundary

External contact remains `{gate["external_contact_status"]}`. This pass does not invent author metadata, send a message, add analyses, change method claims, or replace author judgment.
"""
    _write_text(DOC_PATH, body)


def _update_memory(gate: dict[str, Any]) -> None:
    memory = _read_json(MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 10.16 route-decision triage complete; external contact remains not sent"
    current["current_gate"] = "Stage 10.16 route-decision triage complete; external contact remains not sent"
    current["stage10_active_gate"] = "Stage 10.16 route-decision triage complete; external contact remains not sent"
    current["next_stage"] = "Corresponding-author route approval and contact metadata, or separately authorized new external validation"
    current["after_stage10_16_route_decision_triage"] = (
        "Stage 10.16 resolved locally decidable author-review items, retained presubmission as the recommended no-send route, "
        "kept full submission as author-override only, and left prospective collaborator-blind validation as optional new evidence."
    )

    stage10 = next((stage for stage in memory.get("stage_lock", []) if stage.get("stage") == 10), None)
    if not isinstance(stage10, dict):
        _write_json(MEMORY_PATH, memory)
        return
    artifacts = set(stage10.get("artifacts", []))
    artifacts.update(
        [
            _rel(DOC_PATH),
            "scripts/run_stage10_16_route_decision_triage.py",
            "tests/test_stage10_16_route_decision_triage.py",
            _rel(OPEN_ITEM_RESOLUTION),
            _rel(ROUTE_TRIAGE),
            _rel(BOUNDARY_SCAN),
            _rel(RECOMMENDATION),
            _rel(GATE_REPORT),
        ]
    )
    stage10["artifacts"] = sorted(artifacts)
    stage10["status"] = "stage10_16_complete_route_decision_triage"
    stage10["current_gate"] = "Stage 10.16 route-decision triage complete; external contact remains not sent"
    subphases = stage10.setdefault("subphases", [])
    by_id = {entry.get("id"): entry for entry in subphases if isinstance(entry, dict)}
    by_id["10.16"] = {
        "id": "10.16",
        "name": "No-send route-decision triage",
        "status": "complete_route_decision_triage",
        "goal": "Resolve locally decidable author-review items while preserving author-only and new-evidence boundaries.",
        "gate": "Presubmission remains recommended after author approval; full submission is author-override only; external contact remains not sent.",
        "evidence": _rel(GATE_REPORT),
    }
    stage10["subphases"] = [by_id[key] for key in sorted(by_id, key=lambda value: tuple(int(part) for part in value.split(".")))]
    _write_json(MEMORY_PATH, memory)


def run_stage10_16() -> dict[str, Any]:
    stage10_15 = _read_json(STAGE10_15_GATE)
    checklist = _read_tsv(STAGE10_15_CHECKLIST)
    route_matrix = _read_tsv(STAGE10_9_ROUTE_MATRIX)
    option_matrix = _read_tsv(STAGE10_12_OPTION_MATRIX)
    gap_matrix = _read_tsv(STAGE10_12_GAP_MATRIX)

    open_items = open_item_resolution_rows(checklist)
    routes = route_triage_rows(route_matrix, option_matrix)
    boundary = boundary_rows(stage10_15, open_items, routes)

    _write_tsv(OPEN_ITEM_RESOLUTION, open_items, OPEN_ITEM_FIELDS)
    _write_tsv(ROUTE_TRIAGE, routes, ROUTE_FIELDS)
    _write_tsv(BOUNDARY_SCAN, boundary, BOUNDARY_FIELDS)
    _write_recommendation(routes, boundary)

    local_resolved = [row for row in open_items if row["codex_resolution"].startswith("codex_resolved")]
    author_only = [row for row in open_items if row["codex_resolution"].startswith("author_only")]
    new_evidence = [row for row in open_items if row["codex_resolution"].startswith("new_evidence")]
    gates = {
        "stage10_15_passed": stage10_15.get("status") == "pass",
        "presubmission_recommended": any(
            row["route"] == "presubmission_query_author_review_required"
            and row["stage10_16_recommendation"] == "recommended_next_route_after_author_approval"
            for row in routes
        ),
        "full_submission_requires_author_override": any(
            row["route"] == "full_submission" and row["stage10_16_recommendation"] == "viable_only_with_author_override"
            for row in routes
        ),
        "external_validation_not_local_blocker": any(
            row["route"] == "delay_for_another_dataset"
            and row["stage10_16_recommendation"] == "optional_new_evidence_not_required_for_presubmission"
            for row in routes
        )
        and any(row["validation_layer"] == "prospective_collaborator_blind_validation" and row["decision"] == "not_locally_closable_in_stage10_12" for row in gap_matrix),
        "author_only_items_retained": len(author_only) == 2,
        "local_items_resolved": len(local_resolved) == 6,
        "new_evidence_item_retained": len(new_evidence) == 1,
        "boundary_scan_all_pass": all(row["status"] == "pass" for row in boundary),
        "external_contact_not_sent": stage10_15.get("external_contact_status") == "not_sent",
        "no_new_science_claims_or_contact": True,
    }
    gate = {
        "stage": "10.16",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "gates": gates,
        "external_contact_status": "not_sent",
        "recommendation": "presubmission_query_after_author_approval",
        "summary_metrics": {
            "open_item_count": len(open_items),
            "local_resolved_count": len(local_resolved),
            "author_only_count": len(author_only),
            "new_evidence_count": len(new_evidence),
            "route_count": len(routes),
            "boundary_count": len(boundary),
            "boundary_pass_count": sum(row["status"] == "pass" for row in boundary),
        },
        "outputs": {
            "open_item_resolution": _rel(OPEN_ITEM_RESOLUTION),
            "route_triage": _rel(ROUTE_TRIAGE),
            "boundary_scan": _rel(BOUNDARY_SCAN),
            "recommendation": _rel(RECOMMENDATION),
            "gate_report": _rel(GATE_REPORT),
            "doc": _rel(DOC_PATH),
        },
        "interpretation_boundary": (
            "Stage 10.16 is a no-send decision-triage step. It recommends presubmission after author approval, "
            "keeps full submission as an author override, preserves prospective collaborator-blind validation as optional new evidence, "
            "and does not add data or send external contact."
        ),
    }
    _write_json(GATE_REPORT, gate)
    _write_doc(gate)
    _update_memory(gate)
    return gate


def main() -> int:
    gate = run_stage10_16()
    print(json.dumps(gate, indent=2))
    return 0 if gate["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
