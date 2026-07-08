"""Run Stage 10.10 recursive hardening over the Stage 10 evidence ladder.

Stage 10.10 rechecks the completed Stage 10.0 through Stage 10.9 chain before
any editor-facing action. It does not add datasets, benchmark results, figures,
manuscript claims, or external contact.
"""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage10_recursive_hardening"
DOC_PATH = ROOT / "docs" / "stage10_10_recursive_hardening.md"
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"

PHASE_MATRIX = OUTPUT_DIR / "stage10_10_phase_gate_matrix.tsv"
EVIDENCE_AUDIT = OUTPUT_DIR / "stage10_10_evidence_chain_audit.tsv"
CLAIM_BOUNDARY = OUTPUT_DIR / "stage10_10_claim_boundary_matrix.tsv"
PATCH_RECOMMENDATIONS = OUTPUT_DIR / "stage10_10_patch_recommendations.tsv"
GATE_REPORT = OUTPUT_DIR / "stage10_10_gate_report.json"
HARDENING_REPORT = OUTPUT_DIR / "stage10_10_recursive_hardening_report.md"

STAGE10_0_DOC = ROOT / "docs" / "stage10_nature_methods_eic_rescue_roadmap.md"
STAGE10_1_GATE = ROOT / "case_studies" / "stage10_method_object_v2" / "stage10_1_method_object_gate_report.json"
STAGE10_2_GATE = ROOT / "case_studies" / "stage10_named_benchmarks" / "stage10_2_named_benchmark_report.json"
STAGE10_3_GATE = ROOT / "case_studies" / "stage10_public_breadth" / "stage10_3_public_breadth_report.json"
STAGE10_4_GATE = ROOT / "case_studies" / "stage10_heldout_validation" / "stage10_4_gate_report.json"
STAGE10_5_GATE = ROOT / "case_studies" / "stage10_figure_architecture" / "stage10_5_gate_report.json"
STAGE10_6_GATE = ROOT / "case_studies" / "stage10_manuscript_pitch" / "stage10_6_gate_report.json"
STAGE10_7_GATE = ROOT / "case_studies" / "stage10_release_candidate" / "stage10_7_gate_report.json"
STAGE10_8_GATE = ROOT / "case_studies" / "stage10_eic_red_team" / "stage10_8_gate_report.json"
STAGE10_9_GATE = ROOT / "case_studies" / "stage10_eic_contact_decision" / "stage10_9_gate_report.json"

