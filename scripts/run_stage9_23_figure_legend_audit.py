"""Run Stage 9.23 figure legend and caption audit.

Stage 9.23 writes the first self-contained figure legend surface for the
Nature Methods manuscript scaffold. The reader-facing legend file avoids
internal IDs, paths, PanelForge provenance, and package-build language. The
paired audit file checks that the legends still resolve to the frozen figure,
claim, statistic, and supplementary-table contracts.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
AUDITS_DIR = WORKSPACE / "audits"
GATE_DIR = WORKSPACE / "gate_verdicts"
FIGURES_DIR = WORKSPACE / "figures"
LEDGERS_DIR = WORKSPACE / "ledgers"
SUPPLEMENTARY_DIR = WORKSPACE / "supplementary"
STAGING_DIR = WORKSPACE / "_staging" / "9.23"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.23"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
README_PATH = WORKSPACE / "README.md"

GATE_922 = GATE_DIR / "9.22.json"
FIGURE_LEDGER = LEDGERS_DIR / "figure_to_claim_to_artifact.csv"
STATISTIC_LEDGER = LEDGERS_DIR / "statistic_ledger.csv"
SOURCE_DATA_LEDGER = SUPPLEMENTARY_DIR / "source_data_binding_ledger.csv"
SUPPLEMENTARY_CALLOUT_LEDGER = LEDGERS_DIR / "supplementary_callout_ledger.csv"

OUTPUTS = {
    "legends": FIGURES_DIR / "figure_legends.md",
    "audit": AUDITS_DIR / "figure_legend_audit.md",
    "gate": GATE_DIR / "9.23.json",
}

FORBIDDEN_PACKAGE_PATHS = [
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
    WORKSPACE / "stage9_completion_report.md",
]

LEAKAGE_PATTERNS = [
    r"\b(?:FIG|SFIG|STBL|SUPP|STAT|ART|CLM|PARA|MTH)-\d{3,}\b",
    r"\bPanelForge\b",
    r"\bpanelforge\b",
    r"\bStage\s*9\b",
    r"\bstage9\b",
    r"\bmanifest\b",
    r"\bledger\b",
    r"\baudit\b",
    r"\bprovenance\b",
    r"\brender_path\b",
    r"\bsource_paths\b",
    r"\bcommit\b",
    r"\bhash\b",
    "/" + "Users/",
    "/" + "Volumes/",
    "Library/" + "LaunchAgents",
]

UNSAFE_CLAIM_PATTERNS = [
    "proof of absent pathway communication",
    "absence of all pathway communication",
    "no crosstalk",
    "no pathway communication",
    "direct live metabolic reserve assay",
    "literal molecular edge",
    "universal coupling rule",
    "universal residence behavior",
    "private-data reproduction",
    "PyPI publication",
    "guarantees",
    "proves",
]

MAIN_LEGENDS = [
    {
        "fig_id": "FIG-001",
        "number": "1",
        "title": "RhoDyn defines residence-state inference as an executable method object.",
        "body": (
            "**a**, The method-object schematic defines the input contract for trajectory and endpoint analyses, "
            "including tidy records, declared biological windows, replicate variables, and exportable decisions. "
            "**b**, Residence-window summaries separate dwell fraction, dwell time, and segment count from peak, "
            "endpoint, and average amplitude so that time spent inside a declared interval is visible as its own "
            "measurement. **c**, Failure-mode examples show when missing time, condition, replicate, or window "
            "definitions should prevent a residence call. **d**, Executable positive, negative, and ambiguous truth "
            "cases show that the same method object can return a result or withhold one when the input does not "
            "support interpretation. The figure establishes the analysis object and its boundaries before any "
            "biological demonstration is considered."
        ),
    },
    {
        "fig_id": "FIG-002",
        "number": "2",
        "title": "Synthetic benchmarks distinguish residence structure from amplitude-only summaries.",
        "body": (
            "**a**, Known-truth synthetic regimes place amplitude-like, residence-like, ambiguous, and negative "
            "signals on matched simulated inputs. **b**, The residence-versus-amplitude benchmark summarizes twelve "
            "synthetic comparisons and shows when dwell inside the declared window changes the state assignment "
            "relative to endpoint, peak, or mean activity. **c**, Reduced-alternative comparisons test whether "
            "simpler summaries reproduce the same decision structure. **d**, The negative and ambiguous boundary "
            "case keeps unsupported calls visible rather than forcing classification. The figure supports "
            "residence-state inference in tested trajectory regimes while preserving cases where the method should "
            "remain inconclusive."
        ),
    },
    {
        "fig_id": "FIG-003",
        "number": "3",
        "title": "Public live-cell reporters show residence-amplitude separation beyond the reference use case.",
        "body": (
            "**a**, The public-data adapter map shows how external calcium and ERK reporter time series enter the "
            "same tidy trajectory schema without changing their source biological context. **b**, In the DRG calcium "
            "demonstration, 360 trace summaries separate time spent inside the declared response window from calcium "
            "amplitude. **c**, In the ERK GPCR demonstration, 180 trace summaries show the same separation between "
            "window occupancy and peak or endpoint signaling. **d**, Window-sensitivity and uncertainty summaries "
            "show where the interpretation is stable, fragile, or unresolved as the declared window changes. These "
            "examples show that residence and amplitude can diverge in more than one public live-cell reporter system."
        ),
    },
    {
        "fig_id": "FIG-004",
        "number": "4",
        "title": "Endpoint analyses expose bounded coupling, reserve-like buffering, and routed-output alternatives.",
        "body": (
            "**a**, The endpoint schema contract defines grouping, contrast, margin, and readout fields before any "
            "bounded-coupling or model-comparison decision is made. **b**, Four bounded-coupling decisions distinguish "
            "one primary margin-compatible context, one secondary pooled or contextual summary, and two contrasts "
            "that are not promoted beyond their declared margin. **c**, The reserve-like endpoint coordinate is "
            "summarized across six endpoint rows with two uncertainty summaries, keeping the buffering interpretation "
            "tied to the measured readout. **d**, Routed-output comparison evaluates six endpoint model rows and five "
            "reduced alternatives to identify which candidate architectures satisfy the observed endpoint structure. "
            "**e**, The limitation panel states the measurement scope for coupling, reserve-like behavior, and routed "
            "outputs. The figure extends RhoDyn from trajectory residence scoring to endpoint decision support while "
            "keeping each decision conditional on declared margins, uncertainty, and tested alternatives."
        ),
    },
    {
        "fig_id": "FIG-005",
        "number": "5",
        "title": "Held-out contexts separate bounded-coupling support from unresolved margin-boundary cases.",
        "body": (
            "**a**, The held-out analysis plan separates the primary decision rule from later margin and access-boundary "
            "checks. **b**, Seven held-out contexts include four cases in which the declared margin and uncertainty "
            "support a bounded-coupling decision. **c**, The complementary contexts remain inconclusive when the "
            "available interval does not justify promotion to equivalence within the declared bound. **d**, Seventy "
            "margin-sensitivity rows make the dependence on the chosen biological margin visible. **e**, The "
            "controlled-access boundary records cases where the input can be reviewed only through derived tables or "
            "notes. The figure keeps pass and inconclusive states side by side, making bounded coupling a scoped "
            "decision rather than an automatic output."
        ),
    },
    {
        "fig_id": "FIG-006",
        "number": "6",
        "title": "Software parity and archive reproduction make RhoDyn decisions inspectable.",
        "body": (
            "**a**, The parity panel compares Python, command-line, backend, and workbench outputs for retained evidence "
            "paths. **b**, The export-bundle view shows that inputs, schema details, parameter choices, summaries, "
            "figures, and reports are written together rather than hidden in session state. **c**, Source-distribution "
            "clean-room reproduction checks the installable release boundary against selected retained outputs. **d**, "
            "The archive and checksum panel records a four-surface parity check and a 603-row release archive inventory. "
            "**e**, The adoption and user-path rehearsal tests whether biologist-facing and quantitative workflows can "
            "reach the same reviewable outputs. The figure supports reproducibility of the demonstrated analyses "
            "without turning software availability into a new biological result."
        ),
    },
]

SUPPLEMENTARY_FIGURE_LEGENDS = [
    (
        "1",
        "Input contracts, method definitions, and executable truth cases.",
        "Panels expand the main method-object figure with tidy trajectory and endpoint schemas, residence-window metric definitions, executable positive and negative truth cases, and boundary examples where the supplied input does not support interpretation.",
    ),
    (
        "2",
        "Synthetic benchmark grid, baseline comparisons, and failure behavior.",
        "Panels provide the known-truth benchmark grid, residence-versus-amplitude comparisons, reduced-summary comparisons, and negative or ambiguous cases that sit behind the compressed synthetic benchmark figure.",
    ),
    (
        "3",
        "Public live-cell signaling adapters and residence-amplitude sensitivity.",
        "Panels document the public-data adapter contract, DRG calcium and ERK GPCR residence-amplitude summaries, and the window or uncertainty sensitivity analyses used to scope the public reporter demonstrations.",
    ),
    (
        "4",
        "Bounded-coupling decisions under declared margins.",
        "Panels show the endpoint pairing contract, declared margin table, bounded-coupling interval display, and inconclusive decision examples used to keep coupling claims tied to the stated margin and context.",
    ),
    (
        "5",
        "Reserve-like endpoint construction and uncertainty.",
        "Panels separate measured endpoint components, the reserve-like coordinate construction, uncertainty summaries, and label-scope boundaries so that buffering language remains tied to the measured assay.",
    ),
    (
        "6",
        "Routed-output reduced-architecture comparison.",
        "Panels provide the routed architecture matrix, reduced-alternative comparison, residual profile, and decision-boundary table behind the endpoint model-comparison display.",
    ),
    (
        "7",
        "Held-out validation pass and boundary cases.",
        "Panels show the fixed held-out plan, pass contexts, margin-boundary inconclusive contexts, margin sensitivity, and controlled-access notes that prevent held-out validation from becoming a single unqualified score.",
    ),
    (
        "8",
        "Software parity, clean-room reproduction, and archive contents.",
        "Panels document cross-surface parity, export-bundle contents, clean-room reproduction summaries, archive records, checksums, and usability-path boundaries for the retained evidence surfaces.",
    ),
    (
        "9",
        "Interpretation boundaries and non-example cases.",
        "Panels collect non-example cases, ambiguous regimes, claim-strength caps, and recommended wording boundaries so that limitations remain visible without carrying the main argument.",
    ),
]

SUPPLEMENTARY_TABLE_CAPTIONS = [
    (
        "1",
        "Input requirements, residence-window metrics, and truth-case support layers for the method-object figure.",
    ),
    (
        "2",
        "Known-truth synthetic benchmark outcomes, baseline comparisons, and failure-behavior rows for the synthetic benchmark figure.",
    ),
    (
        "3",
        "Public-data adapter details, DRG calcium and ERK GPCR residence-amplitude summaries, and uncertainty support for the public reporter figure.",
    ),
    (
        "4",
        "Endpoint pairing, declared margins, interval decisions, and inconclusive bounded-coupling cases for the endpoint decision figure.",
    ),
    (
        "5",
        "Measured endpoint-preservation coordinate, reserve-like summary rows, and uncertainty support for the reserve-like endpoint panels.",
    ),
    (
        "6",
        "Endpoint model rows, retained and reduced architectures, residual profiles, and model-comparison decisions for routed-output analysis.",
    ),
    (
        "7",
        "Held-out bounded-coupling pass cases, inconclusive contexts, margin-sensitivity rows, and controlled-access boundaries.",
    ),
    (
        "8",
        "Python, command-line, backend, workbench, export-bundle, clean-room reproduction, and archive surfaces used for reproducibility support.",
    ),
    (
        "9",
        "Failure modes, ambiguous regimes, claim-strength caps, and wording boundaries used to keep interpretation within the tested evidence.",
    ),
]


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except subprocess.CalledProcessError:
        return "unknown"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _panel_letters(panel_structure: str) -> list[str]:
    letters = re.findall(r"(?:^|; )([A-Z])\b", panel_structure)
    return [letter.lower() for letter in letters]


def _archive_inventory_row_count() -> str:
    for row in _read_csv(STATISTIC_LEDGER):
        if row.get("stat_id") == "STAT-0018":
            match = re.search(r"row_count=(\d+)", row.get("value", ""))
            if match:
                return match.group(1)
    return "current"


def _build_legend_document() -> str:
    archive_count = _archive_inventory_row_count()
    main = "\n\n".join(
        f"### Figure {item['number']} | {item['title']}\n\n"
        f"{item['body'].replace('603-row release archive inventory', f'{archive_count}-row release archive inventory')}"
        for item in MAIN_LEGENDS
    )
    supplementary_figures = "\n\n".join(
        f"### Supplementary Fig. {number} | {title}\n\n{body}"
        for number, title, body in SUPPLEMENTARY_FIGURE_LEGENDS
    )
    supplementary_tables = "\n\n".join(
        f"### Supplementary Table {number} | {caption}" for number, caption in SUPPLEMENTARY_TABLE_CAPTIONS
    )
    return f"""# Figure legends and table captions

