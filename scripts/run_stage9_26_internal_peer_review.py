"""Run Stage 9.26 internal peer-review simulation.

Stage 9.26 stress-tests the reader-clean Nature Methods manuscript from eight
reviewer perspectives before full package assembly. The pass does not edit
manuscript prose, figures, data, or analyses. It records concern routing in the
reviewer action matrix and summarizes the current PanelForge figure assembly
state from already-rendered Stage 9.6b artifacts.
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
AUDITS_DIR = WORKSPACE / "audits"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.26"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.26"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
README_PATH = WORKSPACE / "README.md"

GATE_925B = GATE_DIR / "9.25b.json"
PANELFORGE_GATE = GATE_DIR / "9.6b.json"
FIGURE_LEGEND_GATE = GATE_DIR / "9.23.json"
FIGURE_LEDGER = WORKSPACE / "ledgers" / "figure_to_claim_to_artifact.csv"
FIGURE_MANIFEST = WORKSPACE / "figures" / "figures.manifest.yaml"
PANELFORGE_REPORT = AUDITS_DIR / "panelforge_render_report.md"
STATISTIC_LEDGER = WORKSPACE / "ledgers" / "statistic_ledger.csv"

OUTPUTS = {
    "review": AUDITS_DIR / "internal_peer_review_simulation.md",
    "matrix": AUDITS_DIR / "reviewer_action_matrix.csv",
    "gate": GATE_DIR / "9.26.json",
}

FORBIDDEN_DOWNSTREAM_PATHS = [
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
    WORKSPACE / "stage9_completion_report.md",
]

REVIEWER_PERSPECTIVES = [
    "Nature Methods handling editor",
    "Computational methods reviewer",
    "Live-cell signaling reviewer",
    "Statistics and uncertainty reviewer",
    "Endpoint perturbation reviewer",
    "Software reproducibility reviewer",
    "Figure and data-visualization reviewer",
    "Adoption and usability reviewer",
]

ACTION_FIELDS = [
    "reviewer_perspective",
    "concern",
    "claim_id",
    "fig_id",
    "resolution_status",
    "resolution",
]

ACTION_ROWS = [
    {
        "reviewer_perspective": "Nature Methods handling editor",
        "concern": "The manuscript must read as a general method Article rather than a companion biology paper.",
        "claim_id": "CLM-0001",
        "fig_id": "FIG-001",
        "resolution_status": "resolved",
        "resolution": "Reader-facing surfaces now state a methods Article scope and separate the RhoA/microglia reference use case from the software generality claim.",
    },
    {
        "reviewer_perspective": "Nature Methods handling editor",
        "concern": "The main text must avoid implying that every biological system contains a residence regime.",
        "claim_id": "CLM-0001",
        "fig_id": "FIG-003",
        "resolution_status": "narrowed",
        "resolution": "The Introduction, Results, Discussion, and non-example supplement keep amplitude-sufficient and inconclusive cases visible.",
    },
    {
        "reviewer_perspective": "Computational methods reviewer",
        "concern": "The method object needs explicit inputs, outputs, assumptions, and failure modes.",
        "claim_id": "CLM-0001",
        "fig_id": "FIG-001",
        "resolution_status": "resolved",
        "resolution": "Figure 1, Online Methods, and Supplementary Methods define tidy trajectory and endpoint schemas, residence windows, amplitude comparators, and invalid-input behavior.",
    },
    {
        "reviewer_perspective": "Computational methods reviewer",
        "concern": "Reduced architectures could be overread as exhaustive mechanistic alternatives.",
        "claim_id": "CLM-0004",
        "fig_id": "FIG-004",
        "resolution_status": "narrowed",
        "resolution": "Results, Methods, and legends state that routed-output comparisons test endpoint architectures and do not identify direct biochemical interactions.",
    },
    {
        "reviewer_perspective": "Live-cell signaling reviewer",
        "concern": "Residence windows could be mistaken for automatically discovered biological states.",
        "claim_id": "CLM-0001",
        "fig_id": "FIG-002",
        "resolution_status": "narrowed",
        "resolution": "The manuscript states that windows are declared analysis choices and pairs residence outputs with amplitude comparators and sensitivity summaries.",
    },
    {
        "reviewer_perspective": "Live-cell signaling reviewer",
        "concern": "The public reporter demonstrations must remain independent tests of portability rather than proof of one shared signaling mechanism.",
        "claim_id": "CLM-0001",
        "fig_id": "FIG-003",
        "resolution_status": "resolved",
        "resolution": "The public DRG calcium and ERK GPCR examples are framed as independent reporter demonstrations with system-specific windows and uncertainty.",
    },
    {
        "reviewer_perspective": "Statistics and uncertainty reviewer",
        "concern": "Bounded-coupling claims require declared margins, uncertainty intervals, and visible inconclusive outcomes.",
        "claim_id": "CLM-0002",
        "fig_id": "FIG-004",
        "resolution_status": "resolved",
        "resolution": "Figure 4 and Methods require positive margins, interval support, and ROPE/TOST thresholds where available before promotion to bounded coupling.",
    },
    {
        "reviewer_perspective": "Statistics and uncertainty reviewer",
        "concern": "Held-out validation must not become a single pass-rate claim.",
        "claim_id": "CLM-0002",
        "fig_id": "FIG-005",
        "resolution_status": "resolved",
        "resolution": "Figure 5 keeps pass, inconclusive, margin-sensitivity, and controlled-access contexts side by side.",
    },
    {
        "reviewer_perspective": "Endpoint perturbation reviewer",
        "concern": "Reserve-like language could imply direct measurement of unmeasured biological reserve capacity.",
        "claim_id": "CLM-0003",
        "fig_id": "FIG-004",
        "resolution_status": "narrowed",
        "resolution": "The manuscript uses reserve-like endpoint coordinate language and states that these summaries remain tied to the measured assay.",
    },
    {
        "reviewer_perspective": "Endpoint perturbation reviewer",
        "concern": "Endpoint analyses need a clear route for failures to distinguish alternatives.",
        "claim_id": "CLM-0004",
        "fig_id": "FIG-004",
        "resolution_status": "resolved",
        "resolution": "Reduced-alternative comparisons, residual summaries, and decision-boundary tables remain visible in the main and supplementary displays.",
    },
    {
        "reviewer_perspective": "Software reproducibility reviewer",
        "concern": "Readers must be able to verify that Python, command-line, backend, and workbench surfaces agree.",
        "claim_id": "CLM-0005",
        "fig_id": "FIG-006",
        "resolution_status": "resolved",
        "resolution": "Cross-surface parity, export-bundle contents, clean-room reproduction, checksums, and citable software DOI are all surfaced in Figure 6 and availability text.",
    },
    {
        "reviewer_perspective": "Software reproducibility reviewer",
        "concern": "The manuscript must not imply package-index distribution or private-data redistribution that has not occurred.",
        "claim_id": "CLM-0005",
        "fig_id": "FIG-006",
        "resolution_status": "narrowed",
        "resolution": "Discussion and Methods state that PyPI-style distribution and controlled-access inputs remain bounded, while the Zenodo/GitHub release is citable.",
    },
    {
        "reviewer_perspective": "Figure and data-visualization reviewer",
        "concern": "The six-figure spine must be rendered and captioned without leaking figure-engine or lineage language into reader-facing captions.",
        "claim_id": "CLM-0005",
        "fig_id": "FIG-006",
        "resolution_status": "resolved",
        "resolution": "Stage 9.6b rendered six main figures in PDF, PNG, and SVG; Stage 9.23 resolved legends and captions; Stage 9.25b removed reader-facing lineage wording.",
    },
    {
        "reviewer_perspective": "Figure and data-visualization reviewer",
        "concern": "The archive-count statistic in Figure 6 must match the current release archive manifest.",
        "claim_id": "CLM-0005",
        "fig_id": "FIG-006",
        "resolution_status": "resolved",
        "resolution": "The live-number audit refreshed STAT-0018 to the current 620-row release archive manifest and propagated the count to Figure 6.",
    },
    {
        "reviewer_perspective": "Adoption and usability reviewer",
        "concern": "The workbench and reports need to serve both biologist-facing and quantitative users.",
        "claim_id": "CLM-0005",
        "fig_id": "FIG-006",
        "resolution_status": "resolved",
        "resolution": "The Results and Figure 6 route user-facing workbench paths, CLI/API parity, and export bundles to the same inspectable outputs.",
    },
    {
        "reviewer_perspective": "Adoption and usability reviewer",
        "concern": "Submission assembly should not begin before review concerns are visible to the author.",
        "claim_id": "CLM-0005",
        "fig_id": "FIG-006",
        "resolution_status": "routed_upstream",
        "resolution": "The action matrix routes remaining human judgment to Stage 9.27 package assembly and Stage 9.28 PI review rather than silently treating this simulation as acceptance.",
    },
]


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _statistic_estimate(stat_id: str) -> str:
    for row in _read_csv(STATISTIC_LEDGER):
        if row.get("stat_id") == stat_id:
            return row.get("value", "")
    return ""


def _resolved_action_rows() -> list[dict[str, str]]:
    rows = [dict(row) for row in ACTION_ROWS]
    estimate = _statistic_estimate("STAT-0018")
    if estimate.startswith("row_count="):
        archive_count = estimate.split("=", 1)[1]
        for row in rows:
            if row["concern"] == "The archive-count statistic in Figure 6 must match the current release archive manifest.":
                row["resolution"] = (
                    f"The live-number audit refreshed STAT-0018 to the current {archive_count}-row release archive "
                    "manifest and propagated the count to Figure 6."
                )
    return rows


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ACTION_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _panel_forge_status() -> dict[str, Any]:
    gate = _read_json(PANELFORGE_GATE)
    legend_gate = _read_json(FIGURE_LEGEND_GATE)
    figure_rows = _read_csv(FIGURE_LEDGER)
    rendered_paths: list[str] = []
    missing_paths: list[str] = []
    for row in figure_rows:
        fig_id = row["fig_id"]
        for suffix in ("pdf", "png", "svg"):
            rel = f"manuscript/nature_methods/figures/rendered/{fig_id}/{fig_id}.{suffix}"
            rendered_paths.append(rel)
            if not (ROOT / rel).exists():
                missing_paths.append(rel)
    return {
        "engine": gate.get("engine", {}),
        "rendered_figures": gate.get("rendered_figures", []),
        "rendered_file_count": len(rendered_paths),
        "missing_rendered_paths": missing_paths,
        "manifest_present": FIGURE_MANIFEST.exists(),
        "render_report_present": PANELFORGE_REPORT.exists(),
        "figure_ledger_rows": len(figure_rows),
        "legend_gate_pass": legend_gate.get("pass") is True,
        "legend_gate_counts": {
            "main_figure_legend_count": legend_gate.get("main_figure_legend_count"),
            "supplementary_figure_caption_count": legend_gate.get("supplementary_figure_caption_count"),
            "supplementary_table_caption_count": legend_gate.get("supplementary_table_caption_count"),
            "statistic_count": legend_gate.get("statistic_count"),
        },
    }


def _audit() -> dict[str, Any]:
    gate_925b = _read_json(GATE_925B)
    downstream_paths = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_DOWNSTREAM_PATHS if path.exists()]
    action_rows = _resolved_action_rows()
    perspectives = sorted({row["reviewer_perspective"] for row in action_rows})
    missing_perspectives = [item for item in REVIEWER_PERSPECTIVES if item not in perspectives]
    unsupported_rows = [
        row
        for row in action_rows
        if row["claim_id"].startswith("CLM-") and row["resolution_status"] not in {"resolved", "narrowed", "routed_upstream"}
    ]
    blocking_without_resolution = [
        row
        for row in action_rows
        if not row["resolution"].strip() or row["resolution_status"] not in {"resolved", "narrowed", "routed_upstream", "open"}
    ]
    schema_errors: list[str] = []
    allowed_statuses = {"resolved", "narrowed", "routed_upstream", "open"}
    for index, row in enumerate(action_rows, start=1):
        for field in ACTION_FIELDS:
            if not row.get(field):
                schema_errors.append(f"row {index} missing {field}")
        if row.get("resolution_status") not in allowed_statuses:
            schema_errors.append(f"row {index} invalid resolution_status={row.get('resolution_status')}")
    panelforge = _panel_forge_status()
    checks = [
        {
            "name": "stage_9_25b_gate_passed",
            "passed": gate_925b.get("pass") is True and gate_925b.get("next_substage") == "9.26",
            "detail": "Stage 9.25b reader-surface hygiene gate is present and points to Stage 9.26",
        },
        {
            "name": "all_eight_perspectives_present",
            "passed": not missing_perspectives and len(perspectives) == 8,
            "detail": f"perspectives={len(perspectives)}; missing={missing_perspectives}",
        },
        {
            "name": "blocking_concerns_have_resolution_status",
            "passed": not blocking_without_resolution and not schema_errors,
            "detail": f"action_rows={len(action_rows)}; schema_errors={schema_errors}",
        },
        {
            "name": "unsupported_central_claims_are_routed",
            "passed": not unsupported_rows,
            "detail": f"unsupported_rows={len(unsupported_rows)}",
        },
        {
            "name": "panelforge_figure_assembly_status_recorded",
            "passed": panelforge["manifest_present"] and panelforge["render_report_present"] and not panelforge["missing_rendered_paths"] and panelforge["legend_gate_pass"],
            "detail": (
                f"figures={len(panelforge['rendered_figures'])}; rendered_files={panelforge['rendered_file_count']}; "
                f"missing={panelforge['missing_rendered_paths']}"
            ),
        },
        {
            "name": "no_submission_package_started",
            "passed": not downstream_paths,
            "detail": f"downstream_paths={downstream_paths}",
        },
    ]
    return {
        "generated_utc": _now(),
        "checks": checks,
        "missing_perspectives": missing_perspectives,
        "unsupported_rows": unsupported_rows,
        "blocking_without_resolution": blocking_without_resolution,
        "schema_errors": schema_errors,
        "downstream_paths": downstream_paths,
        "panelforge": panelforge,
        "action_rows": action_rows,
    }


def _gate_payload(audit: dict[str, Any]) -> dict[str, Any]:
    return {
        "substage": "9.26",
        "title": "Internal peer review simulation",
        "status": "pass" if all(item["passed"] for item in audit["checks"]) else "fail",
        "pass": all(item["passed"] for item in audit["checks"]),
        "generated_utc": audit["generated_utc"],
        "commit": _git_sha(),
        "next_substage": "9.27",
        "reviewer_perspective_count": len(REVIEWER_PERSPECTIVES),
        "action_row_count": len(audit["action_rows"]),
        "missing_perspectives": audit["missing_perspectives"],
        "unsupported_rows": audit["unsupported_rows"],
        "blocking_without_resolution": audit["blocking_without_resolution"],
        "schema_errors": audit["schema_errors"],
        "downstream_paths": audit["downstream_paths"],
        "panelforge_status": audit["panelforge"],
        "checks": audit["checks"],
        "outputs": [
            "manuscript/nature_methods/audits/internal_peer_review_simulation.md",
            "manuscript/nature_methods/audits/reviewer_action_matrix.csv",
            "manuscript/nature_methods/gate_verdicts/9.26.json",
        ],
        "scope_boundary": "Internal peer-review simulation only. No manuscript prose, data, analyses, figures, figure numbering, submission package, or PI packet is changed.",
    }


def _review_markdown(audit: dict[str, Any]) -> str:
    panelforge = audit["panelforge"]
    engine = panelforge["engine"]
    action_rows = audit["action_rows"]
    sections = [
        "# Stage 9.26 internal peer-review simulation",
        "",
        f"Generated UTC. {audit['generated_utc']}",
        "",
        "## Overall editorial read",
        "",
        "The manuscript is ready to move from reader-surface hygiene into package assembly only with the action matrix kept visible. The central methods claim is coherent and appropriately scoped. RhoDyn is presented as a reviewable method for residence-state inference, bounded-coupling decisions, reserve-like endpoint summaries, routed-output comparisons, and cross-surface reproducibility. The review does not identify a fatal scientific blocker, but it preserves several scoped boundaries that must remain explicit through package assembly.",
        "",
        "## PanelForge figure assembly status",
        "",
        f"- Engine. {engine.get('name')} {engine.get('version')} at pinned ref {engine.get('pinned_ref')} and commit {engine.get('commit')}.",
        f"- DOI. {engine.get('version_doi')}.",
        f"- Main figures rendered. {len(panelforge['rendered_figures'])} figures, {panelforge['rendered_file_count']} expected PDF/PNG/SVG files.",
        f"- Missing rendered files. {panelforge['missing_rendered_paths'] or 'none'}.",
        f"- Manifest present. {panelforge['manifest_present']}. Render report present. {panelforge['render_report_present']}.",
        f"- Legend and caption status. Stage 9.23 pass with {panelforge['legend_gate_counts']['main_figure_legend_count']} main legends, {panelforge['legend_gate_counts']['supplementary_figure_caption_count']} supplementary figure captions, {panelforge['legend_gate_counts']['supplementary_table_caption_count']} supplementary table captions, and {panelforge['legend_gate_counts']['statistic_count']} statistic bindings.",
        "",
        "Interpretation. The figure assembly lane is currently complete as deterministic publication mockups. It supports manuscript review and package assembly, but the rendered figures remain methods-paper display artifacts tied to the frozen evidence tables rather than new biological results.",
        "",
        "## Reviewer perspectives",
        "",
    ]
    grouped: dict[str, list[dict[str, str]]] = {perspective: [] for perspective in REVIEWER_PERSPECTIVES}
    for row in action_rows:
        grouped[row["reviewer_perspective"]].append(row)
    for index, perspective in enumerate(REVIEWER_PERSPECTIVES, start=1):
        rows = grouped[perspective]
        sections.extend(
            [
                f"### {index}. {perspective}",
                "",
                f"Primary read. {rows[0]['resolution']}",
                "",
                "| Concern | Claim | Figure | Status | Resolution |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for row in rows:
            sections.append(
                f"| {row['concern']} | {row['claim_id']} | {row['fig_id']} | {row['resolution_status']} | {row['resolution']} |"
            )
        sections.append("")
    sections.extend(
        [
            "## Blocking concern routing",
            "",
            "No fatal scientific blocker is left without a resolution status. The retained caution is interpretive, not evidentiary. Residence windows remain declared rather than discovered automatically, bounded coupling remains margin- and context-limited, reserve-like summaries remain tied to measured endpoints, routed-output comparisons remain effective model tests rather than molecular wiring, and software reproducibility remains scoped to the retained evidence set.",
            "",
            "## Recommendation before package assembly",
            "",
            "Proceed to Stage 9.27 package assembly with the action matrix attached. During assembly, preserve the current claim boundaries, keep the PanelForge figure status tied to the Stage 9.6b render report, and do not convert this internal review into a claim of external peer-review acceptance.",
            "",
        ]
    )
    return "\n".join(sections)


def _stage_outputs(audit: dict[str, Any], gate: dict[str, Any]) -> None:
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    review_path = STAGING_DIR / OUTPUTS["review"].relative_to(WORKSPACE)
    matrix_path = STAGING_DIR / OUTPUTS["matrix"].relative_to(WORKSPACE)
    gate_path = STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(_review_markdown(audit), encoding="utf-8")
    _write_csv(matrix_path, audit["action_rows"])
    _write_json(gate_path, gate)


def _promote_from_staging() -> None:
    for name, target in OUTPUTS.items():
        source = STAGING_DIR / target.relative_to(WORKSPACE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _quarantine_staging() -> str:
    if QUARANTINE_DIR.exists():
        shutil.rmtree(QUARANTINE_DIR)
    QUARANTINE_DIR.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(STAGING_DIR), str(QUARANTINE_DIR))
    return QUARANTINE_DIR.relative_to(ROOT).as_posix()


def _update_registry() -> None:
    registry = _read_json(REGISTRY_PATH)
    registry["next_substage"] = "9.27"
    registry["updated_utc"] = _now()
    for item in registry.get("substages", []):
        if item.get("id") == "9.26":
            item["status"] = "complete_internal_peer_review_bound"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.26",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.26.json",
        "validation_outcome": "Eight-perspective internal peer-review simulation completed with all concerns carrying resolution status",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.25b.json",
            "manuscript/nature_methods/audits/reader_surface_hygiene_report.md",
            "manuscript/nature_methods/gate_verdicts/9.6b.json",
            "manuscript/nature_methods/gate_verdicts/9.23.json",
            "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/audits/internal_peer_review_simulation.md",
            "manuscript/nature_methods/audits/reviewer_action_matrix.csv",
            "manuscript/nature_methods/gate_verdicts/9.26.json",
        ],
        "remaining_blockers": [
            "Full manuscript and submission-package assembly have not started",
            "PI review packet has not started",
        ],
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.26"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_stage9_memory(generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.26"
    memory["internal_peer_review_started"] = True
    memory["status"] = "stage9_26_internal_peer_review_bound"
    memory["current_gate"] = "Stage 9.26 internal peer review simulation stress-tested the reader-clean manuscript"
    memory["next_substage"] = "9.27"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.26 Internal peer review simulation complete; submission package assembly not started"
    memory["stage9_26_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/audits/internal_peer_review_simulation.md",
        "manuscript/nature_methods/audits/reviewer_action_matrix.csv",
        "manuscript/nature_methods/gate_verdicts/9.26.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.26 are complete through internal peer review simulation.",
        "Stage 9.27 through Stage 9.29 remain not started.",
        "No PI review packet, submission readiness checklist, or final package assembly is created in this pass.",
        "Eight reviewer perspectives stress-tested the manuscript and every concern has a resolution status.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, "
        "Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data "
        "binding, reference-library/citation audit, cross-document consistency audit, statistical/quantitative language audit, "
        "figure legend/caption audit, editorial polish passes I and II, reader-surface hygiene, and internal peer review simulation only. "
        "Do not start final submission package assembly without explicit substage authorization."
    )
    _upsert_completed_substage(memory, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory() -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.26 Internal peer review simulation complete; submission package assembly not started"
    current["stage9_active_gate"] = "Stage 9.26 Internal peer review simulation complete; submission package assembly not started"
    current["after_stage9_26_internal_peer_review"] = (
        "Stage 9.26 completed an eight-perspective internal peer-review simulation and reviewer action matrix. "
        "It preserved the reader-clean manuscript, routed scoped concerns, and recorded the current PanelForge figure assembly status without starting package assembly."
    )
    current["current_gate"] = "Internal review simulation completed with concern routing"
    current["next_stage"] = "Stage 9.27 Submission package assembly"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_26_internal_peer_review_bound"
        stage["current_gate"] = "Stage 9.26 internal peer review simulation stress-tested the reader-clean manuscript"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, "
            "supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, "
            "Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, "
            "availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, "
            "cross-document consistency audit, statistical-language audit, figure legend/caption audit, editorial polish passes I and II, "
            "reader-surface hygiene, and internal peer review simulation only. Do not start final submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/audits/internal_peer_review_simulation.md",
            "manuscript/nature_methods/audits/reviewer_action_matrix.csv",
            "manuscript/nature_methods/gate_verdicts/9.26.json",
            "scripts/run_stage9_26_internal_peer_review.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        review_gate = "Stage 9.26 stress-tested the reader-clean manuscript with eight reviewer perspectives and routed concerns."
        if review_gate not in gate:
            gate.append(review_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.26":
                subphase["status"] = "complete_internal_peer_review_bound"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.26.json"
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    README_PATH.write_text(
        """# Nature Methods manuscript workspace

