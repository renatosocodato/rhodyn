"""Run Stage 9.13 Discussion interpretation-map pass.

Stage 9.13 creates a limitation-aware Discussion blueprint from the Stage 9.8
section contract, Stage 9.12 Introduction boundary, and Stage 7 limitations.
It does not draft the Discussion, Methods, full reference library, figure
legends, or submission package.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SECTIONS_DIR = WORKSPACE / "sections"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.13"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.13"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"

GATE_912 = GATE_DIR / "9.12.json"
SECTION_CONTRACTS = SECTIONS_DIR / "section_contracts.md"
LIMITATIONS_MATRIX = ROOT / "docs" / "stage7_limitations_matrix.md"
LIMITATIONS_TRACEABILITY = ROOT / "case_studies" / "stage7_methods_readiness" / "limitations_traceability.tsv"
RESULTS_DRAFT = SECTIONS_DIR / "results.md"
INTRODUCTION_DRAFT = SECTIONS_DIR / "introduction.md"

OUTPUTS = {
    "blueprint": SECTIONS_DIR / "discussion_blueprint.md",
    "gate": GATE_DIR / "9.13.json",
}

FORBIDDEN_STARTED_PATHS = [
    SECTIONS_DIR / "discussion.md",
    SECTIONS_DIR / "methods.md",
    SECTIONS_DIR / "data_availability.md",
    SECTIONS_DIR / "code_availability.md",
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
]

FORBIDDEN_DISCUSSION_MAP_PHRASES = (
    "universal residence law",
    "guarantees",
    "therapeutic",
    "clinical",
    "diagnostic",
    "absence of all coupling",
    "proof of no crosstalk",
    "true biological reserve",
    "literal molecular edge",
    "RhoDyn generated the original",
)

LIMITATION_TERMS = (
    "declared biological window",
    "not a causal mechanism",
    "amplitude or endpoint summaries can be sufficient",
    "inconclusive",
    "slower or context-specific coupling",
    "reserve-like",
    "measured endpoint",
    "direct biochemical interactions",
    "not a new biological result",
    "reference use case",
)


DISCUSSION_MAP_PARAGRAPHS = [
    {
        "para_ids": ("PARA-DISCUSSION-001",),
        "claim_ids": ("CLM-0001", "CLM-0005"),
        "role": "Opening synthesis",
        "text": (
            "The Discussion should open by stating that RhoDyn makes residence-state inference a reviewable method object for live-cell perturbation data. "
            "The central interpretation is that dwell fraction, dwell time, and segment count can preserve time-in-state information that endpoints, peaks, mean activity, or generic trajectory summaries may miss in tested trajectory regimes. "
            "The paragraph must also state the first boundary directly. A declared biological window is an author-specified analysis choice, not a causal mechanism, and amplitude or endpoint summaries can be sufficient when residence does not change the interpretation."
        ),
    },
    {
        "para_ids": ("PARA-DISCUSSION-001",),
        "claim_ids": ("CLM-0001",),
        "role": "Scope of public biological demonstrations",
        "text": (
            "The second paragraph should explain why the public DRG calcium and ERK GPCR examples matter for method scope. "
            "They show that residence-amplitude separation is not confined to the RhoA/microglia reference use case, but they do not establish a universal residence regime across all reporters or perturbations. "
            "This paragraph should preserve the distinction between a methods demonstration and a new primary disease-biology claim."
        ),
    },
    {
        "para_ids": ("PARA-DISCUSSION-002",),
        "claim_ids": ("CLM-0002", "CLM-0003", "CLM-0004"),
        "role": "Decision boundaries for non-trajectory inputs",
        "text": (
            "The third paragraph should synthesize bounded-coupling, reserve-like, and routed-output behavior without upgrading any limitation into a strength. "
            "Bounded-coupling decisions are admissible only under declared margins, uncertainty support, and visible inconclusive cases, and they do not exclude slower or context-specific coupling. "
            "Reserve-like summaries should remain tied to the measured endpoint rather than unmeasured biological reserve capacity. "
            "Routed-output comparisons can reject reduced alternatives in the tested endpoint demonstration without treating effective parameters as direct biochemical interactions."
        ),
    },
    {
        "para_ids": ("PARA-DISCUSSION-002",),
        "claim_ids": ("CLM-0005",),
        "role": "Software and reproducibility boundary",
        "text": (
            "The fourth paragraph should discuss inspectability through Python, CLI, backend, workbench, export bundles, checksums, and source-distribution clean-room reproduction. "
            "The supported claim is software reproducibility for the retained Stage 7 evidence, not a new biological result, regulatory qualification, hidden private-data reproduction, or PyPI publication claim. "
            "This paragraph should also make clear that controlled-access or non-redistributable inputs remain boundary cases rather than defects that the method can erase."
        ),
    },
    {
        "para_ids": ("PARA-DISCUSSION-001", "PARA-DISCUSSION-002"),
        "claim_ids": ("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"),
        "role": "Closing scope and future-use plan",
        "text": (
            "The closing paragraph should connect the method contribution to future use without adding new evidence. "
            "It should say that future applications should predeclare windows, margins, grouping levels, and reduced alternatives, then report pass, fail, and inconclusive outcomes with the same visibility. "
            "The final note should position RhoDyn as a decision framework for dynamic operating-state interpretation, not as an automatic mechanism-discovery engine."
        ),
    },
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


def _visible_text(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.startswith("<!--")).strip()


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", text))


def _build_discussion_blueprint(generated_utc: str, map_version: str) -> str:
    blocks = [
        f"<!-- DISCUSSION-BLUEPRINT stage=9.13 generated_utc={generated_utc} map_version={map_version} -->",
        "",
        (
            "<!-- map_rule=no_markdown_subheadings; source_contract=SEC-005; "
            "next_surface=discussion.md only after Stage 9.13 gate passes -->"
        ),
        "",
    ]
    for index, paragraph in enumerate(DISCUSSION_MAP_PARAGRAPHS, start=1):
        blocks.extend(
            [
                (
                    "<!-- "
                    f"discussion_paragraph={index} "
                    f"role={paragraph['role']} "
                    f"para_ids={';'.join(paragraph['para_ids'])} "
                    f"claim_ids={';'.join(paragraph['claim_ids'])}"
                    " -->"
                ),
                "",
                str(paragraph["text"]),
                "",
            ]
        )
    return "\n".join(blocks)


def _no_downstream_started() -> tuple[bool, list[str]]:
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden, forbidden


def _validate(blueprint_text: str) -> list[dict[str, Any]]:
    gate_912_pass = False
    if GATE_912.exists():
        try:
            gate_912_pass = _read_json(GATE_912).get("pass") is True
        except json.JSONDecodeError:
            gate_912_pass = False
    section_contract_ok = SECTION_CONTRACTS.exists() and "SEC-005. Discussion" in SECTION_CONTRACTS.read_text(encoding="utf-8")
    limits_available = LIMITATIONS_MATRIX.exists() and LIMITATIONS_TRACEABILITY.exists()
    prior_sections_available = RESULTS_DRAFT.exists() and INTRODUCTION_DRAFT.exists()
    visible = _visible_text(blueprint_text)
    no_subheadings = not any(line.startswith("#") for line in visible.splitlines())
    limitation_terms_present = all(term in visible for term in LIMITATION_TERMS)
    forbidden_absent = not any(phrase.lower() in visible.lower() for phrase in FORBIDDEN_DISCUSSION_MAP_PHRASES)
    no_downstream, downstream_paths = _no_downstream_started()
    para_comments = re.findall(r"para_ids=([^ ]+)", blueprint_text)
    covered_para_ids = sorted({item for group in para_comments for item in group.split(";") if item})
    claim_comments = re.findall(r"claim_ids=([^ ]+)", blueprint_text)
    covered_claim_ids = sorted({item for group in claim_comments for item in group.split(";") if item})
    return [
        {
            "name": "stage_9_12_gate_passed",
            "passed": gate_912_pass,
            "detail": "Stage 9.12 Introduction literature binding exists and passes" if gate_912_pass else "Stage 9.12 gate is missing or not passing",
        },
        {
            "name": "discussion_contract_available",
            "passed": section_contract_ok,
            "detail": "Stage 9.8 Discussion section contract is available",
        },
        {
            "name": "stage_7_limitations_represented",
            "passed": limits_available and limitation_terms_present,
            "detail": "Discussion map represents Stage 7 limitations and interpretation boundaries",
        },
        {
            "name": "no_limitation_converted_into_strength_without_evidence",
            "passed": forbidden_absent and "not a new biological result" in visible and "inconclusive" in visible,
            "detail": "Discussion map keeps limits visible rather than converting them into strengths",
        },
        {
            "name": "map_has_no_subheadings",
            "passed": no_subheadings and _word_count(visible) >= 250,
            "detail": f"Discussion map visible word count: {_word_count(visible)}; headings present: {not no_subheadings}",
        },
        {
            "name": "discussion_para_and_claim_ids_mapped",
            "passed": covered_para_ids == ["PARA-DISCUSSION-001", "PARA-DISCUSSION-002"]
            and covered_claim_ids == ["CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"],
            "detail": f"covered_para_ids={';'.join(covered_para_ids)} covered_claim_ids={';'.join(covered_claim_ids)}",
        },
        {
            "name": "prior_sections_available",
            "passed": prior_sections_available,
            "detail": "Introduction and Results draft are present as upstream context",
        },
        {
            "name": "no_discussion_or_downstream_surfaces_started",
            "passed": no_downstream,
            "detail": "No discussion.md, references.bib, Methods, figure legends, or submission package detected"
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
        if substage.get("id") == "9.13":
            substage["status"] = "complete_discussion_interpretation_mapped"
    registry["last_completed_substage"] = "9.13"
    registry["next_substage"] = "9.14"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], map_version: str, checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.13",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.13.json",
        "validation_outcome": "Discussion interpretation map registered with Stage 7 limitations represented",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.12.json",
            "manuscript/nature_methods/sections/section_contracts.md",
            "docs/stage7_limitations_matrix.md",
            "case_studies/stage7_methods_readiness/limitations_traceability.tsv",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/sections/discussion_blueprint.md",
            "manuscript/nature_methods/gate_verdicts/9.13.json",
        ],
        "remaining_blockers": [
            "Stage 9.14 Discussion drafting pass has not started",
            "Full reference library and citation audit have not started",
            "Online Methods and figure legends have not started",
            "Submission-package assembly has not started",
        ],
        "discussion_map_version": map_version,
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.13"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(map_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.13"
    memory["discussion_interpretation_map_started"] = True
    memory["discussion_map_version"] = map_version
    memory["status"] = "stage9_13_discussion_interpretation_mapped"
    memory["current_gate"] = "Stage 9.13 registered limitation-aware Discussion map without drafting Discussion"
    memory["next_substage"] = "9.14"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.13 Discussion interpretation map complete; Discussion drafting pass not started"
    memory["stage9_13_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/sections/discussion_blueprint.md",
        "manuscript/nature_methods/gate_verdicts/9.13.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.13 are complete through the Discussion interpretation map.",
        "Stage 9.14 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No discussion.md, Methods, full reference library, figure legends, or submission package contents are created in this map pass.",
        "Stage 7 limitations remain visible and are not converted into unsupported strengths.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "subsection architecture, Results drafting, Introduction literature binding, and Discussion interpretation mapping only. "
        "Do not start Discussion drafting, Methods, full reference library, figure legends, review response, or submission packaging "
        "without explicit substage authorization."
    )
    _upsert_completed_substage(memory, map_version, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(map_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.13 Discussion interpretation map complete; Discussion drafting pass not started"
    current["stage9_active_gate"] = "Stage 9.13 Discussion interpretation map complete; Discussion drafting pass not started"
    current["after_stage9_13_discussion_interpretation_map"] = (
        "Stage 9.13 registered a limitation-aware Discussion interpretation map. "
        "It represented Stage 7 limitations without drafting discussion.md, Methods, full reference library, figure legends, or submission-package assembly."
    )
    current["current_gate"] = "Discussion interpretation map complete without Discussion draft"
    current["next_stage"] = "Stage 9.14 Discussion drafting pass"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_13_discussion_interpretation_mapped"
        stage["current_gate"] = "Stage 9.13 registered limitation-aware Discussion map without drafting Discussion"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, and Discussion interpretation mapping only. Do not start Discussion drafting, "
            "Methods, full reference library, figure legends, review response, or submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/sections/discussion_blueprint.md",
            "manuscript/nature_methods/gate_verdicts/9.13.json",
            "scripts/run_stage9_13_discussion_interpretation_map.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        discussion_gate = "Stage 9.13 Discussion map represents Stage 7 limitations and contains no Discussion subheadings."
        if discussion_gate not in gate:
            gate.append(discussion_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.13":
                subphase["status"] = "complete_discussion_interpretation_mapped"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.13.json"
                subphase["discussion_map_version"] = map_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.12 registers Introduction prose in `sections/introduction.md`, `refs/introduction_citation_ledger.csv`, and `gate_verdicts/9.12.json`. The current state intentionally does not create `sections/discussion.md`, `sections/methods.md`, `refs/references.bib`, or submission-package files.",
            "Stage 9.12 registers Introduction prose in `sections/introduction.md`, `refs/introduction_citation_ledger.csv`, and `gate_verdicts/9.12.json`. Stage 9.13 registers a limitation-aware Discussion map in `sections/discussion_blueprint.md` and `gate_verdicts/9.13.json`. The current state intentionally does not create `sections/discussion.md`, `sections/methods.md`, `refs/references.bib`, or submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.13 | Discussion interpretation map | not_started | Plan limitation-aware Discussion before drafting. |",
            "| 9.13 | Discussion interpretation map | complete_discussion_interpretation_mapped | Plan limitation-aware Discussion before drafting. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "9.10 has registered Results subsection architecture, Stage 9.11 has\nregistered Results drafting, and Stage 9.12 has registered Introduction\nliterature binding. Discussion, Methods, full reference-library assembly, and\npackage assembly remain not started.",
            "9.10 has registered Results subsection architecture, Stage 9.11 has\nregistered Results drafting, Stage 9.12 has registered Introduction literature\nbinding, and Stage 9.13 has registered the Discussion interpretation map.\nDiscussion drafting, Methods, full reference-library assembly, and package\nassembly remain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.12 Introduction literature binding complete, Discussion interpretation map not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, and Introduction literature binding only. Do not start Discussion, Methods, full reference-library assembly, figure legends, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.13 Discussion interpretation map complete, Discussion drafting pass not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, and Discussion interpretation mapping only. Do not start Discussion drafting, Methods, full reference-library assembly, figure legends, review response, or submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map remains the next unstarted manuscript step. Discussion, Methods, full reference-library assembly, and package assembly remain not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass remains the next unstarted manuscript step. Discussion drafting, Methods, full reference-library assembly, and package assembly remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    map_version = f"discussion-map@{generated_utc[:10]}@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    blueprint_text = _build_discussion_blueprint(generated_utc, map_version)
    _write_text(STAGING_DIR / OUTPUTS["blueprint"].relative_to(WORKSPACE), blueprint_text)
    checks = _validate(blueprint_text)
    passed = all(check["passed"] for check in checks)
    visible = _visible_text(blueprint_text)
    gate = {
        "substage": "9.13",
        "timestamp": generated_utc,
        "discussion_map_version": map_version,
        "pass": passed,
        "checks": checks,
        "paragraph_count": len(DISCUSSION_MAP_PARAGRAPHS),
        "para_ids": ["PARA-DISCUSSION-001", "PARA-DISCUSSION-002"],
        "claim_ids": ["CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"],
        "discussion_map_word_count": _word_count(visible),
        "next_substage": "9.14",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Discussion interpretation map only. No discussion.md, Methods, full reference library, figure legends, or submission-package assembly.",
    }
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)
    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(map_version, generated_utc, checks)
        _update_roadmap_memory(map_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)
    return {
        "status": "pass" if passed else "fail",
        "substage": "9.13",
        "discussion_map_version": map_version,
        "paragraph_count": len(DISCUSSION_MAP_PARAGRAPHS),
        "discussion_map_word_count": _word_count(visible),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
        "next_allowed_action": "Proceed to Stage 9.14 Discussion drafting pass after validation and explicit authorization.",
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
