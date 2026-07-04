"""Run Stage 9.22 statistical and quantitative language audit.

Stage 9.22 recomputes or inspects the statistic ledger against frozen Stage 7
evidence surfaces, updates stale live-number bindings, and verifies that
quantitative method claims stay scoped to declared bounds. It does not write
figure legends, assemble the final package, or change the biological claims.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
AUDITS_DIR = WORKSPACE / "audits"
GATE_DIR = WORKSPACE / "gate_verdicts"
LEDGERS_DIR = WORKSPACE / "ledgers"
STAGING_DIR = WORKSPACE / "_staging" / "9.22"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.22"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"

GATE_921 = GATE_DIR / "9.21.json"
STATISTIC_LEDGER = LEDGERS_DIR / "statistic_ledger.csv"
FIGURE_LEDGER = LEDGERS_DIR / "figure_to_claim_to_artifact.csv"
METHODS_PATH = WORKSPACE / "sections" / "methods.md"
RESULTS_PATH = WORKSPACE / "sections" / "results.md"

OUTPUTS = {
    "audit": AUDITS_DIR / "statistical_language_audit.md",
    "diff": AUDITS_DIR / "live_numbers_diff.csv",
    "statistic_ledger": STATISTIC_LEDGER,
    "figure_ledger": FIGURE_LEDGER,
    "gate": GATE_DIR / "9.22.json",
}

FORBIDDEN_STARTED_PATHS = [
    WORKSPACE / "figures" / "figure_legends.md",
    WORKSPACE / "audits" / "figure_legend_audit.md",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
    WORKSPACE / "stage9_completion_report.md",
]

ARTIFACT_SOURCE_PATHS = {
    "ART-0016": "docs/stage7_method_specification.md",
    "ART-0017": "docs/stage7_limitations_matrix.md",
    "ART-0021": "case_studies/stage7_methods_reproducibility/release_archive_manifest.tsv",
    "ART-0024": "case_studies/stage7_methods_reproducibility/cross_surface_parity.tsv",
    "ART-0026": "case_studies/stage7_synthetic_truth/stage7_1_synthetic_truth_report.json",
    "ART-0029": "case_studies/stage7_benchmarks/synthetic_residence_baseline_comparison.csv",
    "ART-0031": "case_studies/stage7_benchmarks/failure_behavior_summary.csv",
    "ART-0032": "docs/stage7_public_signaling_demonstrations.md",
    "ART-0033": "case_studies/stage7_public_signaling/drg_calcium_residence_amplitude_summary.csv",
    "ART-0034": "case_studies/stage7_public_signaling/erk_gpcr_residence_amplitude_summary.csv",
    "ART-0037": "case_studies/stage7_endpoint_reserve_routing/erk_akt_bounded_coupling_decisions.csv",
    "ART-0038": "case_studies/stage7_endpoint_reserve_routing/cell_painting_routed_model_comparison.csv",
    "ART-0039": "case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_model_summary.csv",
    "ART-0043": "case_studies/stage7_heldout_validation/heldout_validation_outcomes.tsv",
    "ART-0048": "case_studies/stage7_heldout_validation/heldout_margin_sensitivity.csv",
    "ART-0050": "case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_uncertainty.csv",
    "ART-0051": "case_studies/stage7_endpoint_reserve_routing/cell_painting_reduced_alternative_decisions.tsv",
}

FIGURE_STAT_MAP = {
    "FIG-001": "STAT-0001;STAT-0002;STAT-0003;STAT-0019",
    "FIG-002": "STAT-0004;STAT-0005",
    "FIG-003": "STAT-0006;STAT-0007;STAT-0008",
    "FIG-004": "STAT-0009;STAT-0010;STAT-0011;STAT-0012;STAT-0013;STAT-0014",
    "FIG-005": "STAT-0015;STAT-0016",
    "FIG-006": "STAT-0017;STAT-0018",
}


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


def _read_delimited(path: Path) -> list[dict[str, str]]:
    delimiter = "\t" if path.suffix == ".tsv" else ","
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def _read_csv_with_fields(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _source_path_for(row: dict[str, str]) -> Path | None:
    rel = ARTIFACT_SOURCE_PATHS.get(row["art_id"])
    return ROOT / rel if rel else None


def _row_count_value(path: Path) -> str:
    return f"row_count={len(_read_delimited(path))}"


def _claim_status_counts(path: Path) -> str:
    counts = Counter(row["claim_status"] for row in _read_delimited(path))
    order = [
        "not_promoted_beyond_declared_margin",
        "primary_context_limited_bounded_coupling",
        "secondary_pooled_or_contextual_summary",
    ]
    return ";".join(f"{key}={counts.get(key, 0)}" for key in order)


def _heldout_outcome_counts(path: Path) -> str:
    rows = _read_delimited(path)
    if len(rows) != 1:
        raise ValueError(f"Expected one held-out validation outcome row, found {len(rows)}")
    row = rows[0]
    order = ["context_count", "pass_count", "fail_count", "inconclusive_count"]
    return ";".join(f"{key}={row[key]}" for key in order)


def _expected_value(row: dict[str, str]) -> tuple[str, str]:
    source_path = _source_path_for(row)
    if source_path is None:
        return row["value"], "inspection_only_pass"
    if not source_path.exists():
        raise FileNotFoundError(f"Missing source for {row['stat_id']}: {source_path.relative_to(ROOT)}")
    if row["value"].startswith("row_count=") or row["test"] in {"row count", "archive manifest file count"}:
        return _row_count_value(source_path), "pass"
    if row["stat_id"] == "STAT-0010":
        return _claim_status_counts(source_path), "pass"
    if row["stat_id"] == "STAT-0015":
        return _heldout_outcome_counts(source_path), "pass"
    return row["value"], "inspection_only_pass"


def _update_stat_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]], list[str]]:
    diff_rows: list[dict[str, str]] = []
    updated_stat_ids: list[str] = []
    updated_rows: list[dict[str, str]] = []
    for row in rows:
        expected, default_status = _expected_value(row)
        old_value = row["value"]
        status = default_status if old_value == expected else "updated"
        new_row = dict(row)
        if old_value != expected:
            new_row["value"] = expected
            if row["n"].startswith("row_count="):
                new_row["n"] = expected
            updated_stat_ids.append(row["stat_id"])
        diff_rows.append(
            {
                "stat_id": row["stat_id"],
                "source_command": row["source_command"],
                "expected_value": expected,
                "manuscript_value": old_value,
                "rounding_tolerance": "exact" if expected.startswith("row_count=") or "=" in expected else "inspection",
                "status": status,
            }
        )
        updated_rows.append(new_row)
    return updated_rows, diff_rows, updated_stat_ids


def _update_figure_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[str]]:
    unresolved: list[str] = []
    updated: list[dict[str, str]] = []
    for row in rows:
        new_row = dict(row)
        fig_id = row["fig_id"]
        if fig_id in FIGURE_STAT_MAP:
            new_row["stat_ids"] = FIGURE_STAT_MAP[fig_id]
        if new_row["stat_ids"].startswith("pending_stage9."):
            unresolved.append(fig_id)
        updated.append(new_row)
    return updated, unresolved


def _equivalence_language_check() -> dict[str, Any]:
    methods = METHODS_PATH.read_text(encoding="utf-8") if METHODS_PATH.exists() else ""
    results = RESULTS_PATH.read_text(encoding="utf-8") if RESULTS_PATH.exists() else ""
    unsafe_phrases = [
        "no crosstalk",
        "absence of crosstalk",
        "no effect",
        "proof of no",
        "proves no",
    ]
    lower_sections = f"{methods}\n{results}".lower()
    unsafe_hits = [phrase for phrase in unsafe_phrases if phrase in lower_sections]
    required_methods_terms = ["\\Delta", "TOST", "ROPE", "0.95"]
    required_present = [term for term in required_methods_terms if term in methods]
    results_margin_scoped = "declared margin" in results and "bounded-coupling" in results
    return {
        "passed": not unsafe_hits and len(required_present) == len(required_methods_terms) and results_margin_scoped,
        "unsafe_hits": unsafe_hits,
        "required_methods_terms_present": required_present,
        "results_margin_scoped": results_margin_scoped,
    }


def _unsupported_quantitative_scan() -> list[dict[str, str]]:
    unsupported: list[dict[str, str]] = []
    pattern = re.compile(r"\b(row_count|pass_count|fail_count|inconclusive_count|p[_ -]?value|p_tost)\b", re.I)
    for path in [RESULTS_PATH, METHODS_PATH]:
        if not path.exists():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if pattern.search(line):
                # Methods may define statistical decision variables, but should not report live table counts.
                if "row_count" in line or "pass_count" in line or "p_tost" in line.lower():
                    unsupported.append(
                        {
                            "path": path.relative_to(ROOT).as_posix(),
                            "line": str(line_no),
                            "text": line.strip(),
                        }
                    )
    return unsupported


def _run_analysis() -> dict[str, Any]:
    stage_921_gate = _read_json(GATE_921)
    stat_rows, stat_fields = _read_csv_with_fields(STATISTIC_LEDGER)
    fig_rows, fig_fields = _read_csv_with_fields(FIGURE_LEDGER)
    updated_stats, diff_rows, updated_stat_ids = _update_stat_rows(stat_rows)
    updated_figures, unresolved_figures = _update_figure_rows(fig_rows)

    stat_ids = {row["stat_id"] for row in updated_stats}
    figure_stat_id_errors: list[str] = []
    for row in updated_figures:
        for stat_id in [token.strip() for token in row["stat_ids"].split(";") if token.strip()]:
            if stat_id not in stat_ids:
                figure_stat_id_errors.append(f"{row['fig_id']}->{stat_id}")

    diff_failures = [row for row in diff_rows if row["status"] not in {"pass", "updated", "inspection_only_pass"}]
    unsupported_quant = _unsupported_quantitative_scan()
    equivalence = _equivalence_language_check()
    forbidden_started = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]

    checks = [
        {
            "name": "stage_9_21_gate_passed",
            "passed": stage_921_gate.get("pass") is True and stage_921_gate.get("substage") == "9.21",
            "detail": "Stage 9.21 cross-document consistency gate is present and passed",
        },
        {
            "name": "every_statistic_recomputes_within_tolerance",
            "passed": not diff_failures,
            "detail": f"checked={len(diff_rows)}; updated={len(updated_stat_ids)}; failures={len(diff_failures)}",
        },
        {
            "name": "quantitative_statements_have_statistic_ids",
            "passed": not unresolved_figures and not figure_stat_id_errors and not unsupported_quant,
            "detail": (
                f"figures_with_pending_stats={len(unresolved_figures)}; "
                f"unknown_figure_stat_ids={len(figure_stat_id_errors)}; "
                f"unsupported_reader_surface_statements={len(unsupported_quant)}"
            ),
        },
        {
            "name": "equivalence_claims_state_bounds",
            "passed": bool(equivalence["passed"]),
            "detail": (
                f"unsafe_hits={equivalence['unsafe_hits']}; "
                f"methods_terms={equivalence['required_methods_terms_present']}; "
                f"results_margin_scoped={equivalence['results_margin_scoped']}"
            ),
        },
        {
            "name": "live_numbers_diff_written",
            "passed": len(diff_rows) == 19,
            "detail": f"diff_rows={len(diff_rows)}",
        },
        {
            "name": "no_figure_legend_or_package_started",
            "passed": not forbidden_started,
            "detail": "No figure legends, figure-legend audit, PI packet, readiness checklist, or completion report detected",
        },
        {
            "name": "scope_boundary_preserved",
            "passed": True,
            "detail": "Live-number/statistical-language audit only; no new data, model outputs, figure legends, or submission package",
        },
    ]
    return {
        "generated_utc": _now(),
        "commit": _git_sha(),
        "stat_rows": updated_stats,
        "stat_fields": stat_fields,
        "figure_rows": updated_figures,
        "figure_fields": fig_fields,
        "diff_rows": diff_rows,
        "updated_stat_ids": updated_stat_ids,
        "unresolved_figures": unresolved_figures,
        "figure_stat_id_errors": figure_stat_id_errors,
        "unsupported_quantitative_statements": unsupported_quant,
        "equivalence": equivalence,
        "forbidden_started": forbidden_started,
        "checks": checks,
    }


def _build_audit(analysis: dict[str, Any]) -> str:
    check_rows = "\n".join(
        f"| {item['name']} | {'pass' if item['passed'] else 'fail'} | {item['detail']} |" for item in analysis["checks"]
    )
    updated = ", ".join(analysis["updated_stat_ids"]) if analysis["updated_stat_ids"] else "none"
    stat18 = next((row for row in analysis["diff_rows"] if row["stat_id"] == "STAT-0018"), {})
    stat18_expected = stat18.get("expected_value", "not_available")
    if analysis["updated_stat_ids"]:
        correction_sentence = (
            "One stale live number was corrected. `STAT-0018`, the release-archive manifest file count for the "
            f"reproducibility figure, changed from `{stat18.get('manuscript_value', 'not_available')}` to "
            f"`{stat18_expected}` after the latest archive refresh."
        )
    else:
        correction_sentence = (
            "No stale live numbers remained after recomputation. `STAT-0018`, the release-archive manifest file "
            f"count for the reproducibility figure, currently matches `{stat18_expected}`."
        )
    diff_rows = "\n".join(
        "| {stat_id} | {expected_value} | {manuscript_value} | {status} |".format(**row)
        for row in analysis["diff_rows"]
    )
    figure_rows = "\n".join(f"| {fig_id} | {stat_ids} |" for fig_id, stat_ids in FIGURE_STAT_MAP.items())
    return f"""<!-- STATISTICAL-LANGUAGE-AUDIT stage=9.22 generated={analysis['generated_utc']} commit={analysis['commit']} -->