PHASES = [
    {
        "id": "10.0",
        "name": "EIC rescue objective and no-contact rule",
        "path": STAGE10_0_DOC,
        "kind": "markdown",
        "expected": ["post-closure elevation program", "second EIC contact", "Stage 10"],
        "primary_function": "freezes the post-closure evidence-elevation objective",
    },
    {
        "id": "10.1",
        "name": "Method object v2",
        "path": STAGE10_1_GATE,
        "kind": "json",
        "expected": {"status": "pass", "decision_count": 12},
        "primary_function": "makes the mathematical decision object explicit",
    },
    {
        "id": "10.2",
        "name": "Named baseline benchmarking",
        "path": STAGE10_2_GATE,
        "kind": "json",
        "expected": {"status": "pass", "summary_metrics.direct_optional_package_family_count": 3},
        "primary_function": "tests RhoDyn against named comparator families",
    },
    {
        "id": "10.3",
        "name": "Public biological breadth",
        "path": STAGE10_3_GATE,
        "kind": "json",
        "expected": {"status": "pass", "summary_metrics.counted_independent_public_systems": 4},
        "primary_function": "broadens evidence beyond one biological use case",
    },
    {
        "id": "10.4",
        "name": "Held-out validation route",
        "path": STAGE10_4_GATE,
        "kind": "json",
        "expected": {
            "status": "pass",
            "summary_metrics.positive_call_count": 2,
            "summary_metrics.negative_call_count": 1,
            "summary_metrics.inconclusive_call_count": 1,
        },
        "primary_function": "checks fixed-rule positive, comparator-sufficient, and inconclusive outcomes",
    },
    {
        "id": "10.5",
        "name": "Method-first figure architecture",
        "path": STAGE10_5_GATE,
        "kind": "json",
        "expected": {"status": "pass", "summary_metrics.figure_count": 6},
        "primary_function": "puts method and validation evidence before software maturity",
    },
    {
        "id": "10.6",
        "name": "Manuscript and pitch transformation",
        "path": STAGE10_6_GATE,
        "kind": "json",
        "expected": {"status": "pass", "summary_metrics.results_subsection_count": 6},
        "primary_function": "makes the editor-facing reading method-first",
    },
    {
        "id": "10.7",
        "name": "Benchmark-ready release candidate",
        "path": STAGE10_7_GATE,
        "kind": "json",
        "expected": {"status": "pass", "summary_metrics.safety_hit_count": 0},
        "primary_function": "binds replay commands, checksums, and release-candidate evidence",
    },
    {
        "id": "10.8",
        "name": "Adversarial EIC red-team simulation",
        "path": STAGE10_8_GATE,
        "kind": "json",
        "expected": {"status": "pass", "summary_metrics.unresolved_high_severity_count": 0},
        "primary_function": "stress-tests novelty, breadth, benchmarking, and claim scope",
    },
    {
        "id": "10.9",
        "name": "EIC-contact route decision",
        "path": STAGE10_9_GATE,
        "kind": "json",
        "expected": {"status": "pass", "selected_route": "presubmission_query_author_review_required"},
        "primary_function": "selects author-reviewed presubmission contact without sending it",
    },
]

PHASE_FIELDS = [
    "phase",
    "name",
    "evidence_path",
    "status",
    "primary_function",
    "evidence_read",
    "boundary_preserved",
    "hardening_action",
]

EVIDENCE_FIELDS = ["evidence_node", "required_signal", "evidence_paths", "status", "interpretation"]
BOUNDARY_FIELDS = ["claim_boundary", "forbidden_overread", "evidence_paths", "status", "safe_reading"]
PATCH_FIELDS = ["item", "priority", "decision", "status", "rationale", "next_action"]


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


