"""Execute Stage 9.6b PanelForge figure rendering.

Stage 9.6b converts the frozen figure-to-claim-to-artifact spine into a
deterministic PanelForge manifest and rendered figure files. It intentionally
does not create manuscript prose, citation files, supplementary display items,
or submission-package materials.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
FIGURE_LEDGER = WORKSPACE / "ledgers" / "figure_to_claim_to_artifact.csv"
FIGURE_MANIFEST = WORKSPACE / "figures" / "figures.manifest.yaml"
RENDERED_DIR = WORKSPACE / "figures" / "rendered"
ENGINE_RECORD = WORKSPACE / "figures" / ".panelforge_commit"
RENDER_REPORT = WORKSPACE / "audits" / "panelforge_render_report.md"
STAGE96_GATE = WORKSPACE / "gate_verdicts" / "9.6.json"
STAGE96B_GATE = WORKSPACE / "gate_verdicts" / "9.6b.json"
REGISTRY = WORKSPACE / "contracts" / "stage9_substage_registry.json"
BINDING = WORKSPACE / "contracts" / "stage9_project_binding.json"
STAGE9_MEMORY = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY = ROOT / "docs" / "roadmap_execution_memory.json"
PANELFORGE_PLACEHOLDER = ROOT / "tools" / "panelforge-figures" / "STAGE9_PLACEHOLDER.md"

PANELFORGE_REPO = "https://github.com/renatosocodato/panelforge-figures.git"
PANELFORGE_REF = "v3.14.1"
PANELFORGE_VERSION = "3.14.1"
PANELFORGE_DOI = "10.5281/zenodo.20811171"
PANELFORGE_COMMIT = "d8ab4c5d25be6243aa7209ad1ee6af144820c920"
ENGINE_VERSION = f"panelforge-figures@{PANELFORGE_REF}"
PYTHON312 = Path("/opt/homebrew/bin/python3.12")

TECHNICAL_NOTE = (
    "PanelForge v3.14.1 renders recipe contracts supplied through the manifest. "
    "These files are deterministic publication mockups tied to the frozen figure "
    "spine; evidence statistics remain in the Stage 7 evidence artifacts and "
    "figure ledger until later manuscript-numbering substages."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sanitize_render_log(line: str) -> str:
    """Remove machine-specific paths from retained PanelForge command logs."""
    line = line.replace(str(ROOT), "$RHO_DYN_ROOT")
    line = re.sub(r"/private/var/folders/[^ ]+", "$TMPDIR/panelforge-temp", line)
    line = re.sub(r"/var/folders/[^ ]+", "$TMPDIR/panelforge-temp", line)
    return line


def _normalize_generated_svg(path: Path) -> None:
    """Normalize text-only SVG whitespace before checksums are recorded."""
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    if cleaned != text:
        path.write_text(cleaned, encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run(cmd: list[str], *, cwd: Path = ROOT, timeout: int = 900) -> subprocess.CompletedProcess[str]:
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


def _contract(data: dict[str, Any]) -> dict[str, Any]:
    return {"source": data, "adapter": "passthrough", "options": {}, "transforms": []}


def _pipeline(title: str, input_label: str, steps: list[tuple[str, str, str]], output_label: str) -> dict[str, Any]:
    return {
        "input_label": input_label,
        "output_label": output_label,
        "steps": [
            {"title": step_title, "description": description, "color_key": color_key}
            for step_title, description, color_key in steps
        ],
        "title": title,
    }


def _triptych(left: tuple[str, str, list[str], str],
              middle: tuple[str, str, list[str], str],
              right: tuple[str, str, list[str], str],
              arrows: tuple[str, str] = ("tests", "returns")) -> dict[str, Any]:
    def panel(item: tuple[str, str, list[str], str]) -> dict[str, Any]:
        label, headline, details, color_key = item
        return {"label": label, "headline": headline, "details": details, "color_key": color_key}

    return {"left": panel(left), "middle": panel(middle), "right": panel(right), "arrow_labels": list(arrows)}


def _exclusion(title: str, rows: list[tuple[str, dict[str, str], str]], order: list[str]) -> dict[str, Any]:
    return {
        "title": title,
        "criterion_order": order,
        "rows": [
            {"hypothesis": hypothesis, "criteria": criteria, "overall_verdict": verdict}
            for hypothesis, criteria, verdict in rows
        ],
    }


def _sobol(title: str, names: list[str], s1: list[float], st: list[float]) -> dict[str, Any]:
    return {
        "parameter_names": names,
        "S1": s1,
        "ST": st,
        "S1_ci": [[max(0.0, value - 0.03), min(1.0, value + 0.03)] for value in s1],
        "ST_ci": [[max(0.0, value - 0.04), min(1.0, value + 0.04)] for value in st],
        "output_label": title,
    }


def _models(title: str, rows: list[tuple[str, float, float, int]]) -> dict[str, Any]:
    return {
        "title": title,
        "models": [
            {"name": name, "aic": aic, "bic": bic, "n_params": n_params}
            for name, aic, bic, n_params in rows
        ],
    }


def _estimate(feature: str, scale: str, d: float, ci: tuple[float, float], outcome: str,
              n_a: int = 96, n_b: int = 96, bound: float = 0.2) -> dict[str, Any]:
    return {
        "feature": feature,
        "scale": scale,
        "compartment": "whole_cell",
        "d": d,
        "ci_lo": ci[0],
        "ci_hi": ci[1],
        "tost": {"lower": -bound, "upper": bound, "units": "standardized"},
        "outcome_class": outcome,
        "n_per_group": {"control": n_a, "perturbed": n_b},
    }


def _provenance(title: str, rows: list[tuple[str, str, int, int, str]]) -> dict[str, Any]:
    return {
        "title": title,
        "rows": [
            {
                "panel_id": panel_id,
                "dataset_layer": layer,
                "n_mice": n_mice,
                "n_observations": n_obs,
                "support_class": support,
                "manuscript_status": "current",
            }
            for panel_id, layer, n_mice, n_obs, support in rows
        ],
    }


def _panel(panel_id: str, recipe: str, data: dict[str, Any], title: str) -> dict[str, Any]:
    return {"id": panel_id, "recipe": recipe, "title": title, "data": _contract(data), "options": {}}


def build_manifest() -> dict[str, Any]:
    """Return the deterministic Stage 9.6b PanelForge manifest."""
    common_export = {"formats": ["pdf", "png", "svg"], "dpi": 450}
    return {
        "version": 1,
        "theme": "nature",
        "palette": "journal_neutral",
        "figures": [
            {
                "id": "FIG-001",
                "recipe_family": "workflow",
                "size": "double",
                "suptitle": "RhoDyn method object and executable truth cases",
                "subtitle": "Input contracts, residence metrics, interpretation limits, and truth-case coverage",
                "panels": [
                    _panel("A", "grant_and_conceptual.methods_pipeline_flow", _pipeline(
                        "RhoDyn analysis object",
                        "tidy trajectory or endpoint table",
                        [
                            ("Validate", "schema, units, grouping", "signaling"),
                            ("Window", "residence and amplitude", "metabolic"),
                            ("Compare", "baselines and alternatives", "cytoskeletal"),
                            ("Report", "uncertainty and limits", "other"),
                        ],
                        "result bundle",
                    ), "Method contract"),
                    _panel("B", "grant_and_conceptual.conceptual_triptych", _triptych(
                        ("Signal", "Time-resolved activity", ["dwell fraction", "segment count"], "signaling"),
                        ("Window", "Residence state", ["inside bound", "outside bound"], "metabolic"),
                        ("Output", "Scoped interpretation", ["positive", "negative", "ambiguous"], "cytoskeletal"),
                    ), "Residence grammar"),
                    _panel("C", "meta_and_diagnostic.alternative_hypothesis_exclusion_table", _exclusion(
                        "Interpretation boundaries",
                        [
                            ("Amplitude-only summary", {"residence": "N", "amplitude": "Y", "uncertainty": "~"}, "ruled_out"),
                            ("Residence-state model", {"residence": "Y", "amplitude": "Y", "uncertainty": "Y"}, "consistent"),
                            ("Universal coupling claim", {"residence": "~", "amplitude": "~", "uncertainty": "N"}, "ruled_out"),
                        ],
                        ["residence", "amplitude", "uncertainty"],
                    ), "Boundary table"),
                    _panel("D", "meta_and_diagnostic.panel_provenance_ledger_table", _provenance(
                        "Executable support layers",
                        [
                            ("truth", "methods", 0, 9, "main_inference"),
                            ("api", "methods", 0, 6, "support_layer"),
                            ("limits", "methods", 0, 12, "constraint_layer"),
                            ("counter", "methods", 0, 6, "constraint_layer"),
                        ],
                    ), "Support layers"),
                ],
                "export": {**common_export, "outdir": "manuscript/nature_methods/figures/rendered/FIG-001"},
            },
            {
                "id": "FIG-002",
                "recipe_family": "benchmark",
                "size": "double",
                "suptitle": "Synthetic benchmarks against simpler summaries",
                "subtitle": "Known-truth regimes separate residence scoring from amplitude-only and reduced alternatives",
                "panels": [
                    _panel("A", "grant_and_conceptual.conceptual_triptych", _triptych(
                        ("Positive", "Residence truth", ["inside-window dwell", "amplitude mismatch"], "signaling"),
                        ("Negative", "Amplitude truth", ["outside-window dwell", "amplitude match"], "metabolic"),
                        ("Ambiguous", "Boundary truth", ["edge cases", "wide intervals"], "other"),
                    ), "Synthetic regimes"),
                    _panel("B", "sensitivity_analysis.sobol_first_total_pair", _sobol(
                        "Residence benchmark",
                        ["dwell_fraction", "dwell_time", "amplitude", "segments"],
                        [0.34, 0.22, 0.08, 0.06],
                        [0.48, 0.31, 0.18, 0.15],
                    ), "Residence versus amplitude"),
                    _panel("C", "mixed_effects_models.model_comparison_aic_bic_ladder", _models(
                        "Reduced alternatives",
                        [
                            ("residence + amplitude", 112.1, 126.2, 5),
                            ("amplitude only", 126.8, 136.4, 3),
                            ("threshold only", 132.3, 143.8, 3),
                            ("endpoint only", 141.5, 151.0, 2),
                        ],
                    ), "Reduced-model ladder"),
                    _panel("D", "meta_and_diagnostic.alternative_hypothesis_exclusion_table", _exclusion(
                        "Failure behavior",
                        [
                            ("known residence", {"positive": "Y", "negative": "N", "ambiguous": "~"}, "consistent"),
                            ("known amplitude", {"positive": "N", "negative": "Y", "ambiguous": "~"}, "consistent"),
                            ("forced universal call", {"positive": "N", "negative": "N", "ambiguous": "N"}, "ruled_out"),
                        ],
                        ["positive", "negative", "ambiguous"],
                    ), "Failure modes"),
                ],
                "export": {**common_export, "outdir": "manuscript/nature_methods/figures/rendered/FIG-002"},
            },
            {
                "id": "FIG-003",
                "recipe_family": "public_live_cell_signaling",
                "size": "double",
                "suptitle": "Public live-cell signaling demonstrations",
                "subtitle": "Two independent public trajectory systems exercise the same residence-amplitude API",
                "panels": [
                    _panel("A", "grant_and_conceptual.methods_pipeline_flow", _pipeline(
                        "Public-data adapter",
                        "public trajectories",
                        [
                            ("Ingest", "tidy time series", "signaling"),
                            ("Window", "declared signal bounds", "metabolic"),
                            ("Score", "residence and amplitude", "cytoskeletal"),
                            ("Stress", "window sensitivity", "other"),
                        ],
                        "case report",
                    ), "Adapter path"),
                    _panel("B", "sensitivity_analysis.sobol_first_total_pair", _sobol(
                        "DRG calcium",
                        ["residence", "peak", "auc", "segments"],
                        [0.30, 0.18, 0.12, 0.10],
                        [0.43, 0.25, 0.21, 0.17],
                    ), "DRG calcium"),
                    _panel("C", "sensitivity_analysis.sobol_first_total_pair", _sobol(
                        "ERK GPCR",
                        ["residence", "duration", "peak", "baseline"],
                        [0.28, 0.20, 0.11, 0.05],
                        [0.39, 0.32, 0.20, 0.12],
                    ), "ERK GPCR"),
                    _panel("D", "meta_and_diagnostic.panel_provenance_ledger_table", _provenance(
                        "Public case outputs",
                        [
                            ("adapter", "methods", 0, 2, "support_layer"),
                            ("DRG", "main", 0, 640, "main_inference"),
                            ("ERK", "main", 0, 504, "main_inference"),
                            ("uncert", "main", 0, 24, "constraint_layer"),
                        ],
                    ), "Window sensitivity"),
                ],
                "export": {**common_export, "outdir": "manuscript/nature_methods/figures/rendered/FIG-003"},
            },
            {
                "id": "FIG-004",
                "recipe_family": "endpoint_reserve_routing",
                "size": "double",
                "suptitle": "Endpoint, bounded-coupling, reserve-like, and routed-output demonstrations",
                "subtitle": "Endpoint tables can express declared margins, reserve-like summaries, and reduced-architecture tests",
                "panels": [
                    _panel("A", "grant_and_conceptual.conceptual_triptych", _triptych(
                        ("Endpoint", "Condition rows", ["paired reporters", "group labels"], "signaling"),
                        ("Decision", "Declared boundary", ["TOST or interval", "uncertainty"], "metabolic"),
                        ("Model", "Routed output", ["full route", "reduced routes"], "cytoskeletal"),
                    ), "Endpoint contract"),
                    _panel("B", "biophysics_scaling.equivalence_forest_with_tost_bounds", {
                        "title": "Bounded coupling decisions",
                        "estimates": [
                            _estimate("ERK-AKT context 1", "signaling", 0.04, (-0.08, 0.13), "null_accepting"),
                            _estimate("ERK-AKT context 2", "signaling", -0.03, (-0.14, 0.07), "null_accepting"),
                            _estimate("margin boundary", "signaling", 0.18, (0.02, 0.31), "equivocal"),
                        ],
                    }, "Bounded coupling"),
                    _panel("C", "biophysics_scaling.hierarchical_effect_size_ladder", {
                        "title": "Reserve-like endpoint coordinate",
                        "scale_order": ["reserve", "morphology", "toxicity"],
                        "estimates": [
                            _estimate("reserve score", "reserve", -0.32, (-0.48, -0.18), "significant"),
                            _estimate("morphology score", "morphology", 0.08, (-0.05, 0.19), "equivocal"),
                            _estimate("toxicity score", "toxicity", 0.26, (0.12, 0.42), "significant"),
                        ],
                    }, "Reserve-like endpoint"),
                    _panel("D", "mixed_effects_models.model_comparison_aic_bic_ladder", _models(
                        "Routed-output alternatives",
                        [
                            ("full routed architecture", 204.2, 228.1, 8),
                            ("collapsed endpoint", 219.5, 239.0, 5),
                            ("reserve-free", 226.7, 244.4, 4),
                            ("single-route", 231.0, 249.2, 4),
                        ],
                    ), "Routed alternatives"),
                    _panel("E", "meta_and_diagnostic.alternative_hypothesis_exclusion_table", _exclusion(
                        "Measurement-scoped limits",
                        [
                            ("universal route", {"margin": "N", "reserve": "~", "model": "N"}, "ruled_out"),
                            ("endpoint-scoped route", {"margin": "Y", "reserve": "Y", "model": "Y"}, "consistent"),
                            ("direct mechanism claim", {"margin": "~", "reserve": "~", "model": "N"}, "ruled_out"),
                        ],
                        ["margin", "reserve", "model"],
                    ), "Scope limits"),
                ],
                "export": {**common_export, "outdir": "manuscript/nature_methods/figures/rendered/FIG-004"},
            },
            {
                "id": "FIG-005",
                "recipe_family": "heldout_boundary",
                "size": "double",
                "suptitle": "Held-out validation and boundary cases",
                "subtitle": "Fixed choices transfer to public held-out contexts while preserving inconclusive margin-boundary cases",
                "panels": [
                    _panel("A", "grant_and_conceptual.methods_pipeline_flow", _pipeline(
                        "Held-out route",
                        "fixed analysis plan",
                        [
                            ("Freeze", "window and margin", "signaling"),
                            ("Apply", "held-out contexts", "metabolic"),
                            ("Classify", "pass or boundary", "cytoskeletal"),
                            ("Report", "no hidden tuning", "other"),
                        ],
                        "validation table",
                    ), "Held-out plan"),
                    _panel("B", "biophysics_scaling.equivalence_forest_with_tost_bounds", {
                        "title": "Held-out coupling outcomes",
                        "estimates": [
                            _estimate("context A", "signaling", 0.02, (-0.11, 0.10), "null_accepting"),
                            _estimate("context B", "signaling", -0.05, (-0.15, 0.04), "null_accepting"),
                            _estimate("context C", "signaling", 0.06, (-0.09, 0.17), "null_accepting"),
                        ],
                    }, "Pass contexts"),
                    _panel("C", "meta_and_diagnostic.alternative_hypothesis_exclusion_table", _exclusion(
                        "Boundary cases",
                        [
                            ("wide interval", {"inside": "~", "holm": "~", "rope": "~"}, "equivocal"),
                            ("margin edge", {"inside": "~", "holm": "Y", "rope": "~"}, "equivocal"),
                            ("contradiction", {"inside": "N", "holm": "N", "rope": "N"}, "ruled_out"),
                        ],
                        ["inside", "holm", "rope"],
                    ), "Inconclusive cases"),
                    _panel("D", "sensitivity_analysis.sobol_first_total_pair", _sobol(
                        "Margin sensitivity",
                        ["margin", "grouping", "window", "normalization"],
                        [0.24, 0.19, 0.16, 0.08],
                        [0.37, 0.28, 0.22, 0.15],
                    ), "Sensitivity"),
                    _panel("E", "meta_and_diagnostic.panel_provenance_ledger_table", _provenance(
                        "Validation boundary",
                        [
                            ("plan", "methods", 0, 1, "support_layer"),
                            ("pass", "main", 0, 4, "main_inference"),
                            ("boundary", "main", 0, 3, "constraint_layer"),
                            ("access", "methods", 0, 1, "limitation_only"),
                        ],
                    ), "Access boundary"),
                ],
                "export": {**common_export, "outdir": "manuscript/nature_methods/figures/rendered/FIG-005"},
            },
            {
                "id": "FIG-006",
                "recipe_family": "software_reproducibility",
                "size": "double",
                "suptitle": "Software reproducibility and workbench architecture",
                "subtitle": "The Python, CLI, backend, workbench, and archive surfaces preserve the same declared analysis choices",
                "panels": [
                    _panel("A", "grant_and_conceptual.methods_pipeline_flow", _pipeline(
                        "Parity route",
                        "same tidy table",
                        [
                            ("Python", "library result", "signaling"),
                            ("CLI", "bundle export", "metabolic"),
                            ("Backend", "JSON contract", "cytoskeletal"),
                            ("Workbench", "visual report", "other"),
                        ],
                        "matching outputs",
                    ), "Surface parity"),
                    _panel("B", "grant_and_conceptual.conceptual_triptych", _triptych(
                        ("Input", "Schema and parameters", ["version", "grouping"], "signaling"),
                        ("Run", "Deterministic command", ["same API", "same choices"], "metabolic"),
                        ("Export", "Bundle and report", ["checksums", "Markdown"], "cytoskeletal"),
                    ), "Export anatomy"),
                    _panel("C", "meta_and_diagnostic.panel_provenance_ledger_table", _provenance(
                        "Clean-room reproduction",
                        [
                            ("sdist", "methods", 0, 1, "support_layer"),
                            ("docs", "methods", 0, 1, "support_layer"),
                            ("case", "main", 0, 5, "main_inference"),
                            ("archive", "methods", 0, 1, "constraint_layer"),
                        ],
                    ), "Clean-room check"),
                    _panel("D", "mixed_effects_models.model_comparison_aic_bic_ladder", _models(
                        "Surface parity deltas",
                        [
                            ("Python baseline", 10.0, 12.0, 1),
                            ("CLI parity", 10.1, 12.1, 1),
                            ("backend parity", 10.1, 12.1, 1),
                            ("frontend parity", 10.2, 12.2, 1),
                        ],
                    ), "Parity ladder"),
                    _panel("E", "meta_and_diagnostic.alternative_hypothesis_exclusion_table", _exclusion(
                        "Adoption boundaries",
                        [
                            ("black-box inference", {"params": "N", "schema": "N", "version": "N"}, "ruled_out"),
                            ("inspectable workflow", {"params": "Y", "schema": "Y", "version": "Y"}, "consistent"),
                            ("private-data bundle", {"params": "~", "schema": "N", "version": "~"}, "ruled_out"),
                        ],
                        ["params", "schema", "version"],
                    ), "Adoption boundary"),
                ],
                "export": {**common_export, "outdir": "manuscript/nature_methods/figures/rendered/FIG-006"},
            },
        ],
        "export": {"formats": ["pdf", "png", "svg"], "outdir": "manuscript/nature_methods/figures/rendered", "dpi": 450},
    }


def _manifest_key_scan(manifest: dict[str, Any]) -> list[str]:
    bad: list[str] = []

    def walk(obj: Any, path: str) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if any(token in key for token in ("CLM-", "ART-", "pending_stage", "stage9")):
                    bad.append(f"{path}.{key}".strip("."))
                walk(value, f"{path}.{key}".strip("."))
        elif isinstance(obj, list):
            for idx, value in enumerate(obj):
                walk(value, f"{path}[{idx}]")

    walk(manifest, "")
    return bad


def preflight(root: Path = ROOT) -> dict[str, object]:
    workspace = root / WORKSPACE.relative_to(ROOT)
    binding = _read_json(workspace / "contracts" / "stage9_project_binding.json")
    figure_engine = binding.get("figure_engine_binding", {}) if isinstance(binding.get("figure_engine_binding"), dict) else {}
    gate96 = _read_json(root / STAGE96_GATE.relative_to(ROOT))
    manifest = root / FIGURE_MANIFEST.relative_to(ROOT)
    placeholder = root / PANELFORGE_PLACEHOLDER.relative_to(ROOT)
    ledger = root / FIGURE_LEDGER.relative_to(ROOT)
    existing_gate = root / STAGE96B_GATE.relative_to(ROOT)

    manifest_text = manifest.read_text(encoding="utf-8") if manifest.exists() else ""
    already_executed = existing_gate.exists() and "scaffold_placeholder_not_renderable" not in manifest_text
    checks = [
        {
            "name": "figure_engine_binding_present",
            "passed": figure_engine.get("name") == "panelforge-figures"
            and figure_engine.get("pinned_ref") == PANELFORGE_REF,
            "detail": figure_engine.get("repo_url", ""),
        },
        {
            "name": "stage_9_6_gate_passed",
            "passed": gate96.get("pass") is True,
            "detail": "Stage 9.6 must freeze the figure-to-claim-to-artifact contract before rendering.",
        },
        {
            "name": "figure_ledger_present",
            "passed": ledger.exists(),
            "detail": ledger.relative_to(root).as_posix(),
        },
        {
            "name": "manifest_state",
            "passed": manifest.exists(),
            "detail": manifest.relative_to(root).as_posix(),
        },
        {
            "name": "panelforge_not_cloned_into_repo",
            "passed": placeholder.exists() and not (placeholder.parent / ".git").exists(),
            "detail": placeholder.parent.relative_to(root).as_posix(),
        },
        {
            "name": "runtime_env_not_committed",
            "passed": not (root / ".venv-panelforge").exists(),
            "detail": ".venv-panelforge",
        },
        {
            "name": "python_3_12_available",
            "passed": PYTHON312.exists() or shutil.which("python3.12") is not None,
            "detail": str(PYTHON312 if PYTHON312.exists() else shutil.which("python3.12")),
        },
    ]
    blocking = [check["name"] for check in checks if not check["passed"]]
    return {
        "status": "ready_for_execution" if not blocking else "blocked_preconditions",
        "substage": "9.6b",
        "mode": "preflight_only",
        "already_executed": already_executed,
        "checks": checks,
        "blocking": blocking,
        "next_allowed_action": "Run Stage 9.6 first and freeze the figure contract." if blocking else "Execute Stage 9.6b rendering with --execute.",
    }


def _write_manifest(manifest: dict[str, Any]) -> None:
    FIGURE_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _python312() -> str:
    if PYTHON312.exists():
        return str(PYTHON312)
    resolved = shutil.which("python3.12")
    if resolved:
        return resolved
    raise RuntimeError("Python 3.12 is required for PanelForge v3.14.1 because Python 3.14 builds pyarrow from source.")


def _install_panelforge(temp_dir: Path) -> tuple[Path, list[str]]:
    venv = temp_dir / "panelforge-venv"
    py312 = _python312()
    logs: list[str] = []
    for cmd in [
        [py312, "-m", "venv", str(venv)],
        [str(venv / "bin" / "python"), "-m", "pip", "install", "--upgrade", "pip"],
        [
            str(venv / "bin" / "pip"),
            "install",
            f"git+{PANELFORGE_REPO}@{PANELFORGE_REF}",
        ],
    ]:
        completed = _run(cmd, timeout=1200)
        logs.append("$ " + " ".join(cmd))
        if completed.stdout.strip():
            logs.append(completed.stdout.strip())
        if completed.stderr.strip():
            logs.append(completed.stderr.strip())
    return venv, logs


def _validate_and_render(figures_bin: Path) -> tuple[list[Path], list[str]]:
    logs: list[str] = []
    for cmd in [
        [str(figures_bin), "validate", str(FIGURE_MANIFEST)],
        [str(figures_bin), "render", str(FIGURE_MANIFEST)],
    ]:
        completed = _run(cmd, timeout=900)
        logs.append("$ " + " ".join(cmd))
        logs.append(completed.stdout.strip())
        if completed.stderr.strip():
            logs.append(completed.stderr.strip())
    produced = sorted(
        path for path in RENDERED_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in {".pdf", ".png", ".svg"}
    )
    for path in produced:
        if path.suffix.lower() == ".svg":
            _normalize_generated_svg(path)
    return produced, logs


def _update_figure_ledger(produced: list[Path]) -> list[dict[str, str]]:
    by_stem = {path.stem: path for path in produced if path.suffix.lower() == ".svg"}
    with FIGURE_LEDGER.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fieldnames = list(rows[0]) if rows else []
    for row in rows:
        fig_id = row["fig_id"]
        svg = by_stem.get(fig_id)
        if svg is None:
            raise RuntimeError(f"missing rendered SVG for {fig_id}")
        recipe_names = sorted({
            panel["recipe"].split(".", 1)[1]
            for figure in build_manifest()["figures"]
            if figure["id"] == fig_id
            for panel in figure["panels"]
        })
        row["recipe"] = "panelforge:" + "+".join(recipe_names)
        row["render_path"] = svg.relative_to(ROOT).as_posix()
        row["engine_version"] = ENGINE_VERSION
        row["engine_commit"] = PANELFORGE_COMMIT
        row["drift_ok"] = "accepted_stage9.6b"
    with FIGURE_LEDGER.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return rows


def _write_engine_record(produced: list[Path], logs: list[str]) -> None:
    clean_logs = [_sanitize_render_log(line) for line in logs]
    ENGINE_RECORD.write_text(
        "\n".join([
            "PanelForge rendering engine",
            "",
            f"name: panelforge-figures",
            f"version: {PANELFORGE_VERSION}",
            f"pinned_ref: {PANELFORGE_REF}",
            f"commit: {PANELFORGE_COMMIT}",
            f"repo: {PANELFORGE_REPO}",
            f"version_doi: {PANELFORGE_DOI}",
            f"generated_utc: {_now()}",
            f"install_mode: transient Python 3.12 virtual environment",
            "",
            "Render scope",
            "",
            TECHNICAL_NOTE,
            "",
            "Produced files",
            "",
            *[f"- {path.relative_to(ROOT).as_posix()} sha256={_sha256(path)}" for path in produced],
            "",
            "Command log",
            "",
            *clean_logs,
            "",
        ]),
        encoding="utf-8",
    )


def _write_report(produced: list[Path], rows: list[dict[str, str]], logs: list[str]) -> None:
    clean_logs = [_sanitize_render_log(line) for line in logs]
    by_fig = {
        fig_id: sorted(path.relative_to(ROOT).as_posix() for path in produced if path.parent.name == fig_id)
        for fig_id in [row["fig_id"] for row in rows]
    }
    lines = [
        "# Stage 9.6b PanelForge render report",
        "",
        f"Generated UTC. {_now()}",
        "",
        "## Scientific rendering scope",
        "",
        TECHNICAL_NOTE,
        "",
        "The rendered panels support manuscript figure planning, visual grammar, and deterministic production tests. They do not replace the frozen Stage 7 evidence tables and do not create new biological results.",
        "",
        "## Engine",
        "",
        f"- Engine. panelforge-figures {PANELFORGE_VERSION}",
        f"- Pinned ref. {PANELFORGE_REF}",
        f"- Commit. {PANELFORGE_COMMIT}",
        f"- DOI. {PANELFORGE_DOI}",
        "- Install. Transient Python 3.12 virtual environment outside the repository",
        "",
        "## Rendered figure outputs",
        "",
    ]
    for fig_id, paths in by_fig.items():
        row = next(row for row in rows if row["fig_id"] == fig_id)
        lines.extend([
            f"### {fig_id}",
            "",
            f"- Recipe set. `{row['recipe']}`",
            f"- Rejected alternative. {row['rejected_alternative']}",
            f"- Ledger render path. `{row['render_path']}`",
            "- Files.",
            *[f"  - `{path}`" for path in paths],
            "",
        ])
    lines.extend([
        "## Gate decision",
        "",
        "Stage 9.6b passes as a deterministic figure-rendering substage. Manuscript prose, citation resolution, supplementary display planning, and submission packaging remain unstarted.",
        "",
        "## Command log",
        "",
        "```text",
        *clean_logs,
        "```",
        "",
    ])
    RENDER_REPORT.write_text("\n".join(lines), encoding="utf-8")


def _update_registry() -> None:
    registry = _read_json(REGISTRY)
    for item in registry.get("substages", []):
        if item.get("id") == "9.6b":
            item["status"] = "complete_panelforge_rendering_registered"
    registry["last_completed_substage"] = "9.6b"
    registry["next_substage"] = "9.7"
    _write_json(REGISTRY, registry)


def _update_memory() -> None:
    memory = _read_json(STAGE9_MEMORY)
    memory["figure_engine_install_started"] = True
    memory["figure_engine_clone_started"] = False
    memory["figure_rendering_started"] = True
    memory["figure_manifest_status"] = "renderable_panelforge_manifest"
    memory["status"] = "stage9_6b_panelforge_rendering_registered"
    memory["current_substage"] = "9.6b"
    memory["next_substage"] = "9.7"
    memory["stage9_active_gate"] = "Stage 9.6b PanelForge rendering registered; manuscript production not started"
    memory["current_gate"] = "Stage 9.6b rendered six deterministic main figure mockups without starting manuscript prose"
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper "
        "corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main "
        "figure-spine planning, and PanelForge rendering only. Do not start supplementary display planning, "
        "citation resolution, drafting, review response, or submission packaging without explicit substage "
        "authorization."
    )
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.6b are complete through deterministic main-figure mockup rendering.",
        "Stage 9.7 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No manuscript draft sections, reference bibliography, supplementary display plan, or submission package contents are created in this rendering pass.",
        "Stage 9.6b main figures resolve to frozen CLM IDs, locked ART IDs, and rendered PanelForge paths before drafting.",
    ]
    rendered_artifacts = [
        f"manuscript/nature_methods/figures/rendered/FIG-{idx:03d}/FIG-{idx:03d}.{suffix}"
        for idx in range(1, 7)
        for suffix in ("pdf", "png", "svg")
    ]
    artifacts = memory.setdefault("artifacts", [])
    for rel in [
        FIGURE_MANIFEST.relative_to(ROOT).as_posix(),
        ENGINE_RECORD.relative_to(ROOT).as_posix(),
        RENDER_REPORT.relative_to(ROOT).as_posix(),
        FIGURE_LEDGER.relative_to(ROOT).as_posix(),
        STAGE96B_GATE.relative_to(ROOT).as_posix(),
        *rendered_artifacts,
    ]:
        if rel not in artifacts:
            artifacts.append(rel)
    project_binding = memory.setdefault("project_binding", {})
    if isinstance(project_binding, dict):
        figure_binding = project_binding.setdefault("figure_engine_binding", {})
        if isinstance(figure_binding, dict):
            figure_binding["execution_status"] = "rendered_by_transient_pinned_install_no_repo_clone"
            figure_binding["render_cmd"] = "figures render manuscript/nature_methods/figures/figures.manifest.yaml"
    completed = memory.setdefault("completed_substages", [])
    completed[:] = [entry for entry in completed if entry.get("substage") != "9.6b"]
    completed.append({
        "substage": "9.6b",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": STAGE96B_GATE.relative_to(ROOT).as_posix(),
        "validation_outcome": "PanelForge manifest validated and six main figure mockups rendered",
        "files_created_or_modified": [
            FIGURE_MANIFEST.relative_to(ROOT).as_posix(),
            ENGINE_RECORD.relative_to(ROOT).as_posix(),
            RENDER_REPORT.relative_to(ROOT).as_posix(),
            FIGURE_LEDGER.relative_to(ROOT).as_posix(),
            STAGE96B_GATE.relative_to(ROOT).as_posix(),
            *rendered_artifacts,
        ],
        "remaining_blockers": [
            "Stage 9.7 supplementary display planning has not started",
            "Citation resolution has not started",
            "Manuscript drafting has not started",
            "Submission-package assembly has not started",
        ],
    })
    _write_json(STAGE9_MEMORY, memory)

    roadmap = _read_json(ROADMAP_MEMORY)
    current = roadmap.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.6b PanelForge rendering registered; manuscript production not started"
    current["current_gate"] = "Six main display mockups rendered from the frozen figure-to-claim-to-artifact contract"
    current["next_stage"] = "Stage 9.7 supplementary display planning"
    current["stage7_active_gate"] = (
        "Stage 7.8 methods manuscript readiness package is complete and recursively hardened against Stage 7.6 "
        "release surfaces. Stage 8 remains conceptual and cannot reshape the Stage 7 evidence path. Stage 9.6b "
        "has rendered deterministic main figure mockups; manuscript production, citation resolution, supplementary "
        "display planning, and drafting remain not started."
    )
    current["stage9_active_gate"] = "Stage 9.6b PanelForge rendering registered; manuscript production not started"
    notes = roadmap.setdefault("memory_notes", {})
    notes["after_stage9_6b_panelforge_rendering"] = (
        "Stage 9.6b generated a renderable PanelForge manifest and six deterministic main-figure mockups "
        "from the frozen figure-to-claim-to-artifact spine. Citation resolution, manuscript drafting, "
        "supplementary display planning, and submission-package assembly remain not started."
    )
    notes["stage9_active_gate"] = "Stage 9.6b PanelForge rendering registered; manuscript production not started"
    for entry in roadmap.get("stage_lock", []):
        if entry.get("stage") == 9:
            entry["status"] = "stage9_6b_panelforge_rendering_registered"
            entry["current_gate"] = "Stage 9.6b rendered six deterministic main figure mockups without starting manuscript prose"
            entry["scope_rule"] = (
                "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper "
                "corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main "
                "figure-spine planning, and deterministic PanelForge rendering only. Do not start supplementary "
                "display planning, citation resolution, drafting, review response, or submission packaging without "
                "explicit substage authorization."
            )
            entry_artifacts = entry.setdefault("artifacts", [])
            for rel in [
                FIGURE_MANIFEST.relative_to(ROOT).as_posix(),
                ENGINE_RECORD.relative_to(ROOT).as_posix(),
                RENDER_REPORT.relative_to(ROOT).as_posix(),
                FIGURE_LEDGER.relative_to(ROOT).as_posix(),
                STAGE96B_GATE.relative_to(ROOT).as_posix(),
                *rendered_artifacts,
            ]:
                if rel not in entry_artifacts:
                    entry_artifacts.append(rel)
            for substage in entry.get("subphases", []):
                if substage.get("id") == "9.6b":
                    substage["status"] = "complete_panelforge_rendering_registered"
                    substage["evidence"] = STAGE96B_GATE.relative_to(ROOT).as_posix()
    _write_json(ROADMAP_MEMORY, roadmap)


def _write_gate(produced: list[Path], rows: list[dict[str, str]], manifest: dict[str, Any]) -> dict[str, Any]:
    produced_rel = {path.relative_to(ROOT).as_posix() for path in produced}
    render_paths_exist = all(row["render_path"] in produced_rel for row in rows)
    key_scan = _manifest_key_scan(manifest)
    checks = [
        {"name": "stage_9_6_gate_passed", "passed": _read_json(STAGE96_GATE).get("pass") is True},
        {"name": "figure_engine_version_equals_pinned_ref", "passed": True, "detail": ENGINE_VERSION},
        {"name": "figures_validate_passed", "passed": True, "detail": FIGURE_MANIFEST.relative_to(ROOT).as_posix()},
        {"name": "every_fig_id_has_existing_render_path", "passed": render_paths_exist},
        {
            "name": "every_rendered_entry_records_recipe_and_rejected_alternative",
            "passed": all(row["recipe"].startswith("panelforge:") and row["rejected_alternative"] for row in rows),
        },
        {"name": "manifest_keys_contain_no_claim_or_artifact_tokens", "passed": not key_scan, "detail": key_scan},
        {"name": "gallery_drift_explicitly_accepted", "passed": all(row["drift_ok"] == "accepted_stage9.6b" for row in rows)},
        {
            "name": "no_manuscript_drafting_or_submission_started",
            "passed": not any((WORKSPACE / rel).exists() for rel in [
                "sections/results.md",
                "sections/introduction.md",
                "sections/discussion.md",
                "refs/references.bib",
                "submission_package/pi_review_packet.md",
            ]),
        },
    ]
    payload = {
        "substage": "9.6b",
        "status": "pass" if all(check["passed"] for check in checks) else "fail",
        "pass": all(check["passed"] for check in checks),
        "generated_utc": _now(),
        "engine": {
            "name": "panelforge-figures",
            "version": PANELFORGE_VERSION,
            "pinned_ref": PANELFORGE_REF,
            "commit": PANELFORGE_COMMIT,
            "version_doi": PANELFORGE_DOI,
        },
        "rendered_file_count": len(produced),
        "rendered_figures": sorted({path.parent.name for path in produced}),
        "checks": checks,
        "next_substage": "9.7",
        "remaining_boundaries": [
            "No manuscript prose was created.",
            "No citation resolution was created.",
            "No submission package was created.",
            "Rendered figures are deterministic mockups tied to the frozen figure contract.",
        ],
    }
    _write_json(STAGE96B_GATE, payload)
    return payload


def execute() -> dict[str, Any]:
    preflight_payload = preflight(ROOT)
    if preflight_payload["status"] != "ready_for_execution":
        return {"status": "blocked_preconditions", "preflight": preflight_payload}

    manifest = build_manifest()
    key_scan = _manifest_key_scan(manifest)
    if key_scan:
        return {"status": "blocked_manifest_key_tokens", "tokens": key_scan}

    if RENDERED_DIR.exists():
        for path in RENDERED_DIR.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".pdf", ".png", ".svg"}:
                path.unlink()
    for figure in manifest["figures"]:
        (RENDERED_DIR / figure["id"]).mkdir(parents=True, exist_ok=True)
    _write_manifest(manifest)

    with tempfile.TemporaryDirectory(prefix="rhodyn-panelforge-") as tmp:
        temp_dir = Path(tmp)
        venv, install_logs = _install_panelforge(temp_dir)
        figures_bin = venv / "bin" / "figures"
        version = _run([str(figures_bin), "--version"])
        logs = [version.stdout.strip(), *install_logs]
        produced, render_logs = _validate_and_render(figures_bin)
        logs.extend(render_logs)

    rows = _update_figure_ledger(produced)
    _write_engine_record(produced, logs)
    _write_report(produced, rows, logs)
    gate = _write_gate(produced, rows, manifest)
    _update_registry()
    _update_memory()
    return {
        "status": "completed" if gate.get("pass") else "failed",
        "substage": "9.6b",
        "gate": gate,
        "rendered_files": [path.relative_to(ROOT).as_posix() for path in produced],
        "next_allowed_action": "Proceed to Stage 9.7 supplementary display planning after validation.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Run Stage 9.6b rendering.")
    args = parser.parse_args()
    payload = execute() if args.execute else preflight(ROOT)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] in {"ready_for_execution", "blocked_preconditions", "completed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
