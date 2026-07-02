"""Run Stage 9.3 archetype, content-type, and narrative-spine registration.

Stage 9.3 pins the Nature Methods Article archetype for RhoDyn and records the
manuscript narrative spine before claim freeze or drafting. It does not create
reader-facing sections, a reference bibliography, rendered figures, or a
submission package.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
AUDIT_DIR = WORKSPACE / "audits"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.3"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.3"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
BINDING_PATH = WORKSPACE / "contracts" / "stage9_project_binding.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
GATE_9_2 = GATE_DIR / "9.2.json"
GUIDANCE_PATH = WORKSPACE / "refs" / "nature_methods_guidance_register.md"
VENUE_CONSTRAINTS_PATH = AUDIT_DIR / "venue_policy_constraints.md"
ARCHETYPE_PATH = AUDIT_DIR / "methods_paper_archetype_analysis.md"
STAGE7_8_GATE = ROOT / "docs" / "stage7_8_gate_report.json"

OUTPUTS = {
    "spine": WORKSPACE / "stage9_narrative_spine.md",
    "rationale": AUDIT_DIR / "venue_fit_rationale.md",
    "gate": GATE_DIR / "9.3.json",
}

FORBIDDEN_STARTED_PATHS = [
    WORKSPACE / "sections" / "results.md",
    WORKSPACE / "sections" / "introduction.md",
    WORKSPACE / "sections" / "discussion.md",
    WORKSPACE / "sections" / "methods.md",
    WORKSPACE / "sections" / "abstract.md",
    WORKSPACE / "sections" / "data_availability.md",
    WORKSPACE / "sections" / "code_availability.md",
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
    WORKSPACE / "figures" / ".panelforge_commit",
    WORKSPACE / "audits" / "panelforge_render_report.md",
    ROOT / ".venv-panelforge",
    ROOT / "tools" / "panelforge-figures" / ".git",
]


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


def _markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("|", "\\|") for column in columns) + " |")
    return "\n".join(lines)


def _path_exists(path: Path) -> bool:
    return path.exists()


def _stage7_8_passes() -> bool:
    if not STAGE7_8_GATE.exists():
        return False
    try:
        return _read_json(STAGE7_8_GATE).get("status") == "pass"
    except json.JSONDecodeError:
        return False


def _no_downstream_started() -> tuple[bool, list[str]]:
    rendered = [
        path.relative_to(ROOT).as_posix()
        for path in (WORKSPACE / "figures" / "rendered").rglob("*")
        if path.is_file() and path.suffix.lower() in {".png", ".pdf", ".svg"}
    ]
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden and not rendered, forbidden + rendered


def _build_spine_markdown(generated_utc: str, narrative_version: str) -> str:
    rows = [
        {
            "spine_step": "1. Problem",
            "role": "Show why endpoint amplitude, threshold crossing, and static endpoint summaries miss dwell-time structure in live-cell perturbation data.",
            "evidence_source": "Stage 7.1 method definitions and Stage 7.2 synthetic truth benchmarks.",
        },
        {
            "spine_step": "2. Method object",
            "role": "Define RhoDyn as residence-state inference for dynamic operating-state analysis, with tidy trajectory and endpoint inputs.",
            "evidence_source": "Stage 7.1 formal specification and stable API notes.",
        },
        {
            "spine_step": "3. Benchmark contrast",
            "role": "Compare residence windows, dwell metrics, bounded coupling, reserve-like summaries, and routed-output alternatives against simpler summaries on shared inputs.",
            "evidence_source": "Stage 7.2 benchmark harness and Stage 7.4 endpoint/reserve/routing outputs.",
        },
        {
            "spine_step": "4. Biological breadth",
            "role": "Use independent public live-cell signaling systems and endpoint demonstrations to show when RhoDyn changes interpretation beyond amplitude-only summaries.",
            "evidence_source": "Stage 7.3 public signaling, Stage 7.4 endpoint/reserve/routing, and Stage 7.5 held-out validation.",
        },
        {
            "spine_step": "5. Software adoption",
            "role": "Make CLI, Python, backend, workbench, export bundles, documentation, versioning, and archive DOI part of the methods evidence.",
            "evidence_source": "Stage 6 public release and Stage 7.6 to Stage 7.8 reproducibility/adoption evidence.",
        },
        {
            "spine_step": "6. Boundary conditions",
            "role": "State when residence, reserve-like, bounded-coupling, or routed-output claims cannot be identified from the input data.",
            "evidence_source": "Stage 7 limitations matrix, benchmark failure behavior, and held-out inconclusive cases.",
        },
    ]
    return f"""# Stage 9.3 narrative spine

Generated UTC. {generated_utc}

Narrative-spine version. {narrative_version}

Stage. 9.3 archetype, content type, and narrative spine.