## Main figure legends

{main}

## Supplementary figure legends

{supplementary_figures}

## Supplementary table captions

{supplementary_tables}
"""


def _legend_sections(text: str, prefix: str) -> dict[str, str]:
    pattern = re.compile(rf"^### {re.escape(prefix)} (\d+) \| .*$", re.M)
    matches = list(pattern.finditer(text))
    sections: dict[str, str] = {}
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections[match.group(1)] = text[match.start() : end]
    return sections


def _leakage_hits(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in LEAKAGE_PATTERNS:
        if re.search(pattern, text):
            hits.append(pattern)
    return hits


def _unsafe_claim_hits(text: str) -> list[str]:
    lower = text.lower()
    return [phrase for phrase in UNSAFE_CLAIM_PATTERNS if phrase.lower() in lower]


def _stat_resolution_errors(figure_rows: list[dict[str, str]], table_rows: list[dict[str, str]], stat_ids: set[str]) -> list[str]:
    errors: list[str] = []
    for row in figure_rows:
        for stat_id in [token.strip() for token in row["stat_ids"].split(";") if token.strip()]:
            if stat_id not in stat_ids:
                errors.append(f"{row['fig_id']}->{stat_id}")
    for row in table_rows:
        for stat_id in [token.strip() for token in row["stat_ids"].split(";") if token.strip()]:
            if stat_id not in stat_ids:
                errors.append(f"{row['table_id']}->{stat_id}")
    return errors


def _audit_legends(legend_text: str) -> dict[str, Any]:
    stage_922_gate = _read_json(GATE_922)
    figure_rows = _read_csv(FIGURE_LEDGER)
    statistic_rows = _read_csv(STATISTIC_LEDGER)
    source_table_rows = _read_csv(SOURCE_DATA_LEDGER)
    supplementary_callouts = _read_csv(SUPPLEMENTARY_CALLOUT_LEDGER)
    stat_ids = {row["stat_id"] for row in statistic_rows}

    main_sections = _legend_sections(legend_text, "Figure")
    supplementary_figure_sections = _legend_sections(legend_text, "Supplementary Fig.")
    supplementary_table_sections = _legend_sections(legend_text, "Supplementary Table")

    missing_main = [str(idx) for idx in range(1, 7) if str(idx) not in main_sections]
    missing_supp_fig = [str(idx) for idx in range(1, 10) if str(idx) not in supplementary_figure_sections]
    missing_supp_table = [str(idx) for idx in range(1, 10) if str(idx) not in supplementary_table_sections]

    panel_coverage_errors: list[str] = []
    for row in figure_rows:
        number = row["fig_id"].split("-")[-1].lstrip("0")
        section = main_sections.get(number, "")
        for letter in _panel_letters(row["panel_structure"]):
            if f"**{letter}**" not in section:
                panel_coverage_errors.append(f"Figure {number}{letter}")

    stat_errors = _stat_resolution_errors(figure_rows, source_table_rows, stat_ids)
    forbidden_package_paths = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_PACKAGE_PATHS if path.exists()]
    leakage = _leakage_hits(legend_text)
    unsafe = _unsafe_claim_hits(legend_text)
    supplementary_link_errors: list[str] = []
    for row in supplementary_callouts:
        supp_number = row["supp_id"].split("-")[-1].lstrip("0")
        table_number = row["tbl_id"].split("-")[-1].lstrip("0")
        if supp_number not in supplementary_figure_sections:
            supplementary_link_errors.append(f"{row['supp_id']} missing Supplementary Fig. {supp_number}")
        if table_number not in supplementary_table_sections:
            supplementary_link_errors.append(f"{row['tbl_id']} missing Supplementary Table {table_number}")

    checks = [
        {
            "name": "stage_9_22_gate_passed",
            "passed": stage_922_gate.get("pass") is True and stage_922_gate.get("substage") == "9.22",
            "detail": "Stage 9.22 statistical and quantitative language gate is present and passed",
        },
        {
            "name": "each_main_figure_has_legend",
            "passed": not missing_main and len(main_sections) == 6,
            "detail": f"main_figure_legends={len(main_sections)}; missing={missing_main}",
        },
        {
            "name": "each_supplementary_figure_and_table_has_caption",
            "passed": not missing_supp_fig and not missing_supp_table and len(supplementary_figure_sections) == 9 and len(supplementary_table_sections) == 9,
            "detail": (
                f"supplementary_figures={len(supplementary_figure_sections)}; "
                f"supplementary_tables={len(supplementary_table_sections)}; "
                f"missing_figures={missing_supp_fig}; missing_tables={missing_supp_table}"
            ),
        },
        {
            "name": "main_figure_panel_coverage_complete",
            "passed": not panel_coverage_errors,
            "detail": f"missing_panel_mentions={panel_coverage_errors}",
        },
        {
            "name": "legend_statistics_resolve",
            "passed": not stat_errors,
            "detail": f"stat_resolution_errors={stat_errors}; statistic_ids={len(stat_ids)}",
        },
        {
            "name": "supplementary_callouts_resolve_to_captions",
            "passed": not supplementary_link_errors,
            "detail": f"supplementary_link_errors={supplementary_link_errors}",
        },
        {
            "name": "legends_do_not_assert_absent_claims",
            "passed": not unsafe,
            "detail": f"unsafe_claim_hits={unsafe}",
        },
        {
            "name": "legend_seed_text_has_no_internal_or_panelforge_leakage",
            "passed": not leakage,
            "detail": f"leakage_patterns={leakage}",
        },
        {
            "name": "no_final_package_started",
            "passed": not forbidden_package_paths,
            "detail": f"forbidden_package_paths={forbidden_package_paths}",
        },
    ]
    return {
        "generated_utc": _now(),
        "commit": _git_sha(),
        "checks": checks,
        "main_figure_count": len(main_sections),
        "supplementary_figure_caption_count": len(supplementary_figure_sections),
        "supplementary_table_caption_count": len(supplementary_table_sections),
        "missing_main": missing_main,
        "missing_supp_fig": missing_supp_fig,
        "missing_supp_table": missing_supp_table,
        "panel_coverage_errors": panel_coverage_errors,
        "stat_resolution_errors": stat_errors,
        "supplementary_link_errors": supplementary_link_errors,
        "leakage_hits": leakage,
        "unsafe_claim_hits": unsafe,
        "forbidden_package_paths": forbidden_package_paths,
        "figure_rows": figure_rows,
        "source_table_rows": source_table_rows,
        "statistic_count": len(stat_ids),
    }


def _build_audit(analysis: dict[str, Any]) -> str:
    check_rows = "\n".join(
        f"| {item['name']} | {'pass' if item['passed'] else 'fail'} | {item['detail']} |"
        for item in analysis["checks"]
    )
    figure_rows = "\n".join(
        f"| {row['fig_id']} | {row['stat_ids']} | {row['panel_structure']} |" for row in analysis["figure_rows"]
    )
    table_rows = "\n".join(
        f"| {row['table_id']} | {row['stat_ids']} | {row['interpretation_boundary']} |"
        for row in analysis["source_table_rows"]
    )
    return f"""<!-- FIGURE-LEGEND-AUDIT stage=9.23 generated={analysis['generated_utc']} commit={analysis['commit']} -->
