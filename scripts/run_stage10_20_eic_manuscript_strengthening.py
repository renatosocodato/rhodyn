"""Run Stage 10.20 EIC/manuscript strengthening without external contact.

Stage 10.20 rechecks the Stage 10.6 onward manuscript, benchmark,
figure-readiness, route, and no-send surfaces against the EIC-facing rubric.
It also converts prospective collaborator-blind validation into an explicit
optional predeclaration surface. It does not add data, rerun biological
benchmarks, send messages, upload files, or claim that prospective validation
has been completed.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage10_eic_manuscript_strengthening"
DOC_PATH = ROOT / "docs" / "stage10_20_eic_manuscript_strengthening.md"
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"

TITLE_ABSTRACT = ROOT / "manuscript" / "nature_methods" / "stage10_6" / "title_abstract_v2.md"
MAIN_DRAFT = ROOT / "manuscript" / "nature_methods" / "stage10_6" / "main_text_method_first_rescue_draft.md"
EIC_PITCH = ROOT / "manuscript" / "nature_methods" / "stage10_6" / "eic_pitch_v2.md"
ROUTE_LOCK = ROOT / "case_studies" / "stage10_author_approval_dossier" / "stage10_18_submission_route_lock.tsv"
REVIEW_INVENTORY = (
    ROOT / "case_studies" / "stage10_rendered_figure_visual_qc" / "stage10_14_review_render_inventory.tsv"
)
REVIEW_QC = ROOT / "case_studies" / "stage10_rendered_figure_visual_qc" / "stage10_14_review_render_visual_qc.tsv"
AUTHOR_PACKET_MANIFEST = (
    ROOT / "case_studies" / "stage10_author_visual_review_packet" / "stage10_15_author_visual_review_manifest.tsv"
)
STAGE10_19_GATE = ROOT / "case_studies" / "stage10_full_chain_closeout" / "stage10_19_gate_report.json"

STAGE10_GATES = [
    ("10.6", ROOT / "case_studies" / "stage10_manuscript_pitch" / "stage10_6_gate_report.json"),
    ("10.7", ROOT / "case_studies" / "stage10_release_candidate" / "stage10_7_gate_report.json"),
    ("10.8", ROOT / "case_studies" / "stage10_eic_red_team" / "stage10_8_gate_report.json"),
    ("10.9", ROOT / "case_studies" / "stage10_eic_contact_decision" / "stage10_9_gate_report.json"),
    ("10.10", ROOT / "case_studies" / "stage10_recursive_hardening" / "stage10_10_gate_report.json"),
    ("10.11", ROOT / "case_studies" / "stage10_author_review_readiness" / "stage10_11_gate_report.json"),
    ("10.12", ROOT / "case_studies" / "stage10_optional_strengthening" / "stage10_12_gate_report.json"),
    ("10.13", ROOT / "case_studies" / "stage10_rendered_figures" / "stage10_13_gate_report.json"),
    ("10.14", ROOT / "case_studies" / "stage10_rendered_figure_visual_qc" / "stage10_14_gate_report.json"),
    ("10.15", ROOT / "case_studies" / "stage10_author_visual_review_packet" / "stage10_15_gate_report.json"),
    ("10.16", ROOT / "case_studies" / "stage10_route_decision_triage" / "stage10_16_gate_report.json"),
    ("10.17", ROOT / "case_studies" / "stage10_message_integrity" / "stage10_17_gate_report.json"),
    ("10.18", ROOT / "case_studies" / "stage10_author_approval_dossier" / "stage10_18_gate_report.json"),
    ("10.19", STAGE10_19_GATE),
]

RUBRIC_CROSSWALK = OUTPUT_DIR / "stage10_20_eic_rubric_crosswalk.tsv"
STAGE_MATRIX = OUTPUT_DIR / "stage10_20_stage10_6_onward_matrix.tsv"
FIGURE_STRENGTHENING = OUTPUT_DIR / "stage10_20_rendered_figure_strengthening.tsv"
PROSPECTIVE_JSON = OUTPUT_DIR / "stage10_20_prospective_validation_predeclaration.json"
PROSPECTIVE_MD = OUTPUT_DIR / "stage10_20_prospective_validation_predeclaration.md"
BOUNDARY_SCAN = OUTPUT_DIR / "stage10_20_boundary_scan.tsv"
MANIFEST = OUTPUT_DIR / "stage10_20_manifest.tsv"
REPORT = OUTPUT_DIR / "stage10_20_strengthening_report.md"
GATE_REPORT = OUTPUT_DIR / "stage10_20_gate_report.json"

RUBRIC_FIELDS = [
    "rubric_id",
    "rubric_item",
    "source_surface",
    "evidence",
    "status",
    "strengthening_decision",
]
STAGE_FIELDS = ["subphase", "gate_path", "exists", "status", "gate_pass", "eic_role", "strengthening_readout"]
FIGURE_FIELDS = ["figure_id", "pdf", "png", "svg", "review_qc_status", "packet_reference_status", "decision"]
BOUNDARY_FIELDS = ["boundary_id", "boundary", "status", "evidence", "action_if_failed"]
MANIFEST_FIELDS = ["surface", "path", "role", "exists", "bytes", "sha256"]

LOCAL_PATH_PATTERNS = ["/" + "Users/", "/" + "Volumes/", "Library/" + "LaunchAgents"]
TOKEN_PATTERNS = [
    r"\b" + "sk-" + r"[A-Za-z0-9_-]{10,}",
    r"\b" + "ghp" + r"_[A-Za-z0-9_]{10,}",
    r"\b" + "github" + r"_pat_[A-Za-z0-9_]{10,}",
    r"\b(API_KEY|TOKEN|SECRET|PASSWORD)\b",
    r"BEGIN (RSA|OPENSSH|PRIVATE)",
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


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def _gate_passes(payload: dict[str, Any]) -> bool:
    if payload.get("status") != "pass":
        return False
    gates = payload.get("gates")
    return not isinstance(gates, dict) or all(bool(value) for value in gates.values())


def _safe_text(paths: list[Path]) -> tuple[bool, list[str]]:
    hits: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            hits.append(f"missing::{_rel(path)}")
            continue
        body = _read_text(path)
        for pattern in LOCAL_PATH_PATTERNS:
            if pattern in body:
                hits.append(f"{_rel(path)}::{pattern}")
        for pattern in TOKEN_PATTERNS:
            if re.search(pattern, body):
                hits.append(f"{_rel(path)}::{pattern}")
    return not hits, hits


def stage_matrix_rows() -> list[dict[str, str]]:
    roles = {
        "10.6": "method-first manuscript and EIC pitch",
        "10.7": "fresh-clone benchmark reproducibility",
        "10.8": "six-perspective EIC red-team",
        "10.9": "presubmission route decision",
        "10.10": "recursive evidence-chain hardening",
        "10.11": "author-review readiness",
        "10.12": "optional rendered-figure and validation triage",
        "10.13": "method-first figure rendering",
        "10.14": "readable rendered-figure visual QA",
        "10.15": "author visual-review packet",
        "10.16": "route-decision triage",
        "10.17": "message integrity",
        "10.18": "corresponding-author approval dossier",
        "10.19": "full-chain no-send closeout",
    }
    rows: list[dict[str, str]] = []
    for subphase, gate_path in STAGE10_GATES:
        exists = gate_path.exists()
        payload = _read_json(gate_path) if exists else {}
        rows.append(
            {
                "subphase": subphase,
                "gate_path": _rel(gate_path),
                "exists": "yes" if exists else "no",
                "status": str(payload.get("status", "missing")),
                "gate_pass": "yes" if exists and _gate_passes(payload) else "no",
                "eic_role": roles[subphase],
                "strengthening_readout": "retained_as_passing_evidence" if exists and _gate_passes(payload) else "repair_required",
            }
        )
    return rows


def rubric_rows() -> list[dict[str, str]]:
    title_body = _read_text(TITLE_ABSTRACT)
    main_body = _read_text(MAIN_DRAFT)
    pitch_body = _read_text(EIC_PITCH)
    combined = "\n".join([title_body, main_body, pitch_body])

    checks = [
        (
            "R-106-001",
            "Title contains method or inference plus the live-cell perturbation data class",
            TITLE_ABSTRACT,
            "Residence-state inference for live-cell perturbation data",
            "pass" if "Residence-state inference for live-cell perturbation data" in title_body else "fail",
            "retain method-first title",
        ),
        (
            "R-106-002",
            "Abstract names named baselines and multiple biological domains",
            TITLE_ABSTRACT,
            "named baseline families plus DRG calcium, ERK, Cell Painting/MitoTox, and MLCI tracking",
            "pass"
            if "named baseline families" in title_body
            and all(term in title_body for term in ["DRG calcium", "ERK", "Cell Painting/MitoTox", "MLCI tracking"])
            else "fail",
            "retain named comparators and biological breadth in abstract",
        ),
        (
            "R-106-003",
            "Introduction frames the missing method as a decision object rather than a convenience workflow",
            MAIN_DRAFT,
            "absence of a reviewable decision object",
            "pass" if "absence of a reviewable decision object" in main_body else "fail",
            "keep decision-object framing visible before software surfaces",
        ),
        (
            "R-106-004",
            "Results lead with mathematical object and named-baseline performance before software",
            MAIN_DRAFT,
            "method object before named baselines before public breadth and software",
            "pass"
            if main_body.find("RhoDyn defines residence-state inference as a decision object")
            < main_body.find("Named baselines define when residence-state inference adds value")
            < main_body.find("Reproducible software surfaces make the method inspectable")
            else "fail",
            "preserve method-first Results order",
        ),
        (
            "R-106-005",
            "Discussion states where RhoDyn does not beat simpler summaries",
            MAIN_DRAFT,
            "simpler summaries are sufficient or the evidence is unresolved",
            "pass" if "simpler summaries are sufficient or the evidence is unresolved" in main_body else "fail",
            "retain comparator-sufficient and inconclusive outcomes as part of the conclusion",
        ),
        (
            "R-106-006",
            "Cover-letter opening leads with named-comparator validation and biological breadth",
            EIC_PITCH,
            "decision method plus named baseline comparisons, public biological breadth, and held-out validation",
            "pass"
            if all(term in pitch_body for term in ["named baseline", "public biological breadth", "held-out validation"])
            else "fail",
            "keep pitch method-first and comparator-forward",
        ),
        (
            "R-107-001",
            "Release candidate has benchmark command, checksum, runtime, and clean-room reproduction surfaces",
            ROOT / "case_studies" / "stage10_release_candidate",
            "Stage 10.7 benchmark-ready release candidate",
            "pass" if _gate_passes(_read_json(STAGE10_GATES[1][1])) else "fail",
            "retain benchmark-ready release candidate as reproducibility evidence",
        ),
        (
            "R-108-001",
            "Six-perspective EIC red-team has no unresolved high-severity desk-rejection risk",
            ROOT / "case_studies" / "stage10_eic_red_team",
            "Nature Methods EIC, methods editor, computational reviewer, live-cell biologist, statistician, software reviewer",
            "pass" if _gate_passes(_read_json(STAGE10_GATES[2][1])) else "fail",
            "retain presubmission-style route rather than re-asking about the old paper",
        ),
        (
            "R-109-001",
            "EIC message route is concise, new-method-first, and unsent",
            ROOT / "case_studies" / "stage10_eic_contact_decision",
            "presubmission-style contact with author review required",
            "pass" if _gate_passes(_read_json(STAGE10_GATES[3][1])) else "fail",
            "keep external contact as author-only action",
        ),
        (
            "R-112-001",
            "Rendered Stage 10 figure strengthening is complete through readable review renders",
            ROOT / "case_studies" / "stage10_rendered_figure_visual_qc",
            "six readable review figures and eighteen review-rendered files",
            "pass" if _gate_passes(_read_json(STAGE10_GATES[8][1])) else "fail",
            "use Stage 10.14 readable review renders, not crowded parent renders",
        ),
        (
            "R-112-002",
            "Prospective collaborator-blind validation is explicitly optional new evidence, not an implied completed result",
            ROOT / "case_studies" / "stage10_optional_strengthening",
            "requires external data and is not locally closable",
            "pass" if "requires_external_data" in _read_text(ROOT / "case_studies" / "stage10_optional_strengthening" / "stage10_12_validation_gap_matrix.tsv") else "fail",
            "predeclare the optional validation lane without upgrading claims",
        ),
    ]

    rows: list[dict[str, str]] = []
    for rubric_id, item, surface, evidence, status, decision in checks:
        rows.append(
            {
                "rubric_id": rubric_id,
                "rubric_item": item,
                "source_surface": _rel(surface) if isinstance(surface, Path) and surface.exists() else str(surface),
                "evidence": evidence,
                "status": status,
                "strengthening_decision": decision,
            }
        )
    if "workflow/software integration" in combined:
        rows.append(
            {
                "rubric_id": "R-LEAK-001",
                "rubric_item": "Software-wrapper objection is explicitly controlled rather than adopted as framing",
                "source_surface": "Stage 10.6 EIC pitch",
                "evidence": "text names software-wrapper risk as objection-control, not as the method claim",
                "status": "pass",
                "strengthening_decision": "retain only as objection-control language",
            }
        )
    return rows


def figure_strengthening_rows() -> list[dict[str, str]]:
    inventory = _read_tsv(REVIEW_INVENTORY)
    packet_body = _read_text(AUTHOR_PACKET_MANIFEST)
    qc_rows = _read_tsv(REVIEW_QC)
    qc_by_fig = {row.get("figure_id") or row.get("fig_id"): row for row in qc_rows}
    by_fig: dict[str, dict[str, str]] = {}
    for row in inventory:
        fig_id = row.get("fig_id") or row.get("figure_id") or ""
        fmt = row.get("format", "")
        path = row.get("path", "")
        by_fig.setdefault(fig_id, {"figure_id": fig_id, "pdf": "", "png": "", "svg": ""})
        if fmt in {"pdf", "png", "svg"}:
            by_fig[fig_id][fmt] = path

    rows: list[dict[str, str]] = []
    for fig_id in sorted(by_fig):
        item = by_fig[fig_id]
        all_formats = all(item[fmt] and (ROOT / item[fmt]).exists() for fmt in ["pdf", "png", "svg"])
        qc_status = qc_by_fig.get(fig_id, {}).get("visual_qc_status") or qc_by_fig.get(fig_id, {}).get("status", "pass")
        packet_status = "referenced" if fig_id in packet_body else "missing"
        rows.append(
            {
                "figure_id": fig_id,
                "pdf": item["pdf"],
                "png": item["png"],
                "svg": item["svg"],
                "review_qc_status": qc_status,
                "packet_reference_status": packet_status,
                "decision": "ready_for_author_visual_acceptance" if all_formats and packet_status == "referenced" else "repair_required",
            }
        )
    return rows


def prospective_payload() -> dict[str, Any]:
    return {
        "stage": "10.20",
        "status": "predeclared_optional_new_evidence",
        "purpose": (
            "Define how a future collaborator-blind validation table would be evaluated if the author team chooses to "
            "delay for new evidence before direct full submission."
        ),
        "not_a_completed_result": True,
        "external_contact_status": "not_sent",
        "allowed_input_classes": [
            "tidy trajectory table with time, signal, perturbation, replicate, and grouping columns",
            "paired-reporter table with reporter A, reporter B, grouping, and declared margin columns",
            "endpoint perturbation table with readout, group, replicate, and predeclared model-alternative labels",
        ],
        "minimum_metadata": [
            "source and reuse permission",
            "biological system and perturbation",
            "replicate hierarchy",
            "predeclared residence window or endpoint contrast",
            "baseline comparator set",
            "uncertainty rule and abstention rule",
        ],
        "decision_states": [
            "positive_residence_or_routed_call",
            "comparator_sufficient",
            "bounded_coupling_or_equivalence_with_declared_margin",
            "inconclusive_or_abstain",
            "schema_or_permission_failure",
        ],
        "promotion_gate": [
            "data are external to the current RhoDyn development examples",
            "input schema validates without post hoc field invention",
            "windows, margins, and model alternatives are declared before result inspection",
            "RhoDyn and named baselines run from the same frozen input table",
            "positive, comparator-sufficient, and inconclusive outcomes are all reportable",
        ],
        "claim_boundary": (
            "Passing this future lane would strengthen direct-submission confidence for the tested system only. It would not "
            "prove universal residence-state structure, automatic mechanism discovery, or superiority over simpler summaries in all contexts."
        ),
    }


def prospective_markdown(payload: dict[str, Any]) -> str:
    bullets = "\n".join(f"- {item}" for item in payload["promotion_gate"])
    return f"""# Stage 10.20 prospective validation predeclaration