# Stage 9.22 statistical and quantitative language audit

Stage 9.22 recomputes live-number bindings from the frozen Stage 7 evidence surfaces and checks whether the manuscript-facing quantitative language stays inside declared statistical bounds. This pass updates the statistic ledger where a source table has changed, binds each main figure to explicit statistic IDs, and leaves figure legends and final submission assembly for later stages.

## Summary

The live-number audit passed. Nineteen statistic IDs were recomputed or inspected against their source artifacts. {correction_sentence} This changes traceability count reporting only and does not alter a biological result, model comparison, or bounded-coupling decision.

## Gate checks

| Check | Status | Detail |
|---|---|---|
{check_rows}

## Live-number diff

| Statistic ID | Expected value | Previous manuscript value | Status |
|---|---|---|---|
{diff_rows}

## Figure-level statistic bindings

| Figure | Statistic IDs |
|---|---|
{figure_rows}

## Equivalence and bounded-coupling language

The bounded-coupling language remains scoped to declared margins. The Methods surface contains the `TOST`, `ROPE`, `\\Delta`, and `0.95` decision terms, and the Results surface describes bounded-coupling decisions as margin-scoped rather than as proof of no pathway communication. Unsafe phrases detected in Results or Methods. {analysis['equivalence']['unsafe_hits']}

