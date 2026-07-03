"""Run Stage 9.14 Discussion drafting pass.

Stage 9.14 drafts the no-subheading Discussion from the Stage 9.13
interpretation map. It does not create Methods, the full reference library,
figure legends, or a submission package.
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
STAGING_DIR = WORKSPACE / "_staging" / "9.14"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.14"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"

GATE_913 = GATE_DIR / "9.13.json"
DISCUSSION_BLUEPRINT = SECTIONS_DIR / "discussion_blueprint.md"
SECTION_CONTRACTS = SECTIONS_DIR / "section_contracts.md"

OUTPUTS = {
    "discussion": SECTIONS_DIR / "discussion.md",
    "gate": GATE_DIR / "9.14.json",
}

FORBIDDEN_STARTED_PATHS = [
    SECTIONS_DIR / "methods.md",
    SECTIONS_DIR / "data_availability.md",
    SECTIONS_DIR / "code_availability.md",
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
]

FORBIDDEN_DISCUSSION_PHRASES = (
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

REQUIRED_LIMIT_TERMS = (
    "declared biological window",
    "not a causal mechanism",
    "amplitude and endpoint summaries remain useful",
    "inconclusive",
    "slower or context-specific coupling",
    "reserve-like",
    "measured endpoint",
    "direct biochemical interactions",
    "not a new biological result",
    "Future directions",
)

DISCUSSION_PARAGRAPHS = [
    {
        "para_ids": ("PARA-DISCUSSION-001",),
        "claim_ids": ("CLM-0001", "CLM-0005"),
        "text": (
            "RhoDyn supports a methods claim that is deliberately narrower than a general theory of cell fate. "
            "The work makes residence-state inference an executable and inspectable object for live-cell perturbation data, so dwell fraction, dwell time, and segment count can be compared directly with endpoint, peak, mean, latency, and threshold-style summaries. "
            "That comparison matters because time spent inside a declared biological window can alter the interpretation of a trajectory even when amplitude summaries remain similar. "
            "At the same time, the declared window is not discovered automatically by the software, and residence is not a causal mechanism by itself. "
            "The appropriate conclusion is therefore not that residence replaces amplitude. It is that RhoDyn gives users a controlled way to ask when residence carries additional state information and when amplitude and endpoint summaries remain useful."
        ),
    },
    {
        "para_ids": ("PARA-DISCUSSION-001",),
        "claim_ids": ("CLM-0001",),
        "text": (
            "The public trajectory demonstrations extend that method claim beyond the motivating RhoA/microglia reference use case without turning it into a universal biological rule. "
            "DRG calcium and ERK GPCR reporter trajectories provide independent live-cell settings in which residence and amplitude can be separated under the same input schema, window-sensitivity logic, and uncertainty summaries. "
            "Those examples show that the method can travel across reporters and biological contexts, but they also mark the boundary of the evidence. "
            "They do not show that every signaling system contains a biologically meaningful residence regime, and they do not imply that the software generated the original RhoA/microglia manuscript results. "
            "They instead establish a reproducible route for asking the residence-versus-amplitude question on public time-series data. "
            "This distinction is important for a methods Article because the biological examples are not interchangeable validations of one mechanism. "
            "They are stress tests of an analysis object that must sometimes report separation, sometimes report agreement with simpler summaries, and sometimes withhold interpretation."
        ),
    },
    {
        "para_ids": ("PARA-DISCUSSION-002",),
        "claim_ids": ("CLM-0002", "CLM-0003", "CLM-0004"),
        "text": (
            "The same restraint is essential for the non-trajectory demonstrations. "
            "Bounded-coupling decisions are useful only when the margin, uncertainty rule, grouping level, and decision state are declared before interpretation, and the held-out ERK/Akt contexts show why inconclusive cases must remain visible. "
            "A passing bounded-coupling result supports equivalence within the stated margin and context, not the exclusion of slower or context-specific coupling. "
            "Reserve-like summaries are likewise interpretable only as coordinates tied to the measured endpoint, not as direct assays of unmeasured biological reserve capacity. "
            "Routed-output comparisons can show that reduced alternatives fail the tested endpoint constraints, but effective model parameters should not be treated as direct biochemical interactions."
        ),
    },
    {
        "para_ids": ("PARA-DISCUSSION-002",),
        "claim_ids": ("CLM-0005",),
        "text": (
            "RhoDyn's software evidence strengthens the method by making those decisions inspectable across use surfaces. "
            "The retained Stage 7 evidence can be regenerated through the source-distribution clean-room route, checked across Python, command-line, backend, and workbench paths, and exported with input schemas, parameter choices, summaries, figures, reports, and checksums. "
            "This supports software reproducibility for the demonstrated analyses, not a new biological result, regulatory qualification, or hidden private-data reproduction claim. "
            "It also leaves distribution boundaries visible. PyPI remains a later distribution decision, controlled-access inputs remain access-limited, and non-redistributable source material must be represented by reviewable derived tables or notes rather than silently absorbed into the method."
        ),
    },
    {
        "para_ids": ("PARA-DISCUSSION-001", "PARA-DISCUSSION-002"),
        "claim_ids": ("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"),
        "text": (
            "Future directions are therefore methodological as much as biological. "
            "Applications should predeclare residence windows, bounded-coupling margins, grouping levels, uncertainty rules, and reduced alternatives, then report pass, fail, and inconclusive outcomes with equal visibility. "
            "New biological systems can sharpen the method by showing when residence, reserve-like endpoints, or routed outputs add information and when simpler summaries are sufficient. "
            "The most informative next demonstrations will be those that preserve replicate structure, expose enough sampling density to justify a declared window, and include perturbation designs capable of separating timing from amplitude. "
            "Equally useful will be negative examples in which RhoDyn returns the same conclusion as a simpler endpoint method, because those cases define where extra dynamic structure is unnecessary. "
            "The present evidence supports RhoDyn as a decision framework for dynamic operating-state interpretation in live-cell perturbation biology. "
            "RhoDyn is not an automatic mechanism-discovery engine, a substitute for perturbation experiments, or a claim that one dynamical summary is privileged in every cell-state problem."
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


def _build_discussion(generated_utc: str, draft_version: str) -> str:
    blocks = [
        f"<!-- DISCUSSION-DRAFT stage=9.14 generated_utc={generated_utc} draft_version={draft_version} -->",
        "",
    ]
    for index, paragraph in enumerate(DISCUSSION_PARAGRAPHS, start=1):
        blocks.extend(
            [
                (
                    "<!-- "
                    f"discussion_paragraph={index} "
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


def _validate(discussion_text: str) -> list[dict[str, Any]]:
    gate_913_pass = False
    if GATE_913.exists():
        try:
            gate_913_pass = _read_json(GATE_913).get("pass") is True
        except json.JSONDecodeError:
            gate_913_pass = False
    blueprint_available = DISCUSSION_BLUEPRINT.exists()
    section_contract_ok = SECTION_CONTRACTS.exists() and "SEC-005. Discussion" in SECTION_CONTRACTS.read_text(encoding="utf-8")
    visible = _visible_text(discussion_text)
    no_subheadings = not any(line.startswith("#") for line in visible.splitlines())
    word_count = _word_count(visible)
    limit_terms_present = all(term in visible for term in REQUIRED_LIMIT_TERMS)
    forbidden_absent = not any(phrase.lower() in visible.lower() for phrase in FORBIDDEN_DISCUSSION_PHRASES)
    future_labeled = "Future directions" in visible
    no_downstream, downstream_paths = _no_downstream_started()
    para_comments = re.findall(r"para_ids=([^ ]+)", discussion_text)
    covered_para_ids = sorted({item for group in para_comments for item in group.split(";") if item})
    claim_comments = re.findall(r"claim_ids=([^ ]+)", discussion_text)
    covered_claim_ids = sorted({item for group in claim_comments for item in group.split(";") if item})
    return [
        {
            "name": "stage_9_13_gate_passed",
            "passed": gate_913_pass,
            "detail": "Stage 9.13 Discussion map exists and passes" if gate_913_pass else "Stage 9.13 gate is missing or not passing",
        },
        {
            "name": "discussion_contract_and_blueprint_available",
            "passed": section_contract_ok and blueprint_available,
            "detail": "Stage 9.8 Discussion contract and Stage 9.13 blueprint are available",
        },
        {
            "name": "discussion_contains_no_subheadings",
            "passed": no_subheadings and 650 <= word_count <= 900,
            "detail": f"Discussion visible word count: {word_count}; headings present: {not no_subheadings}",
        },
        {
            "name": "limitations_remain_visible",
            "passed": limit_terms_present and "not a new biological result" in visible and "not a causal mechanism" in visible,
            "detail": "Discussion retains Stage 7 limitations and interpretation boundaries",
        },
        {
            "name": "future_directions_are_labeled",
            "passed": future_labeled,
            "detail": "Discussion labels future directions without creating a subheading",
        },
        {
            "name": "no_limitation_or_scope_overclaim",
            "passed": forbidden_absent,
            "detail": "Discussion avoids universal, therapeutic, clinical, and mechanism-overclaim language",
        },
        {
            "name": "discussion_para_and_claim_ids_mapped",
            "passed": covered_para_ids == ["PARA-DISCUSSION-001", "PARA-DISCUSSION-002"]
            and covered_claim_ids == ["CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"],
            "detail": f"covered_para_ids={';'.join(covered_para_ids)} covered_claim_ids={';'.join(covered_claim_ids)}",
        },
        {
            "name": "no_methods_references_or_package_started",
            "passed": no_downstream,
            "detail": "No references.bib, Methods, figure legends, or submission package detected"
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
        if substage.get("id") == "9.14":
            substage["status"] = "complete_discussion_drafted"
    registry["last_completed_substage"] = "9.14"
    registry["next_substage"] = "9.15"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], draft_version: str, checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.14",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.14.json",
        "validation_outcome": "No-subheading Discussion draft registered with visible limitations and labeled future directions",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.13.json",
            "manuscript/nature_methods/sections/discussion_blueprint.md",
            "manuscript/nature_methods/sections/section_contracts.md",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/sections/discussion.md",
            "manuscript/nature_methods/gate_verdicts/9.14.json",
        ],
        "remaining_blockers": [
            "Stage 9.15 Online Methods contract implementation has not started",
            "Full reference library and citation audit have not started",
            "Figure legends have not started",
            "Submission-package assembly has not started",
        ],
        "discussion_draft_version": draft_version,
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.14"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(draft_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.14"
    memory["discussion_drafting_started"] = True
    memory["discussion_draft_version"] = draft_version
    memory["status"] = "stage9_14_discussion_drafted"
    memory["current_gate"] = "Stage 9.14 registered no-subheading Discussion draft without starting Methods"
    memory["next_substage"] = "9.15"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.14 Discussion drafting pass complete; Online Methods not started"
    memory["stage9_14_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/sections/discussion.md",
        "manuscript/nature_methods/gate_verdicts/9.14.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.14 are complete through Discussion drafting.",
        "Stage 9.15 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No Methods, full reference library, figure legends, or submission package contents are created in this Discussion pass.",
        "The Discussion contains no subheadings, keeps limitations visible, and labels future directions.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "subsection architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, and "
        "Discussion drafting only. Do not start Online Methods, full reference library, figure legends, review response, or "
        "submission packaging without explicit substage authorization."
    )
    _upsert_completed_substage(memory, draft_version, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(draft_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.14 Discussion drafting pass complete; Online Methods not started"
    current["stage9_active_gate"] = "Stage 9.14 Discussion drafting pass complete; Online Methods not started"
    current["after_stage9_14_discussion_drafting"] = (
        "Stage 9.14 registered a no-subheading Discussion draft with visible limitations and labeled future directions. "
        "It did not start Online Methods, full reference library, figure legends, or submission-package assembly."
    )
    current["current_gate"] = "Discussion draft complete without Online Methods"
    current["next_stage"] = "Stage 9.15 Online Methods contract implementation"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_14_discussion_drafted"
        stage["current_gate"] = "Stage 9.14 registered no-subheading Discussion draft without starting Methods"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, Discussion interpretation mapping, and Discussion drafting only. Do not start "
            "Online Methods, full reference library, figure legends, review response, or submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/sections/discussion.md",
            "manuscript/nature_methods/gate_verdicts/9.14.json",
            "scripts/run_stage9_14_discussion_drafting.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        discussion_gate = "Stage 9.14 Discussion draft contains no subheadings, visible limitations, and labeled future directions."
        if discussion_gate not in gate:
            gate.append(discussion_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.14":
                subphase["status"] = "complete_discussion_drafted"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.14.json"
                subphase["discussion_draft_version"] = draft_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.12 registers Introduction prose in `sections/introduction.md`, `refs/introduction_citation_ledger.csv`, and `gate_verdicts/9.12.json`. Stage 9.13 registers a limitation-aware Discussion map in `sections/discussion_blueprint.md` and `gate_verdicts/9.13.json`. The current state intentionally does not create `sections/discussion.md`, `sections/methods.md`, `refs/references.bib`, or submission-package files.",
            "Stage 9.12 registers Introduction prose in `sections/introduction.md`, `refs/introduction_citation_ledger.csv`, and `gate_verdicts/9.12.json`. Stage 9.13 registers a limitation-aware Discussion map in `sections/discussion_blueprint.md` and `gate_verdicts/9.13.json`. Stage 9.14 registers no-subheading Discussion prose in `sections/discussion.md` and `gate_verdicts/9.14.json`. The current state intentionally does not create `sections/methods.md`, `refs/references.bib`, or submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.14 | Discussion drafting pass | not_started | Draft balanced Discussion with no subheadings. |",
            "| 9.14 | Discussion drafting pass | complete_discussion_drafted | Draft balanced Discussion with no subheadings. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "9.10 has registered Results subsection architecture, Stage 9.11 has\nregistered Results drafting, Stage 9.12 has registered Introduction literature\nbinding, and Stage 9.13 has registered the Discussion interpretation map.\nDiscussion drafting, Methods, full reference-library assembly, and package\nassembly remain not started.",
            "9.10 has registered Results subsection architecture, Stage 9.11 has\nregistered Results drafting, Stage 9.12 has registered Introduction literature\nbinding, Stage 9.13 has registered the Discussion interpretation map, and\nStage 9.14 has registered Discussion drafting. Methods, full reference-library\nassembly, and package assembly remain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.13 Discussion interpretation map complete, Discussion drafting pass not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, and Discussion interpretation mapping only. Do not start Discussion drafting, Methods, full reference-library assembly, figure legends, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.14 Discussion drafting pass complete, Online Methods not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, and Discussion drafting only. Do not start Online Methods, full reference-library assembly, figure legends, review response, or submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass remains the next unstarted manuscript step. Discussion drafting, Methods, full reference-library assembly, and package assembly remain not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Online Methods contract implementation remains the next unstarted manuscript step. Methods, full reference-library assembly, and package assembly remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    draft_version = f"discussion-draft@{generated_utc[:10]}@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    discussion_text = _build_discussion(generated_utc, draft_version)
    _write_text(STAGING_DIR / OUTPUTS["discussion"].relative_to(WORKSPACE), discussion_text)
    checks = _validate(discussion_text)
    passed = all(check["passed"] for check in checks)
    visible = _visible_text(discussion_text)
    gate = {
        "substage": "9.14",
        "timestamp": generated_utc,
        "discussion_draft_version": draft_version,
        "pass": passed,
        "checks": checks,
        "paragraph_count": len(DISCUSSION_PARAGRAPHS),
        "para_ids": ["PARA-DISCUSSION-001", "PARA-DISCUSSION-002"],
        "claim_ids": ["CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"],
        "discussion_word_count": _word_count(visible),
        "next_substage": "9.15",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Discussion draft only. No Online Methods, full reference library, figure legends, or submission-package assembly.",
    }
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)
    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(draft_version, generated_utc, checks)
        _update_roadmap_memory(draft_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)
    return {
        "status": "pass" if passed else "fail",
        "substage": "9.14",
        "discussion_draft_version": draft_version,
        "paragraph_count": len(DISCUSSION_PARAGRAPHS),
        "discussion_word_count": _word_count(visible),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
        "next_allowed_action": "Proceed to Stage 9.15 Online Methods contract implementation after validation and explicit authorization.",
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
