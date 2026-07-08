"""Run Stage 10.12 optional-strengthening triage.

Stage 10.12 converts the remaining medium-risk route items into a concrete
decision surface. It does not render figures, recruit collaborator data, send
editor contact, add manuscript claims, or change evidence. Its purpose is to
separate the locally actionable next hardening step from external-data and
author-only decisions.
"""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage10_optional_strengthening"
DOC_PATH = ROOT / "docs" / "stage10_12_optional_strengthening_triage.md"
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"

STAGE10_11_GATE = (
    ROOT
    / "case_studies"
    / "stage10_author_review_readiness"
    / "stage10_11_gate_report.json"
)
STAGE10_10_PATCHES = (
    ROOT
    / "case_studies"
    / "stage10_recursive_hardening"
    / "stage10_10_patch_recommendations.tsv"
)
STAGE10_9_ROUTES = (
    ROOT
    / "case_studies"
    / "stage10_eic_contact_decision"
    / "stage10_9_route_decision_matrix.tsv"
)
FIGURE_SPINE = ROOT / "manuscript" / "nature_methods" / "figures" / "stage10_5_method_first_figure_spine.md"
PANEL_CROSSWALK = ROOT / "manuscript" / "nature_methods" / "figures" / "stage10_5_panel_evidence_crosswalk.csv"

OPTION_MATRIX = OUTPUT_DIR / "stage10_12_strengthening_option_matrix.tsv"
FIGURE_READINESS = OUTPUT_DIR / "stage10_12_figure_render_readiness.tsv"
VALIDATION_GAP = OUTPUT_DIR / "stage10_12_validation_gap_matrix.tsv"
RECOMMENDED_NEXT = OUTPUT_DIR / "stage10_12_recommended_next_step.md"
GATE_REPORT = OUTPUT_DIR / "stage10_12_gate_report.json"

OPTION_FIELDS = [
    "option",
    "current_state",
    "local_feasibility",
    "risk_addressed",
    "blocking_dependency",
    "recommended_decision",
    "safe_next_action",
]
FIGURE_FIELDS = [
    "figure",
    "panel_count",
    "architecture_status",
    "evidence_files_exist",
    "render_status",
    "local_feasibility",
    "next_action",
]
VALIDATION_FIELDS = [
    "validation_layer",
    "current_evidence",
    "what_it_resolves",
    "what_it_does_not_resolve",
    "local_status",
    "decision",
]


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def _write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _stage10_11_passes() -> bool:
    if not STAGE10_11_GATE.exists():
        return False
    payload = _read_json(STAGE10_11_GATE)
    gates = payload.get("gates", {})
    return (
        payload.get("status") == "pass"
        and payload.get("selected_route") == "presubmission_query_author_review_required"
        and payload.get("external_contact_status") == "not_sent"
        and isinstance(gates, dict)
        and all(bool(value) for value in gates.values())
    )


def _patch_recommendation_state() -> dict[str, str]:
    if not STAGE10_10_PATCHES.exists():
        return {}
    rows = _read_tsv(STAGE10_10_PATCHES)
    return {row.get("item", ""): row.get("status", "") for row in rows}


def _route_state() -> dict[str, dict[str, str]]:
    if not STAGE10_9_ROUTES.exists():
        return {}
    rows = _read_tsv(STAGE10_9_ROUTES)
    return {row.get("route", ""): row for row in rows}


def _crosswalk_rows() -> list[dict[str, str]]:
    with PANEL_CROSSWALK.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def figure_readiness_rows() -> list[dict[str, str]]:
    rows = _crosswalk_rows()
    by_figure: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_figure.setdefault(row["fig_id"], []).append(row)

    output_rows: list[dict[str, str]] = []
    for figure in sorted(by_figure):
        panels = by_figure[figure]
        evidence_paths = [
            rel.strip()
            for row in panels
            for rel in row.get("evidence_files", "").split(";")
            if rel.strip()
        ]
        all_exist = all((ROOT / rel).exists() for rel in evidence_paths)
        output_rows.append(
            {
                "figure": figure,
                "panel_count": str(len(panels)),
                "architecture_status": "method_first_crosswalk_complete",
                "evidence_files_exist": "yes" if all_exist else "no",
                "render_status": "not_rendered_in_stage10",
                "local_feasibility": "high",
                "next_action": "render Stage 10 PanelForge figures after author approval of the figure spine",
            }
        )
    return output_rows


