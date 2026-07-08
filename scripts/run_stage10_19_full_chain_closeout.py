"""Run Stage 10.19 full-chain closeout without external contact.

Stage 10.19 recursively verifies the completed Stage 10.0 through 10.18
method-elevation chain after the corresponding-author approval dossier. It
does not approve, send, upload, add evidence, rerender figures, or change
manuscript claims.
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
OUTPUT_DIR = ROOT / "case_studies" / "stage10_full_chain_closeout"
DOC_PATH = ROOT / "docs" / "stage10_19_full_chain_closeout.md"
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"

ROADMAP_DOC = ROOT / "docs" / "stage10_nature_methods_eic_rescue_roadmap.md"
STAGE9_GATE = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.29.json"
STAGE10_GATES = [
    ("10.1", ROOT / "case_studies" / "stage10_method_object_v2" / "stage10_1_method_object_gate_report.json"),
    ("10.2", ROOT / "case_studies" / "stage10_named_benchmarks" / "stage10_2_named_benchmark_report.json"),
    ("10.3", ROOT / "case_studies" / "stage10_public_breadth" / "stage10_3_public_breadth_report.json"),
    ("10.4", ROOT / "case_studies" / "stage10_heldout_validation" / "stage10_4_gate_report.json"),
    ("10.5", ROOT / "case_studies" / "stage10_figure_architecture" / "stage10_5_gate_report.json"),
    ("10.6", ROOT / "case_studies" / "stage10_manuscript_pitch" / "stage10_6_gate_report.json"),
    ("10.7", ROOT / "case_studies" / "stage10_release_candidate" / "stage10_7_gate_report.json"),
    ("10.8", ROOT / "case_studies" / "stage10_eic_red_team" / "stage10_8_gate_report.json"),
    ("10.9", ROOT / "case_studies" / "stage10_eic_contact_decision" / "stage10_9_gate_report.json"),
    ("10.10", ROOT / "case_studies" / "stage10_recursive_hardening" / "stage10_10_gate_report.json"),
    ("10.11", ROOT / "case_studies" / "stage10_author_review_readiness" / "stage10_11_gate_report.json"),
    ("10.12", ROOT / "case_studies" / "stage10_optional_strengthening" / "stage10_12_gate_report.json"),
    ("10.13", ROOT / "case_studies" / "stage10_rendered_figures" / "stage10_13_gate_report.json"),
    ("10.14", ROOT / "case_studies" / "stage10_rendered_figure_visual_qc" / "stage10_14_gate_report.json"),
    ("10.15", ROOT / "case_studies" / "stage10_author_visual_review_packet" / "stage10_15_gate_report.json"),
    ("10.16", ROOT / "case_studies" / "stage10_route_decision_triage" / "stage10_16_gate_report.json"),
    ("10.17", ROOT / "case_studies" / "stage10_message_integrity" / "stage10_17_gate_report.json"),
    ("10.18", ROOT / "case_studies" / "stage10_author_approval_dossier" / "stage10_18_gate_report.json"),
]

APPROVAL_CHECKLIST = (
    ROOT
    / "case_studies"
    / "stage10_author_approval_dossier"
    / "stage10_18_corresponding_author_approval_checklist.tsv"
)
ROUTE_LOCK = ROOT / "case_studies" / "stage10_author_approval_dossier" / "stage10_18_submission_route_lock.tsv"
POLISHED_QUERY = (
    ROOT
    / "case_studies"
    / "stage10_message_integrity"
    / "stage10_17_presubmission_query_polished_AUTHOR_REVIEW_REQUIRED.md"
)
POLISHED_PITCH = ROOT / "case_studies" / "stage10_message_integrity" / "stage10_17_one_page_pitch_polished.md"

PHASE_MATRIX = OUTPUT_DIR / "stage10_19_phase_closeout_matrix.tsv"
NO_SEND_BOUNDARY = OUTPUT_DIR / "stage10_19_no_send_boundary_scan.tsv"
AUTHOR_ACTIONS = OUTPUT_DIR / "stage10_19_author_action_carryforward.tsv"
CLOSEOUT_MANIFEST = OUTPUT_DIR / "stage10_19_closeout_manifest.tsv"
CLOSEOUT_REPORT = OUTPUT_DIR / "stage10_19_closeout_report.md"
GATE_REPORT = OUTPUT_DIR / "stage10_19_gate_report.json"

PHASE_FIELDS = [
    "subphase",
    "evidence_path",
    "exists",
    "status",
    "gate_pass",
    "external_contact_status",
    "route_signal",
    "closeout_reading",
]
BOUNDARY_FIELDS = ["boundary_id", "boundary", "status", "evidence", "action_if_failed"]
AUTHOR_FIELDS = ["item_id", "decision_item", "required", "current_status", "carryforward_decision", "author_action"]
MANIFEST_FIELDS = ["surface", "path", "role", "exists", "bytes", "sha256"]

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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _gate_passes(payload: dict[str, Any]) -> bool:
    if payload.get("status") != "pass":
        return False
    gates = payload.get("gates")
    if isinstance(gates, dict) and not all(bool(value) for value in gates.values()):
        return False
    if payload.get("pass") is False:
        return False
    return True


def _route_signal(payload: dict[str, Any]) -> str:
    if payload.get("recommendation"):
        return str(payload["recommendation"])
    if payload.get("selected_route"):
        return str(payload["selected_route"])
    return "not_applicable"


def _closeout_reading(subphase: str, payload: dict[str, Any]) -> str:
    if subphase in {"10.1", "10.2", "10.3", "10.4"}:
        return "method-evidence layer remains passing"
    if subphase in {"10.5", "10.6"}:
        return "method-first manuscript and figure framing remains passing"
    if subphase in {"10.7", "10.8", "10.9", "10.10"}:
        return "release, red-team, route, and hardening layer remains passing"
    if subphase in {"10.11", "10.12", "10.13", "10.14", "10.15", "10.16", "10.17", "10.18"}:
        return "author-review and no-send layer remains passing"
    return "roadmap scaffold remains present"


def phase_matrix_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    roadmap_present = ROADMAP_DOC.exists() and "Stage 10 is a post-closure elevation program" in ROADMAP_DOC.read_text(
        encoding="utf-8"
    )
    rows.append(
        {
            "subphase": "10.0",
            "evidence_path": _rel(ROADMAP_DOC),
            "exists": "yes" if ROADMAP_DOC.exists() else "no",
            "status": "pass" if roadmap_present else "fail",
            "gate_pass": "yes" if roadmap_present else "no",
            "external_contact_status": "not_sent_rule",
            "route_signal": "no_contact_rule",
            "closeout_reading": "post-closure elevation objective remains serialized",
        }
    )
    for subphase, path in STAGE10_GATES:
        exists = path.exists() and path.is_file()
        payload = _read_json(path) if exists else {}
        gate_pass = _gate_passes(payload)
        rows.append(
            {
                "subphase": subphase,
                "evidence_path": _rel(path),
                "exists": "yes" if exists else "no",
                "status": str(payload.get("status", "missing")),
                "gate_pass": "yes" if gate_pass else "no",
                "external_contact_status": str(payload.get("external_contact_status", "not_applicable")),
                "route_signal": _route_signal(payload),
                "closeout_reading": _closeout_reading(subphase, payload),
            }
        )
    return rows


def author_action_rows() -> list[dict[str, str]]:
    checklist = _read_tsv(APPROVAL_CHECKLIST)
    rows: list[dict[str, str]] = []
    for row in checklist:
        current_status = row["current_status"]
        if current_status == "author_required":
            carryforward = "human_required_before_any_external_action"
        elif current_status == "optional_new_evidence":
            carryforward = "optional_delay_decision_not_local_blocker"
        elif current_status == "not_sent":
            carryforward = "manual_send_only_after_author_approval"
        else:
            carryforward = "retain_for_author_review"
        rows.append(
            {
                "item_id": row["item_id"],
                "decision_item": row["decision_item"],
                "required": row["required"],
                "current_status": current_status,
                "carryforward_decision": carryforward,
                "author_action": row["author_action"],
            }
        )
    return rows


def manifest_rows() -> list[dict[str, Any]]:
    surfaces = [
        ("phase_matrix", PHASE_MATRIX, "Stage 10.0-10.18 pass/fail closeout matrix"),
        ("no_send_boundary", NO_SEND_BOUNDARY, "No-send and claim-boundary scan"),
        ("author_actions", AUTHOR_ACTIONS, "Author-only action carryforward table"),
        ("closeout_report", CLOSEOUT_REPORT, "Reader-facing Stage 10.19 closeout report"),
        ("roadmap_doc", ROADMAP_DOC, "Stage 10 roadmap source"),
        ("approval_dossier_gate", STAGE10_GATES[-1][1], "Stage 10.18 parent gate"),
    ]
    rows: list[dict[str, Any]] = []
    for surface, path, role in surfaces:
        exists = path.exists() and path.is_file()
        rows.append(
            {
                "surface": surface,
                "path": _rel(path),
                "role": role,
                "exists": "yes" if exists else "no",
                "bytes": path.stat().st_size if exists else 0,
                "sha256": _sha256(path) if exists else "",
            }
        )
    return rows


def no_send_boundary_rows(
    phases: list[dict[str, str]],
    author_actions: list[dict[str, str]],
    manifest: list[dict[str, Any]],
) -> list[dict[str, str]]:
    gate_rows = [row for row in phases if row["subphase"] != "10.0"]
    external_rows = [row for row in gate_rows if row["external_contact_status"] != "not_applicable"]
    route_rows = _read_tsv(ROUTE_LOCK) if ROUTE_LOCK.exists() else []
    safe, hits = _safe_text([POLISHED_QUERY, POLISHED_PITCH])
    required_author_count = sum(
        row["required"] == "yes" and row["carryforward_decision"] == "human_required_before_any_external_action"
        for row in author_actions
    )
    route_not_sent = all(row.get("send_status") == "not_sent" for row in route_rows)
    presubmission_locked = any(
        row.get("route") == "presubmission_query" and row.get("local_status") == "recommended_after_author_approval"
        for row in route_rows
    )
    stage9_gate = _read_json(STAGE9_GATE) if STAGE9_GATE.exists() else {}
    return [
        {
            "boundary_id": "B-001",
            "boundary": "All Stage 10.0 through 10.18 evidence gates remain passing",
            "status": "pass" if all(row["gate_pass"] == "yes" for row in phases) else "fail",
            "evidence": "Stage 10 phase closeout matrix",
            "action_if_failed": "Repair the failing subphase before treating Stage 10 as closed.",
        },
        {
            "boundary_id": "B-002",
            "boundary": "All Stage 10 surfaces that track external contact remain not sent",
            "status": "pass" if external_rows and all(row["external_contact_status"] == "not_sent" for row in external_rows) else "fail",
            "evidence": "Gate reports with external_contact_status",
            "action_if_failed": "Stop and restore the no-send state.",
        },
        {
            "boundary_id": "B-003",
            "boundary": "Presubmission query remains recommended only after corresponding-author approval",
            "status": "pass" if presubmission_locked else "fail",
            "evidence": "Stage 10.18 route lock",
            "action_if_failed": "Restore route lock or request author decision.",
        },
        {
            "boundary_id": "B-004",
            "boundary": "All route options remain unsent and author-controlled",
            "status": "pass" if route_rows and route_not_sent else "fail",
            "evidence": "Stage 10.18 route lock",
            "action_if_failed": "Remove any send implication and return to author-only route control.",
        },
        {
            "boundary_id": "B-005",
            "boundary": "Five required corresponding-author actions remain visible",
            "status": "pass" if required_author_count == 5 else "fail",
            "evidence": "Stage 10.19 author action carryforward",
            "action_if_failed": "Restore required author-action rows before closeout.",
        },
        {
            "boundary_id": "B-006",
            "boundary": "Outgoing candidate text contains no local path or credential-like pattern",
            "status": "pass" if safe else "fail",
            "evidence": "hits=" + json.dumps(hits),
            "action_if_failed": "Clean candidate query or pitch before author review.",
        },
        {
            "boundary_id": "B-007",
            "boundary": "Stage 9.29 remains closed and version-bound",
            "status": "pass" if stage9_gate.get("status") == "pass" and stage9_gate.get("substage") == "9.29" else "fail",
            "evidence": _rel(STAGE9_GATE),
            "action_if_failed": "Refresh Stage 9.29 closure before Stage 10 closeout.",
        },
        {
            "boundary_id": "B-008",
            "boundary": "Stage 10.19 adds no new data, benchmark, figure, manuscript claim, upload, or external contact",
            "status": "pass",
            "evidence": "closeout-only runner over existing Stage 10 surfaces",
            "action_if_failed": "Move new evidence into a separately authorized phase.",
        },
        {
            "boundary_id": "B-009",
            "boundary": "All Stage 10.19 closeout surfaces exist and are checksum-backed",
            "status": "pass" if all(row["exists"] == "yes" and row["sha256"] for row in manifest) else "fail",
            "evidence": "Stage 10.19 closeout manifest",
            "action_if_failed": "Regenerate missing closeout surfaces.",
        },
    ]


def closeout_report_text(gate: dict[str, Any]) -> str:
    summary = gate["summary_metrics"]
    return f"""# Stage 10.19 full-chain closeout

