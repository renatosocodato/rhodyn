"""Run Stage 9.11 Results drafting pass.

Stage 9.11 drafts the Results section in the locked FIG-001 through FIG-006
order from the Stage 9.10 Results architecture. It does not resolve citations,
draft the Introduction, Discussion, Methods, figure legends, references, or a
submission package.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SECTIONS_DIR = WORKSPACE / "sections"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.11"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.11"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"

GATE_910 = GATE_DIR / "9.10.json"
RESULTS_BLUEPRINT = SECTIONS_DIR / "results_blueprint.md"

OUTPUTS = {
    "results": SECTIONS_DIR / "results.md",
    "gate": GATE_DIR / "9.11.json",
}

FORBIDDEN_STARTED_PATHS = [
    SECTIONS_DIR / "introduction.md",
    SECTIONS_DIR / "discussion.md",
    SECTIONS_DIR / "methods.md",
    SECTIONS_DIR / "data_availability.md",
    SECTIONS_DIR / "code_availability.md",
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
]

FORBIDDEN_RESULTS_PHRASES = (
    "universal",
    "guarantees",
    "therapeutic",
    "clinical",
    "diagnostic",
    "proves no crosstalk",
    "absence of all coupling",
    "literal molecular edge",
    "RhoDyn generated the original",
)


@dataclass(frozen=True)
class ResultsParagraph:
    para_ids: tuple[str, ...]
    unit_id: str
    figure_id: str
    figure_number: str
    claim_ids: tuple[str, ...]
    heading: str
    text: str


RESULTS_PARAGRAPHS = [
    ResultsParagraph(
        para_ids=("PARA-RESULTS-001",),
        unit_id="RES-001",
        figure_id="FIG-001",
        figure_number="1",
        claim_ids=("CLM-0001", "CLM-0005"),
        heading="RhoDyn defines residence-state inference as an executable method object",
        text=(
            "RhoDyn first had to be defined as a method object rather than as a collection of post hoc trajectory summaries. "
            "The input contract and workflow schematic (Fig. 1a) specify tidy trajectory or endpoint tables, declared biological windows, replicate variables, and exportable decision outputs. "
            "The residence-window panel (Fig. 1b) separates dwell fraction, dwell time, and segment count from peak, endpoint, and average amplitude, making time-in-state an explicit summary of the supplied trajectory rather than a hidden fitted state. "
            "Boundary cases (Fig. 1c) identify inputs that remain unresolved when time, condition, replicate, or window definitions are missing. "
            "Executable truth cases (Fig. 1d) then provide positive, negative, and ambiguous examples in which the same API returns a result or withholds one. "
            "This establishes RhoDyn as an inspectable residence-state analysis object with explicit failure modes, and it creates the need to test whether those summaries change interpretation relative to simpler baselines."
        ),
    ),
    ResultsParagraph(
        para_ids=("PARA-RESULTS-001",),
        unit_id="RES-002",
        figure_id="FIG-002",
        figure_number="2",
        claim_ids=("CLM-0001", "CLM-0004"),
        heading="Synthetic benchmarks separate residence structure from simpler summaries",
        text=(
            "Known synthetic regimes provide the first controlled test because the correct interpretation is available before any biological example is considered. "
            "The regime grid (Fig. 2a) places amplitude-like, residence-like, ambiguous, and negative cases on shared simulated inputs. "
            "Comparing residence and amplitude summaries on those inputs (Fig. 2b) shows when dwell within a declared window changes the state assignment relative to endpoint, peak, or mean activity. "
            "The reduced-alternative comparison (Fig. 2c) asks whether simpler summaries can reproduce the same decision structure, while the negative and ambiguous cases (Fig. 2d) keep unsupported calls visible instead of forcing classification. "
            "Together, these benchmarks support residence-state inference in tested trajectory regimes while preserving cases where RhoDyn should remain inconclusive."
        ),
    ),
    ResultsParagraph(
        para_ids=("PARA-RESULTS-002",),
        unit_id="RES-003",
        figure_id="FIG-003",
        figure_number="3",
        claim_ids=("CLM-0001",),
        heading="Public live-cell trajectories test residence-amplitude separation beyond the reference use case",
        text=(
            "After synthetic truth cases, independent public trajectories tested whether the same analysis object could expose residence-amplitude separation outside the reference use case. "
            "The public-data adapter map (Fig. 3a) shows how external calcium and ERK time-series tables are converted into the tidy input schema without changing their biological provenance. "
            "In the DRG calcium example (Fig. 3b), residence summaries capture time spent inside the declared response window separately from the amplitude of the calcium trace. "
            "In the ERK GPCR example (Fig. 3c), the same comparison separates window occupancy from peak or endpoint signaling. "
            "Window-sensitivity and uncertainty summaries (Fig. 3d) then show whether the interpretation is stable, fragile, or unresolved as the declared window changes. "
            "These public examples support the claim that residence and amplitude can diverge in more than one live-cell signaling system, without implying that residence summaries replace amplitude analysis for every reporter."
        ),
    ),
    ResultsParagraph(
        para_ids=("PARA-RESULTS-003", "PARA-RESULTS-004", "PARA-RESULTS-005"),
        unit_id="RES-004",
        figure_id="FIG-004",
        figure_number="4",
        claim_ids=("CLM-0002", "CLM-0003", "CLM-0004"),
        heading="Endpoint demonstrations link bounded coupling, reserve-like buffering, and routed-output alternatives",
        text=(
            "Trajectory summaries do not cover all perturbation biology, so the next test moved to endpoint and paired-reporter inputs. "
            "The endpoint schema contract (Fig. 4a) defines the grouping, contrast, margin, and readout fields needed before any bounded-coupling or model-comparison decision is made. "
            "Bounded-coupling decisions under declared margins (Fig. 4b) distinguish passing, failing, and inconclusive contrasts rather than treating a non-significant difference as equivalence. "
            "The reserve-like coordinate (Fig. 4c) is explicitly tied to the measured endpoint, so the draft can describe buffering-like behavior without claiming unmeasured biological reserve capacity. "
            "Routed-output reduced-architecture comparisons (Fig. 4d) test whether simpler alternatives satisfy the observed endpoint structure, and the limitations panel (Fig. 4e) records which mechanistic interpretations remain outside the measured scope. "
            "This extends RhoDyn from trajectory residence scoring to endpoint decision support, while keeping coupling, reserve-like, and routed-output claims conditional on declared margins, uncertainty, and model alternatives."
        ),
    ),
    ResultsParagraph(
        para_ids=("PARA-RESULTS-003",),
        unit_id="RES-005",
        figure_id="FIG-005",
        figure_number="5",
        claim_ids=("CLM-0002",),
        heading="Held-out contexts expose bounded-coupling pass and inconclusive regimes",
        text=(
            "Because bounded-coupling calls depend on the declared margin and context, held-out cases were used to test whether the decision rule exposes both support and non-resolution. "
            "The held-out analysis plan (Fig. 5a) separates the primary decision rule from later margin and access-boundary checks. "
            "Passing contexts (Fig. 5b) show where the declared margin and uncertainty support a bounded-coupling decision. "
            "Inconclusive margin-boundary contexts (Fig. 5c) show the complementary case, where available evidence does not justify upgrading the contrast to equivalence. "
            "Margin-sensitivity behavior (Fig. 5d) makes that dependence visible, and the controlled-access boundary (Fig. 5e) records cases where the input cannot be fully redistributed. "
            "The held-out Results unit therefore keeps pass and inconclusive states side by side, which is essential for using RhoDyn as a decision framework rather than an automatic equivalence engine."
        ),
    ),
    ResultsParagraph(
        para_ids=("PARA-RESULTS-006",),
        unit_id="RES-006",
        figure_id="FIG-006",
        figure_number="6",
        claim_ids=("CLM-0005",),
        heading="Software parity and archive reproduction make the method inspectable",
        text=(
            "The final Results step asks whether the method can be inspected and reproduced through the software surfaces a user would actually encounter. "
            "The parity panel (Fig. 6a) compares Python, CLI, backend, and workbench outputs for the retained evidence paths. "
            "The export-bundle view (Fig. 6b) shows that inputs, parameter choices, summaries, figures, and reports are written together rather than hidden in session state. "
            "Source-distribution clean-room reproduction (Fig. 6c) tests the archived package from an installable release boundary, while the archive and checksum panel (Fig. 6d) records the release identity and file-level reproducibility surface. "
            "The adoption and user-path rehearsal (Fig. 6e) then checks whether a biologist-facing and a quantitative workflow can reach the same reviewable outputs. "
            "These results support cross-surface reproducibility for the retained Stage 7 evidence and close the Results section by making RhoDyn's computational decisions inspectable rather than merely available as code."
        ),
    ),
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


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", text))


def _result_body_only(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.startswith("<!--")).strip()


def _build_results(generated_utc: str, draft_version: str) -> str:
    blocks = [
        "# Results",
        "",
        f"<!-- RESULTS-DRAFT stage=9.11 generated_utc={generated_utc} draft_version={draft_version} -->",
        "",
    ]
    for paragraph in RESULTS_PARAGRAPHS:
        blocks.extend(
            [
                f"## {paragraph.heading}",
                "",
                (
                    "<!-- "
                    f"para_ids={';'.join(paragraph.para_ids)} "
                    f"unit_id={paragraph.unit_id} "
                    f"figure_id={paragraph.figure_id} "
                    f"claim_ids={';'.join(paragraph.claim_ids)}"
                    " -->"
                ),
                "",
                paragraph.text,
                "",
            ]
        )
    return "\n".join(blocks)


def _contains_citation(text: str) -> bool:
    citation_patterns = [
        r"\([A-Z][A-Za-z-]+ et al\.,? \d{4}\)",
        r"\([A-Z][A-Za-z-]+, \d{4}\)",
        r"\[\d+(?:,\s*\d+)*\]",
        r"\(\d+(?:-\d+|,\s*\d+)*\)",
        r"doi:",
        r"https?://",
        r"REF-\d+",
    ]
    return any(re.search(pattern, text) for pattern in citation_patterns)


def _figure_call_numbers(text: str) -> list[str]:
    return re.findall(r"\bFig\. ([1-6])", text)


def _no_downstream_started() -> tuple[bool, list[str]]:
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden, forbidden


def _validate(results_text: str) -> list[dict[str, Any]]:
    gate_910_pass = False
    if GATE_910.exists():
        try:
            gate_910_pass = _read_json(GATE_910).get("pass") is True
        except json.JSONDecodeError:
            gate_910_pass = False
    blueprint_ok = RESULTS_BLUEPRINT.exists() and "Results unit map" in RESULTS_BLUEPRINT.read_text(encoding="utf-8")
    body = _result_body_only(results_text)
    para_comments = re.findall(r"para_ids=([^ ]+)", results_text)
    covered_para_ids = sorted({item for group in para_comments for item in group.split(";") if item})
    expected_para_ids = [
        "PARA-RESULTS-001",
        "PARA-RESULTS-002",
        "PARA-RESULTS-003",
        "PARA-RESULTS-004",
        "PARA-RESULTS-005",
        "PARA-RESULTS-006",
    ]
    figure_numbers = _figure_call_numbers(body)
    figure_set_ok = set(figure_numbers) == {"1", "2", "3", "4", "5", "6"} and all(
        str(idx) in figure_numbers for idx in range(1, 7)
    )
    figure_order = [figure_numbers.index(str(idx)) for idx in range(1, 7)] if figure_set_ok else []
    figure_order_ok = figure_set_ok and figure_order == sorted(figure_order)
    forbidden_absent = not any(phrase.lower() in body.lower() for phrase in FORBIDDEN_RESULTS_PHRASES)
    no_citations = not _contains_citation(body)
    required_terms = all(
        phrase in body
        for phrase in [
            "residence-state",
            "bounded-coupling",
            "reserve-like",
            "routed-output",
            "inconclusive",
            "cross-surface reproducibility",
        ]
    )
    heading_count = len(re.findall(r"^## ", results_text, flags=re.MULTILINE))
    no_downstream, downstream_paths = _no_downstream_started()
    return [
        {
            "name": "stage_9_10_gate_passed",
            "passed": gate_910_pass,
            "detail": "Stage 9.10 Results architecture exists and passes" if gate_910_pass else "Stage 9.10 gate is missing or not passing",
        },
        {
            "name": "results_blueprint_available",
            "passed": blueprint_ok,
            "detail": "Results draft resolves to Stage 9.10 Results blueprint",
        },
        {
            "name": "every_results_paragraph_has_para_id",
            "passed": covered_para_ids == expected_para_ids and len(para_comments) == len(RESULTS_PARAGRAPHS),
            "detail": f"Covered Results paragraph IDs: {';'.join(covered_para_ids)}",
        },
        {
            "name": "figure_callouts_resolve",
            "passed": figure_order_ok,
            "detail": "Figure callouts resolve in Fig. 1 through Fig. 6 order",
        },
        {
            "name": "strength_caps_hold",
            "passed": forbidden_absent and required_terms,
            "detail": "Results draft preserves bounded residence, coupling, reserve-like, routed-output, inconclusive, and reproducibility language",
        },
        {
            "name": "results_are_unreferenced_until_citation_stage",
            "passed": no_citations,
            "detail": "Results draft contains no citation calls before Stage 9.20 reference resolution",
        },
        {
            "name": "topical_results_subheadings_present",
            "passed": heading_count == 6,
            "detail": "Results draft contains six topical subheadings",
        },
        {
            "name": "no_downstream_stage9_surfaces_started",
            "passed": no_downstream,
            "detail": "No Introduction, Discussion, Methods, references, legends, or submission package detected"
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
        if substage.get("id") == "9.11":
            substage["status"] = "complete_results_draft_registered"
    registry["last_completed_substage"] = "9.11"
    registry["next_substage"] = "9.12"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], draft_version: str, checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.11",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.11.json",
        "validation_outcome": "Results draft registered in figure-locked order with paragraph IDs and strength caps",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.10.json",
            "manuscript/nature_methods/sections/results_blueprint.md",
            "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
            "manuscript/nature_methods/ledgers/paragraph_claim_ledger.csv",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/sections/results.md",
            "manuscript/nature_methods/gate_verdicts/9.11.json",
        ],
        "remaining_blockers": [
            "Stage 9.12 Introduction literature binding has not started",
            "Citation resolution has not started",
            "Discussion, Methods, and figure legends have not started",
            "Submission-package assembly has not started",
        ],
        "results_draft_version": draft_version,
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.11"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(draft_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.11"
    memory["results_drafting_started"] = True
    memory["results_draft_version"] = draft_version
    memory["status"] = "stage9_11_results_draft_registered"
    memory["current_gate"] = "Stage 9.11 registered Results draft without starting Introduction or citation resolution"
    memory["next_substage"] = "9.12"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.11 Results drafting pass registered; Introduction literature binding not started"
    memory["stage9_11_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/sections/results.md",
        "manuscript/nature_methods/gate_verdicts/9.11.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.11 are complete through Results drafting.",
        "Stage 9.12 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No Introduction, Discussion, Methods, references, figure legends, or submission package contents are created in this Results drafting pass.",
        "Every Results paragraph has a PARA ID, figure callouts resolve, and strength caps hold.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "subsection architecture, and Results drafting only. Do not start Introduction, citation resolution, Discussion, Methods, "
        "figure legends, review response, or submission packaging without explicit substage authorization."
    )
    _upsert_completed_substage(memory, draft_version, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(draft_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.11 Results drafting pass registered; Introduction literature binding not started"
    current["stage9_active_gate"] = "Stage 9.11 Results drafting pass registered; Introduction literature binding not started"
    current["after_stage9_11_results_drafting"] = (
        "Stage 9.11 registered a figure-locked Results draft with PARA IDs, resolved Fig. 1 through Fig. 6 callouts, and claim-strength boundaries. "
        "It did not start Introduction literature binding, citation resolution, Discussion, Methods, figure legends, or submission-package assembly."
    )
    current["current_gate"] = "Results draft registered without Introduction or citation resolution"
    current["next_stage"] = "Stage 9.12 Introduction literature binding"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_11_results_draft_registered"
        stage["current_gate"] = "Stage 9.11 registered Results draft without starting Introduction or citation resolution"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
            "subsection architecture, and Results drafting only. Do not start Introduction, citation resolution, Discussion, Methods, "
            "figure legends, review response, or submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/sections/results.md",
            "manuscript/nature_methods/gate_verdicts/9.11.json",
            "scripts/run_stage9_11_results_drafting.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        results_gate = "Stage 9.11 Results draft uses PARA IDs, resolved figure callouts, and strength-capped interpretation."
        if results_gate not in gate:
            gate.append(results_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.11":
                subphase["status"] = "complete_results_draft_registered"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.11.json"
                subphase["results_draft_version"] = draft_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "and registers Results subsection architecture in Stage 9.10. It does not begin Results prose drafting, citation resolution, Introduction, Discussion, Methods, editorial polishing, or package assembly.",
            "registers Results subsection architecture in Stage 9.10, and registers a Results draft in Stage 9.11. It does not begin Introduction literature binding, citation resolution, Discussion, Methods, editorial polishing, or package assembly.",
        )
        body = _replace_once(
            body,
            "Stage 9.10 registers Results subsection architecture in `sections/results_blueprint.md` and `gate_verdicts/9.10.json`. The current state intentionally does not create `sections/results.md`, `sections/introduction.md`,",
            "Stage 9.10 registers Results subsection architecture in `sections/results_blueprint.md` and `gate_verdicts/9.10.json`. Stage 9.11 registers Results prose in `sections/results.md` and `gate_verdicts/9.11.json`. The current state intentionally does not create `sections/introduction.md`,",
        )
        body = _replace_once(
            body,
            "| 9.11 | Results drafting pass | not_started | Draft Results in figure-locked order. |",
            "| 9.11 | Results drafting pass | complete_results_draft_registered | Draft Results in figure-locked order. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.9 has registered title, subtitle, and abstract strategy, and Stage\n9.10 has registered Results subsection architecture. Results prose drafting,\ncitation resolution, Introduction, Discussion, Methods, and package assembly\nremain not started.",
            "Stage 9.9 has registered title, subtitle, and abstract strategy, Stage\n9.10 has registered Results subsection architecture, and Stage 9.11 has\nregistered Results drafting. Introduction literature binding, citation\nresolution, Discussion, Methods, and package assembly remain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.10 Results subsection architecture registered, Results drafting not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, and Results architecture only. Do not start Results drafting, citation resolution, Introduction, Discussion, Methods, figure legends, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.11 Results drafting pass registered, Introduction literature binding not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, and Results drafting only. Do not start Introduction, citation resolution, Discussion, Methods, figure legends, review response, or submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass remains the next unstarted manuscript step. Results prose, citation resolution, Introduction, Discussion, Methods, and package assembly remain not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding remains the next unstarted manuscript step. Introduction, citation resolution, Discussion, Methods, and package assembly remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    draft_version = f"results-draft@{generated_utc[:10]}@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    results_text = _build_results(generated_utc, draft_version)
    _write_text(STAGING_DIR / OUTPUTS["results"].relative_to(WORKSPACE), results_text)
    checks = _validate(results_text)
    passed = all(check["passed"] for check in checks)
    body = _result_body_only(results_text)
    gate = {
        "substage": "9.11",
        "timestamp": generated_utc,
        "results_draft_version": draft_version,
        "pass": passed,
        "checks": checks,
        "paragraph_count": len(RESULTS_PARAGRAPHS),
        "para_ids": sorted({para_id for paragraph in RESULTS_PARAGRAPHS for para_id in paragraph.para_ids}),
        "figure_callouts": sorted({f"Fig. {number}" for number in _figure_call_numbers(body)}),
        "claim_ids": sorted({claim_id for paragraph in RESULTS_PARAGRAPHS for claim_id in paragraph.claim_ids}),
        "results_word_count": _word_count(body),
        "next_substage": "9.12",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Results draft only. No Introduction, citation resolution, Discussion, Methods, figure legends, references, or submission-package assembly.",
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
        "substage": "9.11",
        "results_draft_version": draft_version,
        "paragraph_count": len(RESULTS_PARAGRAPHS),
        "results_word_count": _word_count(body),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
        "next_allowed_action": "Proceed to Stage 9.12 Introduction literature binding after validation and explicit authorization.",
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