def option_rows() -> list[dict[str, str]]:
    patches = _patch_recommendation_state()
    routes = _route_state()
    figure_patch = patches.get("Stage 10 rendered figures", "unknown")
    validation_patch = patches.get("Prospective collaborator-blind validation", "unknown")
    presub = routes.get("presubmission_query_author_review_required", {})
    full_submission = routes.get("full_submission", {})
    return [
        {
            "option": "author_review_presubmission_query",
            "current_state": presub.get("decision", "selected"),
            "local_feasibility": "ready_for_author_review",
            "risk_addressed": "low-risk editor fit check without claiming full-submission readiness",
            "blocking_dependency": "corresponding-author approval",
            "recommended_decision": "keep_active",
            "safe_next_action": "author reviews and decides whether to send the Stage 10.11 query",
        },
        {
            "option": "render_stage10_method_figures",
            "current_state": figure_patch,
            "local_feasibility": "high",
            "risk_addressed": "unrendered Stage 10 figure spine remains a medium direct-submission risk",
            "blocking_dependency": "author approval of figure spine and rendering style",
            "recommended_decision": "next_local_hardening_before_full_submission",
            "safe_next_action": "prepare a PanelForge rendering pass from the Stage 10.5 crosswalk without changing evidence",
        },
        {
            "option": "prospective_collaborator_blind_validation",
            "current_state": validation_patch,
            "local_feasibility": "low_external_data_required",
            "risk_addressed": "stronger direct-submission posture and reviewer confidence",
            "blocking_dependency": "new collaborator table or prospective external dataset",
            "recommended_decision": "defer_not_blocking_presubmission",
            "safe_next_action": "treat as a new evidence phase only if author team can provide suitable data",
        },
        {
            "option": "full_submission_now",
            "current_state": full_submission.get("decision", "not_selected_now"),
            "local_feasibility": "conditional",
            "risk_addressed": "moves directly to journal review but carries medium route risk",
            "blocking_dependency": "author acceptance of unrendered-figure and prospective-validation risks",
            "recommended_decision": "do_not_select_without_author_override",
            "safe_next_action": "use only if the PI explicitly accepts the recorded medium-risk items",
        },
        {
            "option": "venue_pivot",
            "current_state": routes.get("pivot_venue", {}).get("decision", "fallback_only"),
            "local_feasibility": "available_if_needed",
            "risk_addressed": "fallback if Nature Methods reads the work as software integration",
            "blocking_dependency": "editorial feedback or PI venue decision",
            "recommended_decision": "retain_as_fallback",
            "safe_next_action": "do not pivot before the author decides on presubmission or full-submission route",
        },
    ]


def validation_gap_rows() -> list[dict[str, str]]:
    return [
        {
            "validation_layer": "stage10_4_no_retuning_public_derived_replay",
            "current_evidence": "positive, comparator-sufficient, bounded-coupling, and inconclusive calls are preserved under fixed rules",
            "what_it_resolves": "hidden retuning concern for retained public-derived contexts",
            "what_it_does_not_resolve": "prospective collaborator-blind performance on unseen external tables",
            "local_status": "complete",
            "decision": "sufficient_for_presubmission_scope",
        },
        {
            "validation_layer": "prospective_collaborator_blind_validation",
            "current_evidence": "not present in the current repository",
            "what_it_resolves": "stronger direct-submission confidence and external-table generality",
            "what_it_does_not_resolve": "all future biological domains or universal residence-state structure",
            "local_status": "requires_external_data",
            "decision": "not_locally_closable_in_stage10_12",
        },
        {
            "validation_layer": "stage10_rendered_method_figures",
            "current_evidence": "method-first figure crosswalk contains six figures and complete evidence paths",
            "what_it_resolves": "visual-readiness risk for a full manuscript package",
            "what_it_does_not_resolve": "new biological validation or prospective external evidence",
            "local_status": "locally_actionable_after_author_approval",
            "decision": "highest_value_local_hardening_step",
        },
    ]


