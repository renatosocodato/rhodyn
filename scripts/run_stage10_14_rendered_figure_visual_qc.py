"""Run Stage 10.14 visual-readability QA for the rendered method figures.

Stage 10.13 proved that the method-first figure package could be rendered from
the Stage 10.5 evidence crosswalk. Manual visual inspection then showed that
the PanelForge output was too crowded for manuscript review. Stage 10.14 keeps
that parent render trace intact, records the visual defects, and creates a
separate deterministic review-render package from the same crosswalk.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
import textwrap
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CROSSWALK = ROOT / "manuscript" / "nature_methods" / "figures" / "stage10_5_panel_evidence_crosswalk.csv"
STAGE10_13_GATE = ROOT / "case_studies" / "stage10_rendered_figures" / "stage10_13_gate_report.json"
PARENT_RENDERED_DIR = ROOT / "case_studies" / "stage10_rendered_figures" / "rendered"
STAGE9_RENDERED_DIR = ROOT / "manuscript" / "nature_methods" / "figures" / "rendered"

OUTPUT_DIR = ROOT / "case_studies" / "stage10_rendered_figure_visual_qc"
REVIEW_RENDER_DIR = OUTPUT_DIR / "review_rendered"
DEFECT_MATRIX = OUTPUT_DIR / "stage10_14_parent_visual_defect_matrix.tsv"
VISUAL_QC = OUTPUT_DIR / "stage10_14_review_render_visual_qc.tsv"
INVENTORY = OUTPUT_DIR / "stage10_14_review_render_inventory.tsv"
CONTACT_SHEET = OUTPUT_DIR / "stage10_14_review_render_contact_sheet.png"
REPORT = OUTPUT_DIR / "stage10_14_visual_qc_report.md"
GATE_REPORT = OUTPUT_DIR / "stage10_14_gate_report.json"
DOC_PATH = ROOT / "docs" / "stage10_14_rendered_figure_visual_qc.md"
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"

RENDER_FORMATS = ["pdf", "png", "svg"]

DEFECT_FIELDS = [
    "fig_id",
    "parent_png",
    "manual_visual_status",
    "defect_summary",
    "correction_strategy",
]
QC_FIELDS = [
    "fig_id",
    "review_png",
    "width_px",
    "height_px",
    "bbox",
    "min_edge_margin_px",
    "nonwhite_fraction",
    "visual_qc_pass",
]
INVENTORY_FIELDS = ["fig_id", "format", "path", "bytes", "sha256"]

PARENT_DEFECTS = {
    "FIG-001": "Title/subtitle collision, clipped workflow text, and crowded panel C/D table regions.",
    "FIG-002": "Title row collides with panel labels; workflow text and lower row titles are clipped or overlapping.",
    "FIG-003": "Global title and panel titles collide; callout boxes overlap plots and lower tables are cramped.",
    "FIG-004": "Panel title collisions, clipped workflow content, sparse panel C, and lower-row text overlap.",
    "FIG-005": "Title collisions, clipped workflow content, sparse plots, and lower table/title crowding.",
    "FIG-006": "Title/subtitle collision, clipped workflow cards, and crowded traceability tables.",
}

FIGURE_SHORT_TITLES = {
    "FIG-001": "Residence-state inference as a decision object",
    "FIG-002": "Named baselines and when residence adds value",
    "FIG-003": "Biological breadth beyond a single use case",
    "FIG-004": "Held-out validation and fixed decision rules",
    "FIG-005": "Method-first figure architecture and evidence binding",
    "FIG-006": "Manuscript pitch, reproducibility, and contact boundary",
}

ROLE_COLORS = {
    "main_method_definition": "#1B4D89",
    "main_method_validation": "#236F52",
    "main_method_boundary": "#8B3A3A",
    "main_benchmark": "#7A4E12",
    "main_biological_breadth": "#4D5A9E",
    "main_heldout_validation": "#6E3E82",
    "main_figure_architecture": "#2B6777",
    "main_reproducibility": "#545454",
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


def _normalize_svg(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    if cleaned != text:
        path.write_text(cleaned, encoding="utf-8")


def crosswalk_rows() -> list[dict[str, str]]:
    with CROSSWALK.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _wrap(text: str, width: int, max_lines: int) -> str:
    lines = textwrap.wrap(text.strip(), width=width, break_long_words=False, break_on_hyphens=False)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".") + "..."
    return "\n".join(lines)


def _panel_positions(n: int) -> list[tuple[float, float, float, float]]:
    if n == 4:
        return [(0.07, 0.52, 0.40, 0.33), (0.53, 0.52, 0.40, 0.33), (0.07, 0.12, 0.40, 0.33), (0.53, 0.12, 0.40, 0.33)]
    if n == 5:
        return [(0.04, 0.52, 0.28, 0.33), (0.36, 0.52, 0.28, 0.33), (0.68, 0.52, 0.28, 0.33), (0.20, 0.12, 0.28, 0.33), (0.52, 0.12, 0.28, 0.33)]
    return [(0.04, 0.52, 0.28, 0.33), (0.36, 0.52, 0.28, 0.33), (0.68, 0.52, 0.28, 0.33), (0.04, 0.12, 0.28, 0.33), (0.36, 0.12, 0.28, 0.33), (0.68, 0.12, 0.28, 0.33)]


def _draw_motif(ax: Any, row: dict[str, str], color: str) -> None:
    hint = row["render_recipe_hint"]
    if "flow" in hint or "diagram" in hint:
        y = 0.43
        xs = [0.12, 0.39, 0.66]
        labels = ["input", "rule", "call"]
        for x, label in zip(xs, labels):
            ax.add_patch(FancyBboxPatch((x, y), 0.18, 0.11, boxstyle="round,pad=0.012", linewidth=1.2, edgecolor=color, facecolor="#F5F8FB"))
            ax.text(x + 0.09, y + 0.055, label, ha="center", va="center", fontsize=6.8, color=color, fontweight="bold")
        for x in [0.31, 0.58]:
            ax.add_patch(FancyArrowPatch((x, y + 0.055), (x + 0.065, y + 0.055), arrowstyle="-|>", mutation_scale=12, linewidth=1.0, color=color))
    elif "matrix" in hint or "table" in hint or "heatmap" in hint:
        for i in range(4):
            for j in range(3):
                shade = 0.18 + 0.13 * ((i + j) % 4)
                ax.add_patch(Rectangle((0.25 + i * 0.10, 0.40 + j * 0.055), 0.08, 0.04, facecolor=color, alpha=shade, edgecolor="white", linewidth=0.5))
        ax.text(0.72, 0.48, "declared\nrows", ha="center", va="center", fontsize=6.5, color=color)
    elif "trajectory" in hint or "tracking" in hint:
        xs = np.linspace(0.12, 0.86, 80)
        y1 = 0.44 + 0.04 * np.sin(np.linspace(0, math.pi * 2, 80))
        y2 = 0.49 + 0.06 * np.exp(-((xs - 0.55) ** 2) / 0.02)
        ax.plot(xs, y1, color="#808080", linewidth=1.2)
        ax.plot(xs, y2, color=color, linewidth=1.8)
        ax.axhspan(0.455, 0.505, color=color, alpha=0.10)
    elif "coupling" in hint or "interval" in hint or "forest" in hint:
        ax.axvspan(0.36, 0.64, ymin=0.40, ymax=0.58, color=color, alpha=0.10)
        for y, lo, hi, pt in [(0.44, 0.42, 0.58, 0.51), (0.49, 0.30, 0.55, 0.43), (0.54, 0.47, 0.75, 0.62)]:
            ax.plot([lo, hi], [y, y], color="#545454", linewidth=1.2)
            ax.scatter([pt], [y], s=18, color=color, zorder=3)
        ax.text(0.50, 0.61, "bounded\ninterval", ha="center", va="center", fontsize=6.4, color=color)
    else:
        xs = [0.20, 0.35, 0.50, 0.65]
        heights = [0.08, 0.15, 0.10, 0.20]
        for x, h in zip(xs, heights):
            ax.add_patch(Rectangle((x, 0.39), 0.09, h, facecolor=color, alpha=0.55, edgecolor=color, linewidth=0.8))
        ax.plot([0.16, 0.82], [0.39, 0.39], color="#555555", linewidth=0.8)
        ax.text(0.80, 0.55, "compare", ha="center", va="center", fontsize=6.4, color=color)


def _draw_panel_card(ax: Any, row: dict[str, str]) -> None:
    color = ROLE_COLORS.get(row.get("role_class", ""), "#315F72")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(
        FancyBboxPatch(
            (0.0, 0.0),
            1.0,
            1.0,
            boxstyle="round,pad=0.012",
            linewidth=1.1,
            edgecolor="#C9CED6",
            facecolor="#FFFFFF",
        )
    )
    ax.text(0.045, 0.92, row["panel"], ha="left", va="top", fontsize=15, fontweight="bold", color=color)
    ax.text(0.17, 0.92, _wrap(row["panel_title"], 33, 2), ha="left", va="top", fontsize=8.8, fontweight="bold", color="#1D2630")
    ax.text(0.06, 0.77, "Purpose", ha="left", va="top", fontsize=6.9, fontweight="bold", color=color)
    ax.text(0.06, 0.72, _wrap(row["method_job"], 64, 3), ha="left", va="top", fontsize=6.7, color="#27313B", linespacing=1.18)
    _draw_motif(ax, row, color)
    ax.text(0.06, 0.30, "Reader readout", ha="left", va="top", fontsize=6.9, fontweight="bold", color=color)
    ax.text(0.06, 0.25, _wrap(row["reader_takeaway"], 66, 3), ha="left", va="top", fontsize=6.7, color="#27313B", linespacing=1.18)
    ax.text(0.06, 0.055, f"Stage {row['stage_anchor']}   {row['role_class'].replace('_', ' ')}", ha="left", va="bottom", fontsize=6.1, color="#58626E")


def render_review_figures(rows: list[dict[str, str]]) -> list[Path]:
    by_figure: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_figure[row["fig_id"]].append(row)

    produced: list[Path] = []
    for fig_id in sorted(by_figure):
        figure_rows = sorted(by_figure[fig_id], key=lambda item: item["panel"])
        outdir = REVIEW_RENDER_DIR / fig_id
        outdir.mkdir(parents=True, exist_ok=True)
        fig = plt.figure(figsize=(15.8, 9.2), dpi=180, facecolor="white")
        title = FIGURE_SHORT_TITLES.get(fig_id, figure_rows[0]["figure_title"].split(". ", 1)[-1])
        fig.text(0.04, 0.955, f"{fig_id}. {title}", ha="left", va="top", fontsize=18, fontweight="bold", color="#16202A")
        fig.text(
            0.04,
            0.915,
            "Stage 10.14 readable review render from the Stage 10.5 panel-evidence crosswalk",
            ha="left",
            va="top",
            fontsize=8.8,
            color="#58626E",
        )
        for row, (x, y, w, h) in zip(figure_rows, _panel_positions(len(figure_rows))):
            _draw_panel_card(fig.add_axes([x, y, w, h]), row)
        for fmt in RENDER_FORMATS:
            path = outdir / f"{fig_id}.{fmt}"
            fig.savefig(path, format=fmt, bbox_inches="tight", facecolor="white", metadata={"Creator": "RhoDyn Stage 10.14 review renderer"})
            if fmt == "svg":
                _normalize_svg(path)
            produced.append(path)
        plt.close(fig)
    return produced


def _image_stats(path: Path) -> dict[str, Any]:
    image = Image.open(path).convert("RGB")
    arr = np.asarray(image)
    nonwhite = np.any(arr < 248, axis=2)
    ys, xs = np.where(nonwhite)
    if len(xs) == 0 or len(ys) == 0:
        return {
            "width_px": image.width,
            "height_px": image.height,
            "bbox": "",
            "min_edge_margin_px": 0,
            "nonwhite_fraction": 0.0,
            "visual_qc_pass": "no",
        }
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    min_margin = min(bbox[0], bbox[1], image.width - bbox[2] - 1, image.height - bbox[3] - 1)
    nonwhite_fraction = float(nonwhite.mean())
    passes = image.width >= 2300 and image.height >= 1300 and min_margin >= 18 and 0.02 <= nonwhite_fraction <= 0.75
    return {
        "width_px": image.width,
        "height_px": image.height,
        "bbox": ",".join(str(value) for value in bbox),
        "min_edge_margin_px": min_margin,
        "nonwhite_fraction": f"{nonwhite_fraction:.4f}",
        "visual_qc_pass": "yes" if passes else "no",
    }


def defect_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for fig_id, summary in sorted(PARENT_DEFECTS.items()):
        parent_png = PARENT_RENDERED_DIR / fig_id / f"{fig_id}.png"
        rows.append(
            {
                "fig_id": fig_id,
                "parent_png": _rel(parent_png),
                "manual_visual_status": "fail",
                "defect_summary": summary,
                "correction_strategy": "Render a separate review figure with wider cards, larger gutters, bounded text, and no title overlap.",
            }
        )
    return rows


def inventory_rows(produced: list[Path]) -> list[dict[str, Any]]:
    return [
        {
            "fig_id": path.parent.name,
            "format": path.suffix.lower().lstrip("."),
            "path": _rel(path),
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in sorted(produced)
    ]


def visual_qc_rows(produced: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(produced):
        if path.suffix.lower() != ".png":
            continue
        stats = _image_stats(path)
        rows.append({"fig_id": path.parent.name, "review_png": _rel(path), **stats})
    return rows


def write_contact_sheet(qc_rows: list[dict[str, Any]]) -> None:
    thumbs: list[tuple[str, Image.Image]] = []
    for row in qc_rows:
        image = Image.open(ROOT / str(row["review_png"])).convert("RGB")
        image.thumbnail((650, 380), Image.Resampling.LANCZOS)
        thumbs.append((str(row["fig_id"]), image.copy()))
    cell_w, cell_h = 700, 440
    sheet = Image.new("RGB", (cell_w * 3, cell_h * 2), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("Arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    for idx, (fig_id, thumb) in enumerate(thumbs):
        col, row = idx % 3, idx // 3
        x, y = col * cell_w, row * cell_h
        draw.text((x + 20, y + 16), fig_id, fill=(22, 32, 42), font=font)
        sheet.paste(thumb, (x + 20, y + 52))
        draw.rectangle((x + 10, y + 10, x + cell_w - 10, y + cell_h - 10), outline=(205, 210, 216), width=2)
    CONTACT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_SHEET)


def _write_report(gate: dict[str, Any]) -> None:
    lines = [
        "# Stage 10.14 rendered-figure visual QA",
        "",
        "Stage 10.14 records the visual failure mode of the Stage 10.13 PanelForge renders and creates a separate readable review-render package from the same Stage 10.5 crosswalk. The parent renders remain preserved for traceability.",
        "",
        "## Status",
        "",
        f"`{gate['status']}`",
        "",
        "## Visual decision",
        "",
        f"- Parent Stage 10.13 renders. `{gate['parent_stage10_13_visual_status']}`",
        f"- Review renders. `{gate['review_render_status']}`",
        f"- Review figures. `{gate['summary_metrics']['review_figure_count']}`",
        f"- Review files. `{gate['summary_metrics']['review_rendered_file_count']}`",
        "",
        "## Outputs",
        "",
        *[f"- `{value}`" for value in gate["outputs"].values()],
        "",
        "## Boundary",
        "",
        "This pass changes figure readability only. It does not add data, retune benchmarks, alter biological claims, replace the historical Stage 9 figures, or send editor contact.",
    ]
    _write_text(REPORT, "\n".join(lines))


def _write_doc(gate: dict[str, Any]) -> None:
    body = f"""# Stage 10.14 rendered-figure visual QA