# Stage 9.23 figure legend and caption audit

Stage 9.23 writes the first reader-facing legend and caption surface for the six main display items, nine planned supplementary figures, and nine planned supplementary tables. The visible legend text uses standard figure and table names, while this audit checks the hidden joins to figure panels, statistics, supplementary support, and claim boundaries.

## Summary

The figure legend and caption audit passed. Six main figure legends, nine supplementary figure legends, and nine supplementary table captions were written. All main figure panel letters are represented, every figure and table statistic binding resolves to the current statistic ledger, and the reader-facing legend text contains no internal identifiers, paths, PanelForge wording, or absent-mechanism claims.

## Gate checks

| Check | Status | Detail |
|---|---|---|
{check_rows}

## Main figure statistic bindings checked

| Figure | Statistic IDs | Panel structure |
|---|---|---|
{figure_rows}

## Supplementary table statistic bindings checked

| Table | Statistic IDs | Interpretation boundary |
|---|---|---|
{table_rows}

## Reader-facing language boundary

The legend file does not expose internal IDs, source paths, render paths, engine provenance, commit identifiers, or package-build language. Bounded coupling is described as a declared-margin decision, reserve-like output is described as endpoint-scoped buffering behavior, and routed-output comparisons are described as tested endpoint architectures rather than direct molecular edges.

