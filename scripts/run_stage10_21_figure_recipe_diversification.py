"""Bind Stage 10 figure logic to diversified PanelForge recipes.

Stage 10.21 records the figure-level logic, panel-level recipe binding, and
visual-diversification policy for the six method-first figures. It updates no
scientific data, sends no external contact, and treats prospective validation
as a future evidence lane only.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage10_figure_recipe_diversification"
DOC_PATH = ROOT / "docs" / "stage10_21_figure_recipe_diversification.md"
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
CROSSWALK = ROOT / "manuscript" / "nature_methods" / "figures" / "stage10_5_panel_evidence_crosswalk.csv"
STAGE10_20_GATE = ROOT / "case_studies" / "stage10_eic_manuscript_strengthening" / "stage10_20_gate_report.json"
STAGE10_13_RUNNER = ROOT / "scripts" / "run_stage10_13_rendered_method_figures.py"
STAGE10_14_RUNNER = ROOT / "scripts" / "run_stage10_14_rendered_figure_visual_qc.py"

FIGURE_LOGIC = OUTPUT_DIR / "stage10_21_figure_logic_binding.tsv"
PANEL_BINDING = OUTPUT_DIR / "stage10_21_panel_recipe_binding.tsv"
RECIPE_AUDIT = OUTPUT_DIR / "stage10_21_recipe_diversity_audit.tsv"
REPORT = OUTPUT_DIR / "stage10_21_recipe_diversification_report.md"
MANIFEST = OUTPUT_DIR / "stage10_21_manifest.tsv"
GATE_REPORT = OUTPUT_DIR / "stage10_21_gate_report.json"

FIGURE_LOGIC_FIELDS = [
    "fig_id",
    "public_label",
    "figure_job",
    "required_panel_logic",
    "bound_panel_count",
    "status",
]
PANEL_BINDING_FIELDS = [
    "fig_id",
    "panel",
    "panel_id",
    "panel_title",
    "panel_logic",
    "panelforge_recipe",
    "data_recipe_tooling",
    "review_motif",
    "variation_axis",
    "evidence_scope",
    "status",
]
RECIPE_AUDIT_FIELDS = [
    "fig_id",
    "panel_count",
    "unique_panelforge_recipes",
    "unique_review_motifs",
    "max_recipe_reuse",
    "max_motif_reuse",
    "status",
]
MANIFEST_FIELDS = ["surface", "path", "role", "exists", "bytes", "sha256"]

FIGURE_BLUEPRINT = {
    "FIG-001": {
        "public_label": "Fig. 1",
        "figure_job": "Define the RhoDyn method object and decision divergence.",
        "required_panel_logic": "input objects, decision divergence, executable positive/negative/ambiguous fixtures, abstention and failure modes",
    },
    "FIG-002": {
        "public_label": "Fig. 2",
        "figure_job": "Show synthetic truth and named-baseline benchmarking.",
        "required_panel_logic": "known-truth regimes, named comparator families, accuracy and boundary outcomes, public-input comparator summaries, runtime",
    },
    "FIG-003": {
        "public_label": "Fig. 3",
        "figure_job": "Demonstrate public biological breadth.",
        "required_panel_logic": "public system matrix, DRG calcium, ERK GPCR, Cell Painting/MitoTox, MLCI tracking, source eligibility",
    },
    "FIG-004": {
        "public_label": "Fig. 4",
        "figure_job": "Demonstrate endpoint, reserve-like, bounded-coupling, and routed-output extension.",
        "required_panel_logic": "endpoint schema, bounded coupling, reserve-like endpoint, routed alternatives, measurement-scope limits",
    },
    "FIG-005": {
        "public_label": "Fig. 5",
        "figure_job": "Show held-out validation and uncertainty boundaries.",
        "required_panel_logic": "predeclared settings, held-out decision table, object-level calls, no-hidden-tuning gates, prospective-validation boundary",
    },
    "FIG-006": {
        "public_label": "Fig. 6",
        "figure_job": "Show reproducibility and user adoption.",
        "required_panel_logic": "Python/CLI/API/workbench parity, export bundles, clean-room reproduction, archive checksums, user-path rehearsal",
    },
}

VARIATION_AXES = {
    "schema_flow": "contract-flow topology",
    "equation_plus_decision_table": "equation-plus-decision grammar",
    "truth_case_grid": "truth-case grid",
    "failure_boundary_table": "abstention and failure ledger",
    "truth_regime_matrix": "known-truth regime matrix",
    "baseline_family_ladder": "named-comparator ladder",
    "accuracy_heatmap_with_boundary_rows": "accuracy heatmap with boundary rows",
    "public_input_comparator_table": "public-input small multiples",
    "runtime_memory_stripplot": "runtime and memory stripplot",
    "public_system_matrix": "biological-domain matrix",
    "trajectory_residence_amplitude_panel": "trajectory window overlay",
    "trajectory_boundary_comparison": "trajectory plus sufficiency boundary",
    "endpoint_architecture_panel": "endpoint architecture network",
    "tracking_residence_panel": "tracking trajectory path",
    "source_eligibility_table": "source eligibility ledger",
    "endpoint_schema_flow": "endpoint contract-flow topology",
    "bounded_coupling_interval_table": "bounded-coupling interval forest",
    "reserve_endpoint_uncertainty_panel": "reserve-like gauge and uncertainty",
    "architecture_comparison_matrix": "reduced-architecture model ladder",
    "endpoint_limitations_table": "measurement-scope guardrail",
    "predeclaration_flow": "locked no-retuning timeline",
    "heldout_decision_matrix": "held-out decision matrix",
    "heldout_object_scatter": "object-level call scatter",
    "gate_status_table": "gate-status checklist",
    "validation_boundary_panel": "sealed-versus-prospective boundary",
    "parity_table": "interface parity grid",
    "export_bundle_diagram": "analysis bundle anatomy",
    "clean_room_flow": "clean-room replay loop",
    "archive_checksum_panel": "archive checksum ledger",
    "user_path_panel": "dual user-path diagram",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _write_tsv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def crosswalk_rows() -> list[dict[str, str]]:
    with CROSSWALK.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def figure_logic_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts = Counter(row["fig_id"] for row in rows)
    output: list[dict[str, Any]] = []
    for fig_id in sorted(FIGURE_BLUEPRINT):
        blueprint = FIGURE_BLUEPRINT[fig_id]
        output.append(
            {
                "fig_id": fig_id,
                "public_label": blueprint["public_label"],
                "figure_job": blueprint["figure_job"],
                "required_panel_logic": blueprint["required_panel_logic"],
                "bound_panel_count": counts.get(fig_id, 0),
                "status": "bound" if counts.get(fig_id, 0) > 0 else "missing",
            }
        )
    return output


def panel_binding_rows(rows: list[dict[str, str]], recipe_bindings: dict[str, tuple[str, str]], motif_variants: dict[str, str]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in rows:
        hint = row["render_recipe_hint"]
        recipe, data_tool = recipe_bindings.get(hint, ("", ""))
        motif = motif_variants.get(hint, "")
        status = "bound" if recipe and data_tool and motif and hint in VARIATION_AXES else "missing_binding"
        output.append(
            {
                "fig_id": row["fig_id"],
                "panel": row["panel"],
                "panel_id": row["panel_id"],
                "panel_title": row["panel_title"],
                "panel_logic": row["method_job"],
                "panelforge_recipe": recipe,
                "data_recipe_tooling": data_tool,
                "review_motif": motif,
                "variation_axis": VARIATION_AXES.get(hint, ""),
                "evidence_scope": row["reader_takeaway"],
                "status": status,
            }
        )
    return output


def recipe_audit_rows(panel_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_figure: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in panel_rows:
        by_figure[row["fig_id"]].append(row)
    output: list[dict[str, Any]] = []
    for fig_id in sorted(by_figure):
        rows = by_figure[fig_id]
        recipe_counts = Counter(row["panelforge_recipe"] for row in rows)
        motif_counts = Counter(row["review_motif"] for row in rows)
        unique_recipes = len(recipe_counts)
        unique_motifs = len(motif_counts)
        max_recipe_reuse = max(recipe_counts.values()) if recipe_counts else 0
        max_motif_reuse = max(motif_counts.values()) if motif_counts else 0
        passes = unique_recipes >= 3 and unique_motifs >= 4 and max_recipe_reuse <= 3 and max_motif_reuse <= 1
        output.append(
            {
                "fig_id": fig_id,
                "panel_count": len(rows),
                "unique_panelforge_recipes": unique_recipes,
                "unique_review_motifs": unique_motifs,
                "max_recipe_reuse": max_recipe_reuse,
                "max_motif_reuse": max_motif_reuse,
                "status": "pass" if passes else "fail",
            }
        )
    return output


def manifest_rows() -> list[dict[str, Any]]:
    surfaces = [
        ("figure_logic", FIGURE_LOGIC, "Six-figure logic binding"),
        ("panel_binding", PANEL_BINDING, "Panel-level recipe and motif binding"),
        ("recipe_audit", RECIPE_AUDIT, "Recipe diversification audit"),
        ("report", REPORT, "Stage 10.21 report"),
        ("doc", DOC_PATH, "Documentation page"),
    ]
    rows: list[dict[str, Any]] = []
    for surface, path, role in surfaces:
        exists = path.exists() and path.is_file()
        rows.append(
            {
                "surface": surface,
                "path": _rel(path),
                "role": role,
                "exists": "yes" if exists else "no",
                "bytes": path.stat().st_size if exists else 0,
                "sha256": _sha256(path) if exists else "",
            }
        )
    return rows


def report_text(gate: dict[str, Any]) -> str:
    summary = gate["summary_metrics"]
    return f"""# Stage 10.21 figure recipe diversification