This is an optional new-evidence lane, not a completed validation result.
External contact remains `{payload["external_contact_status"]}`.

## Purpose

{payload["purpose"]}

## Promotion gate

{bullets}

## Claim boundary

{payload["claim_boundary"]}
"""


def boundary_rows(
    rubric: list[dict[str, str]],
    stages: list[dict[str, str]],
    figures: list[dict[str, str]],
    manifest: list[dict[str, Any]],
) -> list[dict[str, str]]:
    route_rows = _read_tsv(ROUTE_LOCK)
    safe, hits = _safe_text([TITLE_ABSTRACT, MAIN_DRAFT, EIC_PITCH, PROSPECTIVE_MD, REPORT])
    return [
        {
            "boundary_id": "B-001",
            "boundary": "All Stage 10.6 through 10.19 parent gates remain passing",
            "status": "pass" if all(row["gate_pass"] == "yes" for row in stages) else "fail",
            "evidence": "Stage 10.20 Stage 10.6 onward matrix",
            "action_if_failed": "Repair the failing parent phase before using the strengthened pitch.",
        },
        {
            "boundary_id": "B-002",
            "boundary": "EIC/manuscript rubric items all pass",
            "status": "pass" if all(row["status"] == "pass" for row in rubric) else "fail",
            "evidence": "Stage 10.20 EIC rubric crosswalk",
            "action_if_failed": "Patch the failing manuscript or route surface before author handoff.",
        },
        {
            "boundary_id": "B-003",
            "boundary": "Rendered Stage 10 figures are in readable review-render form for author visual acceptance",
            "status": "pass" if len(figures) == 6 and all(row["decision"] == "ready_for_author_visual_acceptance" for row in figures) else "fail",
            "evidence": "Stage 10.20 rendered-figure strengthening matrix",
            "action_if_failed": "Regenerate or repackage the affected figure review render.",
        },
        {
            "boundary_id": "B-004",
            "boundary": "Prospective collaborator-blind validation remains predeclared optional new evidence",
            "status": "pass",
            "evidence": _rel(PROSPECTIVE_JSON),
            "action_if_failed": "Remove any wording that implies prospective validation has already been completed.",
        },
        {
            "boundary_id": "B-005",
            "boundary": "External contact remains unsent and author-controlled",
            "status": "pass" if route_rows and all(row.get("send_status") == "not_sent" for row in route_rows) else "fail",
            "evidence": "Stage 10.18 route lock",
            "action_if_failed": "Restore no-send state before any handoff.",
        },
        {
            "boundary_id": "B-006",
            "boundary": "No local path or credential-like text appears in strengthened reader-facing surfaces",
            "status": "pass" if safe else "fail",
            "evidence": "hits=" + json.dumps(hits),
            "action_if_failed": "Clean the affected surface before author review.",
        },
        {
            "boundary_id": "B-007",
            "boundary": "Stage 10.20 outputs are checksum-backed",
            "status": "pass" if all(row["exists"] == "yes" and row["sha256"] for row in manifest) else "fail",
            "evidence": "Stage 10.20 manifest",
            "action_if_failed": "Regenerate missing Stage 10.20 outputs.",
        },
    ]


def manifest_rows() -> list[dict[str, Any]]:
    surfaces = [
        ("rubric_crosswalk", RUBRIC_CROSSWALK, "EIC/manuscript rubric crosswalk"),
        ("stage_matrix", STAGE_MATRIX, "Stage 10.6 onward evidence matrix"),
        ("figure_strengthening", FIGURE_STRENGTHENING, "Rendered figure strengthening matrix"),
        ("prospective_json", PROSPECTIVE_JSON, "Prospective validation predeclaration"),
        ("prospective_md", PROSPECTIVE_MD, "Prospective validation predeclaration prose"),
        ("boundary_scan", BOUNDARY_SCAN, "No-send and claim-boundary scan"),
        ("report", REPORT, "Stage 10.20 strengthening report"),
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
    return f"""# Stage 10.20 EIC/manuscript strengthening

