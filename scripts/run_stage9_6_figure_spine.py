"""Run Stage 9.6 figure-first manuscript-spine registration.

Stage 9.6 builds the display-item contract before manuscript prose. It maps
main figures to frozen claims and locked Stage 7 artifacts, but it does not
render figures, run PanelForge, resolve citations, draft sections, or assemble
a submission package.
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
FIGURE_DIR = WORKSPACE / "figures"
LEDGER_DIR = WORKSPACE / "ledgers"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.6"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.6"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
CLAIM_CSV_PATH = LEDGER_DIR / "claim_hierarchy.csv"
ARTIFACT_CSV_PATH = LEDGER_DIR / "stage9_evidence_manifest.csv"
PARAGRAPH_CSV_PATH = LEDGER_DIR / "paragraph_claim_ledger.csv"
GATE_9_5 = GATE_DIR / "9.5.json"

OUTPUTS = {
    "main_spine": FIGURE_DIR / "main_figure_spine.md",
    "figure_csv": LEDGER_DIR / "figure_to_claim_to_artifact.csv",
    "display_plan": FIGURE_DIR / "display_item_plan.md",
    "gate": GATE_DIR / "9.6.json",
}

FIELDNAMES = [
    "fig_id",
    "claim_id",
    "art_ids",
    "stat_ids",
    "panel_structure",
    "placement",
    "recipe",
    "render_path",
    "engine_version",
    "engine_commit",
    "drift_ok",
    "rejected_alternative",
]

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


@dataclass(frozen=True)
class FigureRow:
    fig_id: str
    claim_ids: tuple[str, ...]
    art_ids: tuple[str, ...]
    panel_structure: str
    recipe: str
    render_path: str
    rejected_alternative: str


FIGURE_ROWS = [
    FigureRow(
        fig_id="FIG-001",
        claim_ids=("CLM-0001", "CLM-0005"),
        art_ids=("ART-0025", "ART-0026", "ART-0016", "ART-0017"),
        panel_structure="A method object and input contract; B residence-window metrics; C failure modes and interpretation boundaries; D executable truth-case ladder.",
        recipe="panelforge_pending:method_workflow_and_truth_cases",
        render_path="manuscript/nature_methods/figures/rendered/FIG-001_pending_stage9.6b.svg",
        rejected_alternative="Do not use a text-only workflow schematic because the method object needs explicit input, output, and limitation panels.",
    ),
    FigureRow(
        fig_id="FIG-002",
        claim_ids=("CLM-0001", "CLM-0004"),
        art_ids=("ART-0027", "ART-0028", "ART-0029", "ART-0030", "ART-0031"),
        panel_structure="A synthetic regime grid; B residence-versus-amplitude benchmark; C reduced-alternative comparison; D negative and ambiguous failure behavior.",
        recipe="panelforge_pending:synthetic_benchmark_against_simpler_summaries",
        render_path="manuscript/nature_methods/figures/rendered/FIG-002_pending_stage9.6b.svg",
        rejected_alternative="Do not collapse the benchmark to a single score because ambiguity and failure behavior must remain visible.",
    ),
    FigureRow(
        fig_id="FIG-003",
        claim_ids=("CLM-0001",),
        art_ids=("ART-0032", "ART-0033", "ART-0034", "ART-0035"),
        panel_structure="A public-data adapter map; B DRG calcium residence-amplitude separation; C ERK GPCR residence-amplitude separation; D window-sensitivity and uncertainty summary.",
        recipe="panelforge_pending:public_live_cell_signaling_demonstrations",
        render_path="manuscript/nature_methods/figures/rendered/FIG-003_pending_stage9.6b.svg",
        rejected_alternative="Do not present only the RhoA reference use case because the methods claim requires independent public live-cell systems.",
    ),
    FigureRow(
        fig_id="FIG-004",
        claim_ids=("CLM-0002", "CLM-0003", "CLM-0004"),
        art_ids=("ART-0036", "ART-0037", "ART-0038", "ART-0039", "ART-0040", "ART-0049", "ART-0050", "ART-0051"),
        panel_structure="A endpoint schema contract; B bounded-coupling decisions under declared margins; C reserve-like endpoint coordinate; D routed-output reduced-architecture comparison; E measurement-scoped limitations.",
        recipe="panelforge_pending:endpoint_bounded_coupling_reserve_routing",
        render_path="manuscript/nature_methods/figures/rendered/FIG-004_pending_stage9.6b.svg",
        rejected_alternative="Do not split bounded coupling, reserve-like behavior, and routed-output comparison into isolated main figures because their shared endpoint contract is the method point.",
    ),
    FigureRow(
        fig_id="FIG-005",
        claim_ids=("CLM-0002",),
        art_ids=("ART-0041", "ART-0042", "ART-0043", "ART-0044", "ART-0048"),
        panel_structure="A held-out analysis plan; B bounded-coupling pass contexts; C inconclusive margin-boundary contexts; D margin sensitivity; E controlled-access boundary.",
        recipe="panelforge_pending:heldout_validation_and_boundary_cases",
        render_path="manuscript/nature_methods/figures/rendered/FIG-005_pending_stage9.6b.svg",
        rejected_alternative="Do not bury held-out inconclusive cases in supplement because they define the method boundary for bounded-coupling decisions.",
    ),
    FigureRow(
        fig_id="FIG-006",
        claim_ids=("CLM-0005",),
        art_ids=("ART-0045", "ART-0046", "ART-0047", "ART-0052", "ART-0053", "ART-0010", "ART-0021", "ART-0022", "ART-0023", "ART-0024"),
        panel_structure="A Python, CLI, backend, and workbench parity; B export bundle anatomy; C source-distribution clean-room reproduction; D archive and checksum provenance; E adoption and user-path rehearsal.",
        recipe="panelforge_pending:software_reproducibility_and_workbench",
        render_path="manuscript/nature_methods/figures/rendered/FIG-006_pending_stage9.6b.svg",
        rejected_alternative="Do not treat software maturity as availability text only because the methods claim requires visible reproducibility and adoption evidence.",
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


def _figure_dict(row: FigureRow) -> dict[str, str]:
    return {
        "fig_id": row.fig_id,
        "claim_id": ";".join(row.claim_ids),
        "art_ids": ";".join(row.art_ids),
        "stat_ids": "pending_stage9.22",
        "panel_structure": row.panel_structure,
        "placement": "main",
        "recipe": row.recipe,
        "render_path": row.render_path,
        "engine_version": "panelforge-figures@v3.14.1",
        "engine_commit": "pending_stage9.6b",
        "drift_ok": "pending",
        "rejected_alternative": row.rejected_alternative,
    }


def _write_figure_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in FIGURE_ROWS:
            writer.writerow(_figure_dict(row))


def _markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("|", "\\|") for column in columns) + " |")
    return "\n".join(lines)


def _build_main_spine(generated_utc: str, spine_version: str) -> str:
    rows = [
        {
            "fig_id": row.fig_id,
            "main_role": {
                "FIG-001": "Define method object and truth-case boundary",
                "FIG-002": "Benchmark against simpler summaries",
                "FIG-003": "Demonstrate independent public live-cell breadth",
                "FIG-004": "Demonstrate endpoint, bounded-coupling, reserve-like, and routed-output behavior",
                "FIG-005": "Expose held-out validation and boundary cases",
                "FIG-006": "Show software reproducibility and adoption architecture",
            }[row.fig_id],
            "claim_ids": ";".join(row.claim_ids),
            "art_ids": ";".join(row.art_ids),
            "panel_structure": row.panel_structure,
        }
        for row in FIGURE_ROWS
    ]
    return f"""# Stage 9.6 main figure spine

