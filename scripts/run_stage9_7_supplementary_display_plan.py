"""Run Stage 9.7 supplementary display-item planning.

Stage 9.7 plans supplementary figures, tables, and callout locations as
structured support for the already locked main figure spine. It does not draft
the SI, create legends, resolve citations, render supplementary figures, or
start manuscript prose.
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SUPPLEMENTARY_DIR = WORKSPACE / "supplementary"
LEDGER_DIR = WORKSPACE / "ledgers"
GATE_DIR = WORKSPACE / "gate_verdicts"
FIGURE_DIR = WORKSPACE / "figures"
STAGING_DIR = WORKSPACE / "_staging" / "9.7"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.7"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"

GATE_96B = GATE_DIR / "9.6b.json"
FIGURE_LEDGER = LEDGER_DIR / "figure_to_claim_to_artifact.csv"
PARAGRAPH_LEDGER = LEDGER_DIR / "paragraph_claim_ledger.csv"
ARTIFACT_LEDGER = LEDGER_DIR / "stage9_evidence_manifest.csv"
FIGURE_MANIFEST = FIGURE_DIR / "figures.manifest.yaml"

OUTPUTS = {
    "supplementary_plan": SUPPLEMENTARY_DIR / "supplementary_item_plan.md",
    "callout_ledger": LEDGER_DIR / "supplementary_callout_ledger.csv",
    "manifest": FIGURE_MANIFEST,
    "gate": GATE_DIR / "9.7.json",
}

FIELDNAMES = ["supp_id", "fig_id", "tbl_id", "callout_location", "role"]

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
    ROOT / ".venv-panelforge",
    ROOT / "tools" / "panelforge-figures" / ".git",
]


@dataclass(frozen=True)
class SupplementaryItem:
    supp_id: str
    sfig_id: str
    fig_id: str
    tbl_id: str
    role: str
    callout_location: str
    title: str
    support_function: str
    source_artifacts: tuple[str, ...]
    planned_panels: str
    interpretation_boundary: str


SUPPLEMENTARY_ITEMS = [
    SupplementaryItem(
        supp_id="SUPP-001",
        sfig_id="SFIG-001",
        fig_id="FIG-001",
        tbl_id="STBL-001",
        role="essential",
        callout_location="PARA-RESULTS-001; PARA-METHODS-001",
        title="Input contracts, method definitions, and executable truth cases",
        support_function="Extends the method-object figure with tidy-input requirements, residence-window definitions, and positive, negative, and ambiguous truth-case examples.",
        source_artifacts=("ART-0016", "ART-0017", "ART-0025", "ART-0026"),
        planned_panels="A tidy trajectory and endpoint schemas; B residence-window metric definitions; C executable truth-case examples; D limitation and failure-mode matrix.",
        interpretation_boundary="Supports method definition and counterexamples only. It does not add biological evidence.",
    ),
    SupplementaryItem(
        supp_id="SUPP-002",
        sfig_id="SFIG-002",
        fig_id="FIG-002",
        tbl_id="STBL-002",
        role="essential",
        callout_location="PARA-RESULTS-001; PARA-METHODS-001",
        title="Synthetic benchmark grid, baseline comparisons, and failure behavior",
        support_function="Keeps full synthetic benchmark tables visible while the main figure shows the compressed benchmark logic.",
        source_artifacts=("ART-0027", "ART-0028", "ART-0029", "ART-0030", "ART-0031"),
        planned_panels="A known-truth regime grid; B residence versus amplitude baseline comparison; C model-comparison table; D negative and ambiguous boundary cases.",
        interpretation_boundary="Synthetic benchmarks validate decision behavior. They are not independent biological demonstrations.",
    ),
    SupplementaryItem(
        supp_id="SUPP-003",
        sfig_id="SFIG-003",
        fig_id="FIG-003",
        tbl_id="STBL-003",
        role="essential",
        callout_location="PARA-RESULTS-002; PARA-METHODS-001",
        title="Public live-cell signaling adapters and residence-amplitude sensitivity",
        support_function="Provides the public-data adapter details and window-sensitivity summaries behind the DRG calcium and ERK GPCR main panels.",
        source_artifacts=("ART-0032", "ART-0033", "ART-0034", "ART-0035"),
        planned_panels="A public-data adapter contract; B DRG calcium residence-amplitude cases; C ERK GPCR residence-amplitude cases; D window and uncertainty sensitivity.",
        interpretation_boundary="Demonstrates two public live-cell trajectory systems without claiming universal residence behavior across all reporters.",
    ),
    SupplementaryItem(
        supp_id="SUPP-004",
        sfig_id="SFIG-004",
        fig_id="FIG-004",
        tbl_id="STBL-004",
        role="essential",
        callout_location="PARA-RESULTS-003; PARA-METHODS-002",
        title="Bounded-coupling decisions under declared margins",
        support_function="Shows the declared margins, interval decisions, and inconclusive bounded-coupling cases that are compressed in the endpoint main figure.",
        source_artifacts=("ART-0036", "ART-0037", "ART-0040"),
        planned_panels="A endpoint pairing contract; B declared margin table; C bounded-coupling forest plot; D inconclusive decision examples.",
        interpretation_boundary="Bounded coupling remains margin- and context-limited. It is not proof of no crosstalk.",
    ),
    SupplementaryItem(
        supp_id="SUPP-005",
        sfig_id="SFIG-005",
        fig_id="FIG-004",
        tbl_id="STBL-005",
        role="essential",
        callout_location="PARA-RESULTS-004; PARA-METHODS-003",
        title="Reserve-like endpoint construction and uncertainty",
        support_function="Separates endpoint-level buffering coordinates from unmeasured biological reserve and exposes the uncertainty summaries.",
        source_artifacts=("ART-0039", "ART-0049", "ART-0050"),
        planned_panels="A measured endpoint components; B reserve-like coordinate construction; C uncertainty summary; D label-scope table.",
        interpretation_boundary="Reserve-like means scoped endpoint preservation. It is not a direct live metabolic reserve assay.",
    ),
    SupplementaryItem(
        supp_id="SUPP-006",
        sfig_id="SFIG-006",
        fig_id="FIG-004",
        tbl_id="STBL-006",
        role="essential",
        callout_location="PARA-RESULTS-005; PARA-METHODS-004",
        title="Routed-output reduced-architecture comparison",
        support_function="Provides the reduced alternatives and model-comparison diagnostics behind the routed-output main display item.",
        source_artifacts=("ART-0038", "ART-0051"),
        planned_panels="A routed architecture matrix; B reduced-alternative comparison; C residual profile; D decision boundary table.",
        interpretation_boundary="Effective model terms constrain the endpoint architecture but do not identify literal molecular edges.",
    ),
    SupplementaryItem(
        supp_id="SUPP-007",
        sfig_id="SFIG-007",
        fig_id="FIG-005",
        tbl_id="STBL-007",
        role="essential",
        callout_location="PARA-RESULTS-003; PARA-DISCUSSION-002",
        title="Held-out validation pass and boundary cases",
        support_function="Keeps pass, inconclusive, margin-sensitivity, and controlled-access cases visible rather than hiding them behind a single validation score.",
        source_artifacts=("ART-0041", "ART-0042", "ART-0043", "ART-0044", "ART-0048"),
        planned_panels="A fixed held-out plan; B pass contexts; C margin-boundary inconclusive contexts; D margin sensitivity; E access boundary.",
        interpretation_boundary="Held-out validation supports scoped transfer of declared decisions, not a universal biological law.",
    ),
    SupplementaryItem(
        supp_id="SUPP-008",
        sfig_id="SFIG-008",
        fig_id="FIG-006",
        tbl_id="STBL-008",
        role="essential",
        callout_location="PARA-RESULTS-006; PARA-METHODS-005",
        title="Software parity, clean-room reproduction, and archive contents",
        support_function="Shows how Python, CLI, backend, exported bundles, source-distribution checks, and archive records preserve the same analysis choices.",
        source_artifacts=("ART-0010", "ART-0021", "ART-0022", "ART-0023", "ART-0024", "ART-0045", "ART-0046", "ART-0047", "ART-0052", "ART-0053"),
        planned_panels="A cross-surface parity matrix; B export-bundle anatomy; C clean-room reproduction summary; D archive manifest and checksums; E usability-path boundary.",
        interpretation_boundary="Supports reproducibility of retained evidence surfaces. It does not imply PyPI publication or private-data reproduction.",
    ),
    SupplementaryItem(
        supp_id="SUPP-009",
        sfig_id="SFIG-009",
        fig_id="FIG-001",
        tbl_id="STBL-009",
        role="supportive",
        callout_location="PARA-DISCUSSION-001; PARA-DISCUSSION-002",
        title="Interpretation boundaries and non-example cases",
        support_function="Collects failure modes, non-claims, and biological-scope limits so the main narrative can stay concise without hiding caveats.",
        source_artifacts=("ART-0017",),
        planned_panels="A non-example matrix; B ambiguous regime examples; C claim-strength caps; D recommended wording boundaries.",
        interpretation_boundary="A limitation display supports interpretation discipline. It is not a new result.",
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


def _ledger_row(item: SupplementaryItem) -> dict[str, str]:
    return {
        "supp_id": item.supp_id,
        "fig_id": item.fig_id,
        "tbl_id": item.tbl_id,
        "callout_location": item.callout_location,
        "role": item.role,
    }


def _markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("|", "\\|") for column in columns) + " |")
    return "\n".join(lines)


def _supplementary_manifest_items() -> list[dict[str, Any]]:
    return [
        {
            "id": item.supp_id,
            "planned_supplementary_figure": item.sfig_id,
            "planned_supplementary_table": item.tbl_id,
            "linked_main_figure": item.fig_id,
            "role": item.role,
            "callout_location": item.callout_location,
            "title": item.title,
            "support_function": item.support_function,
            "source_artifacts": list(item.source_artifacts),
            "render_status": "not_rendered_stage9.7_plan_only",
        }
        for item in SUPPLEMENTARY_ITEMS
    ]


def _update_manifest(source_path: Path, output_path: Path) -> None:
    manifest = _read_json(source_path)
    manifest["supplementary_items"] = _supplementary_manifest_items()
    manifest["supplementary_plan_status"] = "planned_stage9.7_not_rendered"
    _write_json(output_path, manifest)


def _write_callout_ledger(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(_ledger_row(item) for item in SUPPLEMENTARY_ITEMS)


def _build_plan(generated_utc: str, plan_version: str) -> str:
    rows = [
        {
            "supp_id": item.supp_id,
            "display": f"{item.sfig_id} / {item.tbl_id}",
            "linked_main_figure": item.fig_id,
            "role": item.role,
            "callout_location": item.callout_location,
            "support_function": item.support_function,
        }
        for item in SUPPLEMENTARY_ITEMS
    ]
    detail = []
    for item in SUPPLEMENTARY_ITEMS:
        detail.extend(
            [
                f"### {item.supp_id}. {item.title}",
                "",
                f"- Planned display. `{item.sfig_id}` plus `{item.tbl_id}`.",
                f"- Linked main figure. `{item.fig_id}`.",
                f"- Planned callout. `{item.callout_location}`.",
                f"- Source artifacts. `{';'.join(item.source_artifacts)}`.",
                f"- Planned panels. {item.planned_panels}",
                f"- Interpretation boundary. {item.interpretation_boundary}",
                "",
            ]
        )
    return f"""# Stage 9.7 supplementary display item plan

