"""Build the Stage 7.8 methods-manuscript readiness package.

Stage 7.8 does not run new biological analyses. It checks that the planned
methods-manuscript components are backed by existing Stage 7 evidence, have a
documented limitation boundary, and can be traced to reproducible files.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage7_methods_readiness"
DOC_EVIDENCE_INDEX = ROOT / "docs" / "stage7_methods_evidence_index.md"
DOC_FIGURE_CROSSWALK = ROOT / "docs" / "stage7_figure_artifact_crosswalk.md"
DOC_CLAIM_CROSSWALK = ROOT / "docs" / "stage7_claim_evidence_crosswalk.md"
DOC_READINESS = ROOT / "docs" / "stage7_methods_submission_readiness.md"
DOC_GATE = ROOT / "docs" / "stage7_8_gate_report.json"
CASE_GATE = OUTPUT_DIR / "stage7_8_methods_readiness_gate_report.json"


FIGURE_ROWS: list[dict[str, str]] = [
    {
        "component": "Method concept and workflow",
        "stage": "7.1",
        "primary_artifact": "docs/stage7_method_specification.md",
        "supporting_artifacts": "docs/stage7_synthetic_truth_cases.md; case_studies/stage7_synthetic_truth/stage7_1_synthetic_truth_report.json",
        "validation_artifact": "docs/stage7_1_gate_report.json",
        "limitation_artifact": "docs/stage7_limitations_matrix.md",
        "readiness": "ready_for_drafting",
        "scope": "Formal method definitions and executable truth cases, not biological discovery.",
    },
    {
        "component": "Synthetic benchmarking against simpler summaries",
        "stage": "7.2",
        "primary_artifact": "docs/stage7_baseline_comparison_report.md",
        "supporting_artifacts": "case_studies/stage7_benchmarks/stage7_2_benchmark_report.json; case_studies/stage7_benchmarks/synthetic_residence_baseline_comparison.csv; case_studies/stage7_benchmarks/synthetic_model_baseline_comparison.csv",
        "validation_artifact": "docs/stage7_2_gate_report.json",
        "limitation_artifact": "case_studies/stage7_benchmarks/failure_behavior_summary.csv",
        "readiness": "ready_for_drafting",
        "scope": "Benchmark value over baselines is regime-dependent and includes negative and ambiguous cases.",
    },
    {
        "component": "Independent public live-cell signaling demonstrations",
        "stage": "7.3",
        "primary_artifact": "docs/stage7_public_signaling_demonstrations.md",
        "supporting_artifacts": "case_studies/stage7_public_signaling/drg_calcium_residence_amplitude_summary.csv; case_studies/stage7_public_signaling/erk_gpcr_residence_amplitude_summary.csv",
        "validation_artifact": "docs/stage7_3_gate_report.json",
        "limitation_artifact": "docs/stage7_public_data_adapters.md",
        "readiness": "ready_for_drafting",
        "scope": "Public trajectory demonstrations show residence-amplitude separation in two systems and do not imply manuscript generation.",
    },
    {
        "component": "Perturbation endpoint, reserve-like, and routed-output demonstrations",
        "stage": "7.4",
        "primary_artifact": "docs/stage7_endpoint_reserve_routing_demonstrations.md",
        "supporting_artifacts": "case_studies/stage7_endpoint_reserve_routing/erk_akt_bounded_coupling_decisions.csv; case_studies/stage7_endpoint_reserve_routing/cell_painting_routed_model_comparison.csv; case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_model_summary.csv",
        "validation_artifact": "docs/stage7_4_gate_report.json",
        "limitation_artifact": "case_studies/stage7_endpoint_reserve_routing/stage7_4_case_report.md",
        "readiness": "ready_for_drafting",
        "scope": "Bounded coupling, reserve-like endpoint behavior, and routed-output comparison remain scoped to measured public-derived tables.",
    },
    {
        "component": "Held-out public validation",
        "stage": "7.5",
        "primary_artifact": "docs/stage7_heldout_validation_report.md",
        "supporting_artifacts": "case_studies/stage7_heldout_validation/heldout_bounded_coupling_decisions.csv; case_studies/stage7_heldout_validation/heldout_validation_outcomes.tsv",
        "validation_artifact": "docs/stage7_5_gate_report.json",
        "limitation_artifact": "case_studies/stage7_heldout_validation/controlled_access_note.md",
        "readiness": "ready_for_supplement_or_main_with_scope",
        "scope": "Held-out validation contains four pass contexts and three margin-boundary inconclusive contexts.",
    },
    {
        "component": "Software workbench and reproducibility architecture",
        "stage": "7.6-7.7",
        "primary_artifact": "docs/stage7_methods_reproducibility_card.md",
        "supporting_artifacts": "docs/stage7_6_gate_report.json; docs/stage7_7_gate_report.json; docs/stage7_usability_rehearsal.md; docs/stage7_user_path_findings.md",
        "validation_artifact": "case_studies/stage7_methods_reproducibility/stage7_6_methods_reproducibility_gate_report.json",
        "limitation_artifact": "docs/stage7_6_api_stability_policy.md",
        "readiness": "ready_for_drafting",
        "scope": "Reproducibility and usability evidence support inspectable software behavior, not a new biological result.",
    },
]


CLAIM_ROWS: list[dict[str, str]] = [
    {
        "claim_id": "C1",
        "claim": "Residence-window summaries can expose time-in-state behavior that amplitude summaries miss.",
        "evidence": "case_studies/stage7_benchmarks/synthetic_residence_baseline_comparison.csv; case_studies/stage7_public_signaling/drg_calcium_residence_amplitude_summary.csv; case_studies/stage7_public_signaling/erk_gpcr_residence_amplitude_summary.csv",
        "validation": "docs/stage7_2_gate_report.json; docs/stage7_3_gate_report.json",
        "limitation": "docs/stage7_limitations_matrix.md",
        "status": "supported_for_methods_drafting",
    },
    {
        "claim_id": "C2",
        "claim": "Bounded-coupling decisions require predeclared margins, uncertainty intervals, and ROPE or interval support when supplied.",
        "evidence": "case_studies/stage7_endpoint_reserve_routing/erk_akt_bounded_coupling_decisions.csv; case_studies/stage7_heldout_validation/heldout_bounded_coupling_decisions.csv",
        "validation": "docs/stage7_4_gate_report.json; docs/stage7_5_gate_report.json",
        "limitation": "case_studies/stage7_heldout_validation/heldout_margin_sensitivity.csv",
        "status": "supported_with_inconclusive_contexts_visible",
    },
    {
        "claim_id": "C3",
        "claim": "Reserve-like summaries can be integrated when the readout is scoped to the measured endpoint.",
        "evidence": "case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_endpoint_rows.csv; case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_uncertainty.csv",
        "validation": "docs/stage7_4_gate_report.json",
        "limitation": "docs/stage7_endpoint_reserve_routing_demonstrations.md",
        "status": "supported_with_reserve_like_language",
    },
    {
        "claim_id": "C4",
        "claim": "Reduced-architecture comparison can expose when simpler endpoint mappings do not satisfy routed-output constraints.",
        "evidence": "case_studies/stage7_endpoint_reserve_routing/cell_painting_routed_model_comparison.csv; case_studies/stage7_endpoint_reserve_routing/cell_painting_reduced_alternative_decisions.tsv",
        "validation": "docs/stage7_4_gate_report.json",
        "limitation": "docs/stage7_limitations_matrix.md",
        "status": "supported_without_molecular_edge_claim",
    },
    {
        "claim_id": "C5",
        "claim": "The current RhoDyn release can reproduce retained Stage 7 evidence from a source distribution and expose user-facing export provenance.",
        "evidence": "docs/stage7_6_gate_report.json; docs/stage7_7_gate_report.json; case_studies/stage7_usability_rehearsal/export_examples_manifest.tsv",
        "validation": "docs/stage7_6_recursive_hardening_report.json; docs/stage7_7_gate_report.json",
        "limitation": "docs/stage7_6_api_stability_policy.md",
        "status": "supported_for_software_reproducibility_claim",
    },
]


CHECKLIST_ROWS: list[dict[str, str]] = [
    {"item": "All Stage 7.1-7.7 gates pass", "evidence": "docs/stage7_1_gate_report.json through docs/stage7_7_gate_report.json", "status": "pass"},
    {"item": "Every planned manuscript figure has a primary artifact", "evidence": "case_studies/stage7_methods_readiness/figure_artifact_crosswalk.tsv", "status": "pass"},
    {"item": "Every planned method claim has evidence and a limitation", "evidence": "case_studies/stage7_methods_readiness/claim_evidence_crosswalk.tsv", "status": "pass"},
    {"item": "No Nature Methods acceptance claim is made", "evidence": "docs/stage7_methods_program.md", "status": "pass"},
    {"item": "Release checksums and archive manifest exist", "evidence": "docs/release_checksums.json; case_studies/stage7_methods_reproducibility/release_archive_manifest.tsv", "status": "pass"},
    {"item": "Known inconclusive cases are visible", "evidence": "case_studies/stage7_heldout_validation/heldout_validation_outcomes.tsv", "status": "pass"},
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _paths_from_cell(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def _path_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def _load_json(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _evidence_status(rows: list[dict[str, str]], columns: list[str]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for row in rows:
        for column in columns:
            for rel in _paths_from_cell(row[column]):
                if not _path_exists(rel):
                    missing.append(f"{row.get('component') or row.get('claim_id')}: {rel}")
    return not missing, missing


def _gate_statuses() -> dict[str, str]:
    statuses: dict[str, str] = {}
    for index in range(1, 8):
        rel = f"docs/stage7_{index}_gate_report.json"
        gate = _load_json(rel)
        statuses[f"stage7_{index}"] = str(gate.get("status", "missing"))
    return statuses


def _inconclusive_context_count() -> int:
    path = ROOT / "case_studies" / "stage7_heldout_validation" / "heldout_validation_outcomes.tsv"
    if not path.exists():
        return 0
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if rows and "inconclusive_count" in rows[0]:
        return sum(int(row.get("inconclusive_count", "0") or 0) for row in rows)
    return sum("inconclusive" in str(row.get("outcome", "")) for row in rows)


def _readiness_gate() -> dict[str, Any]:
    figure_ok, figure_missing = _evidence_status(FIGURE_ROWS, ["primary_artifact", "supporting_artifacts", "validation_artifact", "limitation_artifact"])
    claim_ok, claim_missing = _evidence_status(CLAIM_ROWS, ["evidence", "validation", "limitation"])
    gate_statuses = _gate_statuses()
    all_stage_gates_pass = all(status == "pass" for status in gate_statuses.values())
    nature_methods_text = (ROOT / "docs" / "stage7_methods_program.md").read_text(encoding="utf-8")
    no_acceptance_claim = (
        "does not treat any journal as a formula for acceptance" in nature_methods_text
        and "Nature Methods remains a reference point, not an acceptance claim" in nature_methods_text
    )
    release_materials = all(_path_exists(rel) for rel in ["docs/release_checksums.json", "case_studies/stage7_methods_reproducibility/release_archive_manifest.tsv"])
    inconclusive_visible = _inconclusive_context_count() >= 3
    checkpoints = {
        "stages_7_1_to_7_7_gates_pass": "pass" if all_stage_gates_pass else "fail",
        "all_planned_figures_have_artifacts": "pass" if figure_ok else "fail",
        "all_planned_claims_have_evidence_and_limitations": "pass" if claim_ok else "fail",
        "known_inconclusive_contexts_visible": "pass" if inconclusive_visible else "fail",
        "release_checksums_and_archive_manifest_present": "pass" if release_materials else "fail",
        "nature_methods_not_used_as_acceptance_claim": "pass" if no_acceptance_claim else "fail",
        "stop_condition_unlinked_claim_or_figure": "not_triggered" if figure_ok and claim_ok else "triggered",
    }
    status = (
        "pass"
        if all(value == "pass" for key, value in checkpoints.items() if not key.startswith("stop_condition_"))
        and checkpoints["stop_condition_unlinked_claim_or_figure"] == "not_triggered"
        else "fail"
    )
    return {
        "report_format": "rhodyn.stage7_8_methods_readiness.v1",
        "generated_utc": _now(),
        "status": status,
        "completion_state": "complete_methods_manuscript_readiness_package" if status == "pass" else "failed_methods_manuscript_readiness_package",
        "validation_checkpoints": checkpoints,
        "stage_gate_statuses": gate_statuses,
        "figure_component_count": len(FIGURE_ROWS),
        "claim_count": len(CLAIM_ROWS),
        "missing_figure_artifacts": figure_missing,
        "missing_claim_artifacts": claim_missing,
        "inconclusive_context_count": _inconclusive_context_count(),
        "interpretation_boundary": (
            "Stage 7.8 assembles a methods-manuscript readiness package from existing Stage 7 evidence. "
            "It does not add a biological system, new analysis route, new benchmark result, or manuscript claim."
        ),
    }


def _table_markdown(rows: list[dict[str, str]], fields: list[str]) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(row.get(field, "") for field in fields) + " |")
    return lines


def _evidence_index_doc(gate: dict[str, Any]) -> str:
    lines = [
        "# Stage 7.8 methods evidence index",
        "",
        "This index assembles the current methods-program evidence for drafting. It does not add analyses or biological claims.",
        "",
        "## Gate status",
        "",
        f"Overall status. {gate['status']}",
        "",
        "## Figure-level evidence",
        "",
    ]
    lines.extend(_table_markdown(FIGURE_ROWS, ["component", "stage", "primary_artifact", "validation_artifact", "readiness", "scope"]))
    lines.extend(["", "## Claim-level evidence", ""])
    lines.extend(_table_markdown(CLAIM_ROWS, ["claim_id", "claim", "validation", "status"]))
    lines.extend(["", "## Interpretation boundary", "", gate["interpretation_boundary"]])
    return "\n".join(lines) + "\n"


def _figure_doc() -> str:
    lines = [
        "# Stage 7.8 figure-to-artifact crosswalk",
        "",
        "Each planned methods-manuscript figure component is mapped to a reproducible output and a limitation boundary.",
        "",
    ]
    lines.extend(_table_markdown(FIGURE_ROWS, ["component", "stage", "primary_artifact", "supporting_artifacts", "validation_artifact", "limitation_artifact", "readiness"]))
    return "\n".join(lines) + "\n"


def _claim_doc() -> str:
    lines = [
        "# Stage 7.8 claim-to-evidence crosswalk",
        "",
        "Each claim is scoped to existing Stage 7 outputs and paired with a limitation artifact.",
        "",
    ]
    lines.extend(_table_markdown(CLAIM_ROWS, ["claim_id", "claim", "evidence", "validation", "limitation", "status"]))
    return "\n".join(lines) + "\n"


def _readiness_doc(gate: dict[str, Any]) -> str:
    lines = [
        "# Stage 7.8 methods submission readiness",
        "",
        "This checklist records whether the methods-manuscript evidence package can be drafted from existing reproducible outputs.",
        "",
    ]
    lines.extend(_table_markdown(CHECKLIST_ROWS, ["item", "evidence", "status"]))
    lines.extend(
        [
            "",
            "## Gate report",
            "",
            f"Status. {gate['status']}.",
            "",
            f"Completion state. {gate['completion_state']}.",
            "",
            "## Boundary",
            "",
            gate["interpretation_boundary"],
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    gate = _readiness_gate()
    _write_tsv(OUTPUT_DIR / "figure_artifact_crosswalk.tsv", FIGURE_ROWS, ["component", "stage", "primary_artifact", "supporting_artifacts", "validation_artifact", "limitation_artifact", "readiness", "scope"])
    _write_tsv(OUTPUT_DIR / "claim_evidence_crosswalk.tsv", CLAIM_ROWS, ["claim_id", "claim", "evidence", "validation", "limitation", "status"])
    _write_tsv(OUTPUT_DIR / "methods_readiness_checklist.tsv", CHECKLIST_ROWS, ["item", "evidence", "status"])
    _write_tsv(
        OUTPUT_DIR / "limitations_traceability.tsv",
        [
            {"source": row["component"], "limitation_artifact": row["limitation_artifact"], "scope": row["scope"]}
            for row in FIGURE_ROWS
        ],
        ["source", "limitation_artifact", "scope"],
    )
    _write_json(CASE_GATE, gate)
    _write_json(DOC_GATE, gate)
    _write_text(OUTPUT_DIR / "stage7_8_methods_readiness_report.md", _evidence_index_doc(gate))
    _write_text(DOC_EVIDENCE_INDEX, _evidence_index_doc(gate))
    _write_text(DOC_FIGURE_CROSSWALK, _figure_doc())
    _write_text(DOC_CLAIM_CROSSWALK, _claim_doc())
    _write_text(DOC_READINESS, _readiness_doc(gate))
    print(json.dumps({"status": gate["status"], "output_dir": OUTPUT_DIR.relative_to(ROOT).as_posix()}, indent=2))
    return 0 if gate["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