Generated UTC. {generated_utc}

Figure-spine version. {spine_version}

Stage. 9.6 figure-first manuscript spine.

Scope. This file plans the main display sequence for a future Nature Methods
Article. It is not a rendered figure set, not a figure legend draft, not
Results prose, and not a submission package.

## Main display sequence

{_markdown_table(rows, ["fig_id", "main_role", "claim_ids", "art_ids", "panel_structure"])}

## Biological and method boundary

The spine makes the method object, benchmark evidence, independent public
trajectory demonstrations, endpoint/reserve/routing demonstrations, held-out
validation boundaries, and software reproducibility visible in main display
items. This prevents the central evidence from being moved into supplementary
material before the paper has a figure-first argument.

## Rendering boundary

All render paths and recipes remain pending until Stage 9.6b runs the pinned
PanelForge route. No panel image, SVG, PDF, or figure legend is created in this
stage.
"""


def _build_display_plan(generated_utc: str, spine_version: str) -> str:
    rows = [
        {
            "constraint": "Nature Methods Article display budget",
            "decision": "Use six main display items, which is the sourced upper bound.",
            "stage": "Stage 9.6",
        },
        {
            "constraint": "Central evidence should not be buried",
            "decision": "All five frozen central claims appear in at least one main figure.",
            "stage": "Stage 9.6",
        },
        {
            "constraint": "Rendering must be deterministic",
            "decision": "PanelForge rendering is deferred to Stage 9.6b with pinned version v3.14.1.",
            "stage": "Stage 9.6b",
        },
        {
            "constraint": "Supplementary display material",
            "decision": "Supplementary display planning is deferred to Stage 9.7 after the main spine is locked.",
            "stage": "Stage 9.7",
        },
    ]
    return f"""# Stage 9.6 display item plan

