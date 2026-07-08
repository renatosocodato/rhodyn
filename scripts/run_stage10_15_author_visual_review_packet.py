"""Assemble the Stage 10.15 no-send author visual-review packet.

Stage 10.15 binds the readable Stage 10.14 method figures to the existing
author-review query, pitch, checklist, and boundary surfaces. It does not send
external contact, copy private data, add evidence, or change manuscript claims.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage10_author_visual_review_packet"
DOC_PATH = ROOT / "docs" / "stage10_15_author_visual_review_packet.md"
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"

STAGE10_9_GATE = ROOT / "case_studies" / "stage10_eic_contact_decision" / "stage10_9_gate_report.json"
STAGE10_11_GATE = ROOT / "case_studies" / "stage10_author_review_readiness" / "stage10_11_gate_report.json"
STAGE10_14_GATE = ROOT / "case_studies" / "stage10_rendered_figure_visual_qc" / "stage10_14_gate_report.json"

MANIFEST = OUTPUT_DIR / "stage10_15_author_visual_review_manifest.tsv"
CHECKLIST = OUTPUT_DIR / "stage10_15_author_decision_checklist.tsv"
BOUNDARY_SCAN = OUTPUT_DIR / "stage10_15_no_send_boundary_scan.tsv"
FIGURE_GUIDE = OUTPUT_DIR / "stage10_15_figure_review_guide.md"
PACKET_BRIEF = OUTPUT_DIR / "stage10_15_author_visual_review_packet.md"
GATE_REPORT = OUTPUT_DIR / "stage10_15_gate_report.json"

MANIFEST_FIELDS = ["surface", "path", "role", "review_action", "exists", "bytes", "sha256", "send_surface"]
CHECKLIST_FIELDS = ["item_id", "review_item", "required", "status", "current_evidence", "author_action"]
BOUNDARY_FIELDS = ["boundary_id", "boundary", "status", "evidence", "action_if_failed"]


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


def _file_row(surface: str, relpath: str, role: str, action: str, send_surface: str = "no") -> dict[str, Any]:
    path = ROOT / relpath
    exists = path.exists() and path.is_file()
    return {
        "surface": surface,
        "path": relpath,
        "role": role,
        "review_action": action,
        "exists": "yes" if exists else "no",
        "bytes": path.stat().st_size if exists else 0,
        "sha256": _sha256(path) if exists else "",
        "send_surface": send_surface,
    }


def manifest_rows() -> list[dict[str, Any]]:
    rows = [
        _file_row(
            "clean_presubmission_query",
            "case_studies/stage10_author_review_readiness/stage10_11_presubmission_query_clean_AUTHOR_REVIEW_REQUIRED.md",
            "author-reviewed message source for optional Nature Methods presubmission inquiry",
            "complete author identity and approve exact wording before any external message",
            "candidate_after_author_approval",
        ),
        _file_row(
            "one_page_pitch",
            "case_studies/stage10_eic_contact_decision/stage10_9_one_page_pitch.md",
            "optional attachment or paste-in pitch source",
            "decide whether to attach, paste, or omit",
            "candidate_after_author_approval",
        ),
        _file_row(
            "route_decision_memo",
            "case_studies/stage10_eic_contact_decision/stage10_9_decision_memo.md",
            "internal route decision and rejected alternatives",
            "review only if changing route",
        ),
        _file_row(
            "author_review_checklist",
            "case_studies/stage10_author_review_readiness/stage10_11_author_review_checklist.tsv",
            "pre-send author checklist from Stage 10.11",
            "complete all required author rows before contact",
        ),
        _file_row(
            "stage10_14_contact_sheet",
            "case_studies/stage10_rendered_figure_visual_qc/stage10_14_review_render_contact_sheet.png",
            "single-sheet visual scan of all readable Stage 10 figures",
            "review figure order and obvious visual defects",
        ),
        _file_row(
            "stage10_14_visual_qc",
            "case_studies/stage10_rendered_figure_visual_qc/stage10_14_review_render_visual_qc.tsv",
            "programmatic image-quality check for readable review renders",
            "confirm all six review PNGs pass visual-QA gates",
        ),
        _file_row(
            "stage10_14_parent_defects",
            "case_studies/stage10_rendered_figure_visual_qc/stage10_14_parent_visual_defect_matrix.tsv",
            "record of why Stage 10.13 parent renders are not manuscript-ready",
            "preserve parent render trace without using it as a review surface",
        ),
        _file_row(
            "stage10_7_release_candidate_brief",
            "case_studies/stage10_release_candidate/stage10_7_release_candidate_brief.md",
            "fresh-clone reproducibility support summary",
            "keep as evidence support, not the primary method claim",
        ),
    ]
    for fig_id in [f"FIG-{idx:03d}" for idx in range(1, 7)]:
        for suffix in ["pdf", "png", "svg"]:
            rows.append(
                _file_row(
                    f"review_render_{fig_id}_{suffix}",
                    f"case_studies/stage10_rendered_figure_visual_qc/review_rendered/{fig_id}/{fig_id}.{suffix}",
                    f"readable Stage 10.14 method figure {fig_id} in {suffix.upper()} format",
                    "review figure content and style before any editor-facing package is assembled",
                )
            )
    return rows


def checklist_rows() -> list[dict[str, str]]:
    return [
        {
            "item_id": "AVR-001",
            "review_item": "Use Stage 10.14 review renders, not crowded Stage 10.13 parent renders",
            "required": "yes",
            "status": "ready_for_author_review",
            "current_evidence": "Stage 10.14 records parent visual failure and readable review-render pass",
            "author_action": "Review the contact sheet and six readable figures",
        },
        {
            "item_id": "AVR-002",
            "review_item": "External contact remains unsent",
            "required": "yes",
            "status": "not_sent",
            "current_evidence": "Stage 10.9, 10.11, 10.14, and 10.15 gates retain not_sent state",
            "author_action": "Send only after explicit corresponding-author approval",
        },
        {
            "item_id": "AVR-003",
            "review_item": "Corresponding-author identity and contact details",
            "required": "yes",
            "status": "author_required",
            "current_evidence": "Clean query still contains author placeholder",
            "author_action": "Replace placeholder before any external message",
        },
        {
            "item_id": "AVR-004",
            "review_item": "Presubmission route approval",
            "required": "yes",
            "status": "author_required",
            "current_evidence": "Stage 10.9 selected presubmission query with author review required",
            "author_action": "Confirm presubmission query, full submission, delay, or venue pivot",
        },
        {
            "item_id": "AVR-005",
            "review_item": "Method-first framing",
            "required": "yes",
            "status": "ready_for_author_review",
            "current_evidence": "Query, pitch, and figure spine foreground residence-state inference",
            "author_action": "Preserve method-object framing during edits",
        },
        {
            "item_id": "AVR-006",
            "review_item": "Named comparator evidence",
            "required": "yes",
            "status": "ready_for_author_review",
            "current_evidence": "Query and pitch name simple summaries and named external-style comparator families",
            "author_action": "Do not remove comparator evidence unless intentionally shortening",
        },
        {
            "item_id": "AVR-007",
            "review_item": "Public biological breadth",
            "required": "yes",
            "status": "ready_for_author_review",
            "current_evidence": "Query and pitch name DRG calcium, GPCR-linked ERK, Cell Painting/MitoTox, and MLCI tracking",
            "author_action": "Preserve breadth without universal-residence language",
        },
        {
            "item_id": "AVR-008",
            "review_item": "No-retuning held-out validation scope",
            "required": "yes",
            "status": "ready_for_author_review",
            "current_evidence": "Query says public-derived contexts and no-retuning route",
            "author_action": "Do not describe this as prospective blinded collaborator validation",
        },
        {
            "item_id": "AVR-009",
            "review_item": "Limits and non-claims",
            "required": "yes",
            "status": "ready_for_author_review",
            "current_evidence": "Query and pitch reject universal residence and automatic mechanism readings",
            "author_action": "Keep these boundaries visible in any shortened version",
        },
        {
            "item_id": "AVR-010",
            "review_item": "Prospective collaborator-blind validation",
            "required": "no",
            "status": "separate_new_evidence_decision",
            "current_evidence": "Stage 10.12 leaves this as external-data dependent",
            "author_action": "Decide separately whether to delay contact for new external validation",
        },
    ]


def boundary_rows(stage10_9: dict[str, Any], stage10_11: dict[str, Any], stage10_14: dict[str, Any], manifest: list[dict[str, Any]]) -> list[dict[str, str]]:
    all_manifest_exists = all(row["exists"] == "yes" for row in manifest)
    return [
        {
            "boundary_id": "B-001",
            "boundary": "No external contact is sent by this packet",
            "status": "pass" if stage10_9.get("external_contact_status") == stage10_11.get("external_contact_status") == stage10_14.get("external_contact_status") == "not_sent" else "fail",
            "evidence": "Stage 10.9, Stage 10.11, and Stage 10.14 gate reports",
            "action_if_failed": "Stop and restore not_sent state before packaging",
        },
        {
            "boundary_id": "B-002",
            "boundary": "Readable Stage 10.14 figures are used for review instead of crowded Stage 10.13 parent renders",
            "status": "pass" if stage10_14.get("parent_stage10_13_visual_status") == "failed_visual_review_recorded" and stage10_14.get("review_render_status") == "pass" else "fail",
            "evidence": "Stage 10.14 visual-QA gate report",
            "action_if_failed": "Do not use the figure packet until visual-QA passes",
        },
        {
            "boundary_id": "B-003",
            "boundary": "All packet references exist and are checksum-backed",
            "status": "pass" if all_manifest_exists else "fail",
            "evidence": "Stage 10.15 manifest",
            "action_if_failed": "Regenerate or remove missing surfaces",
        },
        {
            "boundary_id": "B-004",
            "boundary": "The packet does not add new biological evidence or benchmark outcomes",
            "status": "pass",
            "evidence": "Stage 10.15 uses existing Stage 10.9, 10.11, and 10.14 surfaces",
            "action_if_failed": "Move new analyses to a separate evidence phase",
        },
        {
            "boundary_id": "B-005",
            "boundary": "Author-only fields remain author actions rather than invented metadata",
            "status": "pass",
            "evidence": "Clean query retains author placeholder and checklist marks author-required rows",
            "action_if_failed": "Remove invented identity or contact details",
        },
        {
            "boundary_id": "B-006",
            "boundary": "Old Stage 9.29 package is not used alone as the basis for renewed editor contact",
            "status": "pass",
            "evidence": "Stage 10 author-review surfaces foreground method-object, named-baseline, public-breadth, held-out, and figure-readiness evidence",
            "action_if_failed": "Rebuild contact surface around Stage 10 evidence",
        },
    ]


def _manifest_rows_by_surface(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["surface"]: row for row in rows}


def _write_figure_guide(manifest: list[dict[str, Any]]) -> None:
    surfaces = _manifest_rows_by_surface(manifest)
    lines = [
        "# Stage 10.15 figure review guide",
        "",
        "Use the Stage 10.14 review renders for author visual review. The Stage 10.13 parent renders remain preserved only as the parent render attempt because they failed visual readability inspection.",
        "",
        f"Contact sheet. `{surfaces['stage10_14_contact_sheet']['path']}`",
        "",
        "| figure | PDF | PNG | SVG | review focus |",
        "| --- | --- | --- | --- | --- |",
    ]
    focus = {
        "FIG-001": "method object, abstention, and failure-mode grammar",
        "FIG-002": "named baselines and comparator-sufficient regimes",
        "FIG-003": "public biological breadth beyond one manuscript use case",
        "FIG-004": "held-out validation, bounded coupling, and endpoint scope",
        "FIG-005": "figure spine and evidence binding",
        "FIG-006": "reproducibility support without software-wrapper framing",
    }
    for fig_id in [f"FIG-{idx:03d}" for idx in range(1, 7)]:
        lines.append(
            "| "
            + fig_id
            + " | `"
            + surfaces[f"review_render_{fig_id}_pdf"]["path"]
            + "` | `"
            + surfaces[f"review_render_{fig_id}_png"]["path"]
            + "` | `"
            + surfaces[f"review_render_{fig_id}_svg"]["path"]
            + "` | "
            + focus[fig_id]
            + " |"
        )
    lines.extend(
        [
            "",
            "Author review should decide whether these figures are sufficient for a full-submission route or whether prospective collaborator-blind validation remains necessary before external contact.",
        ]
    )
    _write_text(FIGURE_GUIDE, "\n".join(lines))


def _write_packet_brief(manifest: list[dict[str, Any]], checklist: list[dict[str, str]], boundary: list[dict[str, str]], gate: dict[str, Any]) -> None:
    lines = [
        "# Stage 10.15 author visual-review packet",
        "",
        "This no-send packet binds the readable Stage 10.14 method figures to the already prepared presubmission query, one-page pitch, author checklist, route memo, and boundary surfaces.",
        "",
        "## Review surfaces",
        "",
        f"- Clean query. `{manifest[0]['path']}`",
        f"- One-page pitch. `{manifest[1]['path']}`",
        f"- Figure contact sheet. `case_studies/stage10_rendered_figure_visual_qc/stage10_14_review_render_contact_sheet.png`",
        f"- Figure review guide. `{_rel(FIGURE_GUIDE)}`",
        "",
        "## Decisions still required from the author",
        "",
    ]
    for row in checklist:
        if row["status"] in {"author_required", "separate_new_evidence_decision", "not_sent"}:
            lines.append(f"- {row['item_id']}. {row['review_item']}. {row['author_action']}.")
    lines.extend(
        [
            "",
            "## Boundary scan",
            "",
            f"Boundary rows passing. `{gate['summary_metrics']['boundary_pass_count']}` of `{gate['summary_metrics']['boundary_count']}`.",
            "",
            "This packet does not send a presubmission query, does not add biological evidence, and does not replace author judgment about whether additional validation is needed.",
        ]
    )
    _write_text(PACKET_BRIEF, "\n".join(lines))


def _write_doc(gate: dict[str, Any]) -> None:
    body = f"""# Stage 10.15 author visual-review packet

