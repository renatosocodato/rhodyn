"""Run Stage 9.10 Results subsection architecture generation.

Stage 9.10 converts the frozen claim, paragraph, figure, and supplementary
ledgers into Results drafting units. It may create a Results blueprint. It does
not draft Results prose, resolve references, write legends, start Methods or
Discussion, or assemble a submission package.
"""

from __future__ import annotations

import csv
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
LEDGER_DIR = WORKSPACE / "ledgers"
STAGING_DIR = WORKSPACE / "_staging" / "9.10"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.10"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"

GATE_99 = GATE_DIR / "9.9.json"
CLAIM_LEDGER = LEDGER_DIR / "claim_hierarchy.csv"
PARAGRAPH_LEDGER = LEDGER_DIR / "paragraph_claim_ledger.csv"
FIGURE_LEDGER = LEDGER_DIR / "figure_to_claim_to_artifact.csv"
SUPPLEMENTARY_LEDGER = LEDGER_DIR / "supplementary_callout_ledger.csv"
EVIDENCE_MANIFEST = LEDGER_DIR / "stage9_evidence_manifest.csv"
SECTION_CONTRACTS = SECTIONS_DIR / "section_contracts.md"
MAIN_FIGURE_SPINE = WORKSPACE / "figures" / "main_figure_spine.md"

OUTPUTS = {
    "results_blueprint": SECTIONS_DIR / "results_blueprint.md",
    "gate": GATE_DIR / "9.10.json",
}

FORBIDDEN_STARTED_PATHS = [
    SECTIONS_DIR / "results.md",
    SECTIONS_DIR / "introduction.md",
    SECTIONS_DIR / "discussion.md",
    SECTIONS_DIR / "methods.md",
    SECTIONS_DIR / "data_availability.md",
    SECTIONS_DIR / "code_availability.md",
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
]

