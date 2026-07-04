"""Run Stage 9.19 Supplementary table and source-data binding.

Stage 9.19 converts the planned supplementary table layer into reviewable
evidence objects. It binds each planned table to callout routes, claims,
source artifacts, statistic IDs, and the rendered PanelForge main-figure
surfaces without resolving the full reference library, writing figure legends,
or assembling the final submission package.
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
SUPPLEMENTARY_DIR = WORKSPACE / "supplementary"
LEDGERS_DIR = WORKSPACE / "ledgers"
FIGURES_DIR = WORKSPACE / "figures"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.19"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.19"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"

SUPPLEMENTARY_ITEM_PLAN = SUPPLEMENTARY_DIR / "supplementary_item_plan.md"
SUPPLEMENTARY_CALLOUT_LEDGER = LEDGERS_DIR / "supplementary_callout_ledger.csv"
FIGURE_LEDGER = LEDGERS_DIR / "figure_to_claim_to_artifact.csv"
EVIDENCE_MANIFEST = LEDGERS_DIR / "stage9_evidence_manifest.csv"
CLAIM_HIERARCHY = LEDGERS_DIR / "claim_hierarchy.csv"
GATE_918 = GATE_DIR / "9.18.json"

OUTPUTS = {
    "tables_plan": SUPPLEMENTARY_DIR / "supplementary_tables_plan.md",
    "source_binding": SUPPLEMENTARY_DIR / "source_data_binding_ledger.csv",
    "statistic_ledger": LEDGERS_DIR / "statistic_ledger.csv",
    "gate": GATE_DIR / "9.19.json",
}

FORBIDDEN_STARTED_PATHS = [
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "refs" / "citation_claim_ledger.csv",
    WORKSPACE / "figures" / "figure_legends.md",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
]


@dataclass(frozen=True)
class TableBinding:
    table_id: str
    supp_id: str
    title: str
    role: str
    callout_location: str
    support_function: str
    claim_ids: tuple[str, ...]
    stat_ids: tuple[str, ...]
    source_artifacts: tuple[str, ...]
    linked_figures: tuple[str, ...]
    interpretation_boundary: str


TABLE_BINDINGS = (
    TableBinding(
        table_id="STBL-001",
        supp_id="SUPP-001",
        title="Input contracts, method definitions, and executable truth cases",
        role="essential",
        callout_location="PARA-RESULTS-001; PARA-METHODS-001",
        support_function="Defines trajectory and endpoint input requirements, residence-window metrics, and truth-case support layers.",
        claim_ids=("CLM-0001", "CLM-0005"),
        stat_ids=("STAT-0001", "STAT-0002", "STAT-0003"),
        source_artifacts=("ART-0016", "ART-0017", "ART-0025", "ART-0026"),
        linked_figures=("FIG-001",),
        interpretation_boundary="Method definition and counterexample support only; not independent biological evidence.",
    ),
    TableBinding(
        table_id="STBL-002",
        supp_id="SUPP-002",
        title="Synthetic benchmark grid, baseline comparisons, and failure behavior",
        role="essential",
        callout_location="PARA-RESULTS-001; PARA-METHODS-001",
        support_function="Keeps known-truth synthetic benchmark outcomes visible behind the compressed benchmark display.",
        claim_ids=("CLM-0001", "CLM-0004"),
        stat_ids=("STAT-0004", "STAT-0005"),
        source_artifacts=("ART-0027", "ART-0028", "ART-0029", "ART-0030", "ART-0031"),
        linked_figures=("FIG-002",),
        interpretation_boundary="Synthetic benchmark behavior only; not a new biological system.",
    ),
    TableBinding(
        table_id="STBL-003",
        supp_id="SUPP-003",
        title="Public live-cell signaling adapters and window sensitivity",
        role="essential",
        callout_location="PARA-RESULTS-002; PARA-METHODS-001",
        support_function="Binds DRG calcium and ERK GPCR public trajectories to adapter details, residence-amplitude summaries, and uncertainty surfaces.",
        claim_ids=("CLM-0001",),
        stat_ids=("STAT-0006", "STAT-0007", "STAT-0008"),
        source_artifacts=("ART-0032", "ART-0033", "ART-0034", "ART-0035"),
        linked_figures=("FIG-003",),
        interpretation_boundary="Demonstrates two public live-cell reporter systems without claiming universal residence behavior.",
    ),
    TableBinding(
        table_id="STBL-004",
        supp_id="SUPP-004",
        title="Bounded-coupling decisions under declared margins",
        role="essential",
        callout_location="PARA-RESULTS-003; PARA-METHODS-002",
        support_function="Records endpoint pairing, declared margins, interval decisions, and inconclusive bounded-coupling cases.",
        claim_ids=("CLM-0002",),
        stat_ids=("STAT-0009", "STAT-0010"),
        source_artifacts=("ART-0036", "ART-0037", "ART-0040"),
        linked_figures=("FIG-004",),
        interpretation_boundary="Bounded coupling is margin- and context-limited; it is not proof of no crosstalk.",
    ),
    TableBinding(
        table_id="STBL-005",
        supp_id="SUPP-005",
        title="Reserve-like endpoint construction and uncertainty",
        role="essential",
        callout_location="PARA-RESULTS-004; PARA-METHODS-003",
        support_function="Separates the measured endpoint-preservation coordinate from unmeasured biological reserve and exposes uncertainty.",
        claim_ids=("CLM-0003",),
        stat_ids=("STAT-0011", "STAT-0012"),
        source_artifacts=("ART-0039", "ART-0049", "ART-0050"),
        linked_figures=("FIG-004",),
        interpretation_boundary="Reserve-like means measured endpoint preservation; it is not a direct live metabolic reserve assay.",
    ),
    TableBinding(
        table_id="STBL-006",
        supp_id="SUPP-006",
        title="Routed-output reduced-architecture comparison",
        role="essential",
        callout_location="PARA-RESULTS-005; PARA-METHODS-004",
        support_function="Binds endpoint rows to retained and reduced architectures, residual profiles, and model-comparison decisions.",
        claim_ids=("CLM-0004",),
        stat_ids=("STAT-0013", "STAT-0014"),
        source_artifacts=("ART-0038", "ART-0051"),
        linked_figures=("FIG-004",),
        interpretation_boundary="Effective routed terms constrain endpoint architecture but do not identify literal molecular edges.",
    ),
    TableBinding(
        table_id="STBL-007",
        supp_id="SUPP-007",
        title="Held-out validation pass states and margin-boundary cases",
        role="essential",
        callout_location="PARA-RESULTS-003; PARA-DISCUSSION-002",
        support_function="Keeps pass, inconclusive, margin-sensitivity, and access-boundary cases visible for held-out bounded-coupling contexts.",
        claim_ids=("CLM-0002",),
        stat_ids=("STAT-0015", "STAT-0016"),
        source_artifacts=("ART-0041", "ART-0042", "ART-0043", "ART-0044", "ART-0048"),
        linked_figures=("FIG-005",),
        interpretation_boundary="Supports scoped transfer of declared decisions rather than a universal coupling rule.",
    ),
    TableBinding(
        table_id="STBL-008",
        supp_id="SUPP-008",
        title="Software parity, export bundles, and archive contents",
        role="essential",
        callout_location="PARA-RESULTS-006; PARA-METHODS-005",
        support_function="Binds Python, CLI, backend, workbench, export-bundle, and archive surfaces to the same retained analysis choices.",
        claim_ids=("CLM-0005",),
        stat_ids=("STAT-0017", "STAT-0018"),
        source_artifacts=("ART-0010", "ART-0021", "ART-0022", "ART-0023", "ART-0024", "ART-0045", "ART-0046", "ART-0047", "ART-0052", "ART-0053"),
        linked_figures=("FIG-006",),
        interpretation_boundary="Supports reproducibility of retained evidence surfaces; it does not claim private-data reproduction or PyPI publication.",
    ),
    TableBinding(
        table_id="STBL-009",
        supp_id="SUPP-009",
        title="Interpretation boundaries and non-example cases",
        role="supportive",
        callout_location="PARA-DISCUSSION-001; PARA-DISCUSSION-002",
        support_function="Collects failure modes, ambiguous regimes, claim-strength caps, and recommended wording boundaries.",
        claim_ids=("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"),
        stat_ids=("STAT-0019",),
        source_artifacts=("ART-0017",),
        linked_figures=("FIG-001",),
        interpretation_boundary="A claim-boundary support surface, not a new result.",
    ),
)

STATISTIC_ROWS = {
    "STAT-0001": ("ART-0016", "FIG-001", "method object definitions", "displayed definitions for tidy trajectory, residence window, dwell fraction, dwell time, segment count, and amplitude comparators", "not_applicable", "method specification", "python3 scripts/build_stage7_1_synthetic_truth_cases.py", "STBL-001; SUPP-001"),
    "STAT-0002": ("ART-0026", "FIG-001", "truth-case suite coverage", "positive, negative, and ambiguous executable examples represented", "not_applicable", "json gate summary", "python3 scripts/build_stage7_1_synthetic_truth_cases.py", "STBL-001; SUPP-001"),
    "STAT-0003": ("ART-0017", "FIG-001", "limitation and non-example coverage", "failure modes and interpretation boundaries represented", "not_applicable", "limitations matrix", "not_applicable_manual_doc_binding", "STBL-001; STBL-009; SUPP-001; SUPP-009"),
    "STAT-0004": ("ART-0029", "FIG-002", "synthetic residence benchmark row count", "computed_from_source_rows", "not_applicable", "row count", "python3 scripts/run_stage7_2_benchmark_harness.py", "STBL-002; SUPP-002"),
    "STAT-0005": ("ART-0031", "FIG-002", "failure behavior decision count", "computed_from_source_rows", "not_applicable", "row count", "python3 scripts/run_stage7_2_benchmark_harness.py", "STBL-002; SUPP-002"),
    "STAT-0006": ("ART-0033", "FIG-003", "DRG calcium residence-amplitude summary rows", "computed_from_source_rows", "95% CI in paired uncertainty table", "row count", "python3 scripts/run_stage7_3_public_signaling.py", "STBL-003; SUPP-003"),
    "STAT-0007": ("ART-0034", "FIG-003", "ERK GPCR residence-amplitude summary rows", "computed_from_source_rows", "95% CI in paired uncertainty table", "row count", "python3 scripts/run_stage7_3_public_signaling.py", "STBL-003; SUPP-003"),
    "STAT-0008": ("ART-0032", "FIG-003", "public-data adapter and sensitivity support", "DRG and ERK public adapter reports represented", "not_applicable", "source DOI and adapter notes", "python3 scripts/run_stage7_3_public_signaling.py", "STBL-003; SUPP-003"),
    "STAT-0009": ("ART-0037", "FIG-004", "bounded-coupling declared-margin decisions", "computed_from_source_rows", "source table ci_low and ci_high", "declared-margin interval decision plus TOST where available", "python3 scripts/run_stage7_4_endpoint_reserve_routing.py", "STBL-004; SUPP-004"),
    "STAT-0010": ("ART-0037", "FIG-004", "bounded-coupling pass and inconclusive states", "computed_from_source_claim_status", "source table ci_low and ci_high", "claim_status count", "python3 scripts/run_stage7_4_endpoint_reserve_routing.py", "STBL-004; SUPP-004"),
    "STAT-0011": ("ART-0039", "FIG-004", "reserve-like model summary rows", "computed_from_source_rows", "95% CI in uncertainty table", "row count", "python3 scripts/run_stage7_4_endpoint_reserve_routing.py", "STBL-005; SUPP-005"),
    "STAT-0012": ("ART-0050", "FIG-004", "reserve-like uncertainty summaries", "computed_from_source_rows", "source table ci_low and ci_high", "bootstrap uncertainty", "python3 scripts/run_stage7_4_endpoint_reserve_routing.py", "STBL-005; SUPP-005"),
    "STAT-0013": ("ART-0038", "FIG-004", "routed-output model-comparison rows", "computed_from_source_rows", "not_applicable", "AIC/BIC ranking and delta BIC", "python3 scripts/run_stage7_4_endpoint_reserve_routing.py", "STBL-006; SUPP-006"),
    "STAT-0014": ("ART-0051", "FIG-004", "reduced-architecture decision rows", "computed_from_source_rows", "not_applicable", "reduced-alternative decision count", "python3 scripts/run_stage7_4_endpoint_reserve_routing.py", "STBL-006; SUPP-006"),
    "STAT-0015": ("ART-0043", "FIG-005", "held-out validation pass and inconclusive counts", "computed_from_source_fields", "not_applicable", "pass/inconclusive count", "python3 scripts/run_stage7_5_heldout_validation.py", "STBL-007; SUPP-007"),
    "STAT-0016": ("ART-0048", "FIG-005", "held-out margin sensitivity rows", "computed_from_source_rows", "source table ci_low and ci_high", "margin-sensitivity row count", "python3 scripts/run_stage7_5_heldout_validation.py", "STBL-007; SUPP-007"),
    "STAT-0017": ("ART-0024", "FIG-006", "cross-surface parity rows", "computed_from_source_rows", "not_applicable", "Python CLI backend frontend-contract parity", "python3 scripts/run_stage7_6_methods_reproducibility.py", "STBL-008; SUPP-008"),
    "STAT-0018": ("ART-0021", "FIG-006", "release archive manifest rows", "computed_from_source_rows", "not_applicable", "archive manifest file count", "python3 scripts/run_stage7_6_methods_reproducibility.py", "STBL-008; SUPP-008"),
    "STAT-0019": ("ART-0017", "FIG-001", "interpretation boundary coverage", "failure modes, ambiguous regimes, and claim-strength caps represented", "not_applicable", "manual limitation matrix binding", "not_applicable_manual_doc_binding", "STBL-009; SUPP-009"),
}


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


def _read_csv(path: Path, *, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _artifact_map() -> dict[str, dict[str, str]]:
    return {row["art_id"]: row for row in _read_csv(EVIDENCE_MANIFEST)}


def _figure_map() -> dict[str, dict[str, str]]:
    return {row["fig_id"]: row for row in _read_csv(FIGURE_LEDGER)}


def _callout_map() -> dict[str, dict[str, str]]:
    return {row["supp_id"]: row for row in _read_csv(SUPPLEMENTARY_CALLOUT_LEDGER)}


def _claim_ids() -> set[str]:
    return {row["claim_id"] for row in _read_csv(CLAIM_HIERARCHY)}


def _source_paths(art_ids: tuple[str, ...], artifacts: dict[str, dict[str, str]]) -> tuple[str, ...]:
    return tuple(artifacts[art_id]["path"] for art_id in art_ids if art_id in artifacts)


def _render_paths(fig_id: str) -> tuple[str, str, str]:
    return tuple(
        f"manuscript/nature_methods/figures/rendered/{fig_id}/{fig_id}.{suffix}"
        for suffix in ("svg", "png", "pdf")
    )  # type: ignore[return-value]


def _figure_recipe(fig_ids: tuple[str, ...], figures: dict[str, dict[str, str]]) -> str:
    return ";".join(figures[fig_id]["recipe"] for fig_id in fig_ids if fig_id in figures)


def _figure_render_paths(fig_ids: tuple[str, ...]) -> str:
    return ";".join(path for fig_id in fig_ids for path in _render_paths(fig_id))


def _count_source_rows(rel_path: str) -> int | None:
    path = ROOT / rel_path
    if not path.exists() or path.suffix.lower() not in {".csv", ".tsv"}:
        return None
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    return len(_read_csv(path, delimiter=delimiter))


def _value_for_stat(stat_id: str, artifacts: dict[str, dict[str, str]]) -> str:
    art_id, _, _, template_value, *_ = STATISTIC_ROWS[stat_id]
    if template_value != "computed_from_source_rows":
        if template_value == "computed_from_source_claim_status":
            source = ROOT / artifacts[art_id]["path"]
            rows = _read_csv(source)
            counts: dict[str, int] = {}
            for row in rows:
                key = row.get("claim_status") or row.get("decision") or "unlabeled"
                counts[key] = counts.get(key, 0) + 1
            return ";".join(f"{key}={counts[key]}" for key in sorted(counts))
        if template_value == "computed_from_source_fields":
            source = ROOT / artifacts[art_id]["path"]
            rows = _read_csv(source, delimiter="\t")
            if rows:
                row = rows[0]
                keys = ["context_count", "pass_count", "fail_count", "inconclusive_count"]
                return ";".join(f"{key}={row.get(key, '')}" for key in keys)
        return template_value
    rel_path = artifacts.get(art_id, {}).get("path", "")
    count = _count_source_rows(rel_path)
    return f"row_count={count}" if count is not None else "row_count=unavailable"


def _build_statistic_rows(artifacts: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for stat_id in sorted(STATISTIC_ROWS):
        art_id, fig_id, metric, template_value, ci, test, source_command, manuscript_locations = STATISTIC_ROWS[stat_id]
        rows.append(
            {
                "stat_id": stat_id,
                "art_id": art_id,
                "fig_id": fig_id,
                "value": _value_for_stat(stat_id, artifacts),
                "ci": ci,
                "n": _value_for_stat(stat_id, artifacts) if template_value == "computed_from_source_rows" else "see_source_artifact",
                "test": test,
                "source_command": source_command,
                "manuscript_locations": manuscript_locations,
            }
        )
    return rows


def _build_source_binding_rows() -> list[dict[str, str]]:
    artifacts = _artifact_map()
    figures = _figure_map()
    rows: list[dict[str, str]] = []
    for binding in TABLE_BINDINGS:
        rows.append(
            {
                "table_id": binding.table_id,
                "supp_id": binding.supp_id,
                "linked_main_figures": ";".join(binding.linked_figures),
                "claim_ids": ";".join(binding.claim_ids),
                "stat_ids": ";".join(binding.stat_ids),
                "callout_location": binding.callout_location,
                "role": binding.role,
                "source_artifacts": ";".join(binding.source_artifacts),
                "source_paths": ";".join(_source_paths(binding.source_artifacts, artifacts)),
                "panelforge_recipe": _figure_recipe(binding.linked_figures, figures),
                "render_paths": _figure_render_paths(binding.linked_figures),
                "binding_status": "bound_stage9_19",
                "interpretation_boundary": binding.interpretation_boundary,
            }
        )
    return rows


def _build_tables_plan(generated_utc: str, table_version: str) -> str:
    rows = _build_source_binding_rows()
    lines = [
        f"<!-- SUPPLEMENTARY-TABLE-BINDING stage=9.19 generated_utc={generated_utc} table_version={table_version} -->",
        "",
        "# Supplementary table and source-data binding plan",
        "",
        "Stage 9.19 turns the planned supplementary table layer into reviewable evidence objects. Each table is tied to a callout route, support role, frozen claim set, statistic IDs, source artifacts, and rendered figure surfaces. These are planning and traceability tables only. They do not add new biological demonstrations, new model outputs, reference-library entries, figure legends, or final Supplementary Information prose.",
        "",
        "## Table evidence map",
        "",
        "| table | linked supplement | role | callout route | linked figures | statistic IDs | source artifacts | support function | interpretation boundary |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    by_table = {row["table_id"]: row for row in rows}
    for binding in TABLE_BINDINGS:
        row = by_table[binding.table_id]
        lines.append(
            "| "
            + " | ".join(
                [
                    binding.table_id,
                    binding.supp_id,
                    binding.role,
                    binding.callout_location,
                    row["linked_main_figures"],
                    row["stat_ids"],
                    row["source_artifacts"],
                    binding.support_function,
                    binding.interpretation_boundary,
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Binding rules",
            "",
            "Every planned table has a main-text callout route and a defined support role. Essential tables support the main method argument through cited evidence, while the supportive boundary table preserves interpretation limits without becoming an uncited archive.",
            "",
            "Every table references one or more statistic IDs. The statistic ledger records the source artifact, display location, decision or summary type, and command route that will let the quantitative-language audit recompute or inspect the reported value later.",
            "",
            "Every table also records a figure-source mapping. For each linked main figure, the binding ledger preserves the PanelForge recipe string and the Stage 9.6b render paths for SVG, PNG, and PDF outputs so later figure legends and source-data checks can join the table layer to the visual evidence layer.",
            "",
            "## Scope boundary",
            "",
            "These table bindings are evidence objects for review and later assembly. They do not resolve the reference library, introduce reader-facing figure legends, assemble a submission package, or turn model-derived coordinates into direct biological endpoints.",
        ]
    )
    return "\n".join(lines)


def _no_downstream_started() -> tuple[bool, list[str]]:
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden, forbidden


def _validate(tables_plan: str, source_rows: list[dict[str, str]], statistic_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    gate_918_pass = False
    if GATE_918.exists():
        try:
            gate_918_pass = _read_json(GATE_918).get("pass") is True
        except json.JSONDecodeError:
            gate_918_pass = False
    callouts = _callout_map() if SUPPLEMENTARY_CALLOUT_LEDGER.exists() else {}
    figures = _figure_map() if FIGURE_LEDGER.exists() else {}
    artifacts = _artifact_map() if EVIDENCE_MANIFEST.exists() else {}
    claim_ids = _claim_ids() if CLAIM_HIERARCHY.exists() else set()
    table_ids = {row["table_id"] for row in source_rows}
    supp_ids = {row["supp_id"] for row in source_rows}
    stat_ids_in_tables = {
        stat_id
        for row in source_rows
        for stat_id in row["stat_ids"].split(";")
        if stat_id
    }
    statistic_ids = {row["stat_id"] for row in statistic_rows}
    linked_figures = {
        fig_id
        for row in source_rows
        for fig_id in row["linked_main_figures"].split(";")
        if fig_id
    }
    fig_render_paths = [
        render_path
        for row in source_rows
        for render_path in row["render_paths"].split(";")
        if render_path
    ]
    downstream_ok, downstream_paths = _no_downstream_started()
    required_table_ids = {f"STBL-{idx:03d}" for idx in range(1, 10)}
    required_supp_ids = {f"SUPP-{idx:03d}" for idx in range(1, 10)}
    required_fig_ids = {f"FIG-{idx:03d}" for idx in range(1, 7)}
    required_claim_ids = {f"CLM-{idx:04d}" for idx in range(1, 6)}
    return [
        {
            "name": "stage_9_18_gate_passed",
            "passed": gate_918_pass,
            "detail": "Stage 9.18 Supplementary Methods exists and passes" if gate_918_pass else "Stage 9.18 gate is missing or not passing",
        },
        {
            "name": "planned_table_set_complete",
            "passed": table_ids == required_table_ids and supp_ids == required_supp_ids,
            "detail": f"table_ids={';'.join(sorted(table_ids))}; supp_ids={';'.join(sorted(supp_ids))}",
        },
        {
            "name": "each_table_has_callout_and_role",
            "passed": all(row["callout_location"] and row["role"] for row in source_rows)
            and all(row["supp_id"] in callouts for row in source_rows),
            "detail": "All supplementary table rows retain planned callout routes and support roles",
        },
        {
            "name": "claims_and_source_artifacts_resolve",
            "passed": all(set(row["claim_ids"].split(";")) <= claim_ids for row in source_rows)
            and all(art_id in artifacts for row in source_rows for art_id in row["source_artifacts"].split(";") if art_id)
            and required_claim_ids <= {claim_id for row in source_rows for claim_id in row["claim_ids"].split(";")},
            "detail": "All table claim IDs and source ART IDs resolve to frozen ledgers",
        },
        {
            "name": "statistic_ids_bound_to_tables",
            "passed": stat_ids_in_tables == statistic_ids and len(statistic_rows) == 19,
            "detail": f"statistic_ids={';'.join(sorted(statistic_ids))}",
        },
        {
            "name": "figure_source_mapping_covers_main_figures",
            "passed": linked_figures == required_fig_ids
            and all(fig_id in figures for fig_id in linked_figures)
            and all(row["panelforge_recipe"] and row["render_paths"] for row in source_rows),
            "detail": f"linked_figures={';'.join(sorted(linked_figures))}",
        },
        {
            "name": "render_paths_exist_for_all_bound_figures",
            "passed": bool(fig_render_paths) and all((ROOT / path).exists() for path in fig_render_paths),
            "detail": f"render_path_count={len(fig_render_paths)}",
        },
        {
            "name": "no_reference_legend_or_submission_package_started",
            "passed": downstream_ok,
            "detail": "No references.bib, citation-claim ledger, figure legends, PI packet, or readiness checklist detected"
            if downstream_ok
            else "; ".join(downstream_paths),
        },
        {
            "name": "scope_boundary_preserved",
            "passed": "do not add new biological demonstrations" in tables_plan
            and "do not resolve the reference library" in tables_plan
            and "turn model-derived coordinates into direct biological endpoints" in tables_plan,
            "detail": "Table plan preserves source-data binding scope without new claims",
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
        if substage.get("id") == "9.19":
            substage["status"] = "complete_supplementary_tables_bound"
    registry["last_completed_substage"] = "9.19"
    registry["next_substage"] = "9.20"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], table_version: str, checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.19",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.19.json",
        "validation_outcome": "Supplementary table support objects are bound to callouts, source artifacts, statistics, and rendered figure surfaces",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.18.json",
            "manuscript/nature_methods/supplementary/supplementary_item_plan.md",
            "manuscript/nature_methods/ledgers/supplementary_callout_ledger.csv",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
            "manuscript/nature_methods/ledgers/stage9_evidence_manifest.csv",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/supplementary/supplementary_tables_plan.md",
            "manuscript/nature_methods/supplementary/source_data_binding_ledger.csv",
            "manuscript/nature_methods/ledgers/statistic_ledger.csv",
            "manuscript/nature_methods/gate_verdicts/9.19.json",
        ],
        "remaining_blockers": [
            "Full reference library and citation audit have not started",
            "Cross-document consistency audit has not started",
            "Figure legends have not started",
            "Full submission-package assembly has not started beyond the Reporting Summary requirement placeholder",
        ],
        "supplementary_tables_version": table_version,
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.19"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(table_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.19"
    memory["supplementary_tables_started"] = True
    memory["source_data_binding_started"] = True
    memory["status"] = "stage9_19_supplementary_tables_bound"
    memory["current_gate"] = "Stage 9.19 bound supplementary tables to source data, statistic IDs, and rendered figures"
    memory["next_substage"] = "9.20"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.19 Supplementary tables/source-data binding complete; reference library and citation audit not started"
    memory["stage9_19_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/supplementary/supplementary_tables_plan.md",
        "manuscript/nature_methods/supplementary/source_data_binding_ledger.csv",
        "manuscript/nature_methods/ledgers/statistic_ledger.csv",
        "manuscript/nature_methods/gate_verdicts/9.19.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.19 are complete through supplementary table and source-data binding.",
        "Stage 9.20 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No full reference library, figure legends, PI review packet, or submission readiness checklist are created in this supplementary table pass.",
        "Supplementary table rows map to planned SUPP callout routes, frozen CLM identifiers, source ART records, STAT rows, and Stage 9.6b PanelForge render paths.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, "
        "Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, and supplementary table/source-data "
        "binding only. Do not start the full reference library, figure legends, cross-document audit, or final submission package without explicit substage authorization."
    )
    _upsert_completed_substage(memory, table_version, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(table_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.19 Supplementary tables/source-data binding complete; reference library and citation audit not started"
    current["stage9_active_gate"] = "Stage 9.19 Supplementary tables/source-data binding complete; reference library and citation audit not started"
    current["after_stage9_19_supplementary_tables"] = (
        "Stage 9.19 registered supplementary table support objects and bound them to source artifacts, statistic IDs, rendered figures, and callout routes. "
        "It did not resolve the full reference library, write figure legends, run the cross-document consistency audit, or complete the final submission package."
    )
    current["current_gate"] = "Supplementary tables and source-data binding completed without reference-library or legend assembly"
    current["next_stage"] = "Stage 9.20 Reference library and citation audit"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_19_supplementary_tables_bound"
        stage["current_gate"] = "Stage 9.19 bound supplementary tables to source data, statistic IDs, and rendered figures"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, "
            "Methods drafting, availability assembly, Supplementary Methods drafting, and supplementary table/source-data binding only. "
            "Do not start the full reference library, figure legends, review response, cross-document audit, or final submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/supplementary/supplementary_tables_plan.md",
            "manuscript/nature_methods/supplementary/source_data_binding_ledger.csv",
            "manuscript/nature_methods/ledgers/statistic_ledger.csv",
            "manuscript/nature_methods/gate_verdicts/9.19.json",
            "scripts/run_stage9_19_supplementary_tables.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        table_gate = "Stage 9.19 supplementary table rows map to planned callouts, frozen claims, source artifacts, statistic IDs, and PanelForge render paths."
        if table_gate not in gate:
            gate.append(table_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.19":
                subphase["status"] = "complete_supplementary_tables_bound"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.19.json"
                subphase["supplementary_tables_version"] = table_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.18 registers Supplementary Methods prose in `supplementary/supplementary_methods.md` and `gate_verdicts/9.18.json`. The current state intentionally does not create supplementary tables, source-data binding, `refs/references.bib`, figure legends, or full submission-package files.",
            "Stage 9.18 registers Supplementary Methods prose in `supplementary/supplementary_methods.md` and `gate_verdicts/9.18.json`. Stage 9.19 registers supplementary table/source-data binding in `supplementary/supplementary_tables_plan.md`, `supplementary/source_data_binding_ledger.csv`, `ledgers/statistic_ledger.csv`, and `gate_verdicts/9.19.json`. The current state intentionally does not create `refs/references.bib`, figure legends, cross-document consistency audits, or full submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.19 | Supplementary tables and source-data binding | not_started | Build supplementary tables as reviewable evidence objects. |",
            "| 9.19 | Supplementary tables and source-data binding | complete_supplementary_tables_bound | Build supplementary tables as reviewable evidence objects. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "and Stage 9.18 has registered Supplementary Methods. Supplementary\ntable/source-data binding, full reference-library assembly, figure legends, and\nfinal package assembly remain not started.",
            "Stage 9.18 has registered Supplementary Methods, and Stage 9.19 has\nregistered supplementary table/source-data binding. Full reference-library\nassembly, figure legends, cross-document consistency audit, and final package\nassembly remain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.18 Supplementary Methods complete, supplementary tables and source-data binding not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, and Supplementary Methods drafting only. Do not start supplementary tables/source-data binding, full reference-library assembly, figure legends, review response, or final submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.19 Supplementary tables/source-data binding complete, reference library and citation audit not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, and supplementary table/source-data binding only. Do not start full reference-library assembly, figure legends, cross-document consistency audit, review response, or final submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding remains the next unstarted manuscript step. Supplementary table/source-data binding, full reference-library assembly, figure legends, and final package assembly remain not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit remains the next unstarted manuscript step. Full reference-library assembly, figure legends, cross-document consistency audit, and final package assembly remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    table_version = f"supplementary-table-binding@{generated_utc[:10]}@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    tables_plan = _build_tables_plan(generated_utc, table_version)
    source_rows = _build_source_binding_rows()
    statistic_rows = _build_statistic_rows(_artifact_map())
    _write_text(STAGING_DIR / OUTPUTS["tables_plan"].relative_to(WORKSPACE), tables_plan)
    _write_csv(
        STAGING_DIR / OUTPUTS["source_binding"].relative_to(WORKSPACE),
        source_rows,
        [
            "table_id",
            "supp_id",
            "linked_main_figures",
            "claim_ids",
            "stat_ids",
            "callout_location",
            "role",
            "source_artifacts",
            "source_paths",
            "panelforge_recipe",
            "render_paths",
            "binding_status",
            "interpretation_boundary",
        ],
    )
    _write_csv(
        STAGING_DIR / OUTPUTS["statistic_ledger"].relative_to(WORKSPACE),
        statistic_rows,
        ["stat_id", "art_id", "fig_id", "value", "ci", "n", "test", "source_command", "manuscript_locations"],
    )

    checks = _validate(tables_plan, source_rows, statistic_rows)
    passed = all(check["passed"] for check in checks)
    gate = {
        "substage": "9.19",
        "timestamp": generated_utc,
        "supplementary_tables_version": table_version,
        "pass": passed,
        "checks": checks,
        "table_count": len(source_rows),
        "statistic_row_count": len(statistic_rows),
        "supp_ids": sorted(row["supp_id"] for row in source_rows),
        "table_ids": sorted(row["table_id"] for row in source_rows),
        "stat_ids": sorted(row["stat_id"] for row in statistic_rows),
        "linked_figures": sorted({fig_id for row in source_rows for fig_id in row["linked_main_figures"].split(";")}),
        "next_substage": "9.20",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Supplementary table/source-data binding only. No references.bib, citation-claim ledger, figure legends, PI packet, readiness checklist, cross-document audit, or final submission-package assembly.",
    }
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)
    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(table_version, generated_utc, checks)
        _update_roadmap_memory(table_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)
    return {
        "status": "pass" if passed else "fail",
        "substage": "9.19",
        "supplementary_tables_version": table_version,
        "table_count": len(source_rows),
        "statistic_row_count": len(statistic_rows),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
        "next_allowed_action": "Proceed to Stage 9.20 reference library and citation audit after validation and explicit authorization.",
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