def _safe_no_contact() -> bool:
    if not STAGE10_11_GATE.exists():
        return False
    return _read_json(STAGE10_11_GATE).get("external_contact_status") == "not_sent"


def _no_forbidden_overreads(rows: list[dict[str, str]]) -> bool:
    joined = json.dumps(rows)
    forbidden = [
        "prospective validation complete",
        "editor contacted",
        "mechanism discovery",
    ]
    return not any(term in joined.lower() for term in forbidden)


def recommended_next_step_body(gate: dict[str, Any]) -> str:
    return f"""# Stage 10.12 optional-strengthening triage

## Recommendation

The Stage 10 presubmission query remains ready for author review and external contact remains unsent. If the team wants more local hardening before a full Nature Methods submission, the next best step is rendering the Stage 10 method-first figures from the existing six-figure crosswalk. This is locally feasible because every planned panel already points to an existing evidence file.

Prospective collaborator-blind validation would strengthen the direct-submission posture, but it requires new external data and should be treated as a separate evidence phase rather than as a local cleanup task.

## Decision

- Presubmission query. Ready for author review, not sent.
- Stage 10 rendered figures. Highest-value local strengthening step before full submission.
- Prospective collaborator-blind validation. Valuable but external-data dependent.
- Full submission. Do not choose without author acceptance of the remaining medium-risk items.
- Venue pivot. Retain as fallback only.

## Gate

Status. `{gate["status"]}`.
Recommended local next step. `{gate["recommended_local_next_step"]}`.
External contact. `{gate["external_contact_status"]}`.
"""


def doc_body(gate: dict[str, Any]) -> str:
    return f"""# Stage 10.12 optional-strengthening triage

Stage 10.12 separates locally actionable hardening from author-only and external-data decisions. It is not a new analysis and does not alter the Stage 10 method claims.

## Status

`{gate["status"]}`

## Recommended local next step

`{gate["recommended_local_next_step"]}`

## Outputs

- `{_rel(OPTION_MATRIX)}`
- `{_rel(FIGURE_READINESS)}`
- `{_rel(VALIDATION_GAP)}`
- `{_rel(RECOMMENDED_NEXT)}`
- `{_rel(GATE_REPORT)}`

## Interpretation boundary

Stage 10.12 does not render figures, does not add collaborator-blind validation, and does not contact Nature Methods. It records that rendered Stage 10 figures are the strongest local strengthening step before any full-submission route, while prospective collaborator-blind validation remains a separate new-evidence decision.
"""