RESULTS_FIGURE_ORDER = ("FIG-001", "FIG-002", "FIG-003", "FIG-004", "FIG-005", "FIG-006")
FORBIDDEN_CONCLUSION_PHRASES = (
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
class ResultsUnit:
    unit_id: str
    subheading: str
    figure_id: str
    paragraph_ids: tuple[str, ...]
    claim_ids: tuple[str, ...]
    purpose: str
    evidence_move: str
    drafting_task: str
    allowed_conclusion: str
    prohibited_overclaim: str
    next_pressure: str


RESULTS_UNITS = [
    ResultsUnit(
        unit_id="RES-001",
        subheading="RhoDyn defines residence-state inference as an executable method object",
        figure_id="FIG-001",
        paragraph_ids=("PARA-RESULTS-001",),
        claim_ids=("CLM-0001", "CLM-0005"),
        purpose="Define the input, metric, output, and failure-mode object before the manuscript evaluates any biological example.",
        evidence_move="Use the method-object schematic, residence-window metrics, failure-mode boundary, and truth-case ladder as the visible evidence chain.",
        drafting_task="Explain what RhoDyn accepts, what it scores, what it returns, and what it refuses to infer from insufficient inputs.",
        allowed_conclusion="May conclude that RhoDyn formalizes residence-state analysis with executable truth cases and explicit interpretation boundaries.",
        prohibited_overclaim="Do not imply that every live-cell dataset contains a residence regime or that RhoDyn automatically discovers the correct biological window.",
        next_pressure="Once the method object is explicit, the Results must test whether it adds information beyond endpoint and amplitude summaries.",
    ),
    ResultsUnit(
        unit_id="RES-002",
        subheading="Synthetic benchmarks separate residence structure from simpler summaries",
        figure_id="FIG-002",
        paragraph_ids=("PARA-RESULTS-001",),
        claim_ids=("CLM-0001", "CLM-0004"),
        purpose="Benchmark residence summaries against amplitude, endpoint, threshold, and reduced-architecture alternatives on shared inputs.",
        evidence_move="Use the synthetic regime grid, residence-versus-amplitude comparison, reduced-alternative comparison, and negative or ambiguous failure behavior.",
        drafting_task="Show where residence-state inference changes the interpretation and where the same inputs remain ambiguous or unsupported.",
        allowed_conclusion="May conclude that residence summaries reveal time-in-state structure beyond simpler summaries in tested synthetic regimes while preserving negative and ambiguous cases.",
        prohibited_overclaim="Do not describe synthetic truth cases as new biological evidence or as proof of a universal residence law.",
        next_pressure="A synthetic benchmark is necessary but not sufficient, so the Results must next test independent public live-cell signaling systems.",
    ),
    ResultsUnit(
        unit_id="RES-003",
        subheading="Public live-cell trajectories test residence-amplitude separation beyond the reference use case",
        figure_id="FIG-003",
        paragraph_ids=("PARA-RESULTS-002",),
        claim_ids=("CLM-0001",),
        purpose="Show that residence-amplitude separation is not restricted to the RhoA/microglia reference logic.",
        evidence_move="Use the public-data adapter map, DRG calcium trajectory summary, ERK GPCR trajectory summary, and window-sensitivity or uncertainty summary.",
        drafting_task="Describe how public trajectory inputs are converted into tidy residence and amplitude summaries, then compare the readout-level interpretation.",
        allowed_conclusion="May conclude that independent public calcium and ERK systems contain tested cases where residence and amplitude summaries diverge.",
        prohibited_overclaim="Do not claim that residence logic replaces amplitude analysis in all reporters or perturbation systems.",
        next_pressure="Trajectory evidence does not cover endpoint perturbation experiments, so the Results must define how RhoDyn handles coupling, reserve-like, and routed-output readouts.",
    ),
    ResultsUnit(
        unit_id="RES-004",
        subheading="Endpoint demonstrations link bounded coupling, reserve-like buffering, and routed-output alternatives",
        figure_id="FIG-004",
        paragraph_ids=("PARA-RESULTS-003", "PARA-RESULTS-004", "PARA-RESULTS-005"),
        claim_ids=("CLM-0002", "CLM-0003", "CLM-0004"),
        purpose="Extend the Results from trajectory-only summaries to perturbation endpoint, paired-reporter, reserve-like, and routed-output demonstrations.",
        evidence_move="Use the endpoint schema contract, bounded-coupling decisions under declared margins, reserve-like coordinate, routed-output architecture comparison, and measurement-scoped limitations.",
        drafting_task="Keep the declared margin, uncertainty state, measurement scope, and reduced alternatives visible before drawing any local conclusion.",
        allowed_conclusion="May conclude that RhoDyn can support bounded-coupling, measurement-scoped reserve-like, and routed-output decisions when margins, uncertainty, and model alternatives are explicit.",
        prohibited_overclaim="Do not claim absence of all coupling, unmeasured biological reserve capacity, or direct biochemical wiring from effective model terms.",
        next_pressure="Because bounded decisions depend on margins and context, the Results must test held-out cases and expose inconclusive boundaries.",
    ),
    ResultsUnit(
        unit_id="RES-005",
        subheading="Held-out contexts expose bounded-coupling pass and inconclusive regimes",
        figure_id="FIG-005",
        paragraph_ids=("PARA-RESULTS-003",),
        claim_ids=("CLM-0002",),
        purpose="Show that bounded-coupling decisions remain conditional on declared margins, held-out context, and controlled-access limits.",
        evidence_move="Use the held-out analysis plan, passing bounded-coupling contexts, inconclusive margin-boundary contexts, margin sensitivity, and controlled-access boundary.",
        drafting_task="Report the pass, inconclusive, and boundary cases together so the method is not presented as an automatic equivalence engine.",
        allowed_conclusion="May conclude that bounded-coupling calls are decision-ready in passing contexts and intentionally inconclusive near margin or access boundaries.",
        prohibited_overclaim="Do not convert inconclusive or margin-sensitive held-out behavior into equivalence language.",
        next_pressure="After the method boundaries are visible, the Results must show that the implementation reproduces the same outputs across user-facing surfaces.",
    ),
    ResultsUnit(
        unit_id="RES-006",
        subheading="Software parity and archive reproduction make the method inspectable",
        figure_id="FIG-006",
        paragraph_ids=("PARA-RESULTS-006",),
        claim_ids=("CLM-0005",),
        purpose="Make reproducibility and adoption evidence part of the methods result rather than a back-matter assertion.",
        evidence_move="Use the Python, CLI, backend, and workbench parity checks, export bundle anatomy, source-distribution clean-room reproduction, archive checksums, and user-path rehearsal.",
        drafting_task="Describe cross-surface parity, inspectable export contents, archive identity, and user-path behavior without implying private-data reproduction.",
        allowed_conclusion="May conclude that retained Stage 7 evidence is reproducible across the documented RhoDyn software surfaces and archived release package.",
        prohibited_overclaim="Do not claim PyPI publication, hidden private-data reproduction, or production-grade regulated deployment.",
        next_pressure="The Results can then hand the manuscript to the Discussion, where the method contribution and biological interpretation limits are synthesized without adding new evidence.",
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


def _read_csv(path: Path, key: str) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row[key]: row for row in csv.DictReader(handle)}


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _split_ids(value: str) -> list[str]:
    if not value or value.startswith("pending_") or value == "none":
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def _markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("|", "\\|") for column in columns) + " |")
    return "\n".join(lines)