Scope. This document pins the manuscript archetype and narrative route for a
future Nature Methods Article. It is not a Results draft, not an Introduction
draft, not a reference library, and not a figure plan.

## Content type decision

RhoDyn should be prepared as a Nature Methods Article. Stage 9.1 sourced the
Article budget and structure from official venue guidance, including an
unreferenced abstract budget, a main-text budget, up to six display items, a
Results section with topical subheadings, and a Discussion without subheadings.

## Method object decision

The manuscript should introduce RhoDyn as a computational method for
residence-state inference and dynamic operating-state interpretation in
live-cell perturbation biology. The method object is not a reproduction route
for the RhoA/microglia manuscript. The manuscript reference case can provide
biological depth only after the method and independent public evidence are
defined.

## Discovery-versus-demonstration decision

The manuscript should make a methods claim, not a new primary biological
discovery claim. The evidence supports RhoDyn as a way to detect and interpret
dynamic control regimes where dwell time, buffering, bounded coupling, or routed
outputs can change biological interpretation relative to simpler summaries.
Biological examples demonstrate method behavior and scope. They do not imply
that RhoDyn generated the original RhoA/microglia manuscript results.

## Narrative spine

{_markdown_table(rows, ["spine_step", "role", "evidence_source"])}

## Drafting boundary

Stage 9.3 stops at the narrative-spine decision. Stage 9.4 must freeze the
claim hierarchy before any paragraph-level ledger, figure-first spine,
citation-resolution surface, manuscript section, PanelForge rendering, or
submission package can begin.
"""


def _build_rationale_markdown(generated_utc: str, checks: list[dict[str, Any]]) -> str:
    check_rows = [
        {
            "gate_predicate": str(check["name"]),
            "status": "pass" if check["passed"] else "fail",
            "evidence": str(check["detail"]),
        }
        for check in checks
    ]
    fit_rows = [
        {
            "criterion": "Nature Methods Article budget",
            "decision": "Fit",
            "rationale": "Official cached guidance identifies Article as a report of a novel method or tool with full technical description, strong validation, reproducibility, general applicability, and discovery potential.",
        },
        {
            "criterion": "Method object",
            "decision": "Fit",
            "rationale": "Stage 7 defines executable RhoDyn objects for trajectories, endpoints, residence windows, bounded coupling, reserve-like summaries, routed-output model comparison, and uncertainty.",
        },
        {
            "criterion": "Representative-paper archetype",
            "decision": "Fit",
            "rationale": "The Stage 9.2 corpus supports early method-object definition, benchmark comparison against simpler alternatives, multi-system demonstrations, visible software, and limitations scoped to assumptions.",
        },
        {
            "criterion": "Discovery-versus-demonstration boundary",
            "decision": "Fit with boundary",
            "rationale": "Stage 7 evidence can support method behavior across public examples, while biological findings remain demonstration contexts rather than new manuscript-independent discoveries.",
        },
    ]
    rejected_rows = [
        {
            "content_type": "Review or Perspective",
            "reason": "RhoDyn has executable software, benchmarks, and biological demonstrations rather than a literature-synthesis-only contribution.",
        },
        {
            "content_type": "Resource-only paper",
            "reason": "The central object is a method and interpretation framework, not only a dataset or software catalog.",
        },
        {
            "content_type": "Short format",
            "reason": "The method requires formal definition, benchmarks, public examples, software availability, assumptions, and limitations.",
        },
    ]
    return f"""# Venue-fit rationale

Generated UTC. {generated_utc}

Stage. 9.3 archetype, content type, and narrative spine.

## Gate predicate results

{_markdown_table(check_rows, ["gate_predicate", "status", "evidence"])}

## Nature Methods Article fit

{_markdown_table(fit_rows, ["criterion", "decision", "rationale"])}

## Rejected content-type alternatives

{_markdown_table(rejected_rows, ["content_type", "reason"])}

## Evidence-bound interpretation

The selected archetype is a computational methods Article. The manuscript
should claim that RhoDyn provides a reproducible method for identifying
residence-aware dynamic operating-state regimes in live-cell perturbation data.
It should not claim that RhoDyn generated the original RhoA/microglia manuscript
or that every demonstration establishes a new biological mechanism.

## Next gated step