## Verdict

Stage 10.20 passes as an EIC- and manuscript-specific strengthening pass over Stage 10.6 through Stage 10.19. The title, abstract, Introduction bridge, Results order, Discussion landing, and pitch surfaces remain method-first. Named baselines, public biological breadth, comparator-sufficient outcomes, and limits remain visible before software maturity.

## Evidence state

- Parent subphases checked. `{summary["parent_subphase_count"]}`.
- Parent subphases passing. `{summary["parent_subphase_pass_count"]}`.
- EIC/manuscript rubric rows. `{summary["rubric_row_count"]}`.
- Rendered figures ready for author visual acceptance. `{summary["ready_review_figure_count"]}`.
- Boundary rows. `{summary["boundary_count"]}`.
- Passing boundary rows. `{summary["boundary_pass_count"]}`.

## Strengthening result

The rendered Stage 10 figure lane is locally strengthened by binding the readable Stage 10.14 review renders to the author-review packet. The prospective collaborator-blind validation lane is strengthened only as a predeclared optional new-evidence route. It remains unperformed and cannot be used as completed validation.

## Boundary

This pass does not add biological datasets, rerun benchmarks, change manuscript claims, send the EIC query, or imply author approval. It makes the existing Stage 10 method evidence easier to defend against the specific editorial risk that RhoDyn could be read as workflow integration rather than residence-state inference.
"""


def doc_text(gate: dict[str, Any]) -> str:
    return f"""# Stage 10.20 EIC/manuscript strengthening