Generated UTC. {generated_utc}

Supplementary-plan version. {plan_version}

Stage. 9.7 supplementary display item planning.

Scope. This file plans supplementary figures and tables for a future Nature
Methods Article. It is not Supplementary Information prose, not figure legends,
not citation resolution, and not a submission package.

## Planning rule

Supplementary material should make the main method argument reproducible,
inspectable, and appropriately bounded. It should not carry central evidence
that belongs in the six main display items, and it should not become an
unstructured archive of every intermediate table.

It is not a data dump.

## Supplementary item map

{_markdown_table(rows, ["supp_id", "display", "linked_main_figure", "role", "callout_location", "support_function"])}

## Planned item details

{chr(10).join(detail).rstrip()}

## Main-text visibility rule

Every essential supplementary item has a planned Results or Methods callout.
Supportive items are retained only when they clarify interpretation boundaries
or reproducibility without becoming an uncited data store.

## Rendering boundary

No supplementary display item is rendered in Stage 9.7. The PanelForge manifest
records the planned supplementary items as non-rendered metadata so later
legend, table, and supplementary-methods substages can resolve callouts without
changing the main figure spine.
"""


def _no_downstream_started() -> tuple[bool, list[str]]:
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden, forbidden


def _validate(
    figures: dict[str, dict[str, str]],
    paragraphs: dict[str, dict[str, str]],
    artifacts: dict[str, dict[str, str]],
    manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    gate_96b_pass = False
    if GATE_96B.exists():
        try:
            gate_96b_pass = _read_json(GATE_96B).get("pass") is True
        except json.JSONDecodeError:
            gate_96b_pass = False
    fig_ids = set(figures)
    paragraph_ids = set(paragraphs)
    artifact_ids = set(artifacts)
    item_ids = [item.supp_id for item in SUPPLEMENTARY_ITEMS]
    table_ids = [item.tbl_id for item in SUPPLEMENTARY_ITEMS]
    ledger_validates = (
        len(SUPPLEMENTARY_ITEMS) == 9
        and item_ids == [f"SUPP-00{idx}" for idx in range(1, 10)]
        and len(item_ids) == len(set(item_ids))
        and len(table_ids) == len(set(table_ids))
        and all(item.tbl_id.startswith("STBL-") for item in SUPPLEMENTARY_ITEMS)
        and all(item.role in {"essential", "supportive", "archival"} for item in SUPPLEMENTARY_ITEMS)
        and all(item.fig_id in fig_ids for item in SUPPLEMENTARY_ITEMS)
        and all(set(item.source_artifacts).issubset(artifact_ids) for item in SUPPLEMENTARY_ITEMS)
    )
    each_item_has_callout_and_role = all(item.callout_location and item.role for item in SUPPLEMENTARY_ITEMS)
    essential_items_have_main_text_callouts = all(
        item.role != "essential"
        or any(token.strip() in paragraph_ids for token in item.callout_location.split(";"))
        for item in SUPPLEMENTARY_ITEMS
    )
    central_evidence_remains_main = all(row.get("placement") == "main" for row in figures.values()) and {
        "FIG-001",
        "FIG-002",
        "FIG-003",
        "FIG-004",
        "FIG-005",
        "FIG-006",
    }.issubset(fig_ids)
    manifest_items = manifest.get("supplementary_items", [])
    manifest_ok = (
        isinstance(manifest_items, list)
        and len(manifest_items) == len(SUPPLEMENTARY_ITEMS)
        and {item.get("id") for item in manifest_items if isinstance(item, dict)} == set(item_ids)
        and all(item.get("render_status") == "not_rendered_stage9.7_plan_only" for item in manifest_items if isinstance(item, dict))
        and manifest.get("supplementary_plan_status") == "planned_stage9.7_not_rendered"
    )
    no_downstream, downstream_paths = _no_downstream_started()
    return [
        {
            "name": "stage_9_6b_gate_passed",
            "passed": gate_96b_pass,
            "detail": "Stage 9.6b PanelForge rendering exists and passes" if gate_96b_pass else "Stage 9.6b gate is missing or not passing",
        },
        {
            "name": "supplementary_ledger_validates",
            "passed": ledger_validates,
            "detail": "Nine supplementary support items are uniquely identified, role-scoped, and linked to main figures plus locked artifacts",
        },
        {
            "name": "each_item_has_callout_and_role",
            "passed": each_item_has_callout_and_role,
            "detail": "Every supplementary row records a planned callout location and role",
        },
        {
            "name": "essential_items_have_main_text_callouts",
            "passed": essential_items_have_main_text_callouts,
            "detail": "Every essential item points to an existing planned Results, Methods, or Discussion paragraph row",
        },
        {
            "name": "central_evidence_remains_in_main_figures",
            "passed": central_evidence_remains_main,
            "detail": "Supplementary planning does not demote the six locked main display items",
        },
        {
            "name": "manifest_contains_nonrendered_supplementary_plan",
            "passed": manifest_ok,
            "detail": "PanelForge manifest records supplementary planning metadata without rendering supplementary panels",
        },
        {
            "name": "no_downstream_stage9_surfaces_started",
            "passed": no_downstream,
            "detail": "No manuscript sections, reference bibliography, submission package, PanelForge clone, or runtime environment detected"
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
        if substage.get("id") == "9.7":
            substage["status"] = "complete_supplementary_display_plan_registered"
    registry["last_completed_substage"] = "9.7"
    registry["next_substage"] = "9.8"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], plan_version: str, checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.7",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.7.json",
        "validation_outcome": "Supplementary display items registered with callouts, roles, and non-rendered manifest metadata",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.6b.json",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
            "manuscript/nature_methods/ledgers/paragraph_claim_ledger.csv",
            "manuscript/nature_methods/ledgers/stage9_evidence_manifest.csv",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/supplementary/supplementary_item_plan.md",
            "manuscript/nature_methods/ledgers/supplementary_callout_ledger.csv",
            "manuscript/nature_methods/figures/figures.manifest.yaml",
            "manuscript/nature_methods/gate_verdicts/9.7.json",
        ],
        "remaining_blockers": [
            "Stage 9.8 section contract blueprint has not started",
            "Citation resolution has not started",
            "Manuscript drafting has not started",
            "Submission-package assembly has not started",
        ],
        "supplementary_plan_version": plan_version,
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.7"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(plan_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.7"
    memory["supplementary_display_planning_started"] = True
    memory["supplementary_plan_version"] = plan_version
    memory["status"] = "stage9_7_supplementary_display_plan_registered"
    memory["current_gate"] = "Stage 9.7 registered supplementary display items without starting manuscript prose"
    memory["next_substage"] = "9.8"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.7 supplementary display planning registered; manuscript production not started"
    memory["stage9_7_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/supplementary/supplementary_item_plan.md",
        "manuscript/nature_methods/ledgers/supplementary_callout_ledger.csv",
        "manuscript/nature_methods/gate_verdicts/9.7.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.7 are complete through supplementary display planning.",
        "Stage 9.8 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No manuscript draft sections, reference bibliography, or submission package contents are created in this supplementary planning pass.",
        "Essential supplementary material has planned main-text callouts and does not replace the six main display items.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, and supplementary display planning only. Do not start section contracts, citation resolution, "
        "drafting, review response, or submission packaging without explicit substage authorization."
    )
    _upsert_completed_substage(memory, plan_version, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(plan_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.7 supplementary display planning registered; manuscript production not started"
    current["stage9_active_gate"] = "Stage 9.7 supplementary display planning registered; manuscript production not started"
    current["after_stage9_7_supplementary_plan"] = (
        "Stage 9.7 registered supplementary figures and tables as planned support items with callout locations and roles. "
        "It did not draft Supplementary Information, resolve citations, or begin manuscript sections."
    )
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_7_supplementary_display_plan_registered"
        stage["current_gate"] = "Stage 9.7 registered supplementary display items without starting manuscript prose"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, and supplementary display planning only. Do not start section contracts, citation resolution, "
            "drafting, review response, or submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/supplementary/supplementary_item_plan.md",
            "manuscript/nature_methods/ledgers/supplementary_callout_ledger.csv",
            "manuscript/nature_methods/gate_verdicts/9.7.json",
            "scripts/run_stage9_7_supplementary_display_plan.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        figure_gate = "Stage 9.7 supplementary material has planned callouts and roles without demoting central evidence from the main figures."
        if figure_gate not in gate:
            gate.append(figure_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.7":
                subphase["status"] = "complete_supplementary_display_plan_registered"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.7.json"
                subphase["supplementary_plan_version"] = plan_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "and renders deterministic PanelForge main-figure mockups in Stage 9.6b. It does not begin supplementary display planning, citation resolution, manuscript drafting, editorial polishing, or package assembly.",
            "renders deterministic PanelForge main-figure mockups in Stage 9.6b, and registers the supplementary display plan in Stage 9.7. It does not begin section contracts, citation resolution, manuscript drafting, editorial polishing, or package assembly.",
        )
        body = _replace_once(
            body,
            "Stage 9.6b renders the main display mockups from `figures/figures.manifest.yaml`, records the pinned PanelForge commit in `figures/.panelforge_commit`, writes `audits/panelforge_render_report.md`, and records `gate_verdicts/9.6b.json`. The current state intentionally does not create",
            "Stage 9.6b renders the main display mockups from `figures/figures.manifest.yaml`, records the pinned PanelForge commit in `figures/.panelforge_commit`, writes `audits/panelforge_render_report.md`, and records `gate_verdicts/9.6b.json`. Stage 9.7 registers supplementary display support in `supplementary/supplementary_item_plan.md`, `ledgers/supplementary_callout_ledger.csv`, `figures/figures.manifest.yaml`, and `gate_verdicts/9.7.json`. The current state intentionally does not create",
        )
        body = _replace_once(
            body,
            "| 9.7 | Supplementary display item plan | not_started | Plan supplementary material as cited support rather than a data dump. |",
            "| 9.7 | Supplementary display item plan | complete_supplementary_display_plan_registered | Plan supplementary material as cited support rather than a data dump. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "PanelForge figure-engine integration\nis complete as Stage 9.6b, but manuscript production, citation\nresolution, supplementary display planning, and drafting remain not started.",
            "PanelForge figure-engine integration is complete as Stage 9.6b, and\nStage 9.7 has registered supplementary display planning. Manuscript\nproduction, citation resolution, section contracts, and drafting remain not\nstarted.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.6b PanelForge rendering registered, manuscript production not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, and deterministic PanelForge rendering only. Do not start supplementary display planning, citation resolution, drafting, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.7 supplementary display planning registered, manuscript production not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, and supplementary display planning only. Do not start section contracts, citation resolution, drafting, review response, or submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.6 figure-first manuscript spine has been completed. Stage 9.6b PanelForge rendering has been completed. Stage 9.7 supplementary display planning remains the next unstarted manuscript step. manuscript production, citation resolution, supplementary display planning, and drafting remain not started.",
            "Stage 9.6 figure-first manuscript spine has been completed. Stage 9.6b PanelForge rendering has been completed. Stage 9.7 supplementary display planning has been completed. Stage 9.8 section contract blueprint remains the next unstarted manuscript step. Manuscript production, citation resolution, and drafting remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    plan_version = f"supplementary-plan@{generated_utc[:10]}@{commit}"
    figures = _read_csv(FIGURE_LEDGER, "fig_id")
    paragraphs = _read_csv(PARAGRAPH_LEDGER, "para_id")
    artifacts = _read_csv(ARTIFACT_LEDGER, "art_id")
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    _write_text(
        STAGING_DIR / OUTPUTS["supplementary_plan"].relative_to(WORKSPACE),
        _build_plan(generated_utc, plan_version),
    )
    _write_callout_ledger(STAGING_DIR / OUTPUTS["callout_ledger"].relative_to(WORKSPACE))
    _update_manifest(FIGURE_MANIFEST, STAGING_DIR / OUTPUTS["manifest"].relative_to(WORKSPACE))
    manifest = _read_json(STAGING_DIR / OUTPUTS["manifest"].relative_to(WORKSPACE))
    checks = _validate(figures, paragraphs, artifacts, manifest)
    passed = all(check["passed"] for check in checks)
    gate = {
        "substage": "9.7",
        "timestamp": generated_utc,
        "supplementary_plan_version": plan_version,
        "pass": passed,
        "checks": checks,
        "supplementary_item_count": len(SUPPLEMENTARY_ITEMS),
        "essential_item_count": sum(1 for item in SUPPLEMENTARY_ITEMS if item.role == "essential"),
        "supportive_item_count": sum(1 for item in SUPPLEMENTARY_ITEMS if item.role == "supportive"),
        "next_substage": "9.8",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Supplementary display planning only. No SI prose, legends, rendered supplementary figures, citations, manuscript sections, or submission-package assembly.",
    }
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)

    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(plan_version, generated_utc, checks)
        _update_roadmap_memory(plan_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)

    return {
        "status": "pass" if passed else "fail",
        "substage": "9.7",
        "supplementary_plan_version": plan_version,
        "supplementary_item_count": len(SUPPLEMENTARY_ITEMS),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
        "next_allowed_action": "Proceed to Stage 9.8 section contract blueprint after validation.",
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