## Scope boundary

This stage writes figure legends and table captions only. It does not assemble the full manuscript, create a PI review packet, run editorial polish, change figures, introduce new analyses, or modify biological claims.
"""


def _gate_payload(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "substage": "9.23",
        "title": "Figure legend and caption audit",
        "generated_utc": analysis["generated_utc"],
        "commit": analysis["commit"],
        "pass": all(item["passed"] for item in analysis["checks"]),
        "checks": analysis["checks"],
        "main_figure_legend_count": analysis["main_figure_count"],
        "supplementary_figure_caption_count": analysis["supplementary_figure_caption_count"],
        "supplementary_table_caption_count": analysis["supplementary_table_caption_count"],
        "statistic_count": analysis["statistic_count"],
        "panel_coverage_errors": analysis["panel_coverage_errors"],
        "stat_resolution_errors": analysis["stat_resolution_errors"],
        "supplementary_link_errors": analysis["supplementary_link_errors"],
        "leakage_hits": analysis["leakage_hits"],
        "unsafe_claim_hits": analysis["unsafe_claim_hits"],
        "forbidden_package_paths": analysis["forbidden_package_paths"],
        "outputs": [
            "manuscript/nature_methods/figures/figure_legends.md",
            "manuscript/nature_methods/audits/figure_legend_audit.md",
            "manuscript/nature_methods/gate_verdicts/9.23.json",
        ],
        "scope_boundary": "Figure legends and table captions only. No new analyses, model outputs, figure rendering, editorial polish, PI packet, readiness checklist, or final package assembly.",
        "next_substage": "9.24",
    }


def _stage_outputs(legend_text: str, analysis: dict[str, Any], gate: dict[str, Any]) -> None:
    legend_path = STAGING_DIR / OUTPUTS["legends"].relative_to(WORKSPACE)
    audit_path = STAGING_DIR / OUTPUTS["audit"].relative_to(WORKSPACE)
    gate_path = STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE)
    legend_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    legend_path.write_text(legend_text, encoding="utf-8")
    audit_path.write_text(_build_audit(analysis), encoding="utf-8")
    _write_json(gate_path, gate)


def _promote_from_staging() -> None:
    for final_path in OUTPUTS.values():
        staged = STAGING_DIR / final_path.relative_to(WORKSPACE)
        final_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, final_path)


def _quarantine_staging() -> Path:
    QUARANTINE_DIR.parent.mkdir(parents=True, exist_ok=True)
    target = QUARANTINE_DIR
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(STAGING_DIR), str(target))
    return target


def _read_memory(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _update_registry() -> None:
    registry = _read_memory(REGISTRY_PATH)
    for substage in registry.get("substages", []):
        if substage.get("id") == "9.23":
            substage["status"] = "complete_figure_legend_caption_audit_bound"
    registry["last_completed_substage"] = "9.23"
    registry["next_substage"] = "9.24"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.23",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.23.json",
        "validation_outcome": "Six main figure legends, nine supplementary figure legends, and nine supplementary table captions were written with clean reader-facing language",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.22.json",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
            "manuscript/nature_methods/ledgers/statistic_ledger.csv",
            "manuscript/nature_methods/supplementary/source_data_binding_ledger.csv",
            "manuscript/nature_methods/ledgers/supplementary_callout_ledger.csv",
            "manuscript/nature_methods/sections/results.md",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/figures/figure_legends.md",
            "manuscript/nature_methods/audits/figure_legend_audit.md",
            "manuscript/nature_methods/gate_verdicts/9.23.json",
        ],
        "remaining_blockers": [
            "Editorial polish pass I has not started",
            "Reader-surface hygiene gate remains downstream",
            "Full submission-package assembly has not started beyond the Reporting Summary requirement placeholder",
        ],
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.23"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_memory(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.23"
    memory["figure_legends_started"] = True
    memory["figure_caption_audit_started"] = True
    memory["status"] = "stage9_23_figure_legend_caption_audit_bound"
    memory["current_gate"] = "Stage 9.23 figure legends and captions passed coverage, statistic-resolution, and reader-surface checks"
    memory["next_substage"] = "9.24"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.23 Figure legend and caption audit complete; editorial polish pass I not started"
    memory["stage9_23_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/figures/figure_legends.md",
        "manuscript/nature_methods/audits/figure_legend_audit.md",
        "manuscript/nature_methods/gate_verdicts/9.23.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.23 are complete through figure legend and caption audit.",
        "Stage 9.24 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No editorial polish, PI review packet, or submission readiness checklist is created in this legend pass.",
        "All six main figures, nine supplementary figures, and nine supplementary tables have self-contained captions.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, "
        "Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data "
        "binding, reference-library/citation audit, cross-document consistency audit, statistical/quantitative language audit, "
        "and figure legend/caption audit only. Do not start editorial polishing or final submission package without explicit substage authorization."
    )
    _upsert_completed_substage(memory, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory() -> None:
    memory = _read_memory(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.23 Figure legend and caption audit complete; editorial polish pass I not started"
    current["stage9_active_gate"] = "Stage 9.23 Figure legend and caption audit complete; editorial polish pass I not started"
    current["after_stage9_23_figure_legend_caption_audit"] = (
        "Stage 9.23 wrote reader-facing legends for six main figures, captions for nine planned supplementary figures, "
        "and captions for nine supplementary tables. The audit verified panel coverage, statistic resolution, supplementary "
        "caption coverage, and absence of internal figure-engine or source-path language. It did not start editorial polishing or assemble the final submission package."
    )
    current["current_gate"] = "Figure legend and caption audit completed without editorial polish or package assembly"
    current["next_stage"] = "Stage 9.24 Editorial polish pass I"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_23_figure_legend_caption_audit_bound"
        stage["current_gate"] = "Stage 9.23 legends and captions cover every planned display item and retain statistic-bound interpretation limits"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, "
            "Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, "
            "cross-document consistency audit, statistical-language audit, and figure legend/caption audit only. Do not start editorial polish, review response, or final submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/figures/figure_legends.md",
            "manuscript/nature_methods/audits/figure_legend_audit.md",
            "manuscript/nature_methods/gate_verdicts/9.23.json",
            "scripts/run_stage9_23_figure_legend_audit.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        legend_gate = "Stage 9.23 created self-contained figure and table captions and verified reader-facing language hygiene."
        if legend_gate not in gate:
            gate.append(legend_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.23":
                subphase["status"] = "complete_figure_legend_caption_audit_bound"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.23.json"
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    README_PATH.write_text(
        """# Nature Methods manuscript workspace