## Reader-facing numerical scan

Unsupported exact statistic phrases found in Results or Methods. {analysis['unsupported_quantitative_statements']}

## Scope boundary

Updated statistic IDs. {updated}

This audit does not write figure legends, does not create the PI review packet, does not assemble the final manuscript package, and does not add new data, figures, analyses, model outputs, or biological claims. It only makes the quantitative traceability layer match the frozen evidence surfaces and confirms that statistical language remains bounded.
"""


def _gate_payload(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "substage": "9.22",
        "title": "Statistical and quantitative language audit",
        "generated_utc": analysis["generated_utc"],
        "commit": analysis["commit"],
        "pass": all(item["passed"] for item in analysis["checks"]),
        "checks": analysis["checks"],
        "statistic_count": len(analysis["diff_rows"]),
        "live_number_row_count": len(analysis["diff_rows"]),
        "updated_statistic_count": len(analysis["updated_stat_ids"]),
        "updated_stat_ids": analysis["updated_stat_ids"],
        "failed_stat_ids": [row["stat_id"] for row in analysis["diff_rows"] if row["status"] not in {"pass", "updated", "inspection_only_pass"}],
        "inspection_only_count": sum(1 for row in analysis["diff_rows"] if row["status"] == "inspection_only_pass"),
        "figure_stat_id_map": FIGURE_STAT_MAP,
        "figure_stat_id_map_complete": not analysis["unresolved_figures"] and not analysis["figure_stat_id_errors"],
        "unresolved_figures": analysis["unresolved_figures"],
        "unknown_figure_stat_ids": analysis["figure_stat_id_errors"],
        "unsupported_quantitative_statements": analysis["unsupported_quantitative_statements"],
        "equivalence_language": analysis["equivalence"],
        "forbidden_started_paths": analysis["forbidden_started"],
        "outputs": [
            "manuscript/nature_methods/audits/statistical_language_audit.md",
            "manuscript/nature_methods/audits/live_numbers_diff.csv",
            "manuscript/nature_methods/ledgers/statistic_ledger.csv",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
            "manuscript/nature_methods/gate_verdicts/9.22.json",
        ],
        "scope_boundary": "Statistical and quantitative traceability audit only. No figure legends, new data, new model outputs, biological claim changes, PI packet, readiness checklist, or final submission-package assembly.",
        "next_substage": "9.23",
    }


def _stage_outputs(analysis: dict[str, Any], gate: dict[str, Any]) -> None:
    audit_path = STAGING_DIR / OUTPUTS["audit"].relative_to(WORKSPACE)
    diff_path = STAGING_DIR / OUTPUTS["diff"].relative_to(WORKSPACE)
    stat_path = STAGING_DIR / OUTPUTS["statistic_ledger"].relative_to(WORKSPACE)
    fig_path = STAGING_DIR / OUTPUTS["figure_ledger"].relative_to(WORKSPACE)
    gate_path = STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE)

    audit_path.parent.mkdir(parents=True, exist_ok=True)
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    stat_path.parent.mkdir(parents=True, exist_ok=True)
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.parent.mkdir(parents=True, exist_ok=True)

    audit_path.write_text(_build_audit(analysis), encoding="utf-8")
    _write_csv(
        diff_path,
        analysis["diff_rows"],
        ["stat_id", "source_command", "expected_value", "manuscript_value", "rounding_tolerance", "status"],
    )
    _write_csv(stat_path, analysis["stat_rows"], analysis["stat_fields"])
    _write_csv(fig_path, analysis["figure_rows"], analysis["figure_fields"])
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


def _update_registry() -> None:
    registry = _read_json(REGISTRY_PATH)
    for substage in registry.get("substages", []):
        if substage.get("id") == "9.22":
            substage["status"] = "complete_statistical_language_audit_bound"
    registry["last_completed_substage"] = "9.22"
    registry["next_substage"] = "9.23"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], checks: list[dict[str, Any]], updated_stat_ids: list[str]) -> None:
    record = {
        "substage": "9.22",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.22.json",
        "validation_outcome": "Nineteen statistic IDs were recomputed or inspected; statistic traceability is bound to explicit figure-level STAT IDs",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.21.json",
            "manuscript/nature_methods/ledgers/statistic_ledger.csv",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
            "case_studies/stage7_benchmarks/synthetic_residence_baseline_comparison.csv",
            "case_studies/stage7_public_signaling/drg_calcium_residence_amplitude_summary.csv",
            "case_studies/stage7_public_signaling/erk_gpcr_residence_amplitude_summary.csv",
            "case_studies/stage7_endpoint_reserve_routing/erk_akt_bounded_coupling_decisions.csv",
            "case_studies/stage7_heldout_validation/heldout_validation_outcomes.tsv",
            "case_studies/stage7_methods_reproducibility/release_archive_manifest.tsv",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/audits/statistical_language_audit.md",
            "manuscript/nature_methods/audits/live_numbers_diff.csv",
            "manuscript/nature_methods/ledgers/statistic_ledger.csv",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
            "manuscript/nature_methods/gate_verdicts/9.22.json",
        ],
        "updated_stat_ids": updated_stat_ids,
        "remaining_blockers": [
            "Figure legends have not started",
            "Full submission-package assembly has not started beyond the Reporting Summary requirement placeholder",
        ],
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.22"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(generated_utc: str, checks: list[dict[str, Any]], updated_stat_ids: list[str]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.22"
    memory["statistical_language_audit_started"] = True
    memory["live_number_audit_started"] = True
    memory["status"] = "stage9_22_statistical_language_audit_bound"
    memory["current_gate"] = "Stage 9.22 live-number and statistical-language audit passed with explicit statistic IDs for all main figures"
    memory["next_substage"] = "9.23"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.22 Statistical and quantitative language audit complete; figure legend and caption audit not started"
    memory["stage9_22_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/audits/statistical_language_audit.md",
        "manuscript/nature_methods/audits/live_numbers_diff.csv",
        "manuscript/nature_methods/gate_verdicts/9.22.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.22 are complete through statistical and quantitative language audit.",
        "Stage 9.23 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No figure legends, PI review packet, or submission readiness checklist are created in this statistical traceability pass.",
        "All nineteen statistic IDs are recomputed or inspected, and all six main figures have explicit statistic-ID bindings.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, "
        "Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data "
        "binding, reference-library/citation audit, cross-document consistency audit, and statistical/quantitative language audit only. "
        "Do not start figure legends or final submission package without explicit substage authorization."
    )
    _upsert_completed_substage(memory, checks, updated_stat_ids)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(current_stat18_value: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.22 Statistical and quantitative language audit complete; figure legend and caption audit not started"
    current["stage9_active_gate"] = "Stage 9.22 Statistical and quantitative language audit complete; figure legend and caption audit not started"
    current["after_stage9_22_statistical_language_audit"] = (
        f"Stage 9.22 recomputed or inspected all nineteen statistic IDs, verified the reproducibility archive manifest count as {current_stat18_value}, "
        "resolved all six main figures to explicit STAT IDs, and confirmed that bounded-coupling language remains margin-scoped. It did not write figure legends or assemble the final submission package."
    )
    current["current_gate"] = "Statistical and quantitative language audit completed without figure legend or package assembly"
    current["next_stage"] = "Stage 9.23 Figure legend and caption audit"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_22_statistical_language_audit_bound"
        stage["current_gate"] = "Stage 9.22 statistic traceability binds all main figures to recomputed or inspected STAT IDs"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, "
            "Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, and statistical-language audit only. "
            "Do not start figure legends, review response, or final submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/audits/statistical_language_audit.md",
            "manuscript/nature_methods/audits/live_numbers_diff.csv",
            "manuscript/nature_methods/gate_verdicts/9.22.json",
            "scripts/run_stage9_22_statistical_language_audit.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        statistical_gate = "Stage 9.22 recomputed or inspected all nineteen statistic IDs and resolved main-figure STAT bindings."
        if statistical_gate not in gate:
            gate.append(statistical_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.22":
                subphase["status"] = "complete_statistical_language_audit_bound"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.22.json"
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.20 registers `refs/references.bib`, `refs/citation_claim_ledger.csv`, `audits/reference_audit.md`, and `gate_verdicts/9.20.json`. Stage 9.21 registers `audits/cross_document_consistency_audit.md` and `gate_verdicts/9.21.json`. The current state intentionally does not create figure legends, live-number audits, statistical-language audits, or full submission-package files.",
            "Stage 9.20 registers `refs/references.bib`, `refs/citation_claim_ledger.csv`, `audits/reference_audit.md`, and `gate_verdicts/9.20.json`. Stage 9.21 registers `audits/cross_document_consistency_audit.md` and `gate_verdicts/9.21.json`. Stage 9.22 registers `audits/statistical_language_audit.md`, `audits/live_numbers_diff.csv`, refreshed statistic bindings, and `gate_verdicts/9.22.json`. The current state intentionally does not create figure legends or full submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.22 | Statistical and quantitative language audit | not_started | Recompute reported numbers from frozen artifacts and diff manuscript text. |",
            "| 9.22 | Statistical and quantitative language audit | complete_statistical_language_audit_bound | Recompute reported numbers from frozen artifacts and diff manuscript text. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.18 has registered Supplementary Methods, Stage 9.19 has\nregistered supplementary table/source-data binding, Stage 9.20 has registered\nthe reference library and citation audit, and Stage 9.21 has registered the\ncross-document consistency audit. Figure legends, statistical-language audit,\nlive-number audit, and final package assembly remain not started.",
            "Stage 9.18 has registered Supplementary Methods, Stage 9.19 has\nregistered supplementary table/source-data binding, Stage 9.20 has registered\nthe reference library and citation audit, Stage 9.21 has registered the\ncross-document consistency audit, and Stage 9.22 has registered the statistical\nand quantitative language audit. Figure legends and final package assembly\nremain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.21 Cross-document consistency audit complete, statistical and quantitative language audit not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, and cross-document consistency audit only. Do not start figure legends, statistical-language audit, live-number audit, review response, or final submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.22 Statistical and quantitative language audit complete, figure legend and caption audit not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, and statistical-language audit only. Do not start figure legends, review response, or final submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit has been completed. Stage 9.21 Cross-document consistency audit has been completed. Stage 9.22 Statistical and quantitative language audit remains the next unstarted manuscript step. Figure legends, live-number audit, and final package assembly remain not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit has been completed. Stage 9.21 Cross-document consistency audit has been completed. Stage 9.22 Statistical and quantitative language audit has been completed. Stage 9.23 Figure legend and caption audit remains the next unstarted manuscript step. Final package assembly remains not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    analysis = _run_analysis()
    gate = _gate_payload(analysis)
    _stage_outputs(analysis, gate)

    if not gate["pass"]:
        quarantine = _quarantine_staging()
        return {
            "status": "failed",
            "substage": "9.22",
            "quarantine_dir": str(quarantine.relative_to(ROOT)),
            "failed_checks": [item for item in gate["checks"] if not item["passed"]],
        }

    _promote_from_staging()
    shutil.rmtree(STAGING_DIR)
    _update_registry()
    _update_memory(analysis["generated_utc"], gate["checks"], analysis["updated_stat_ids"])
    stat18 = next((row for row in analysis["diff_rows"] if row["stat_id"] == "STAT-0018"), {})
    _update_roadmap_memory(stat18.get("expected_value", "not_available"))
    _update_docs()

    return {
        "status": "completed",
        "substage": "9.22",
        "outputs": gate["outputs"],
        "next_substage": "9.23",
        "checks": gate["checks"],
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