Generated UTC. {generated_utc}

Figure-spine version. {spine_version}

## Display budget decision

{_markdown_table(rows, ["constraint", "decision", "stage"])}

## Main versus supplementary placement

The current spine uses `FIG-001` through `FIG-006` as main display items. No
supplementary figure is created in Stage 9.6. Stage 9.7 may add supplementary
items only after checking that main claims remain visible in the main paper.

## Stage 9.6b dependency

The display contract intentionally records future recipes and render paths, but
does not create rendered files. Panel images, graphical recipes, drift checks,
and rejected visual alternatives belong to the next rendering substage.
"""


def _no_downstream_started() -> tuple[bool, list[str]]:
    rendered = [
        path.relative_to(ROOT).as_posix()
        for path in (WORKSPACE / "figures" / "rendered").rglob("*")
        if path.is_file() and path.suffix.lower() in {".png", ".pdf", ".svg"}
    ]
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden and not rendered, forbidden + rendered


def _validate(claims: dict[str, dict[str, str]], artifacts: dict[str, dict[str, str]], paragraphs: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    gate_9_5_pass = False
    if GATE_9_5.exists():
        try:
            gate_9_5_pass = _read_json(GATE_9_5).get("pass") is True
        except json.JSONDecodeError:
            gate_9_5_pass = False
    claim_ids = set(claims)
    artifact_ids = set(artifacts)
    paragraph_claims = {row["claim_id"] for row in paragraphs.values()}
    figures = [_figure_dict(row) for row in FIGURE_ROWS]
    fig_ids = [row["fig_id"] for row in figures]
    figures_resolve_claims = all(set(row["claim_id"].split(";")).issubset(claim_ids) for row in figures)
    figures_resolve_artifacts = all(set(row["art_ids"].split(";")).issubset(artifact_ids) for row in figures)
    all_claims_in_main = claim_ids.issubset({claim for row in figures for claim in row["claim_id"].split(";")})
    paragraph_claims_in_figures = paragraph_claims.issubset({claim for row in figures for claim in row["claim_id"].split(";")})
    figure_count_ok = len(figures) <= 6 and all(row["placement"] == "main" for row in figures)
    ledger_validates = (
        len(figures) == 6
        and fig_ids == [f"FIG-00{idx}" for idx in range(1, 7)]
        and len(fig_ids) == len(set(fig_ids))
        and all(row["engine_version"] == "panelforge-figures@v3.14.1" for row in figures)
        and all(row["drift_ok"] == "pending" for row in figures)
    )
    no_downstream, downstream_paths = _no_downstream_started()
    return [
        {
            "name": "stage_9_5_gate_passed",
            "passed": gate_9_5_pass,
            "detail": "Stage 9.5 paragraph claim ledger exists and passes" if gate_9_5_pass else "Stage 9.5 gate is missing or not passing",
        },
        {
            "name": "figure_ledger_validates",
            "passed": ledger_validates,
            "detail": "Six main FIG rows are unique, ordered, and pinned to pending PanelForge v3.14.1 rendering",
        },
        {
            "name": "every_figure_resolves_to_claims_and_artifacts",
            "passed": figures_resolve_claims and figures_resolve_artifacts,
            "detail": "All figure rows resolve to frozen CLM IDs and locked ART IDs",
        },
        {
            "name": "figure_count_respects_sourced_budget",
            "passed": figure_count_ok,
            "detail": "Six main display items fit the sourced Nature Methods Article budget",
        },
        {
            "name": "central_evidence_is_not_buried_in_supplement",
            "passed": all_claims_in_main and paragraph_claims_in_figures,
            "detail": "All frozen claims and paragraph-ledger claims appear in the main figure spine",
        },
        {
            "name": "rendering_is_deferred_to_stage_9_6b",
            "passed": all(row["render_path"].endswith("_pending_stage9.6b.svg") and row["engine_commit"] == "pending_stage9.6b" for row in figures),
            "detail": "Figure recipes and render paths are planned but no rendered files are created",
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
        if substage.get("id") == "9.6":
            substage["status"] = "completed"
    registry["last_completed_substage"] = "9.6"
    _write_json(REGISTRY_PATH, registry)


def _update_memory(spine_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.6"
    memory["figure_spine_started"] = True
    memory["figure_spine_version"] = spine_version
    memory["status"] = "stage9_6_figure_spine_registered"
    memory["next_substage"] = "9.6b"
    memory["next_substage_authorized"] = False
    memory["stage9_6_checks"] = checks
    memory.setdefault("completed_substages", [])
    if not any(item.get("substage") == "9.6" for item in memory["completed_substages"]):
        memory["completed_substages"].append(
            {
                "substage": "9.6",
                "status": "pass",
                "pass": True,
                "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.6.json",
                "validation_outcome": "Main figure spine registered with CLM and ART joins before rendering or drafting",
                "evidence_dependencies": [
                    "manuscript/nature_methods/gate_verdicts/9.5.json",
                    "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
                    "manuscript/nature_methods/ledgers/paragraph_claim_ledger.csv",
                    "manuscript/nature_methods/ledgers/stage9_evidence_manifest.csv",
                ],
                "files_created_or_modified": [
                    "manuscript/nature_methods/figures/main_figure_spine.md",
                    "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
                    "manuscript/nature_methods/figures/display_item_plan.md",
                    "manuscript/nature_methods/gate_verdicts/9.6.json",
                ],
                "remaining_blockers": [
                    "Stage 9.6b PanelForge rendering has not started",
                    "Stage 9.7 supplementary display planning has not started",
                    "Citation resolution, manuscript drafting, and reference library construction remain not started",
                ],
            }
        )
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(spine_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.6 figure-first manuscript spine registered; manuscript production not started"
    current["stage9_active_gate"] = "Stage 9.6 figure-first manuscript spine registered; manuscript production not started"
    current["after_stage9_6_figure_spine"] = (
        "Stage 9.6 registered six main display items for the Nature Methods Article spine, each tied "
        "to frozen CLM identifiers and locked ART evidence. Stage 9.6b PanelForge rendering, "
        "supplementary display planning, citation resolution, manuscript drafting, and submission-package "
        "assembly remain not started."
    )
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_6_figure_spine_registered"
        stage["current_gate"] = "Stage 9.6 figure-first manuscript spine registered; manuscript production not started"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative "
            "methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level "
            "claim planning, and main figure-spine planning only. Do not start PanelForge rendering, "
            "supplementary display planning, citation resolution, drafting, review response, or "
            "submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/figures/main_figure_spine.md",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
            "manuscript/nature_methods/figures/display_item_plan.md",
            "manuscript/nature_methods/gate_verdicts/9.6.json",
            "scripts/run_stage9_6_figure_spine.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        figure_gate = "Stage 9.6 main figures resolve to frozen CLM IDs and locked ART IDs before rendering."
        if figure_gate not in gate:
            gate.append(figure_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.6":
                subphase["status"] = "complete_figure_spine_registered"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.6.json"
                subphase["figure_spine_version"] = spine_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = body.replace(
            "and registers the paragraph-level claim ledger in Stage 9.5. It does not begin figure-spine construction, citation resolution, manuscript drafting, editorial polishing, PanelForge rendering, or package assembly.",
            "registers the paragraph-level claim ledger in Stage 9.5, and registers the figure-first main display spine in Stage 9.6. It does not begin PanelForge rendering, supplementary display planning, citation resolution, manuscript drafting, editorial polishing, or package assembly.",
        )
        body = body.replace(
            "Stage 9.5 registers paragraph-to-claim planning in `ledgers/paragraph_claim_ledger.csv`, `ledgers/claim_strength_rules.md`, and `gate_verdicts/9.5.json`. The current state intentionally does not create",
            "Stage 9.5 registers paragraph-to-claim planning in `ledgers/paragraph_claim_ledger.csv`, `ledgers/claim_strength_rules.md`, and `gate_verdicts/9.5.json`. Stage 9.6 registers the main display spine in `figures/main_figure_spine.md`, `ledgers/figure_to_claim_to_artifact.csv`, `figures/display_item_plan.md`, and `gate_verdicts/9.6.json`. The current state intentionally does not create",
        )
        body = body.replace(
            "| 9.6 | Figure-first manuscript spine | not_started | Build the manuscript around evidence-bearing display items before prose. |",
            "| 9.6 | Figure-first manuscript spine | complete_figure_spine_registered | Build the manuscript around evidence-bearing display items before prose. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = body.replace(
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.5 paragraph claim ledger registered, manuscript production not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, and paragraph-level claim planning only, with PanelForge reserved as a future Stage 9.6b rendering dependency. Do not start figure-spine construction, citation resolution, figure rendering, drafting, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.6 figure-first manuscript spine registered, manuscript production not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, and main figure-spine planning only, with PanelForge reserved for the next Stage 9.6b rendering step. Do not start PanelForge rendering, supplementary display planning, citation resolution, drafting, review response, or submission packaging without explicit substage authorization. |",
        )
        body = body.replace(
            "Stage 9.2 representative methods-paper corpus has been completed. Stage 9.3 narrative spine has been completed. Stage 9.4 claim freeze has been completed. Stage 9.5 paragraph-level claim ledger has been completed. Stage 9.6 remains the next unstarted manuscript step.",
            "Stage 9.2 representative methods-paper corpus has been completed. Stage 9.3 narrative spine has been completed. Stage 9.4 claim freeze has been completed. Stage 9.5 paragraph-level claim ledger has been completed. Stage 9.6 figure-first manuscript spine has been completed. Stage 9.6b remains the next unstarted manuscript step.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    spine_version = f"figure-spine@{generated_utc[:10]}@{commit}"
    claims = _read_csv(CLAIM_CSV_PATH, "claim_id")
    artifacts = _read_csv(ARTIFACT_CSV_PATH, "art_id")
    paragraphs = _read_csv(PARAGRAPH_CSV_PATH, "para_id")
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    checks = _validate(claims, artifacts, paragraphs)
    passed = all(check["passed"] for check in checks)
    gate = {
        "substage": "9.6",
        "timestamp": generated_utc,
        "figure_spine_version": spine_version,
        "pass": passed,
        "checks": checks,
        "main_display_count": len(FIGURE_ROWS),
        "main_display_budget": 6,
        "claim_count": len(claims),
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Figure-to-claim-to-artifact planning only. No rendered figures, manuscript sections, citation resolution, PanelForge execution, or submission-package assembly.",
    }

    _write_text(STAGING_DIR / OUTPUTS["main_spine"].relative_to(WORKSPACE), _build_main_spine(generated_utc, spine_version))
    _write_figure_csv(STAGING_DIR / OUTPUTS["figure_csv"].relative_to(WORKSPACE))
    _write_text(STAGING_DIR / OUTPUTS["display_plan"].relative_to(WORKSPACE), _build_display_plan(generated_utc, spine_version))
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)

    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(spine_version, generated_utc, checks)
        _update_roadmap_memory(spine_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)

    return {
        "status": "pass" if passed else "fail",
        "substage": "9.6",
        "figure_spine_version": spine_version,
        "main_display_count": len(FIGURE_ROWS),
        "claim_count": len(claims),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