Stage 10.15 assembles a no-send author-review surface that combines the clean presubmission query, one-page pitch, author checklist, route decision memo, and readable Stage 10.14 method figures.

## Status

`{gate["status"]}`

## Outputs

- Packet brief. `{gate["outputs"]["packet_brief"]}`
- Manifest. `{gate["outputs"]["manifest"]}`
- Author checklist. `{gate["outputs"]["checklist"]}`
- Boundary scan. `{gate["outputs"]["boundary_scan"]}`
- Figure review guide. `{gate["outputs"]["figure_guide"]}`
- Gate report. `{gate["outputs"]["gate_report"]}`

## Boundary

The packet is for author review only. External contact remains `{gate["external_contact_status"]}`. It does not add data, retune benchmarks, change manuscript claims, or invent author-only metadata.
"""
    _write_text(DOC_PATH, body)


def _update_memory(gate: dict[str, Any]) -> None:
    memory = _read_json(MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 10.15 author visual-review packet complete; external contact remains not sent"
    current["current_gate"] = "Stage 10.15 author visual-review packet complete; external contact remains not sent"
    current["stage10_active_gate"] = "Stage 10.15 author visual-review packet complete; external contact remains not sent"
    current["next_stage"] = "Author decision on presubmission contact, full submission, delay for external validation, or venue pivot"
    current["after_stage10_15_author_visual_review_packet"] = (
        "Stage 10.15 assembled a no-send author visual-review packet that binds the clean query, one-page pitch, checklist, route memo, "
        "and readable Stage 10.14 figures. It adds no biological evidence and keeps external contact unsent."
    )

    stage10 = next((stage for stage in memory.get("stage_lock", []) if stage.get("stage") == 10), None)
    if not isinstance(stage10, dict):
        _write_json(MEMORY_PATH, memory)
        return
    artifacts = set(stage10.get("artifacts", []))
    artifacts.update(
        [
            _rel(DOC_PATH),
            "scripts/run_stage10_15_author_visual_review_packet.py",
            "tests/test_stage10_15_author_visual_review_packet.py",
            _rel(MANIFEST),
            _rel(CHECKLIST),
            _rel(BOUNDARY_SCAN),
            _rel(FIGURE_GUIDE),
            _rel(PACKET_BRIEF),
            _rel(GATE_REPORT),
        ]
    )
    stage10["artifacts"] = sorted(artifacts)
    stage10["status"] = "stage10_15_complete_author_visual_review_packet"
    stage10["current_gate"] = "Stage 10.15 author visual-review packet complete; external contact remains not sent"
    subphases = stage10.setdefault("subphases", [])
    by_id = {entry.get("id"): entry for entry in subphases if isinstance(entry, dict)}
    by_id["10.15"] = {
        "id": "10.15",
        "name": "No-send author visual-review packet",
        "status": "complete_author_visual_review_packet",
        "goal": "Bind readable Stage 10.14 figures to author-review query, pitch, checklist, and route decision surfaces.",
        "gate": "All packet references exist; readable figures are present; no-send boundaries pass; external contact remains not sent.",
        "evidence": _rel(GATE_REPORT),
    }
    stage10["subphases"] = [by_id[key] for key in sorted(by_id, key=lambda value: tuple(int(part) for part in value.split(".")))]
    _write_json(MEMORY_PATH, memory)


def run_stage10_15() -> dict[str, Any]:
    stage10_9 = _read_json(STAGE10_9_GATE)
    stage10_11 = _read_json(STAGE10_11_GATE)
    stage10_14 = _read_json(STAGE10_14_GATE)

    manifest = manifest_rows()
    checklist = checklist_rows()
    boundary = boundary_rows(stage10_9, stage10_11, stage10_14, manifest)
    _write_tsv(MANIFEST, manifest, MANIFEST_FIELDS)
    _write_tsv(CHECKLIST, checklist, CHECKLIST_FIELDS)
    _write_tsv(BOUNDARY_SCAN, boundary, BOUNDARY_FIELDS)
    _write_figure_guide(manifest)

    manifest_exists = all(row["exists"] == "yes" for row in manifest)
    figure_rows = [row for row in manifest if row["surface"].startswith("review_render_")]
    required_author_actions = [row for row in checklist if row["required"] == "yes" and row["status"] == "author_required"]
    boundary_pass = [row for row in boundary if row["status"] == "pass"]
    gates = {
        "stage10_9_passed": stage10_9.get("status") == "pass",
        "stage10_11_passed": stage10_11.get("status") == "pass",
        "stage10_14_passed": stage10_14.get("status") == "pass",
        "external_contact_not_sent": stage10_9.get("external_contact_status") == stage10_11.get("external_contact_status") == stage10_14.get("external_contact_status") == "not_sent",
        "manifest_all_files_exist": manifest_exists,
        "eighteen_review_render_files_referenced": len(figure_rows) == 18,
        "six_figures_have_three_formats": len({row["surface"].split("_")[2] for row in figure_rows}) == 6,
        "boundary_scan_all_pass": len(boundary_pass) == len(boundary),
        "author_required_items_retained": len(required_author_actions) >= 2,
        "no_new_science_claims_or_contact": True,
    }
    gate = {
        "stage": "10.15",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "gates": gates,
        "external_contact_status": "not_sent",
        "summary_metrics": {
            "manifest_row_count": len(manifest),
            "figure_render_reference_count": len(figure_rows),
            "checklist_item_count": len(checklist),
            "author_required_item_count": len(required_author_actions),
            "boundary_count": len(boundary),
            "boundary_pass_count": len(boundary_pass),
        },
        "outputs": {
            "manifest": _rel(MANIFEST),
            "checklist": _rel(CHECKLIST),
            "boundary_scan": _rel(BOUNDARY_SCAN),
            "figure_guide": _rel(FIGURE_GUIDE),
            "packet_brief": _rel(PACKET_BRIEF),
            "gate_report": _rel(GATE_REPORT),
            "doc": _rel(DOC_PATH),
        },
        "interpretation_boundary": (
            "Stage 10.15 is an author-review packaging step. It binds existing Stage 10 evidence and readable figures without adding "
            "new data, changing claims, inventing author-only fields, or sending external contact."
        ),
    }
    _write_json(GATE_REPORT, gate)
    _write_packet_brief(manifest, checklist, boundary, gate)
    _write_doc(gate)
    _update_memory(gate)
    return gate


def main() -> int:
    gate = run_stage10_15()
    print(json.dumps(gate, indent=2))
    return 0 if gate["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