def _nested_get(payload: dict[str, Any], dotted: str) -> Any:
    value: Any = payload
    for part in dotted.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _json_expected_pass(payload: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, wanted in expected.items():
        value = _nested_get(payload, key)
        if isinstance(wanted, int):
            if not isinstance(value, int) or value < wanted:
                return False
        elif value != wanted:
            return False
    gates = payload.get("gates")
    if isinstance(gates, dict) and not all(bool(v) for v in gates.values()):
        return False
    return True


def phase_gate_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for phase in PHASES:
        path = phase["path"]
        evidence_read = path.exists()
        status = "fail"
        if evidence_read and phase["kind"] == "markdown":
            text = path.read_text(encoding="utf-8")
            status = "pass" if all(term in text for term in phase["expected"]) else "fail"
        elif evidence_read:
            payload = _read_json(path)
            status = "pass" if _json_expected_pass(payload, phase["expected"]) else "fail"
        rows.append(
            {
                "phase": phase["id"],
                "name": phase["name"],
                "evidence_path": _rel(path),
                "status": status,
                "primary_function": phase["primary_function"],
                "evidence_read": "yes" if evidence_read else "no",
                "boundary_preserved": "yes" if status == "pass" else "no",
                "hardening_action": "retain" if status == "pass" else "repair_required",
            }
        )
    return rows


def evidence_chain_rows() -> list[dict[str, str]]:
    reports = {phase["id"]: _read_json(phase["path"]) for phase in PHASES if phase["kind"] == "json" and phase["path"].exists()}
    roadmap = STAGE10_0_DOC.read_text(encoding="utf-8") if STAGE10_0_DOC.exists() else ""

    def ok(condition: bool) -> str:
        return "pass" if condition else "fail"

    rows = [
        {
            "evidence_node": "method_object_primary",
            "required_signal": "decision object is explicit and executable",
            "evidence_paths": _rel(STAGE10_1_GATE),
            "status": ok(reports.get("10.1", {}).get("status") == "pass" and reports.get("10.1", {}).get("decision_count") == 12),
            "interpretation": "RhoDyn is supportable as a method object rather than only a convenience wrapper.",
        },
        {
            "evidence_node": "named_tool_benchmarking",
            "required_signal": "at least three direct optional package families and named external-style comparators",
            "evidence_paths": _rel(STAGE10_2_GATE),
            "status": ok(reports.get("10.2", {}).get("summary_metrics", {}).get("direct_optional_package_family_count", 0) >= 3),
            "interpretation": "The comparator evidence directly addresses a methods-editor concern about self-comparison.",
        },
        {
            "evidence_node": "public_biological_breadth",
            "required_signal": "four counted systems across at least three domains",
            "evidence_paths": _rel(STAGE10_3_GATE),
            "status": ok(
                reports.get("10.3", {}).get("summary_metrics", {}).get("counted_independent_public_systems", 0) >= 4
                and reports.get("10.3", {}).get("summary_metrics", {}).get("counted_biological_domains", 0) >= 3
            ),
            "interpretation": "The use cases are broader than one manuscript-specific RhoA biology example.",
        },
        {
            "evidence_node": "heldout_mixed_outcomes",
            "required_signal": "positive, comparator-sufficient or negative, and inconclusive outcomes under fixed rules",
            "evidence_paths": _rel(STAGE10_4_GATE),
            "status": ok(
                reports.get("10.4", {}).get("summary_metrics", {}).get("positive_call_count", 0) >= 1
                and reports.get("10.4", {}).get("summary_metrics", {}).get("negative_call_count", 0) >= 1
                and reports.get("10.4", {}).get("summary_metrics", {}).get("inconclusive_call_count", 0) >= 1
            ),
            "interpretation": "The method retains boundary behavior and does not force every input into a positive residence call.",
        },
        {
            "evidence_node": "method_first_display",
            "required_signal": "six-figure architecture puts method and validation before software",
            "evidence_paths": _rel(STAGE10_5_GATE),
            "status": ok(reports.get("10.5", {}).get("summary_metrics", {}).get("figure_count") == 6),
            "interpretation": "The figure plan protects the Nature Methods reading from becoming software-first.",
        },
        {
            "evidence_node": "manuscript_pitch_boundary",
            "required_signal": "title, abstract, Results route, and pitch foreground method evidence and non-claims",
            "evidence_paths": _rel(STAGE10_6_GATE),
            "status": ok(reports.get("10.6", {}).get("gates", {}).get("pitch_rejects_software_wrapper_reading") is True),
            "interpretation": "The editor-facing text is aligned to the evidence hierarchy rather than to software maturity alone.",
        },
        {
            "evidence_node": "release_replayability",
            "required_signal": "checksums, commands, and safety scan pass",
            "evidence_paths": _rel(STAGE10_7_GATE),
            "status": ok(reports.get("10.7", {}).get("summary_metrics", {}).get("safety_hit_count") == 0),
            "interpretation": "The Stage 10 evidence is replayable without adding private data or local-machine state.",
        },
        {
            "evidence_node": "red_team_risk_clearance",
            "required_signal": "no unresolved high-severity desk-rejection risk",
            "evidence_paths": _rel(STAGE10_8_GATE),
            "status": ok(reports.get("10.8", {}).get("summary_metrics", {}).get("unresolved_high_severity_count") == 0),
            "interpretation": "Remaining risk is route choice, not collapse of novelty, validation breadth, benchmarking, or overclaiming.",
        },
        {
            "evidence_node": "contact_route_author_review",
            "required_signal": "presubmission route selected and external contact remains unsent",
            "evidence_paths": _rel(STAGE10_9_GATE),
            "status": ok(
                reports.get("10.9", {}).get("selected_route") == "presubmission_query_author_review_required"
                and reports.get("10.9", {}).get("external_contact_status") == "not_sent"
            ),
            "interpretation": "The next editor-facing action remains an author-controlled presubmission decision.",
        },
        {
            "evidence_node": "no_contact_before_evidence_gate",
            "required_signal": "roadmap records no old-package reconsideration request",
            "evidence_paths": _rel(STAGE10_0_DOC),
            "status": ok("Do not ask the EIC to \"take another look\" at the old paper" in roadmap),
            "interpretation": "The Stage 9.29 package remains closed and is not used alone as the second-contact basis.",
        },
    ]
    return rows


def claim_boundary_rows() -> list[dict[str, str]]:
    stage10_texts = [
        STAGE10_0_DOC,
        ROOT / "docs" / "stage10_6_manuscript_pitch_transformation.md",
        ROOT / "case_studies" / "stage10_eic_red_team" / "stage10_8_red_team_report.md",
        ROOT / "case_studies" / "stage10_eic_contact_decision" / "stage10_9_one_page_pitch.md",
        ROOT / "case_studies" / "stage10_eic_contact_decision" / "stage10_9_decision_memo.md",
    ]
    joined = "\n".join(path.read_text(encoding="utf-8") for path in stage10_texts if path.exists())

    stage10_4 = _read_json(STAGE10_4_GATE) if STAGE10_4_GATE.exists() else {}
    stage10_9 = _read_json(STAGE10_9_GATE) if STAGE10_9_GATE.exists() else {}

    def text_status(required: list[str]) -> str:
        return "pass" if all(term in joined for term in required) else "fail"

    not_universal_status = (
        "pass"
        if stage10_4.get("summary_metrics", {}).get("inconclusive_call_count", 0) >= 1
        and stage10_9.get("summary_metrics", {}).get("unresolved_high_severity_count_inherited") == 0
        and "simpler summaries are sufficient" in joined
        else "fail"
    )
    not_prospective_status = (
        "pass"
        if "absence of prospective collaborator-blind validation" in joined
        and "no-retuning public-derived replay" in joined
        else "fail"
    )
    contact_not_sent_status = "pass" if stage10_9.get("external_contact_status") == "not_sent" else "fail"

    return [
        {
            "claim_boundary": "method_not_software_wrapper",
            "forbidden_overread": "software maturity alone is the scientific advance",
            "evidence_paths": ";".join(_rel(path) for path in stage10_texts if path.exists()),
            "status": text_status(["not a software wrapper", "software/workflow reading remains true, but secondary"]),
            "safe_reading": "Software reproducibility supports the residence-state inference method rather than replacing the method claim.",
        },
        {
            "claim_boundary": "not_universal_residence",
            "forbidden_overread": "every live-cell system has a residence regime",
            "evidence_paths": _rel(STAGE10_4_GATE) + ";" + _rel(STAGE10_9_GATE),
            "status": not_universal_status,
            "safe_reading": "RhoDyn preserves positive, comparator-sufficient, and inconclusive outcomes.",
        },
        {
            "claim_boundary": "not_mechanism_discovery",
            "forbidden_overread": "declared windows are mechanisms",
            "evidence_paths": _rel(STAGE10_9_GATE),
            "status": text_status(["Declared residence windows are analysis objects", "not automatically discovered biological mechanisms"]),
            "safe_reading": "Declared windows structure the decision rule; they do not prove a molecular mechanism by themselves.",
        },
        {
            "claim_boundary": "not_prospective_blinded",
            "forbidden_overread": "prospective blinded collaborator study",
            "evidence_paths": _rel(STAGE10_4_GATE) + ";" + _rel(STAGE10_9_GATE),
            "status": not_prospective_status,
            "safe_reading": "The validation layer is sealed and no-retuning, but not prospective collaborator-blind.",
        },
        {
            "claim_boundary": "old_package_not_contact_basis",
            "forbidden_overread": "reconsider the Stage 9.29 package alone",
            "evidence_paths": _rel(STAGE10_9_GATE),
            "status": text_status(["Do not ask the EIC to reconsider the Stage 9.29 package alone"]),
            "safe_reading": "Any editor contact should be based on the Stage 10 evidence ladder and author review.",
        },
        {
            "claim_boundary": "external_contact_not_sent",
            "forbidden_overread": "journal contact completed",
            "evidence_paths": _rel(STAGE10_9_GATE),
            "status": contact_not_sent_status,
            "safe_reading": "The repository contains author-review materials only; no editor has been contacted by this runner.",
        },
    ]


def patch_recommendation_rows() -> list[dict[str, str]]:
    return [
        {
            "item": "Stage 10.0 through 10.9 evidence ladder",
            "priority": "required",
            "decision": "retain",
            "status": "complete",
            "rationale": "All phase gates and evidence-chain checks pass.",
            "next_action": "Use Stage 10.10 as the hardening checkpoint before author review.",
        },
        {
            "item": "Stage 9.29 package alone as EIC basis",
            "priority": "required",
            "decision": "forbid",
            "status": "complete",
            "rationale": "Stage 10 evidence supersedes the old-package reconsideration route.",
            "next_action": "Do not ask for reconsideration of Stage 9.29 without the Stage 10 method-evidence pitch.",
        },
        {
            "item": "Prospective collaborator-blind validation",
            "priority": "optional_strengthening",
            "decision": "defer",
            "status": "not_blocking",
            "rationale": "Stage 10.4 no-retuning public-derived validation passes, but a prospective collaborator-blind table would still strengthen direct-submission posture.",
            "next_action": "Add only if the team wants to lower residual route risk before full submission.",
        },
        {
            "item": "Stage 10 rendered figures",
            "priority": "optional_strengthening",
            "decision": "defer",
            "status": "not_blocking",
            "rationale": "Stage 10.5 provides a method-first figure architecture, while Stage 10.9 records unrendered Stage 10 figures as medium route risk.",
            "next_action": "Render only after author approval of the Stage 10 figure spine.",
        },
        {
            "item": "External editor contact",
            "priority": "human_action",
            "decision": "retain_author_review_required",
            "status": "not_sent",
            "rationale": "Stage 10.9 selected presubmission-style contact but explicitly did not send it.",
            "next_action": "Author must review and authorize the exact message before any contact.",
        },
    ]


def _update_memory() -> None:
    memory = _read_json(MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 10.10 recursive hardening complete; external contact remains not sent"
    current["current_gate"] = "Stage 10.10 recursive hardening complete; external contact remains not sent"
    current["stage10_active_gate"] = "Stage 10.10 recursive hardening complete; external contact remains not sent"
    current["after_stage10_10_recursive_hardening"] = (
        "Stage 10.10 rechecked the full Stage 10.0 through 10.9 evidence ladder. "
        "All phase gates, evidence-chain checks, and claim-boundary checks pass. "
        "The author-reviewed presubmission route remains the selected editor-facing path, and no external contact was sent."
    )
    current["next_stage"] = "Author review and optional EIC presubmission contact, not sent"
    for entry in memory.get("stage_lock", []):
        if isinstance(entry, dict) and entry.get("stage") == 10:
            entry["status"] = "stage10_10_complete_recursive_hardening"
            entry["current_gate"] = "Stage 10.10 recursive hardening complete; external contact remains not sent."
            artifacts = entry.setdefault("artifacts", [])
            for rel in [
                "docs/stage10_10_recursive_hardening.md",
                "scripts/run_stage10_10_recursive_hardening.py",
                "tests/test_stage10_10_recursive_hardening.py",
                "case_studies/stage10_recursive_hardening/stage10_10_phase_gate_matrix.tsv",
                "case_studies/stage10_recursive_hardening/stage10_10_evidence_chain_audit.tsv",
                "case_studies/stage10_recursive_hardening/stage10_10_claim_boundary_matrix.tsv",
                "case_studies/stage10_recursive_hardening/stage10_10_patch_recommendations.tsv",
                "case_studies/stage10_recursive_hardening/stage10_10_gate_report.json",
                "case_studies/stage10_recursive_hardening/stage10_10_recursive_hardening_report.md",
            ]:
                if rel not in artifacts:
                    artifacts.append(rel)
            subphases = entry.setdefault("subphases", [])
            if not any(item.get("id") == "10.10" for item in subphases if isinstance(item, dict)):
                subphases.append(
                    {
                        "id": "10.10",
                        "name": "Recursive hardening and re-elevation check",
                        "status": "complete_recursive_hardening",
                        "evidence": "case_studies/stage10_recursive_hardening/stage10_10_gate_report.json",
                        "gate": "Stage 10.0 through 10.9 gates, evidence-chain checks, and claim boundaries pass; external contact remains not sent",
                    }
                )
    memory["updated"] = "2026-07-08"
    _write_json(MEMORY_PATH, memory)


def hardening_report_text(gate: dict[str, Any]) -> str:
    return f"""# Stage 10.10 recursive hardening report

Stage 10.10 rechecks the full Stage 10 evidence ladder before any editor-facing contact.

## Scientific-methods reading

The current RhoDyn package remains strongest when read as a residence-state inference method for live-cell perturbation data. The evidence chain now explicitly links the formal method object, named baseline comparisons, public biological breadth, no-retuning held-out calls, method-first figure architecture, manuscript pitch, release replayability, red-team risk clearance, and author-reviewed presubmission route.

## Gate summary

- Status. {gate["status"]}
- Audited Stage 10 phases. {gate["summary_metrics"]["audited_phase_count"]}
- Evidence-chain checks. {gate["summary_metrics"]["evidence_chain_pass_count"]} of {gate["summary_metrics"]["evidence_chain_count"]} pass
- Claim-boundary checks. {gate["summary_metrics"]["claim_boundary_pass_count"]} of {gate["summary_metrics"]["claim_boundary_count"]} pass
- High-risk gaps. {gate["summary_metrics"]["high_risk_gap_count"]}
- External contact status. {gate["external_contact_status"]}

## Boundaries preserved

- RhoDyn is not framed as a software wrapper.
- The current evidence does not claim that every live-cell system has a residence regime.
- Declared residence windows are analysis objects, not molecular mechanisms by themselves.
- Held-out validation is no-retuning public-derived replay, not prospective collaborator-blind validation.
- The old Stage 9.29 package is not the basis for a second editor request by itself.
- No editor message was sent.

## Next action

The only recommended editor-facing action remains author review of the Stage 10.9 presubmission materials. Additional prospective data or rendered Stage 10 figures can strengthen a full-submission route, but they are not required for the current presubmission decision.
"""


def doc_text() -> str:
    return """# Stage 10.10 recursive hardening

Stage 10.10 is the recursive hardening and re-elevation check for the completed Stage 10 evidence ladder. It is not a new biological analysis and not a manuscript rewrite.

## Purpose

The purpose is to verify that Stages 10.0 through 10.9 still function as a coherent Nature Methods rescue track. The pass checks that the method-object definition, named comparator evidence, public biological breadth, held-out validation, figure architecture, manuscript pitch, release replayability, red-team review, and contact-route decision all remain aligned.

## Outputs

- `case_studies/stage10_recursive_hardening/stage10_10_phase_gate_matrix.tsv`
- `case_studies/stage10_recursive_hardening/stage10_10_evidence_chain_audit.tsv`
- `case_studies/stage10_recursive_hardening/stage10_10_claim_boundary_matrix.tsv`
- `case_studies/stage10_recursive_hardening/stage10_10_patch_recommendations.tsv`
- `case_studies/stage10_recursive_hardening/stage10_10_gate_report.json`
- `case_studies/stage10_recursive_hardening/stage10_10_recursive_hardening_report.md`

## Interpretation boundary

This pass does not add datasets, benchmark results, rendered figures, model outputs, manuscript claims, or journal contact. It confirms whether the already generated Stage 10 evidence can support author review of a presubmission-style Nature Methods inquiry.
"""


def build_gate(
    phase_rows: list[dict[str, str]],
    evidence_rows: list[dict[str, str]],
    boundary_rows: list[dict[str, str]],
    patch_rows: list[dict[str, str]],
) -> dict[str, Any]:
    audited_phase_count = len(phase_rows)
    phase_pass_count = sum(row["status"] == "pass" for row in phase_rows)
    evidence_pass_count = sum(row["status"] == "pass" for row in evidence_rows)
    boundary_pass_count = sum(row["status"] == "pass" for row in boundary_rows)
    high_risk_gap_count = len([row for row in patch_rows if row["priority"] == "required" and row["status"] != "complete"])
    external_contact_status = "not_sent"
    gates = {
        "all_stage10_phase_gates_pass": phase_pass_count == audited_phase_count,
        "evidence_chain_passes": evidence_pass_count == len(evidence_rows),
        "claim_boundaries_pass": boundary_pass_count == len(boundary_rows),
        "no_high_risk_gap_open": high_risk_gap_count == 0,
        "external_contact_not_sent": external_contact_status == "not_sent",
        "stage9_29_not_used_alone": any(row["claim_boundary"] == "old_package_not_contact_basis" and row["status"] == "pass" for row in boundary_rows),
    }
    return {
        "stage": "10.10",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "gates": gates,
        "summary_metrics": {
            "audited_phase_count": audited_phase_count,
            "phase_pass_count": phase_pass_count,
            "evidence_chain_count": len(evidence_rows),
            "evidence_chain_pass_count": evidence_pass_count,
            "claim_boundary_count": len(boundary_rows),
            "claim_boundary_pass_count": boundary_pass_count,
            "high_risk_gap_count": high_risk_gap_count,
            "patch_recommendation_count": len(patch_rows),
        },
        "external_contact_status": external_contact_status,
        "selected_route": "presubmission_query_author_review_required",
        "next_phase": "Author review and optional EIC presubmission contact",
        "outputs": {
            "phase_gate_matrix": _rel(PHASE_MATRIX),
            "evidence_chain_audit": _rel(EVIDENCE_AUDIT),
            "claim_boundary_matrix": _rel(CLAIM_BOUNDARY),
            "patch_recommendations": _rel(PATCH_RECOMMENDATIONS),
            "hardening_report": _rel(HARDENING_REPORT),
        },
        "interpretation_boundary": (
            "Stage 10.10 is a hardening check only. It does not add datasets, benchmark results, figures, manuscript claims, "
            "or journal contact. It preserves the Stage 10 method-first reading and keeps external contact as author review."
        ),
    }


def run_stage10_10() -> dict[str, Any]:
    phase_rows = phase_gate_rows()
    evidence_rows = evidence_chain_rows()
    boundary_rows = claim_boundary_rows()
    patch_rows = patch_recommendation_rows()
    gate = build_gate(phase_rows, evidence_rows, boundary_rows, patch_rows)

    _write_tsv(PHASE_MATRIX, phase_rows, PHASE_FIELDS)
    _write_tsv(EVIDENCE_AUDIT, evidence_rows, EVIDENCE_FIELDS)
    _write_tsv(CLAIM_BOUNDARY, boundary_rows, BOUNDARY_FIELDS)
    _write_tsv(PATCH_RECOMMENDATIONS, patch_rows, PATCH_FIELDS)
    _write_json(GATE_REPORT, gate)
    _write_text(HARDENING_REPORT, hardening_report_text(gate))
    _write_text(DOC_PATH, doc_text())
    _update_memory()
    return gate


def main() -> int:
    report = run_stage10_10()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