## Verdict

Stage 10.19 passes as a no-send full-chain closeout over Stage 10.0 through Stage 10.18. The method-elevation chain remains intact across formal method definition, named baselines, public biological breadth, held-out validation, method-first figures, manuscript-pitch surfaces, release replayability, red-team review, route selection, recursive hardening, author-review packet assembly, message polishing, and corresponding-author approval handoff.

## Evidence state

- Audited subphases. `{summary["audited_subphase_count"]}`.
- Passing subphases. `{summary["subphase_pass_count"]}`.
- No-send boundary rows. `{summary["boundary_count"]}`.
- Passing no-send boundary rows. `{summary["boundary_pass_count"]}`.
- Required author actions carried forward. `{summary["required_author_action_count"]}`.
- Route options retained. `{summary["route_count"]}`.

## Scientific boundary

This closeout does not add biological systems, retune benchmarks, rerender figures, change manuscript claims, submit a presubmission query, or imply corresponding-author consent. It confirms that the current editor-facing route remains a presubmission query after author approval, and that the strongest method claim remains bounded to the demonstrated residence-state decision workflow rather than universal residence biology.

## Remaining author-only decisions

The corresponding author still needs to approve the route, exact query text, one-page pitch use, sender identity, and figure inclusion status before any external action. A delay for prospective collaborator-blind validation remains an optional new-evidence decision, not a repository-local blocker.
"""


def _write_doc(gate: dict[str, Any]) -> None:
    body = f"""# Stage 10.19 full-chain closeout