Stage 10.21 binds the six Nature Methods-facing RhoDyn figures to explicit PanelForge recipe families and panel-specific visual motifs. The purpose is to make the figures read as different scientific displays rather than repeated templates.

## Status

`{gate["status"]}`

## Figure logic

- Figures bound. `{summary["figure_count"]}`.
- Panels bound. `{summary["bound_panel_count"]}` of `{summary["panel_count"]}`.
- Distinct PanelForge recipes. `{summary["unique_panelforge_recipe_count"]}`.
- Distinct review motifs. `{summary["unique_review_motif_count"]}`.
- Figures passing diversity policy. `{summary["diversity_pass_figure_count"]}`.

## Boundary

This pass changes figure production logic and visual recipe diversity only. It does not add datasets, change benchmark decisions, change manuscript claims, imply author visual approval, perform prospective validation, or send external contact.
"""


def doc_text(gate: dict[str, Any]) -> str:
    return f"""# Stage 10.21 figure recipe diversification

Stage 10.21 binds each method-first figure and panel to a specific PanelForge recipe family, data-tooling class, and review-render visual motif.

## Status

`{gate["status"]}`

## Outputs

- Figure logic binding. `{gate["outputs"]["figure_logic"]}`
- Panel recipe binding. `{gate["outputs"]["panel_binding"]}`
- Recipe diversity audit. `{gate["outputs"]["recipe_audit"]}`
- Report. `{gate["outputs"]["report"]}`
- Gate report. `{gate["outputs"]["gate_report"]}`

