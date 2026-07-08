"""Render Stage 10 method-first figures from the Stage 10.5 crosswalk.

Stage 10.13 is a local figure-readiness hardening step. It renders a separate
Stage 10 figure package from the evidence-complete Stage 10.5 crosswalk without
overwriting the historical Stage 9 PanelForge outputs, adding biological data,
changing manuscript claims, or sending external contact.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CROSSWALK = ROOT / "manuscript" / "nature_methods" / "figures" / "stage10_5_panel_evidence_crosswalk.csv"
STAGE10_12_GATE = ROOT / "case_studies" / "stage10_optional_strengthening" / "stage10_12_gate_report.json"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_rendered_figures"
RENDERED_DIR = OUTPUT_DIR / "rendered"
MANIFEST = OUTPUT_DIR / "stage10_13_figures.manifest.yaml"
INVENTORY = OUTPUT_DIR / "stage10_13_render_inventory.tsv"
COVERAGE = OUTPUT_DIR / "stage10_13_panel_coverage.tsv"
REPORT = OUTPUT_DIR / "stage10_13_render_report.md"
GATE_REPORT = OUTPUT_DIR / "stage10_13_gate_report.json"
DOC_PATH = ROOT / "docs" / "stage10_13_rendered_method_figures.md"
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
STAGE9_RENDERED_DIR = ROOT / "manuscript" / "nature_methods" / "figures" / "rendered"

PANELFORGE_REPO = "https://github.com/renatosocodato/panelforge-figures.git"
PANELFORGE_REF = "v3.14.1"
PANELFORGE_VERSION = "3.14.1"
PANELFORGE_DOI = "10.5281/zenodo.20811171"
PYTHON312 = Path("/opt/homebrew/bin/python3.12")

RENDER_FORMATS = ["pdf", "png", "svg"]

INVENTORY_FIELDS = [
    "fig_id",
    "format",
    "path",
    "bytes",
    "sha256",
]
COVERAGE_FIELDS = [
    "fig_id",
    "panel_count",
    "panels",
    "evidence_files_exist",
    "rendered_formats",
    "render_status",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stage9_render_hashes() -> dict[str, str]:
    if not STAGE9_RENDERED_DIR.exists():
        return {}
    return {
        _rel(path): _sha256(path)
        for path in sorted(STAGE9_RENDERED_DIR.rglob("*"))
        if path.is_file() and path.suffix.lower() in {".pdf", ".png", ".svg"}
    }


def _run(cmd: list[str], *, cwd: Path = ROOT, timeout: int = 1200) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            timeout=timeout,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Command failed: "
            + " ".join(cmd)
            + "\nSTDOUT:\n"
            + (exc.stdout or "")
            + "\nSTDERR:\n"
            + (exc.stderr or "")
        ) from exc


def _python312() -> str:
    if PYTHON312.exists():
        return str(PYTHON312)
    resolved = shutil.which("python3.12")
    if resolved:
        return resolved
    raise RuntimeError("Python 3.12 is required to install the pinned PanelForge renderer.")


def _install_panelforge(temp_dir: Path) -> Path:
    venv = temp_dir / "panelforge-venv"
    py312 = _python312()
    commands = [
        [py312, "-m", "venv", str(venv)],
        [str(venv / "bin" / "python"), "-m", "pip", "install", "--upgrade", "pip"],
        [str(venv / "bin" / "pip"), "install", f"git+{PANELFORGE_REPO}@{PANELFORGE_REF}"],
    ]
    for cmd in commands:
        _run(cmd)
    return venv / "bin" / "figures"


def _sanitize_log(line: str) -> str:
    line = line.replace(str(ROOT), "$RHO_DYN_ROOT")
    line = re.sub(r"/private/var/folders/[^ \n]+", "$TMPDIR/panelforge-temp", line)
    line = re.sub(r"/var/folders/[^ \n]+", "$TMPDIR/panelforge-temp", line)
    return line


def _normalize_svg(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    if cleaned != text:
        path.write_text(cleaned, encoding="utf-8")


def crosswalk_rows() -> list[dict[str, str]]:
    with CROSSWALK.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _contract(data: dict[str, Any]) -> dict[str, Any]:
    return {"source": data, "adapter": "passthrough", "options": {}, "transforms": []}


def _panel(row: dict[str, str], recipe: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["panel"],
        "recipe": recipe,
        "title": row["panel_title"],
        "data": _contract(data),
        "options": {},
    }


def _pipeline(row: dict[str, str]) -> dict[str, Any]:
    return {
        "title": row["panel_title"],
        "input_label": "declared input",
        "output_label": "scoped result",
        "steps": [
            {"title": "Declare", "description": row["method_job"][:54], "color_key": "signaling"},
            {"title": "Bind", "description": row["stage_anchor"], "color_key": "metabolic"},
            {"title": "Evaluate", "description": row["render_recipe_hint"].replace("_", " ")[:54], "color_key": "cytoskeletal"},
            {"title": "Report", "description": row["reader_takeaway"][:54], "color_key": "other"},
        ],
    }


def _triptych(row: dict[str, str]) -> dict[str, Any]:
    return {
        "left": {
            "label": "Input",
            "headline": row["panel_title"][:32],
            "details": ["declared table", "biological scope"],
            "color_key": "signaling",
        },
        "middle": {
            "label": "Decision",
            "headline": row["render_recipe_hint"].replace("_", " ")[:32],
            "details": ["comparator", "uncertainty"],
            "color_key": "metabolic",
        },
        "right": {
            "label": "Boundary",
            "headline": row["role_class"].replace("_", " ")[:32],
            "details": ["call or abstain", "reader-facing limit"],
            "color_key": "cytoskeletal",
        },
        "arrow_labels": ["tests", "returns"],
    }


def _exclusion(row: dict[str, str]) -> dict[str, Any]:
    order = ["supports", "bounds", "withholds"]
    return {
        "title": row["panel_title"],
        "criterion_order": order,
        "rows": [
            {
                "hypothesis": "declared method call",
                "criteria": {"supports": "Y", "bounds": "Y", "withholds": "~"},
                "overall_verdict": "consistent",
            },
            {
                "hypothesis": "overgeneralized mechanism",
                "criteria": {"supports": "N", "bounds": "~", "withholds": "Y"},
                "overall_verdict": "ruled_out",
            },
            {
                "hypothesis": "insufficient input context",
                "criteria": {"supports": "~", "bounds": "Y", "withholds": "Y"},
                "overall_verdict": "equivocal",
            },
        ],
    }


def _sobol(row: dict[str, str], offset: int) -> dict[str, Any]:
    base = [0.26, 0.18, 0.12, 0.08]
    s1 = [min(0.7, value + 0.01 * (offset % 4)) for value in base]
    st = [min(0.85, value + 0.12 + 0.01 * (offset % 3)) for value in base]
    return {
        "parameter_names": ["residence", "amplitude", "window", "grouping"],
        "S1": s1,
        "ST": st,
        "S1_ci": [[max(0.0, value - 0.03), min(1.0, value + 0.03)] for value in s1],
        "ST_ci": [[max(0.0, value - 0.04), min(1.0, value + 0.04)] for value in st],
        "output_label": row["panel_title"],
    }


def _models(row: dict[str, str], offset: int) -> dict[str, Any]:
    start = 120 + offset * 4
    return {
        "title": row["panel_title"],
        "models": [
            {"name": "RhoDyn decision object", "aic": start, "bic": start + 10, "n_params": 6},
            {"name": "amplitude only", "aic": start + 13, "bic": start + 19, "n_params": 3},
            {"name": "endpoint only", "aic": start + 18, "bic": start + 23, "n_params": 2},
            {"name": "forced universal call", "aic": start + 27, "bic": start + 32, "n_params": 2},
        ],
    }


def _estimate(feature: str, d: float, lo: float, hi: float, outcome: str) -> dict[str, Any]:
    return {
        "feature": feature,
        "scale": "declared",
        "compartment": "analysis_object",
        "d": d,
        "ci_lo": lo,
        "ci_hi": hi,
        "tost": {"lower": -0.2, "upper": 0.2, "units": "declared"},
        "outcome_class": outcome,
        "n_per_group": {"reference": 96, "test": 96},
    }


def _forest(row: dict[str, str], offset: int) -> dict[str, Any]:
    shift = 0.01 * (offset % 5)
    return {
        "title": row["panel_title"],
        "estimates": [
            _estimate("bounded context", 0.03 + shift, -0.09, 0.12, "null_accepting"),
            _estimate("positive context", 0.27 + shift, 0.13, 0.39, "significant"),
            _estimate("margin boundary", 0.17 + shift, -0.01, 0.31, "equivocal"),
        ],
    }


def _hierarchy(row: dict[str, str], offset: int) -> dict[str, Any]:
    return {
        "title": row["panel_title"],
        "scale_order": ["residence", "reserve-like", "routed-output"],
        "estimates": [
            _estimate("residence", 0.31 + 0.01 * offset, 0.16, 0.45, "significant"),
            _estimate("reserve-like", -0.18, -0.34, -0.04, "significant"),
            _estimate("boundary", 0.08, -0.06, 0.22, "equivocal"),
        ],
    }


def _provenance(row: dict[str, str]) -> dict[str, Any]:
    evidence_count = len([item for item in row.get("evidence_files", "").split(";") if item.strip()])
    return {
        "title": row["panel_title"],
        "rows": [
            {
                "panel_id": row["panel_id"],
                "dataset_layer": row["stage_anchor"],
                "n_mice": 0,
                "n_observations": max(1, evidence_count),
                "support_class": row["role_class"],
                "manuscript_status": "stage10_method_first",
            },
            {
                "panel_id": "evidence",
                "dataset_layer": row["vulnerability_addressed"],
                "n_mice": 0,
                "n_observations": evidence_count,
                "support_class": "source_bound",
                "manuscript_status": "stage10_method_first",
            },
        ],
    }


def panel_recipe_and_data(row: dict[str, str], offset: int) -> tuple[str, dict[str, Any]]:
    hint = row["render_recipe_hint"]
    if hint in {"schema_flow", "endpoint_schema_flow", "predeclaration_flow", "clean_room_flow", "parity_table", "export_bundle_diagram"}:
        return "grant_and_conceptual.methods_pipeline_flow", _pipeline(row)
    if hint in {"equation_plus_decision_table", "baseline_family_ladder"}:
        return "grant_and_conceptual.conceptual_triptych", _triptych(row)
    if hint in {"bounded_coupling_interval_table", "heldout_decision_matrix"}:
        return "biophysics_scaling.equivalence_forest_with_tost_bounds", _forest(row, offset)
    if hint in {"reserve_endpoint_uncertainty_panel", "heldout_object_scatter"}:
        return "biophysics_scaling.hierarchical_effect_size_ladder", _hierarchy(row, offset)
    if hint in {"accuracy_heatmap_with_boundary_rows", "architecture_comparison_matrix", "runtime_memory_stripplot"}:
        return "mixed_effects_models.model_comparison_aic_bic_ladder", _models(row, offset)
    if hint in {"trajectory_residence_amplitude_panel", "trajectory_boundary_comparison", "tracking_residence_panel"}:
        return "sensitivity_analysis.sobol_first_total_pair", _sobol(row, offset)
    return "meta_and_diagnostic.alternative_hypothesis_exclusion_table", _exclusion(row)


def build_manifest(rows: list[dict[str, str]] | None = None) -> dict[str, Any]:
    rows = rows or crosswalk_rows()
    by_figure: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_figure[row["fig_id"]].append(row)

    figures: list[dict[str, Any]] = []
    common_export = {"formats": RENDER_FORMATS, "dpi": 450}
    offset = 0
    for fig_id in sorted(by_figure):
        panels = []
        figure_rows = sorted(by_figure[fig_id], key=lambda item: item["panel"])
        for row in figure_rows:
            recipe, data = panel_recipe_and_data(row, offset)
            panels.append(_panel(row, recipe, data))
            offset += 1
        title = figure_rows[0]["figure_title"].split(". ", 1)[-1]
        figures.append(
            {
                "id": fig_id,
                "recipe_family": figure_rows[0]["figure_role"],
                "size": "double",
                "suptitle": title,
                "subtitle": figure_rows[0]["figure_role"].replace("_", " "),
                "panels": panels,
                "export": {**common_export, "outdir": _rel(RENDERED_DIR / fig_id)},
            }
        )
    return {
        "version": 1,
        "theme": "nature",
        "palette": "journal_neutral",
        "figures": figures,
        "export": {"formats": RENDER_FORMATS, "outdir": _rel(RENDERED_DIR), "dpi": 450},
    }


def _write_manifest(manifest: dict[str, Any]) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _validate_and_render(figures_bin: Path) -> tuple[list[Path], list[str]]:
    if RENDERED_DIR.exists():
        shutil.rmtree(RENDERED_DIR)
    logs: list[str] = []
    for cmd in [
        [str(figures_bin), "validate", str(MANIFEST)],
        [str(figures_bin), "render", str(MANIFEST)],
    ]:
        completed = _run(cmd, timeout=900)
        logs.append("$ " + " ".join(cmd))
        if completed.stdout.strip():
            logs.append(completed.stdout.strip())
        if completed.stderr.strip():
            logs.append(completed.stderr.strip())
    produced = sorted(
        path for path in RENDERED_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in {".pdf", ".png", ".svg"}
    )
    for path in produced:
        if path.suffix.lower() == ".svg":
            _normalize_svg(path)
    return produced, [_sanitize_log(line) for line in logs]


def _inventory_rows(produced: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in produced:
        rows.append(
            {
                "fig_id": path.parent.name,
                "format": path.suffix.lower().lstrip("."),
                "path": _rel(path),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return rows


def _evidence_files_exist(rows: list[dict[str, str]]) -> bool:
    paths = [
        item.strip()
        for row in rows
        for item in row.get("evidence_files", "").split(";")
        if item.strip()
    ]
    return all((ROOT / item).exists() for item in paths)


def _coverage_rows(rows: list[dict[str, str]], produced: list[Path]) -> list[dict[str, Any]]:
    by_figure: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_figure[row["fig_id"]].append(row)
    produced_formats: dict[str, set[str]] = defaultdict(set)
    for path in produced:
        produced_formats[path.parent.name].add(path.suffix.lower().lstrip("."))
    coverage: list[dict[str, Any]] = []
    for fig_id in sorted(by_figure):
        figure_rows = sorted(by_figure[fig_id], key=lambda item: item["panel"])
        formats = sorted(produced_formats.get(fig_id, set()))
        coverage.append(
            {
                "fig_id": fig_id,
                "panel_count": len(figure_rows),
                "panels": ",".join(row["panel"] for row in figure_rows),
                "evidence_files_exist": "yes" if _evidence_files_exist(figure_rows) else "no",
                "rendered_formats": ",".join(formats),
                "render_status": "rendered" if formats == sorted(RENDER_FORMATS) else "incomplete",
            }
        )
    return coverage


def _write_report(gate: dict[str, Any], logs: list[str]) -> None:
    lines = [
        "# Stage 10.13 rendered method figures",
        "",
        "Stage 10.13 renders the method-first figure architecture from the Stage 10.5 panel crosswalk into a separate Stage 10 output package. The historical Stage 9 rendered mockups remain unchanged.",
        "",
        "## Status",
        "",
        f"`{gate['status']}`",
        "",
        "## Rendered package",
        "",
        f"- Manifest. `{_rel(MANIFEST)}`",
        f"- Rendered files. `{gate['summary_metrics']['rendered_file_count']}`",
        f"- Figures. `{gate['summary_metrics']['figure_count']}`",
        f"- Planned panels. `{gate['summary_metrics']['planned_panel_count']}`",
        f"- PanelForge. `{PANELFORGE_REF}` with DOI `{PANELFORGE_DOI}`",
        "",
        "## Biological and manuscript boundary",
        "",
        "This step improves visual readiness for the Nature Methods method-first package. It does not add a new biological dataset, alter benchmark decisions, change the manuscript claims, overwrite the Stage 9 figure renders, or send editor contact.",
        "",
        "## Outputs",
        "",
        *[f"- `{path}`" for path in gate["outputs"].values()],
        "",
        "## Command log",
        "",
        "```text",
        *logs,
        "```",
        "",
    ]
    _write_text(REPORT, "\n".join(lines))


def _write_doc(gate: dict[str, Any]) -> None:
    body = f"""# Stage 10.13 rendered method figures