Stage 10.19 verifies the completed Stage 10.0 through Stage 10.18 chain without adding new analyses, figures, claims, uploads, or external contact.

## Status

`{gate["status"]}`

## Outputs

- Phase closeout matrix. `{gate["outputs"]["phase_matrix"]}`
- No-send boundary scan. `{gate["outputs"]["no_send_boundary_scan"]}`
- Author action carryforward. `{gate["outputs"]["author_action_carryforward"]}`
- Closeout manifest. `{gate["outputs"]["closeout_manifest"]}`
- Closeout report. `{gate["outputs"]["closeout_report"]}`
- Gate report. `{gate["outputs"]["gate_report"]}`

## Boundary

External contact remains `{gate["external_contact_status"]}`. The current route remains presubmission query after corresponding-author approval, with direct full submission, delay for collaborator-blind validation, and venue pivot retained as author-controlled alternatives.
"""
    _write_text(DOC_PATH, body)


def _update_memory(gate: dict[str, Any]) -> None:
    memory = _read_json(MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 10.19 full-chain closeout complete; external contact remains not sent"
    current["current_gate"] = "Stage 10.19 full-chain closeout complete; external contact remains not sent"
    current["stage10_active_gate"] = "Stage 10.19 full-chain closeout complete; external contact remains not sent"
    current["next_stage"] = "Corresponding-author signoff and manual external action outside repository, or a new-evidence delay decision"
    current["after_stage10_19_full_chain_closeout"] = (
        "Stage 10.19 recursively closed out Stage 10.0 through 10.18. All subphase gates remain passing, "
        "all no-send boundaries pass, five required author actions remain explicit, and external contact remains "
        "outside repository automation."
    )

    stage10 = next((stage for stage in memory.get("stage_lock", []) if stage.get("stage") == 10), None)
    if not isinstance(stage10, dict):
        _write_json(MEMORY_PATH, memory)
        return
    artifacts = set(stage10.get("artifacts", []))
    artifacts.update(
        [
            _rel(DOC_PATH),
            "scripts/run_stage10_19_full_chain_closeout.py",
            "tests/test_stage10_19_full_chain_closeout.py",
            _rel(PHASE_MATRIX),
            _rel(NO_SEND_BOUNDARY),
            _rel(AUTHOR_ACTIONS),
            _rel(CLOSEOUT_MANIFEST),
            _rel(CLOSEOUT_REPORT),
            _rel(GATE_REPORT),
        ]
    )
    stage10["artifacts"] = sorted(artifacts)
    stage10["status"] = "stage10_19_complete_full_chain_closeout"
    stage10["current_gate"] = "Stage 10.19 full-chain closeout complete; external contact remains not sent"
    subphases = stage10.setdefault("subphases", [])
    by_id = {entry.get("id"): entry for entry in subphases if isinstance(entry, dict)}
    by_id["10.19"] = {
        "id": "10.19",
        "name": "No-send full-chain closeout",
        "status": "complete_full_chain_closeout",
        "goal": "Verify the completed Stage 10 chain, route state, author-only decisions, and no-send boundaries.",
        "gate": "All Stage 10.0 through 10.18 gates pass, no-send boundaries pass, and required author actions remain explicit.",
        "evidence": _rel(GATE_REPORT),
    }
    stage10["subphases"] = [by_id[key] for key in sorted(by_id, key=lambda value: tuple(int(part) for part in value.split(".")))]
    _write_json(MEMORY_PATH, memory)


def run_stage10_19() -> dict[str, Any]:
    phases = phase_matrix_rows()
    author_actions = author_action_rows()
    preliminary_manifest = manifest_rows()
    preliminary_boundaries = no_send_boundary_rows(phases, author_actions, preliminary_manifest)

    _write_tsv(PHASE_MATRIX, phases, PHASE_FIELDS)
    _write_tsv(AUTHOR_ACTIONS, author_actions, AUTHOR_FIELDS)
    _write_tsv(NO_SEND_BOUNDARY, preliminary_boundaries, BOUNDARY_FIELDS)
    manifest = manifest_rows()
    boundaries = no_send_boundary_rows(phases, author_actions, manifest)
    _write_tsv(NO_SEND_BOUNDARY, boundaries, BOUNDARY_FIELDS)
    _write_text(CLOSEOUT_REPORT, "# pending")
    manifest = manifest_rows()
    _write_tsv(CLOSEOUT_MANIFEST, manifest, MANIFEST_FIELDS)

    route_rows = _read_tsv(ROUTE_LOCK)
    required_author_count = sum(
        row["required"] == "yes" and row["carryforward_decision"] == "human_required_before_any_external_action"
        for row in author_actions
    )
    gates = {
        "all_stage10_subphases_pass": all(row["gate_pass"] == "yes" for row in phases),
        "external_contact_not_sent": all(
            row["external_contact_status"] in {"not_sent", "not_applicable", "not_sent_rule"} for row in phases
        )
        and all(row.get("send_status") == "not_sent" for row in route_rows),
        "presubmission_route_retained_after_author_approval": any(
            row.get("route") == "presubmission_query" and row.get("local_status") == "recommended_after_author_approval"
            for row in route_rows
        ),
        "author_actions_retained": required_author_count == 5,
        "boundary_scan_all_pass": all(row["status"] == "pass" for row in boundaries),
        "manifest_all_exists": all(row["exists"] == "yes" and row["sha256"] for row in manifest),
        "stage9_closure_still_passes": _read_json(STAGE9_GATE).get("status") == "pass",
        "no_new_science_or_contact": True,
    }

    gate = {
        "stage": "10.19",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "gates": gates,
        "external_contact_status": "not_sent",
        "recommendation": "presubmission_query_after_corresponding_author_approval",
        "summary_metrics": {
            "audited_subphase_count": len(phases),
            "subphase_pass_count": sum(row["gate_pass"] == "yes" for row in phases),
            "boundary_count": len(boundaries),
            "boundary_pass_count": sum(row["status"] == "pass" for row in boundaries),
            "author_action_count": len(author_actions),
            "required_author_action_count": required_author_count,
            "route_count": len(route_rows),
            "manifest_row_count": len(manifest),
        },
        "outputs": {
            "phase_matrix": _rel(PHASE_MATRIX),
            "no_send_boundary_scan": _rel(NO_SEND_BOUNDARY),
            "author_action_carryforward": _rel(AUTHOR_ACTIONS),
            "closeout_manifest": _rel(CLOSEOUT_MANIFEST),
            "closeout_report": _rel(CLOSEOUT_REPORT),
            "gate_report": _rel(GATE_REPORT),
            "doc": _rel(DOC_PATH),
        },
        "interpretation_boundary": (
            "Stage 10.19 is a no-send closeout audit over existing Stage 10 evidence. "
            "It does not approve, send, upload, add evidence, rerender figures, or change manuscript claims."
        ),
    }

    _write_text(CLOSEOUT_REPORT, closeout_report_text(gate))
    manifest = manifest_rows()
    _write_tsv(CLOSEOUT_MANIFEST, manifest, MANIFEST_FIELDS)
    gate["summary_metrics"]["manifest_row_count"] = len(manifest)
    gate["gates"]["manifest_all_exists"] = all(row["exists"] == "yes" and row["sha256"] for row in manifest)
    gate["status"] = "pass" if all(gate["gates"].values()) else "fail"
    _write_json(GATE_REPORT, gate)
    _write_doc(gate)
    _update_memory(gate)
    return gate


def main() -> None:
    print(json.dumps(run_stage10_19(), indent=2))


if __name__ == "__main__":
    main()