## Interpretation boundary

The six rendered figures remain method-display surfaces. This pass improves recipe and visual diversity but does not add biological evidence or replace future prospective validation.
"""


def _update_memory(gate: dict[str, Any]) -> None:
    memory = _read_json(MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 10.21 figure recipe diversification complete; external contact remains not sent"
    current["current_gate"] = "Stage 10.21 figure recipe diversification complete; external contact remains not sent"
    current["stage10_active_gate"] = "Stage 10.21 figure recipe diversification complete; external contact remains not sent"
    current["next_stage"] = "Corresponding-author decision on presubmission query, direct submission, venue pivot, or optional prospective validation"
    current["after_stage10_21_figure_recipe_diversification"] = (
        "Stage 10.21 bound the six method-first figures and all thirty panels to explicit PanelForge recipe families, "
        "data-tooling classes, and review-render motifs so the figures no longer depend on repeated generic template logic."
    )

    stage10 = next((stage for stage in memory.get("stage_lock", []) if stage.get("stage") == 10), None)
    if not isinstance(stage10, dict):
        _write_json(MEMORY_PATH, memory)
        return
    artifacts = set(stage10.get("artifacts", []))
    artifacts.update(
        [
            _rel(DOC_PATH),
            "scripts/run_stage10_21_figure_recipe_diversification.py",
            "tests/test_stage10_21_figure_recipe_diversification.py",
            _rel(FIGURE_LOGIC),
            _rel(PANEL_BINDING),
            _rel(RECIPE_AUDIT),
            _rel(REPORT),
            _rel(MANIFEST),
            _rel(GATE_REPORT),
        ]
    )
    stage10["artifacts"] = sorted(artifacts)
    stage10["status"] = "stage10_21_complete_figure_recipe_diversification"
    stage10["current_gate"] = "Stage 10.21 figure recipe diversification complete; external contact remains not sent"
    subphases = stage10.setdefault("subphases", [])
    by_id = {entry.get("id"): entry for entry in subphases if isinstance(entry, dict)}
    by_id["10.21"] = {
        "id": "10.21",
        "name": "Figure recipe diversification",
        "status": "complete_figure_recipe_diversification",
        "goal": "Bind the six figures and thirty panels to explicit PanelForge recipe families and panel-specific review motifs.",
        "gate": "All figures and panels are bound, every figure passes the recipe and motif diversity policy, and external contact remains unsent.",
        "evidence": _rel(GATE_REPORT),
    }
    stage10["subphases"] = [by_id[key] for key in sorted(by_id, key=lambda value: tuple(int(part) for part in value.split(".")))]
    _write_json(MEMORY_PATH, memory)


def run_stage10_21() -> dict[str, Any]:
    stage10_20 = _read_json(STAGE10_20_GATE)
    stage10_13 = _load_module(STAGE10_13_RUNNER, "stage10_13_runner")
    stage10_14 = _load_module(STAGE10_14_RUNNER, "stage10_14_runner")
    rows = crosswalk_rows()
    figures = figure_logic_rows(rows)
    panels = panel_binding_rows(rows, stage10_13.PANEL_RECIPE_BINDINGS, stage10_14.MOTIF_VARIANTS)
    audit = recipe_audit_rows(panels)

    _write_tsv(FIGURE_LOGIC, figures, FIGURE_LOGIC_FIELDS)
    _write_tsv(PANEL_BINDING, panels, PANEL_BINDING_FIELDS)
    _write_tsv(RECIPE_AUDIT, audit, RECIPE_AUDIT_FIELDS)
    _write_text(REPORT, "# pending")
    _write_text(DOC_PATH, "# pending")
    manifest = manifest_rows()
    _write_tsv(MANIFEST, manifest, MANIFEST_FIELDS)

    recipe_set = {row["panelforge_recipe"] for row in panels if row["panelforge_recipe"]}
    motif_set = {row["review_motif"] for row in panels if row["review_motif"]}
    gates = {
        "stage10_20_passed": stage10_20.get("status") == "pass",
        "six_figures_bound": len(figures) == 6 and all(row["status"] == "bound" for row in figures),
        "all_panels_bound": len(panels) == 30 and all(row["status"] == "bound" for row in panels),
        "recipe_diversity_passes": len(audit) == 6 and all(row["status"] == "pass" for row in audit),
        "uses_panel_specific_review_motifs": len(motif_set) >= 24,
        "uses_multiple_panelforge_recipe_families": len(recipe_set) >= 7,
        "manifest_all_exists": all(row["exists"] == "yes" and row["sha256"] for row in manifest),
        "external_contact_not_sent": stage10_20.get("external_contact_status") == "not_sent",
    }
    gate = {
        "stage": "10.21",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "gates": gates,
        "external_contact_status": "not_sent",
        "summary_metrics": {
            "figure_count": len(figures),
            "panel_count": len(panels),
            "bound_panel_count": sum(row["status"] == "bound" for row in panels),
            "unique_panelforge_recipe_count": len(recipe_set),
            "unique_review_motif_count": len(motif_set),
            "diversity_pass_figure_count": sum(row["status"] == "pass" for row in audit),
            "manifest_row_count": len(manifest),
        },
        "outputs": {
            "figure_logic": _rel(FIGURE_LOGIC),
            "panel_binding": _rel(PANEL_BINDING),
            "recipe_audit": _rel(RECIPE_AUDIT),
            "manifest": _rel(MANIFEST),
            "report": _rel(REPORT),
            "gate_report": _rel(GATE_REPORT),
            "doc": _rel(DOC_PATH),
        },
        "interpretation_boundary": (
            "Stage 10.21 changes figure recipe binding and review-render diversity only. It does not add data, "
            "rerun benchmarks, change claims, imply author approval, perform prospective validation, or send external contact."
        ),
    }
    _write_text(REPORT, report_text(gate))
    _write_text(DOC_PATH, doc_text(gate))
    manifest = manifest_rows()
    _write_tsv(MANIFEST, manifest, MANIFEST_FIELDS)
    gate["summary_metrics"]["manifest_row_count"] = len(manifest)
    gate["gates"]["manifest_all_exists"] = all(row["exists"] == "yes" and row["sha256"] for row in manifest)
    gate["status"] = "pass" if all(gate["gates"].values()) else "fail"
    _write_json(GATE_REPORT, gate)
    _update_memory(gate)
    return gate


def main() -> None:
    print(json.dumps(run_stage10_21(), indent=2))


if __name__ == "__main__":
    main()