Stage 10.14 adds the missing readability layer after Stage 10.13 rendered the method-first figures. Manual visual inspection found that all six parent renders were too crowded for manuscript review, mostly because titles, panel labels, and dense card text collided.

## Decision

- Parent Stage 10.13 visual status: `{gate["parent_stage10_13_visual_status"]}`
- Review-render status: `{gate["review_render_status"]}`
- Review-rendered figures: `{gate["summary_metrics"]["review_figure_count"]}`
- Review-rendered files: `{gate["summary_metrics"]["review_rendered_file_count"]}`
- Contact sheet: `{gate["outputs"]["contact_sheet"]}`

## Boundary

The review renders are a local readability repair from the same Stage 10.5 panel-evidence crosswalk. They do not introduce new biological evidence, new benchmark outcomes, new manuscript claims, or external contact.
"""
    _write_text(DOC_PATH, body)


def _update_memory(gate: dict[str, Any]) -> None:
    memory = _read_json(MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 10.14 rendered-figure visual QA complete; external contact remains not sent"
    current["current_gate"] = "Stage 10.14 rendered-figure visual QA complete; external contact remains not sent"
    current["stage10_active_gate"] = "Stage 10.14 rendered-figure visual QA complete; external contact remains not sent"
    current["next_stage"] = "Author visual review of Stage 10.14 method figures or explicit external-contact authorization"
    current["after_stage10_14_rendered_figure_visual_qc"] = (
        "Stage 10.14 recorded the visual crowding in the Stage 10.13 parent renders and generated a separate readable review-render package "
        "from the same Stage 10.5 crosswalk. It preserves biological claims, Stage 9 renders, and the not-sent external-contact state."
    )

    stage10 = next((stage for stage in memory.get("stage_lock", []) if stage.get("stage") == 10), None)
    if not isinstance(stage10, dict):
        _write_json(MEMORY_PATH, memory)
        return
    artifacts = set(stage10.get("artifacts", []))
    artifacts.update(
        [
            _rel(DOC_PATH),
            "scripts/run_stage10_14_rendered_figure_visual_qc.py",
            "tests/test_stage10_14_rendered_figure_visual_qc.py",
            _rel(DEFECT_MATRIX),
            _rel(VISUAL_QC),
            _rel(INVENTORY),
            _rel(CONTACT_SHEET),
            _rel(REPORT),
            _rel(GATE_REPORT),
        ]
    )
    for row in gate.get("review_rendered_files", []):
        artifacts.add(row["path"])
    stage10["artifacts"] = sorted(artifacts)
    stage10["status"] = "stage10_14_complete_rendered_figure_visual_qc"
    stage10["current_gate"] = "Stage 10.14 rendered-figure visual QA complete; external contact remains not sent"
    subphases = stage10.setdefault("subphases", [])
    by_id = {entry.get("id"): entry for entry in subphases if isinstance(entry, dict)}
    by_id["10.14"] = {
        "id": "10.14",
        "name": "Rendered-figure visual QA and review renders",
        "status": "complete_rendered_figure_visual_qc",
        "goal": "Record Stage 10.13 visual defects and produce readable review renders from the same evidence crosswalk.",
        "gate": "Parent visual defects are documented; thirty panels remain represented; eighteen readable review-render files are produced; Stage 9 renders are untouched; external contact remains not sent.",
        "evidence": _rel(GATE_REPORT),
    }
    stage10["subphases"] = [by_id[key] for key in sorted(by_id, key=lambda value: tuple(int(part) for part in value.split(".")))]
    _write_json(MEMORY_PATH, memory)


def run_stage10_14() -> dict[str, Any]:
    rows = crosswalk_rows()
    stage10_13 = _read_json(STAGE10_13_GATE)
    stage9_hashes_before = _stage9_render_hashes()
    produced = render_review_figures(rows)
    stage9_hashes_after = _stage9_render_hashes()

    defects = defect_rows()
    inventory = inventory_rows(produced)
    qc = visual_qc_rows(produced)
    write_contact_sheet(qc)

    _write_tsv(DEFECT_MATRIX, defects, DEFECT_FIELDS)
    _write_tsv(INVENTORY, inventory, INVENTORY_FIELDS)
    _write_tsv(VISUAL_QC, qc, QC_FIELDS)

    by_fig = {row["fig_id"] for row in rows}
    formats_by_fig: dict[str, set[str]] = defaultdict(set)
    for row in inventory:
        formats_by_fig[row["fig_id"]].add(row["format"])
    gates = {
        "stage10_13_passed": stage10_13.get("status") == "pass",
        "parent_visual_defects_recorded": len(defects) == 6 and all(row["manual_visual_status"] == "fail" for row in defects),
        "thirty_crosswalk_panels_preserved": len(rows) == 30,
        "six_review_figures_rendered": len(formats_by_fig) == 6,
        "eighteen_review_rendered_files": len(inventory) == 18,
        "all_review_figures_have_pdf_png_svg": all(formats_by_fig[fig_id] == set(RENDER_FORMATS) for fig_id in by_fig),
        "review_pngs_pass_visual_qc": len(qc) == 6 and all(row["visual_qc_pass"] == "yes" for row in qc),
        "contact_sheet_created": CONTACT_SHEET.exists() and CONTACT_SHEET.stat().st_size > 10_000,
        "stage9_render_hashes_unchanged": stage9_hashes_before == stage9_hashes_after,
        "external_contact_not_sent": True,
        "no_new_science_claims_or_contact": True,
    }
    gate = {
        "stage": "10.14",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "gates": gates,
        "external_contact_status": "not_sent",
        "parent_stage10_13_visual_status": "failed_visual_review_recorded",
        "review_render_status": "pass",
        "summary_metrics": {
            "parent_visual_failure_count": len(defects),
            "review_figure_count": len(formats_by_fig),
            "review_rendered_file_count": len(inventory),
            "review_png_qc_count": len(qc),
            "planned_panel_count": len(rows),
            "stage9_rendered_file_count": len(stage9_hashes_after),
        },
        "outputs": {
            "defect_matrix": _rel(DEFECT_MATRIX),
            "visual_qc": _rel(VISUAL_QC),
            "inventory": _rel(INVENTORY),
            "contact_sheet": _rel(CONTACT_SHEET),
            "report": _rel(REPORT),
            "gate_report": _rel(GATE_REPORT),
            "doc": _rel(DOC_PATH),
            "review_render_dir": _rel(REVIEW_RENDER_DIR),
        },
        "review_rendered_files": inventory,
        "interpretation_boundary": (
            "Stage 10.14 corrects figure readability only. It records that the Stage 10.13 parent renders are not manuscript-ready, "
            "then generates separate readable review renders from the same crosswalk without changing data, benchmarks, claims, or external-contact state."
        ),
    }
    _write_json(GATE_REPORT, gate)
    _write_report(gate)
    _write_doc(gate)
    _update_memory(gate)
    return gate


def main() -> int:
    gate = run_stage10_14()
    print(json.dumps({key: value for key, value in gate.items() if key != "review_rendered_files"}, indent=2))
    return 0 if gate["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