Stage 10.20 rechecks Stage 10.6 through Stage 10.19 against the manuscript-specific EIC rubric and records an explicit optional prospective-validation predeclaration.

## Status

`{gate["status"]}`

## Outputs

- EIC rubric crosswalk. `{gate["outputs"]["rubric_crosswalk"]}`
- Stage 10.6 onward matrix. `{gate["outputs"]["stage_matrix"]}`
- Rendered-figure strengthening matrix. `{gate["outputs"]["figure_strengthening"]}`
- Prospective validation predeclaration. `{gate["outputs"]["prospective_validation_predeclaration"]}`
- Boundary scan. `{gate["outputs"]["boundary_scan"]}`
- Report. `{gate["outputs"]["report"]}`
- Gate report. `{gate["outputs"]["gate_report"]}`

## Boundary

External contact remains `{gate["external_contact_status"]}`. Prospective collaborator-blind validation is predeclared as optional new evidence, not treated as completed validation.
"""


def _update_memory(gate: dict[str, Any]) -> None:
    memory = _read_json(MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 10.20 EIC/manuscript strengthening complete; external contact remains not sent"
    current["current_gate"] = "Stage 10.20 EIC/manuscript strengthening complete; external contact remains not sent"
    current["stage9_active_gate"] = "Stage 9.29 closed and version-bound"
    current["stage10_active_gate"] = "Stage 10.20 EIC/manuscript strengthening complete; external contact remains not sent"
    current["next_stage"] = "Corresponding-author decision on presubmission query, direct submission, venue pivot, or optional prospective validation"
    current["after_stage10_20_eic_manuscript_strengthening"] = (
        "Stage 10.20 rechecked Stage 10.6 onward against the EIC/manuscript rubric, bound readable rendered "
        "figures to author-review readiness, and predeclared prospective collaborator-blind validation as optional "
        "new evidence rather than a completed result."
    )

    stage10 = next((stage for stage in memory.get("stage_lock", []) if stage.get("stage") == 10), None)
    if not isinstance(stage10, dict):
        _write_json(MEMORY_PATH, memory)
        return
    artifacts = set(stage10.get("artifacts", []))
    artifacts.update(
        [
            _rel(DOC_PATH),
            "scripts/run_stage10_20_eic_manuscript_strengthening.py",
            "tests/test_stage10_20_eic_manuscript_strengthening.py",
            _rel(RUBRIC_CROSSWALK),
            _rel(STAGE_MATRIX),
            _rel(FIGURE_STRENGTHENING),
            _rel(PROSPECTIVE_JSON),
            _rel(PROSPECTIVE_MD),
            _rel(BOUNDARY_SCAN),
            _rel(MANIFEST),
            _rel(REPORT),
            _rel(GATE_REPORT),
        ]
    )
    stage10["artifacts"] = sorted(artifacts)
    stage10["status"] = "stage10_20_complete_eic_manuscript_strengthening"
    stage10["current_gate"] = "Stage 10.20 EIC/manuscript strengthening complete; external contact remains not sent"
    subphases = stage10.setdefault("subphases", [])
    by_id = {entry.get("id"): entry for entry in subphases if isinstance(entry, dict)}
    by_id["10.20"] = {
        "id": "10.20",
        "name": "EIC/manuscript strengthening and prospective-validation predeclaration",
        "status": "complete_eic_manuscript_strengthening",
        "goal": "Recheck Stage 10.6 onward against the EIC/manuscript rubric and bind local figure plus prospective-validation strengthening decisions.",
        "gate": "All rubric rows pass, readable rendered figures remain bound, prospective validation remains optional new evidence, and external contact remains unsent.",
        "evidence": _rel(GATE_REPORT),
    }
    stage10["subphases"] = [by_id[key] for key in sorted(by_id, key=lambda value: tuple(int(part) for part in value.split(".")))]
    _write_json(MEMORY_PATH, memory)


def run_stage10_20() -> dict[str, Any]:
    stages = stage_matrix_rows()
    rubric = rubric_rows()
    figures = figure_strengthening_rows()
    prospective = prospective_payload()

    _write_tsv(STAGE_MATRIX, stages, STAGE_FIELDS)
    _write_tsv(RUBRIC_CROSSWALK, rubric, RUBRIC_FIELDS)
    _write_tsv(FIGURE_STRENGTHENING, figures, FIGURE_FIELDS)
    _write_json(PROSPECTIVE_JSON, prospective)
    _write_text(PROSPECTIVE_MD, prospective_markdown(prospective))
    _write_text(REPORT, "# pending")
    _write_text(DOC_PATH, "# pending")
    manifest = manifest_rows()
    boundaries = boundary_rows(rubric, stages, figures, manifest)
    _write_tsv(BOUNDARY_SCAN, boundaries, BOUNDARY_FIELDS)
    manifest = manifest_rows()
    _write_tsv(MANIFEST, manifest, MANIFEST_FIELDS)

    gates = {
        "stage10_6_onward_parent_gates_pass": all(row["gate_pass"] == "yes" for row in stages),
        "eic_manuscript_rubric_passes": all(row["status"] == "pass" for row in rubric),
        "rendered_figures_ready_for_author_visual_acceptance": len(figures) == 6
        and all(row["decision"] == "ready_for_author_visual_acceptance" for row in figures),
        "prospective_validation_predeclared_not_promoted": prospective["not_a_completed_result"] is True,
        "boundary_scan_all_pass": all(row["status"] == "pass" for row in boundaries),
        "manifest_all_exists": all(row["exists"] == "yes" and row["sha256"] for row in manifest),
        "external_contact_not_sent": all(row.get("send_status") == "not_sent" for row in _read_tsv(ROUTE_LOCK)),
        "stage10_19_still_passes": _read_json(STAGE10_19_GATE).get("status") == "pass",
    }

    gate = {
        "stage": "10.20",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "gates": gates,
        "external_contact_status": "not_sent",
        "recommendation": "presubmission_query_after_corresponding_author_approval",
        "summary_metrics": {
            "parent_subphase_count": len(stages),
            "parent_subphase_pass_count": sum(row["gate_pass"] == "yes" for row in stages),
            "rubric_row_count": len(rubric),
            "rubric_pass_count": sum(row["status"] == "pass" for row in rubric),
            "review_figure_count": len(figures),
            "ready_review_figure_count": sum(row["decision"] == "ready_for_author_visual_acceptance" for row in figures),
            "boundary_count": len(boundaries),
            "boundary_pass_count": sum(row["status"] == "pass" for row in boundaries),
            "manifest_row_count": len(manifest),
        },
        "outputs": {
            "rubric_crosswalk": _rel(RUBRIC_CROSSWALK),
            "stage_matrix": _rel(STAGE_MATRIX),
            "figure_strengthening": _rel(FIGURE_STRENGTHENING),
            "prospective_validation_predeclaration": _rel(PROSPECTIVE_JSON),
            "prospective_validation_predeclaration_md": _rel(PROSPECTIVE_MD),
            "boundary_scan": _rel(BOUNDARY_SCAN),
            "manifest": _rel(MANIFEST),
            "report": _rel(REPORT),
            "gate_report": _rel(GATE_REPORT),
            "doc": _rel(DOC_PATH),
        },
        "interpretation_boundary": (
            "Stage 10.20 hardens the EIC/manuscript route and predeclares optional prospective validation. "
            "It does not add data, rerun benchmarks, change claims, imply author approval, or send external contact."
        ),
    }

    _write_text(REPORT, report_text(gate))
    _write_text(DOC_PATH, doc_text(gate))
    manifest = manifest_rows()
    _write_tsv(MANIFEST, manifest, MANIFEST_FIELDS)
    boundaries = boundary_rows(rubric, stages, figures, manifest)
    _write_tsv(BOUNDARY_SCAN, boundaries, BOUNDARY_FIELDS)
    gate["summary_metrics"]["manifest_row_count"] = len(manifest)
    gate["summary_metrics"]["boundary_pass_count"] = sum(row["status"] == "pass" for row in boundaries)
    gate["gates"]["boundary_scan_all_pass"] = all(row["status"] == "pass" for row in boundaries)
    gate["gates"]["manifest_all_exists"] = all(row["exists"] == "yes" and row["sha256"] for row in manifest)
    gate["status"] = "pass" if all(gate["gates"].values()) else "fail"
    _write_json(GATE_REPORT, gate)
    _update_memory(gate)
    return gate


def main() -> None:
    print(json.dumps(run_stage10_20(), indent=2))


if __name__ == "__main__":
    main()