Stage 9.4 must freeze claim hierarchy, evidence links, and strength caps before
any manuscript section or figure spine is drafted.
"""


def _validate(narrative_body: str, rationale_body: str) -> list[dict[str, Any]]:
    gate_9_2_pass = False
    if GATE_9_2.exists():
        try:
            gate_9_2_pass = _read_json(GATE_9_2).get("pass") is True
        except json.JSONDecodeError:
            gate_9_2_pass = False
    binding = _read_json(BINDING_PATH) if BINDING_PATH.exists() else {}
    guidance = GUIDANCE_PATH.read_text(encoding="utf-8") if GUIDANCE_PATH.exists() else ""
    constraints = VENUE_CONSTRAINTS_PATH.read_text(encoding="utf-8") if VENUE_CONSTRAINTS_PATH.exists() else ""
    archetype = ARCHETYPE_PATH.read_text(encoding="utf-8") if ARCHETYPE_PATH.exists() else ""
    no_downstream, downstream_paths = _no_downstream_started()
    content_budget_ok = (
        binding.get("content_type") == "Article"
        and "Article" in guidance
        and "Abstract" in guidance
        and "Main text" in guidance
        and "Display items" in guidance
        and "Nature Methods Article" in constraints
    )
    narrative_ok = all(
        phrase in narrative_body
        for phrase in [
            "Nature Methods Article",
            "residence-state inference",
            "dynamic operating-state",
            "Discovery-versus-demonstration decision",
            "Narrative spine",
            "Stage 9.4 must freeze",
            "claim hierarchy",
        ]
    )
    decision_ok = all(
        phrase in rationale_body + narrative_body + archetype
        for phrase in [
            "method object",
            "benchmarked against simpler summaries",
            "public",
            "biological",
            "limitations",
            "do not imply",
        ]
    ) and _stage7_8_passes()
    return [
        {
            "name": "stage_9_2_gate_passed",
            "passed": gate_9_2_pass,
            "detail": "Stage 9.2 methods-paper corpus exists and passes" if gate_9_2_pass else "Stage 9.2 gate is missing or not passing",
        },
        {
            "name": "content_type_matches_sourced_budget",
            "passed": content_budget_ok,
            "detail": "Nature Methods Article budget is sourced from cached guidance and project binding" if content_budget_ok else "Article budget or project binding is incomplete",
        },
        {
            "name": "narrative_spine_exists",
            "passed": narrative_ok,
            "detail": "Narrative spine defines method object, content type, discovery boundary, and Stage 9.4 stop point",
        },
        {
            "name": "discovery_versus_demonstration_decision_is_evidence_bound",
            "passed": decision_ok,
            "detail": "Decision is anchored to Stage 7.8 evidence readiness and Stage 9.2 methods-paper archetype analysis",
        },
        {
            "name": "no_downstream_stage9_surfaces_started",
            "passed": no_downstream,
            "detail": "No manuscript sections, reference bibliography, submission package, PanelForge clone, runtime environment, or rendered figures detected"
            if no_downstream
            else "; ".join(downstream_paths),
        },
    ]


def _promote_staging() -> None:
    for destination in OUTPUTS.values():
        staged = STAGING_DIR / destination.relative_to(WORKSPACE)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, destination)


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
        if substage.get("id") == "9.3":
            substage["status"] = "completed"
    registry["last_completed_substage"] = "9.3"
    _write_json(REGISTRY_PATH, registry)


def _update_memory(narrative_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.3"
    memory["narrative_spine_started"] = True
    memory["narrative_spine_version"] = narrative_version
    memory["status"] = "stage9_3_narrative_spine_registered"
    memory["next_substage"] = "9.4"
    memory["next_substage_authorized"] = False
    memory["stage9_3_checks"] = checks
    memory.setdefault("completed_substages", [])
    if not any(item.get("substage") == "9.3" for item in memory["completed_substages"]):
        memory["completed_substages"].append(
            {
                "substage": "9.3",
                "status": "pass",
                "pass": True,
                "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.3.json",
                "validation_outcome": "Nature Methods Article content type and RhoDyn narrative spine registered before drafting",
                "evidence_dependencies": [
                    "manuscript/nature_methods/gate_verdicts/9.1.json",
                    "manuscript/nature_methods/gate_verdicts/9.2.json",
                    "docs/stage7_8_gate_report.json",
                ],
                "files_created_or_modified": [
                    "manuscript/nature_methods/stage9_narrative_spine.md",
                    "manuscript/nature_methods/audits/venue_fit_rationale.md",
                    "manuscript/nature_methods/gate_verdicts/9.3.json",
                ],
                "remaining_blockers": [
                    "Stage 9.4 claim freeze has not started",
                    "Stage 9.6 figure-to-claim contract has not started",
                    "Stage 9.6b PanelForge rendering remains blocked until Stage 9.6 passes",
                    "Manuscript drafting and reference library construction remain not started",
                ],
            }
        )
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(narrative_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.3 narrative spine registered; manuscript production not started"
    current["stage9_active_gate"] = "Stage 9.3 narrative spine registered; manuscript production not started"
    current["after_stage9_3_narrative_spine"] = (
        "Stage 9.3 selected the Nature Methods Article archetype, registered the RhoDyn "
        "narrative spine, and fixed the discovery-versus-demonstration boundary. Stage 9.4 "
        "claim freeze, citation resolution, manuscript drafting, figure rendering, PanelForge "
        "execution, and submission-package assembly remain not started."
    )
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_3_narrative_spine_registered"
        stage["current_gate"] = "Stage 9.3 narrative spine registered; manuscript production not started"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative "
            "methods-paper corpus analysis, and narrative-spine selection only. Do not start claim "
            "freeze, citation resolution, drafting, figure rendering, review response, or submission "
            "packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/stage9_narrative_spine.md",
            "manuscript/nature_methods/audits/venue_fit_rationale.md",
            "manuscript/nature_methods/gate_verdicts/9.3.json",
            "scripts/run_stage9_3_narrative_spine.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        spine_gate = "Stage 9.3 narrative spine is registered before claim freeze or manuscript drafting."
        if spine_gate not in gate:
            gate.append(spine_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.3":
                subphase["status"] = "complete_narrative_spine_registered"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.3.json"
                subphase["narrative_version"] = narrative_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = body.replace(
            "registers official Nature Methods venue guidance in Stage 9.1, and registers the representative methods-paper corpus in Stage 9.2. It does not begin citation resolution, manuscript drafting, editorial polishing, PanelForge rendering, or package assembly.",
            "registers official Nature Methods venue guidance in Stage 9.1, registers the representative methods-paper corpus in Stage 9.2, and registers the Nature Methods Article narrative spine in Stage 9.3. It does not begin claim freeze, citation resolution, manuscript drafting, editorial polishing, PanelForge rendering, or package assembly.",
        )
        body = body.replace(
            "Stage 9.2 registers the representative computational methods-paper corpus in `refs/representative_methods_papers.md`, `refs/_cache/methods_corpus/`, `audits/methods_paper_archetype_analysis.md`, and `gate_verdicts/9.2.json`. The current state intentionally does not create",
            "Stage 9.2 registers the representative computational methods-paper corpus in `refs/representative_methods_papers.md`, `refs/_cache/methods_corpus/`, `audits/methods_paper_archetype_analysis.md`, and `gate_verdicts/9.2.json`. Stage 9.3 registers the Nature Methods Article narrative spine in `stage9_narrative_spine.md`, `audits/venue_fit_rationale.md`, and `gate_verdicts/9.3.json`. The current state intentionally does not create",
        )
        body = body.replace(
            "| 9.3 | Archetype, content type, and narrative spine | not_started | Pin paper type, content type, and venue-fit decision before drafting. |",
            "| 9.3 | Archetype, content type, and narrative spine | complete_narrative_spine_registered | Pin paper type, content type, and venue-fit decision before drafting. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = body.replace(
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.2 methods-paper corpus registered, manuscript production not started. | The current boundary is evidence intake, official venue-guidance registration, and representative methods-paper corpus analysis only, with PanelForge reserved as a future Stage 9.6b rendering dependency. Do not start narrative-spine selection, citation resolution, figure rendering, drafting, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.3 narrative spine registered, manuscript production not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, and narrative-spine selection only, with PanelForge reserved as a future Stage 9.6b rendering dependency. Do not start claim freeze, citation resolution, figure rendering, drafting, review response, or submission packaging without explicit substage authorization. |",
        )
        body = body.replace(
            "Stage 9.2 representative methods-paper corpus has been completed. Stage 9.3 remains the next unstarted manuscript step.",
            "Stage 9.2 representative methods-paper corpus has been completed. Stage 9.3 narrative spine has been completed. Stage 9.4 remains the next unstarted manuscript step.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    narrative_version = f"narrative-spine@{generated_utc[:10]}@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    narrative_body = _build_spine_markdown(generated_utc, narrative_version)
    rationale_body = _build_rationale_markdown(generated_utc, [])
    checks = _validate(narrative_body, rationale_body)
    rationale_body = _build_rationale_markdown(generated_utc, checks)
    passed = all(check["passed"] for check in checks)
    gate = {
        "substage": "9.3",
        "timestamp": generated_utc,
        "narrative_version": narrative_version,
        "pass": passed,
        "checks": checks,
        "content_type": "Article",
        "venue": "Nature Methods",
        "method_object": "residence-state inference for live-cell perturbation biology",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Narrative-spine registration only. No claim freeze, citation resolution, drafting, figure rendering, PanelForge execution, or submission-package assembly.",
    }

    _write_text(STAGING_DIR / OUTPUTS["spine"].relative_to(WORKSPACE), narrative_body)
    _write_text(STAGING_DIR / OUTPUTS["rationale"].relative_to(WORKSPACE), rationale_body)
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)

    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(narrative_version, generated_utc, checks)
        _update_roadmap_memory(narrative_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)

    return {
        "status": "pass" if passed else "fail",
        "substage": "9.3",
        "narrative_version": narrative_version,
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