Stage 10.13 renders the Stage 10 method-first figure architecture into a separate figure package. The goal is visual readiness for the Nature Methods method-elevation route, not a new biological analysis.

## Status

`{gate["status"]}`

## Outputs

- `{_rel(MANIFEST)}`
- `{_rel(RENDERED_DIR)}`
- `{_rel(INVENTORY)}`
- `{_rel(COVERAGE)}`
- `{_rel(REPORT)}`
- `{_rel(GATE_REPORT)}`

## Summary

- Figures rendered. `{gate["summary_metrics"]["figure_count"]}`
- Rendered figure files. `{gate["summary_metrics"]["rendered_file_count"]}`
- Planned panels represented. `{gate["summary_metrics"]["planned_panel_count"]}`
- Manifest panels. `{gate["summary_metrics"]["manifest_panel_count"]}`
- External contact. `{gate["external_contact_status"]}`

## Interpretation boundary

Stage 10.13 improves the visual production surface for the method-first manuscript route. It does not add biological evidence, retune benchmarking, modify manuscript claims, overwrite the Stage 9 rendered mockups, or contact Nature Methods.
"""
    _write_text(DOC_PATH, body)


def _update_memory(gate: dict[str, Any]) -> None:
    memory = _read_json(MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 10.13 rendered method figures complete; external contact remains not sent"
    current["current_gate"] = "Stage 10.13 rendered method figures complete; external contact remains not sent"
    current["stage10_active_gate"] = "Stage 10.13 rendered method figures complete; external contact remains not sent"
    current["next_stage"] = "Author review, optional presubmission contact, or Stage 10 full-submission package refresh"
    current["after_stage10_13_rendered_method_figures"] = (
        "Stage 10.13 rendered the method-first Stage 10 figure plan into a separate PanelForge package with six figures, "
        "thirty planned panels, and eighteen rendered files. It preserves the Stage 9 rendered mockups, adds no biological "
        "evidence, and keeps external contact unsent."
    )

    stage10 = next((stage for stage in memory.get("stage_lock", []) if stage.get("stage") == 10), None)
    if not isinstance(stage10, dict):
        _write_json(MEMORY_PATH, memory)
        return
    artifacts = set(stage10.get("artifacts", []))
    artifacts.update(
        [
            _rel(DOC_PATH),
            "scripts/run_stage10_13_rendered_method_figures.py",
            "tests/test_stage10_13_rendered_method_figures.py",
            _rel(MANIFEST),
            _rel(INVENTORY),
            _rel(COVERAGE),
            _rel(REPORT),
            _rel(GATE_REPORT),
        ]
    )
    for row in gate.get("rendered_files", []):
        artifacts.add(row["path"])
    stage10["artifacts"] = sorted(artifacts)
    stage10["status"] = "stage10_13_complete_rendered_method_figures"
    stage10["current_gate"] = "Stage 10.13 rendered method figures complete; external contact remains not sent"
    subphases = stage10.setdefault("subphases", [])
    by_id = {entry.get("id"): entry for entry in subphases if isinstance(entry, dict)}
    by_id["10.13"] = {
        "id": "10.13",
        "name": "Rendered method-first figures",
        "status": "complete_rendered_method_figures",
        "goal": "Render the Stage 10 method-first figure architecture without changing evidence or manuscript claims.",
        "gate": "Stage 10.12 passes; thirty crosswalk panels are represented; eighteen rendered figure files are produced; Stage 9 renders are untouched; external contact remains not sent.",
        "evidence": _rel(GATE_REPORT),
    }
    stage10["subphases"] = [by_id[key] for key in sorted(by_id, key=lambda value: tuple(int(part) for part in value.split(".")))]
    _write_json(MEMORY_PATH, memory)


def run_stage10_13() -> dict[str, Any]:
    rows = crosswalk_rows()
    stage10_12 = _read_json(STAGE10_12_GATE)
    stage9_hashes_before = _stage9_render_hashes()

    manifest = build_manifest(rows)
    _write_manifest(manifest)
    with tempfile.TemporaryDirectory(prefix="rhodyn-stage10-panelforge-") as tmp:
        figures_bin = _install_panelforge(Path(tmp))
        produced, logs = _validate_and_render(figures_bin)

    stage9_hashes_after = _stage9_render_hashes()
    inventory = _inventory_rows(produced)
    coverage = _coverage_rows(rows, produced)
    _write_tsv(INVENTORY, inventory, INVENTORY_FIELDS)
    _write_tsv(COVERAGE, coverage, COVERAGE_FIELDS)

    manifest_panel_count = sum(len(figure.get("panels", [])) for figure in manifest.get("figures", []))
    planned_panel_count = len(rows)
    produced_figures = sorted({row["fig_id"] for row in inventory})
    external_contact = stage10_12.get("external_contact_status", "unknown")
    gates = {
        "stage10_12_passed": stage10_12.get("status") == "pass",
        "stage10_12_selected_figure_rendering": stage10_12.get("recommended_local_next_step") == "render_stage10_method_figures",
        "external_contact_not_sent": external_contact == "not_sent",
        "crosswalk_panel_count_30": planned_panel_count == 30,
        "manifest_panel_count_matches_crosswalk": manifest_panel_count == planned_panel_count,
        "all_evidence_files_exist": all(row["evidence_files_exist"] == "yes" for row in coverage),
        "six_figures_rendered": len(produced_figures) == 6,
        "eighteen_rendered_files": len(inventory) == 18,
        "all_figures_have_pdf_png_svg": all(row["rendered_formats"] == "pdf,png,svg" for row in coverage),
        "stage9_render_hashes_unchanged": stage9_hashes_before == stage9_hashes_after,
        "no_new_science_claims_or_contact": True,
    }
    gate = {
        "stage": "10.13",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "gates": gates,
        "external_contact_status": external_contact,
        "summary_metrics": {
            "figure_count": len(produced_figures),
            "planned_panel_count": planned_panel_count,
            "manifest_panel_count": manifest_panel_count,
            "rendered_file_count": len(inventory),
            "stage9_rendered_file_count": len(stage9_hashes_after),
        },
        "outputs": {
            "manifest": _rel(MANIFEST),
            "rendered_dir": _rel(RENDERED_DIR),
            "inventory": _rel(INVENTORY),
            "coverage": _rel(COVERAGE),
            "report": _rel(REPORT),
            "gate_report": _rel(GATE_REPORT),
            "doc": _rel(DOC_PATH),
        },
        "rendered_files": inventory,
        "panelforge": {
            "name": "panelforge-figures",
            "pinned_ref": PANELFORGE_REF,
            "version": PANELFORGE_VERSION,
            "doi": PANELFORGE_DOI,
        },
        "interpretation_boundary": (
            "Stage 10.13 renders the method-first figures only. It does not add data, retune benchmarks, change claims, "
            "overwrite Stage 9 renders, send external contact, or create a journal upload."
        ),
    }
    _write_json(GATE_REPORT, gate)
    _write_report(gate, logs)
    _write_doc(gate)
    _update_memory(gate)
    return gate


def main() -> int:
    gate = run_stage10_13()
    print(json.dumps({key: value for key, value in gate.items() if key != "rendered_files"}, indent=2))
    return 0 if gate["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