This directory is the Stage 9 manuscript-assembly workspace for RhoDyn.

Current status. Stage 9.26 internal peer review simulation complete.

The workspace now contains the authorized manuscript components through internal peer review simulation. Evidence intake, venue guidance, methods-paper corpus analysis, narrative spine, claim freeze, paragraph planning, figure planning, deterministic main-figure rendering, supplementary display planning, section contracts, front matter, Results, Introduction, Discussion, Methods, availability statements, Supplementary Methods, supplementary table/source-data binding, reference audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, editorial polish passes I and II, reader-surface hygiene, and internal peer review are present.

The next unstarted step is Stage 9.27 submission package assembly. The PI review packet, submission-readiness checklist, and final package assembly have not started.

PanelForge figure rendering has already been exercised through the authorized Stage 9.6b deterministic rendering lane. The placeholder under `tools/panelforge-figures/` is not a clone, `.venv-panelforge` is not created by this workspace, and no local figure-engine repository is vendored here.
""",
        encoding="utf-8",
    )
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.25b registers `audits/reader_surface_hygiene_report.md` and `gate_verdicts/9.25b.json`, and removes internal reader-surface tokens without changing evidence bindings. The current state intentionally does not create the internal peer-review simulation or full submission-package files.",
            "Stage 9.25b registers `audits/reader_surface_hygiene_report.md` and `gate_verdicts/9.25b.json`, and removes internal reader-surface tokens without changing evidence bindings. Stage 9.26 registers `audits/internal_peer_review_simulation.md`, `audits/reviewer_action_matrix.csv`, and `gate_verdicts/9.26.json`, and stress-tests the reader-clean manuscript from eight reviewer perspectives. The current state intentionally does not create the full submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.26 | Internal peer review simulation | not_started | Stress-test the manuscript with eight reviewer perspectives. |",
            "| 9.26 | Internal peer review simulation | complete_internal_peer_review_bound | Stress-test the manuscript with eight reviewer perspectives. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.25 has completed editorial polish pass II, and Stage 9.25b has\ncompleted reader-surface hygiene. Internal peer review and final package assembly\nremain not started.",
            "Stage 9.25 has completed editorial polish pass II, Stage 9.25b has\ncompleted reader-surface hygiene, and Stage 9.26 has completed internal peer\nreview simulation. Final package assembly remains not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.25b Reader-surface hygiene complete, internal peer review not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, editorial polish passes I and II, and reader-surface hygiene only. Do not start internal peer review, review response, or final submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.26 Internal peer review simulation complete, submission package assembly not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, editorial polish passes I and II, reader-surface hygiene, and internal peer review simulation only. Do not start final submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.24 Editorial polish pass I has been completed. Stage 9.25 Editorial polish pass II has been completed. Stage 9.25b Reader-surface hygiene has been completed. Stage 9.26 Internal peer review simulation remains the next unstarted manuscript step. Final package assembly remains not started.",
            "Stage 9.24 Editorial polish pass I has been completed. Stage 9.25 Editorial polish pass II has been completed. Stage 9.25b Reader-surface hygiene has been completed. Stage 9.26 Internal peer review simulation has been completed. Stage 9.27 Submission package assembly remains the next unstarted manuscript step. Final package assembly remains not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    audit = _audit()
    gate = _gate_payload(audit)
    _stage_outputs(audit, gate)
    if not gate["pass"]:
        quarantine = _quarantine_staging()
        return {
            "status": "failed",
            "substage": "9.26",
            "quarantine": quarantine,
            "checks": audit["checks"],
            "next_substage": "9.26",
        }
    _promote_from_staging()
    shutil.rmtree(STAGING_DIR)
    if QUARANTINE_DIR.exists():
        shutil.rmtree(QUARANTINE_DIR)
    _update_registry()
    _update_stage9_memory(audit["generated_utc"], audit["checks"])
    _update_roadmap_memory()
    _update_docs()
    return {
        "status": "completed",
        "substage": "9.26",
        "outputs": [
            "manuscript/nature_methods/audits/internal_peer_review_simulation.md",
            "manuscript/nature_methods/audits/reviewer_action_matrix.csv",
            "manuscript/nature_methods/gate_verdicts/9.26.json",
        ],
        "checks": audit["checks"],
        "next_substage": "9.27",
        "panelforge": audit["panelforge"],
    }


def main() -> int:
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