def _update_memory(gate: dict[str, Any]) -> None:
    memory = _read_json(MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 10.12 optional-strengthening triage complete; external contact remains not sent"
    current["current_gate"] = "Stage 10.12 optional-strengthening triage complete; external contact remains not sent"
    current["stage10_active_gate"] = "Stage 10.12 optional-strengthening triage complete; external contact remains not sent"
    current["next_stage"] = "Author review, optional presubmission contact, or Stage 10 figure rendering"
    current["after_stage10_12_optional_strengthening_triage"] = (
        "Stage 10.12 separated the remaining medium-risk strengthening paths. "
        "Rendered Stage 10 figures are the highest-value local hardening step before full submission, "
        "whereas prospective collaborator-blind validation requires new external data. External contact remains not sent."
    )

    stage10 = None
    for stage in memory.get("stage_lock", []):
        if stage.get("stage") == 10:
            stage10 = stage
            break
    if stage10 is None:
        return
    artifacts = set(stage10.get("artifacts", []))
    artifacts.update(
        [
            _rel(DOC_PATH),
            "scripts/run_stage10_12_optional_strengthening_triage.py",
            "tests/test_stage10_12_optional_strengthening_triage.py",
            _rel(OPTION_MATRIX),
            _rel(FIGURE_READINESS),
            _rel(VALIDATION_GAP),
            _rel(RECOMMENDED_NEXT),
            _rel(GATE_REPORT),
        ]
    )
    stage10["artifacts"] = sorted(artifacts)
    stage10["status"] = "stage10_12_complete_optional_strengthening_triage"
    stage10["current_gate"] = "Stage 10.12 optional-strengthening triage complete; external contact remains not sent"
    subphases = stage10.setdefault("subphases", [])
    existing = {entry.get("id"): entry for entry in subphases if isinstance(entry, dict)}
    existing["10.12"] = {
        "id": "10.12",
        "name": "Optional strengthening triage",
        "status": "complete_optional_strengthening_triage",
        "goal": "Separate locally actionable figure hardening from external collaborator-blind validation and author-only contact decisions.",
        "gate": "Stage 10.11 passes; figure crosswalk is evidence-complete; prospective validation remains external-data dependent; external contact remains not sent.",
        "evidence": _rel(GATE_REPORT),
    }
    stage10["subphases"] = [existing[key] for key in sorted(existing, key=lambda value: tuple(int(part) for part in value.split(".")))]
    MEMORY_PATH.write_text(json.dumps(memory, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def run_stage10_12() -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    options = option_rows()
    figures = figure_readiness_rows()
    validation = validation_gap_rows()

    _write_tsv(OPTION_MATRIX, options, OPTION_FIELDS)
    _write_tsv(FIGURE_READINESS, figures, FIGURE_FIELDS)
    _write_tsv(VALIDATION_GAP, validation, VALIDATION_FIELDS)

    figure_ready = len(figures) == 6 and all(row["evidence_files_exist"] == "yes" for row in figures)
    options_ok = len(options) == 5
    validation_ok = any(row["decision"] == "not_locally_closable_in_stage10_12" for row in validation)
    gates = {
        "stage10_11_author_review_ready": _stage10_11_passes(),
        "external_contact_not_sent": _safe_no_contact(),
        "option_matrix_complete": options_ok,
        "figure_crosswalk_render_ready": figure_ready,
        "prospective_validation_scoped_as_external": validation_ok,
        "no_forbidden_overreads": _no_forbidden_overreads([*options, *validation]),
    }
    gate = {
        "stage": "10.12",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "gates": gates,
        "external_contact_status": "not_sent",
        "recommended_local_next_step": "render_stage10_method_figures",
        "summary_metrics": {
            "option_count": len(options),
            "figure_count": len(figures),
            "planned_panel_count": sum(int(row["panel_count"]) for row in figures),
            "validation_layer_count": len(validation),
            "locally_actionable_option_count": sum(1 for row in options if row["local_feasibility"] in {"high", "ready_for_author_review"}),
        },
        "outputs": {
            "option_matrix": _rel(OPTION_MATRIX),
            "figure_readiness": _rel(FIGURE_READINESS),
            "validation_gap": _rel(VALIDATION_GAP),
            "recommended_next_step": _rel(RECOMMENDED_NEXT),
            "gate_report": _rel(GATE_REPORT),
        },
        "interpretation_boundary": (
            "Stage 10.12 is a strengthening triage only. It does not render figures, add collaborator-blind validation, "
            "send external contact, or change manuscript evidence."
        ),
    }
    _write_json(GATE_REPORT, gate)
    _write_text(RECOMMENDED_NEXT, recommended_next_step_body(gate))
    _write_text(DOC_PATH, doc_body(gate))
    _update_memory(gate)
    return gate


def main() -> int:
    gate = run_stage10_12()
    print(json.dumps(gate, indent=2))
    return 0 if gate["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