def _supplementary_by_unit(unit: ResultsUnit, supplementary_rows: list[dict[str, str]]) -> list[str]:
    matched: list[str] = []
    for row in supplementary_rows:
        callout_location = row.get("callout_location", "")
        if any(para_id in callout_location for para_id in unit.paragraph_ids):
            supp_id = row.get("supp_id", "")
            if supp_id and supp_id not in matched:
                matched.append(supp_id)
    return matched


def _unit_art_ids(unit: ResultsUnit, figure_rows: dict[str, dict[str, str]]) -> list[str]:
    return _split_ids(figure_rows[unit.figure_id]["art_ids"])


def _unit_strength_caps(unit: ResultsUnit, claims: dict[str, dict[str, str]]) -> list[str]:
    return [claims[claim_id]["strength_cap"] for claim_id in unit.claim_ids if claim_id in claims]


def _unit_rows(
    figure_rows: dict[str, dict[str, str]],
    supplementary_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for unit in RESULTS_UNITS:
        rows.append(
            {
                "unit_id": unit.unit_id,
                "subheading": unit.subheading,
                "paragraph_ids": ";".join(unit.paragraph_ids),
                "figure_id": unit.figure_id,
                "claim_ids": ";".join(unit.claim_ids),
                "art_ids": ";".join(_unit_art_ids(unit, figure_rows)),
                "supplementary_ids": ";".join(_supplementary_by_unit(unit, supplementary_rows)) or "none",
            }
        )
    return rows


def _build_results_blueprint(
    generated_utc: str,
    architecture_version: str,
    claims: dict[str, dict[str, str]],
    paragraphs: dict[str, dict[str, str]],
    figure_rows: dict[str, dict[str, str]],
    supplementary_rows: list[dict[str, str]],
) -> str:
    overview_rows = _unit_rows(figure_rows, supplementary_rows)
    detail_blocks: list[str] = []
    for unit in RESULTS_UNITS:
        figure = figure_rows[unit.figure_id]
        supplementary_ids = _supplementary_by_unit(unit, supplementary_rows)
        art_ids = _unit_art_ids(unit, figure_rows)
        strength_caps = _unit_strength_caps(unit, claims)
        paragraph_purposes = [paragraphs[para_id]["purpose"] for para_id in unit.paragraph_ids if para_id in paragraphs]
        detail_blocks.extend(
            [
                f"### {unit.unit_id}. {unit.subheading}",
                "",
                f"- Primary display item. {unit.figure_id}.",
                f"- Paragraph planning rows. {'; '.join(unit.paragraph_ids)}.",
                f"- Claim IDs. {'; '.join(unit.claim_ids)}.",
                f"- Evidence artifact IDs. {'; '.join(art_ids)}.",
                f"- Supplementary support. {'; '.join(supplementary_ids) if supplementary_ids else 'none'}.",
                f"- Panel structure. {figure['panel_structure']}",
                f"- Paragraph purpose. {' | '.join(paragraph_purposes)}",
                f"- Results-unit purpose. {unit.purpose}",
                f"- Evidence move. {unit.evidence_move}",
                f"- Drafting task for Stage 9.11. {unit.drafting_task}",
                f"- Allowed conclusion. {unit.allowed_conclusion}",
                f"- Strength cap. {' | '.join(strength_caps)}",
                f"- Prohibited overclaim. {unit.prohibited_overclaim}",
                f"- Transition pressure. {unit.next_pressure}",
                "",
            ]
        )
    return f"""# Stage 9.10 Results subsection architecture

Generated UTC. {generated_utc}

Architecture version. {architecture_version}

Stage. 9.10 Results subsection architecture.

Scope. This file defines the Results drafting architecture for a future Nature
Methods Article. It is not Results prose, not a reference library, not figure
legend text, not Methods text, and not a submission package.

## Results architecture rule

The Results section must follow the evidence-bearing display sequence in
`FIG-001` through `FIG-006` order. Each subsection must name the specific figure,
claim IDs, evidence artifact IDs, supplementary support when needed, allowed
conclusion, prohibited overclaim, and transition pressure. A future Stage 9.11
Results draft may use these units as paragraph scaffolds, but this blueprint does
not draft reader-facing Results prose.

## Results unit map

{_markdown_table(overview_rows, ["unit_id", "subheading", "paragraph_ids", "figure_id", "claim_ids", "art_ids", "supplementary_ids"])}

## Global drafting constraints for Stage 9.11

- Draft in the locked main-figure order from `FIG-001` through `FIG-006`.
- Keep every subsection evidence-bearing. No subsection may rely on narrative
  framing without at least one main display item and one locked evidence artifact.
- Use topical subheadings, consistent with the Nature Methods Results contract.
- Keep inconclusive cases visible for bounded-coupling and margin-sensitive
  contexts.
- Use reserve-like language unless the measurement directly assays biological
  reserve capacity.
- Do not convert effective routed-output model terms into direct molecular
  wiring.
- Do not claim that RhoDyn generated the RhoA/microglia manuscript results.
- Do not start citation resolution, reference bibliography, full Results prose,
  figure legends, Methods, Discussion, or submission-package assembly in this
  stage.

## Unit details

{chr(10).join(detail_blocks).rstrip()}
"""


def _no_downstream_started() -> tuple[bool, list[str]]:
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden, forbidden


def _validate(
    claims: dict[str, dict[str, str]],
    paragraphs: dict[str, dict[str, str]],
    figures: dict[str, dict[str, str]],
    supplementary_rows: list[dict[str, str]],
    evidence: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    gate_99_pass = False
    if GATE_99.exists():
        try:
            gate_99_pass = _read_json(GATE_99).get("pass") is True
        except json.JSONDecodeError:
            gate_99_pass = False
    figure_order = [unit.figure_id for unit in RESULTS_UNITS]
    all_figures_present = all(fig_id in figures for fig_id in figure_order)
    all_claims_present = all(claim_id in claims for unit in RESULTS_UNITS for claim_id in unit.claim_ids)
    all_paragraphs_present = all(para_id in paragraphs for unit in RESULTS_UNITS for para_id in unit.paragraph_ids)
    all_artifacts_present = all(art_id in evidence for unit in RESULTS_UNITS for art_id in _unit_art_ids(unit, figures))
    all_units_have_artifacts = all(bool(_unit_art_ids(unit, figures)) for unit in RESULTS_UNITS if unit.figure_id in figures)
    all_units_have_supp_or_declared_none = all(_supplementary_by_unit(unit, supplementary_rows) or unit.figure_id == "FIG-006" for unit in RESULTS_UNITS)
    conclusion_text = "\n".join(unit.allowed_conclusion for unit in RESULTS_UNITS)
    forbidden_absent = not any(phrase.lower() in conclusion_text.lower() for phrase in FORBIDDEN_CONCLUSION_PHRASES)
    strength_caps_available = all(_unit_strength_caps(unit, claims) for unit in RESULTS_UNITS)
    no_narrative_only = all(
        unit.figure_id
        and unit.claim_ids
        and unit.paragraph_ids
        and unit.purpose
        and unit.evidence_move
        and unit.allowed_conclusion
        and _unit_art_ids(unit, figures)
        for unit in RESULTS_UNITS
        if unit.figure_id in figures
    )
    no_downstream, downstream_paths = _no_downstream_started()
    contracts_ok = SECTION_CONTRACTS.exists() and "SEC-004. Results" in SECTION_CONTRACTS.read_text(encoding="utf-8")
    figure_spine_ok = MAIN_FIGURE_SPINE.exists() and all(fig_id in MAIN_FIGURE_SPINE.read_text(encoding="utf-8") for fig_id in RESULTS_FIGURE_ORDER)
    return [
        {
            "name": "stage_9_9_gate_passed",
            "passed": gate_99_pass,
            "detail": "Stage 9.9 title and abstract strategy exists and passes" if gate_99_pass else "Stage 9.9 gate is missing or not passing",
        },
        {
            "name": "results_contract_available",
            "passed": contracts_ok,
            "detail": "Results architecture resolves to the Stage 9.8 Results section contract",
        },
        {
            "name": "figure_spine_available",
            "passed": figure_spine_ok,
            "detail": "Main figure spine contains FIG-001 through FIG-006",
        },
        {
            "name": "results_units_follow_locked_figure_order",
            "passed": tuple(figure_order) == RESULTS_FIGURE_ORDER and all_figures_present,
            "detail": "Results units are locked to FIG-001 through FIG-006",
        },
        {
            "name": "each_subsection_maps_to_figure_and_artifact_ids",
            "passed": all_units_have_artifacts and all_artifacts_present,
            "detail": "Every Results unit maps to locked ART identifiers in the evidence manifest",
        },
        {
            "name": "each_subsection_maps_to_claim_and_paragraph_ids",
            "passed": all_claims_present and all_paragraphs_present,
            "detail": "Every Results unit maps to frozen CLM and PARA identifiers",
        },
        {
            "name": "supplementary_support_resolved",
            "passed": all_units_have_supp_or_declared_none,
            "detail": "Essential supplementary callouts resolve for evidence-bearing Results units",
        },
        {
            "name": "allowed_conclusion_respects_strength_cap",
            "passed": strength_caps_available and forbidden_absent,
            "detail": "Allowed conclusions have claim-level strength caps and avoid overclaim phrases",
        },
        {
            "name": "no_subsection_is_narrative_only",
            "passed": no_narrative_only,
            "detail": "Every Results unit includes purpose, evidence move, display item, artifacts, and claim mapping",
        },
        {
            "name": "no_downstream_stage9_surfaces_started",
            "passed": no_downstream,
            "detail": "No Results draft, Introduction, Discussion, Methods, references, legends, or submission package detected"
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
        if substage.get("id") == "9.10":
            substage["status"] = "complete_results_architecture_registered"
    registry["last_completed_substage"] = "9.10"
    registry["next_substage"] = "9.11"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], architecture_version: str, checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.10",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.10.json",
        "validation_outcome": "Results subsection architecture registered as six figure-locked drafting units",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.9.json",
            "manuscript/nature_methods/sections/section_contracts.md",
            "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
            "manuscript/nature_methods/ledgers/paragraph_claim_ledger.csv",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
            "manuscript/nature_methods/ledgers/supplementary_callout_ledger.csv",
            "manuscript/nature_methods/figures/main_figure_spine.md",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/sections/results_blueprint.md",
            "manuscript/nature_methods/gate_verdicts/9.10.json",
        ],
        "remaining_blockers": [
            "Stage 9.11 Results drafting has not started",
            "Citation resolution has not started",
            "Introduction, Discussion, Methods, and figure legends have not started",
            "Submission-package assembly has not started",
        ],
        "results_architecture_version": architecture_version,
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.10"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(architecture_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.10"
    memory["results_architecture_started"] = True
    memory["results_architecture_version"] = architecture_version
    memory["status"] = "stage9_10_results_architecture_registered"
    memory["current_gate"] = "Stage 9.10 registered Results subsection architecture without drafting Results prose"
    memory["next_substage"] = "9.11"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.10 Results subsection architecture registered; Results drafting not started"
    memory["stage9_10_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/sections/results_blueprint.md",
        "manuscript/nature_methods/gate_verdicts/9.10.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.10 are complete through Results subsection architecture.",
        "Stage 9.11 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No Results draft, Introduction, Discussion, Methods, references, figure legends, or submission package contents are created in this Results architecture pass.",
        "The Results blueprint maps every subsection to figure IDs, ART IDs, CLM IDs, paragraph rows, and strength-capped allowed conclusions.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, and Results "
        "subsection architecture only. Do not start Results drafting, citation resolution, Introduction, Discussion, Methods, "
        "figure legends, review response, or submission packaging without explicit substage authorization."
    )
    _upsert_completed_substage(memory, architecture_version, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(architecture_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.10 Results subsection architecture registered; Results drafting not started"
    current["stage9_active_gate"] = "Stage 9.10 Results subsection architecture registered; Results drafting not started"
    current["after_stage9_10_results_architecture"] = (
        "Stage 9.10 registered six Results drafting units mapped to FIG, ART, CLM, PARA, and supplementary support identifiers. "
        "It did not start Results prose, citation resolution, full manuscript drafting, or submission-package assembly."
    )
    current["current_gate"] = "Results architecture registered without Results prose"
    current["next_stage"] = "Stage 9.11 Results drafting pass"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_10_results_architecture_registered"
        stage["current_gate"] = "Stage 9.10 registered Results subsection architecture without drafting Results prose"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, and Results "
            "subsection architecture only. Do not start Results drafting, citation resolution, Introduction, Discussion, Methods, "
            "figure legends, review response, or submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/sections/results_blueprint.md",
            "manuscript/nature_methods/gate_verdicts/9.10.json",
            "scripts/run_stage9_10_results_architecture.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        results_gate = "Stage 9.10 Results architecture maps every subsection to figure, artifact, claim, paragraph, and strength-cap evidence."
        if results_gate not in gate:
            gate.append(results_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.10":
                subphase["status"] = "complete_results_architecture_registered"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.10.json"
                subphase["results_architecture_version"] = architecture_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "and registers the title, subtitle, and abstract strategy in Stage 9.9. It does not begin Results architecture, citation resolution, full manuscript drafting, editorial polishing, or package assembly.",
            "registers the title, subtitle, and abstract strategy in Stage 9.9, and registers Results subsection architecture in Stage 9.10. It does not begin Results prose drafting, citation resolution, Introduction, Discussion, Methods, editorial polishing, or package assembly.",
        )
        body = _replace_once(
            body,
            "Stage 9.9 registers title options, abstract strategy, and an unreferenced abstract draft in `sections/title_options.md`, `sections/abstract_strategy.md`, `sections/abstract.md`, and `gate_verdicts/9.9.json`. The current state intentionally does not create",
            "Stage 9.9 registers title options, abstract strategy, and an unreferenced abstract draft in `sections/title_options.md`, `sections/abstract_strategy.md`, `sections/abstract.md`, and `gate_verdicts/9.9.json`. Stage 9.10 registers Results subsection architecture in `sections/results_blueprint.md` and `gate_verdicts/9.10.json`. The current state intentionally does not create",
        )
        body = _replace_once(
            body,
            "| 9.10 | Results subsection architecture | not_started | Break Results into evidence-locked drafting units. |",
            "| 9.10 | Results subsection architecture | complete_results_architecture_registered | Break Results into evidence-locked drafting units. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "and Stage 9.9 has registered title, subtitle, and abstract\nstrategy. Results architecture, citation resolution, full manuscript drafting,\nand package assembly remain not started.",
            "Stage 9.9 has registered title, subtitle, and abstract strategy, and Stage\n9.10 has registered Results subsection architecture. Results prose drafting,\ncitation resolution, Introduction, Discussion, Methods, and package assembly\nremain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.9 title, subtitle, and abstract strategy registered, Results architecture not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, and front-matter strategy only. Do not start Results architecture, citation resolution, full manuscript drafting, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.10 Results subsection architecture registered, Results drafting not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, and Results architecture only. Do not start Results drafting, citation resolution, Introduction, Discussion, Methods, figure legends, review response, or submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.9 title, subtitle, and abstract strategy has been completed. Stage 9.10 Results subsection architecture remains the next unstarted manuscript step. Results architecture, citation resolution, full manuscript drafting, and package assembly remain not started.",
            "Stage 9.9 title, subtitle, and abstract strategy has been completed. Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass remains the next unstarted manuscript step. Results prose, citation resolution, Introduction, Discussion, Methods, and package assembly remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    architecture_version = f"results-architecture@{generated_utc[:10]}@{commit}"
    claims = _read_csv(CLAIM_LEDGER, "claim_id")
    paragraphs = _read_csv(PARAGRAPH_LEDGER, "para_id")
    figures = _read_csv(FIGURE_LEDGER, "fig_id")
    supplementary_rows = _read_csv_rows(SUPPLEMENTARY_LEDGER)
    evidence = _read_csv(EVIDENCE_MANIFEST, "art_id")
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    _write_text(
        STAGING_DIR / OUTPUTS["results_blueprint"].relative_to(WORKSPACE),
        _build_results_blueprint(generated_utc, architecture_version, claims, paragraphs, figures, supplementary_rows),
    )
    checks = _validate(claims, paragraphs, figures, supplementary_rows, evidence)
    passed = all(check["passed"] for check in checks)
    gate = {
        "substage": "9.10",
        "timestamp": generated_utc,
        "results_architecture_version": architecture_version,
        "pass": passed,
        "checks": checks,
        "results_unit_count": len(RESULTS_UNITS),
        "figure_ids": list(RESULTS_FIGURE_ORDER),
        "claim_ids": sorted({claim_id for unit in RESULTS_UNITS for claim_id in unit.claim_ids}),
        "paragraph_ids": sorted({para_id for unit in RESULTS_UNITS for para_id in unit.paragraph_ids}),
        "art_id_count": sum(len(_unit_art_ids(unit, figures)) for unit in RESULTS_UNITS),
        "next_substage": "9.11",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Results architecture only. No Results prose, citation resolution, figure legends, Methods, Discussion, or submission-package assembly.",
    }
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)
    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(architecture_version, generated_utc, checks)
        _update_roadmap_memory(architecture_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)
    return {
        "status": "pass" if passed else "fail",
        "substage": "9.10",
        "results_architecture_version": architecture_version,
        "results_unit_count": len(RESULTS_UNITS),
        "figure_ids": list(RESULTS_FIGURE_ORDER),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
        "next_allowed_action": "Proceed to Stage 9.11 Results drafting pass after validation and explicit authorization.",
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