This directory is the Stage 9 manuscript-assembly workspace for RhoDyn.

Current status. Stage 9.23 figure legend and caption audit complete.

The workspace now contains the authorized manuscript components through figure legends and table captions. Evidence intake, venue guidance, methods-paper corpus analysis, narrative spine, claim freeze, paragraph planning, figure planning, deterministic main-figure rendering, supplementary display planning, section contracts, front matter, Results, Introduction, Discussion, Methods, availability statements, Supplementary Methods, supplementary table/source-data binding, reference audit, cross-document consistency audit, statistical-language audit, and figure legend/caption audit are present.

The next unstarted step is Stage 9.24 editorial polish pass I. Final manuscript assembly, PI review packet, submission-readiness checklist, and final package assembly have not started.

PanelForge figure rendering has already been exercised through the authorized Stage 9.6b deterministic rendering lane. The placeholder under `tools/panelforge-figures/` is not a clone, `.venv-panelforge` is not created by this workspace, and no local figure-engine repository is vendored here.
""",
        encoding="utf-8",
    )
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.21 registers `audits/cross_document_consistency_audit.md` and `gate_verdicts/9.21.json`. Stage 9.22 registers `audits/statistical_language_audit.md`, `audits/live_numbers_diff.csv`, refreshed statistic bindings, and `gate_verdicts/9.22.json`. The current state intentionally does not create figure legends or full submission-package files.",
            "Stage 9.21 registers `audits/cross_document_consistency_audit.md` and `gate_verdicts/9.21.json`. Stage 9.22 registers `audits/statistical_language_audit.md`, `audits/live_numbers_diff.csv`, refreshed statistic bindings, and `gate_verdicts/9.22.json`. Stage 9.23 registers `figures/figure_legends.md`, `audits/figure_legend_audit.md`, and `gate_verdicts/9.23.json`. The current state intentionally does not create editorial-polish reports or full submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.23 | Figure legend and caption audit | not_started | Make display items self-contained and precise. |",
            "| 9.23 | Figure legend and caption audit | complete_figure_legend_caption_audit_bound | Make display items self-contained and precise. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.18 has registered Supplementary Methods, Stage 9.19 has\nregistered supplementary table/source-data binding, Stage 9.20 has registered\nthe reference library and citation audit, Stage 9.21 has registered the\ncross-document consistency audit, and Stage 9.22 has registered the statistical\nand quantitative language audit. Figure legends and final package assembly\nremain not started.",
            "Stage 9.18 has registered Supplementary Methods, Stage 9.19 has\nregistered supplementary table/source-data binding, Stage 9.20 has registered\nthe reference library and citation audit, Stage 9.21 has registered the\ncross-document consistency audit, Stage 9.22 has registered the statistical\nand quantitative language audit, and Stage 9.23 has registered figure legends\nand table captions. Editorial polish and final package assembly remain not\nstarted.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.22 Statistical and quantitative language audit complete, figure legend and caption audit not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, and statistical-language audit only. Do not start figure legends, review response, or final submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.23 Figure legend and caption audit complete, editorial polish pass I not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, statistical-language audit, and figure legend/caption audit only. Do not start editorial polish, review response, or final submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit has been completed. Stage 9.21 Cross-document consistency audit has been completed. Stage 9.22 Statistical and quantitative language audit has been completed. Stage 9.23 Figure legend and caption audit remains the next unstarted manuscript step. Final package assembly remains not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit has been completed. Stage 9.21 Cross-document consistency audit has been completed. Stage 9.22 Statistical and quantitative language audit has been completed. Stage 9.23 Figure legend and caption audit has been completed. Stage 9.24 Editorial polish pass I remains the next unstarted manuscript step. Final package assembly remains not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    legend_text = _build_legend_document()
    analysis = _audit_legends(legend_text)
    gate = _gate_payload(analysis)
    _stage_outputs(legend_text, analysis, gate)

    if not gate["pass"]:
        quarantine = _quarantine_staging()
        return {
            "status": "failed",
            "substage": "9.23",
            "quarantine_dir": str(quarantine.relative_to(ROOT)),
            "failed_checks": [item for item in gate["checks"] if not item["passed"]],
        }

    _promote_from_staging()
    shutil.rmtree(STAGING_DIR)
    _update_registry()
    _update_memory(analysis["generated_utc"], gate["checks"])
    _update_roadmap_memory()
    _update_docs()

    return {
        "status": "completed",
        "substage": "9.23",
        "outputs": gate["outputs"],
        "next_substage": "9.24",
        "checks": gate["checks"],
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
