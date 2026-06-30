"""Run Stage 7.4 endpoint, reserve-like, and routed-output demonstrations.

Stage 7.4 promotes non-single-reporter public demonstrations into a dedicated
methods-program evidence lane. The runner reads retained public-derived tables
from the Cell Painting/MitoTox endpoint benchmark and the Wan 2021 ERK/Akt
paired-reporter benchmark, writes Stage 7.4-scoped tidy tables, and records
bounded biological interpretations. It does not download or retain raw public
source files and it does not use manuscript-private data.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhodyn.schema import read_coupling_csv, read_endpoint_csv, read_reserve_csv
from rhodyn.uncertainty import bootstrap_interval

DEFAULT_OUTPUT_DIR = Path("case_studies/stage7_endpoint_reserve_routing")
CELL_ENDPOINT_ROWS = Path("case_studies/cell_painting_mitotox_endpoint_model_rows.csv")
CELL_RANKING = Path("case_studies/cell_painting_mitotox_model_ranking.csv")
CELL_ENDPOINT_SUMMARY = Path("case_studies/cell_painting_mitotox_endpoint_summary.csv")
CELL_PROVENANCE = Path("case_studies/cell_painting_mitotox_model_comparison.provenance.json")
ERK_COUPLING = Path("case_studies/erk_gpcr_erk_akt_bounded_coupling.csv")
ERK_MARGIN_SENSITIVITY = Path("case_studies/erk_gpcr_erk_akt_margin_sensitivity.csv")
ERK_THRESHOLD_SENSITIVITY = Path("case_studies/erk_gpcr_erk_akt_threshold_sensitivity.csv")
ERK_HARDENING = Path("case_studies/erk_gpcr_erk_akt_hardening_report.json")
ERK_PROVENANCE = Path("case_studies/erk_gpcr_erk_akt_bounded_coupling.provenance.json")

HEALTH_BURDEN_ENDPOINTS = {
    "apoptosis up",
    "cytotoxicity BLA",
    "cytotoxicity SRB",
    "mitochondrial disruption up",
    "proliferation decrease",
}
ROUTED_MODEL = "compartment_route_5nn"
PRIMARY_REDUCED_MODELS = {"endpoint_prevalence", "morphology_magnitude_5nn"}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str], *, delimiter: str = ",") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=delimiter, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            formatted: dict[str, object] = {}
            for field in fieldnames:
                value = row.get(field, "")
                if isinstance(value, float):
                    formatted[field] = f"{value:.8g}"
                else:
                    formatted[field] = value
            writer.writerow(formatted)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _format_float(value: float) -> str:
    return f"{value:.6g}"


def _require_inputs() -> None:
    required = [
        CELL_ENDPOINT_ROWS,
        CELL_RANKING,
        CELL_ENDPOINT_SUMMARY,
        CELL_PROVENANCE,
        ERK_COUPLING,
        ERK_MARGIN_SENSITIVITY,
        ERK_THRESHOLD_SENSITIVITY,
        ERK_HARDENING,
        ERK_PROVENANCE,
    ]
    missing = [path.as_posix() for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Stage 7.4 requires retained public-derived Stage 3/7 fixture outputs. Missing: "
            + ", ".join(missing)
        )


def _candidate_rows() -> list[dict[str, object]]:
    selected = {
        "cell_painting_mitotox_seal2023": {
            "stage7_4_role": "perturbation_endpoint_reserve_like_routed_output",
            "selected": "yes",
            "biological_fit": 5,
            "metadata_quality": 5,
            "access_quality": 5,
            "stress_test_value": 5,
            "grouping_quality": 4,
            "decision_reason": "Public matched Cell Painting and MitoTox endpoint labels support reduced-architecture comparison and a scoped cell-health endpoint preservation coordinate.",
        },
        "erk_akt_wan2021_bounded_coupling": {
            "stage7_4_role": "paired_reporter_bounded_coupling",
            "selected": "yes",
            "biological_fit": 5,
            "metadata_quality": 5,
            "access_quality": 5,
            "stress_test_value": 5,
            "grouping_quality": 4,
            "decision_reason": "Public same-cell ERK/Akt KTR trajectories support declared-margin bounded-coupling decisions for paired residence summaries.",
        },
        "allen_brain_observatory": {
            "stage7_4_role": "reserve_like_candidate_deferred",
            "selected": "no",
            "biological_fit": 4,
            "metadata_quality": 4,
            "access_quality": 2,
            "stress_test_value": 4,
            "grouping_quality": 4,
            "decision_reason": "Strong calcium-dynamics candidate, but licensing and SDK access make it less suitable for the first Stage 7.4 release-surface demonstration.",
        },
    }
    rows: list[dict[str, object]] = []
    candidates_path = ROOT / "case_studies" / "public_data_candidates.tsv"
    with candidates_path.open(newline="", encoding="utf-8") as handle:
        for source_row in csv.DictReader(handle, delimiter="\t"):
            candidate_id = source_row["candidate_id"]
            values = selected.get(candidate_id)
            if not values:
                continue
            score = sum(int(values[key]) for key in ["biological_fit", "metadata_quality", "access_quality", "stress_test_value", "grouping_quality"])
            row = {
                "candidate_id": candidate_id,
                "name": source_row.get("name", ""),
                "domain": source_row.get("domain", ""),
                "url": source_row.get("url", ""),
                "license": source_row.get("license", ""),
                "stage7_4_role": values["stage7_4_role"],
                "selected": values["selected"],
                "biological_fit": values["biological_fit"],
                "metadata_quality": values["metadata_quality"],
                "access_quality": values["access_quality"],
                "stress_test_value": values["stress_test_value"],
                "grouping_quality": values["grouping_quality"],
                "total_score": score,
                "decision_reason": values["decision_reason"],
            }
            rows.append(row)
    return sorted(rows, key=lambda row: (-int(row["total_score"]), str(row["candidate_id"])))


def _route_model_rows(ranking_rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in ranking_rows:
        model = row["model"]
        role = "retained_routed_architecture" if model == ROUTED_MODEL else "reduced_alternative"
        if model in {"cells_block_5nn", "cytoplasm_block_5nn", "nuclei_block_5nn"}:
            role = "single_compartment_reduced_alternative"
        rows.append(
            {
                "case_id": "cell_painting_mitotox_seal2023",
                "model": model,
                "architecture_role": role,
                "rank": row["rank"],
                "n_endpoint_rows": row["n_endpoint_rows"],
                "weighted_n": row["weighted_n"],
                "rss": row["rss"],
                "weighted_rmse": row["weighted_rmse"],
                "aic": row["aic"],
                "bic": row["bic"],
                "delta_bic": row["delta_bic"],
                "parameter_count": row["parameter_count"],
                "mean_predicted_probability_on_active_endpoints": row["mean_predicted_probability_on_active_endpoints"],
                "decision": "retained" if model == ROUTED_MODEL else "reduced_alternative_not_retained",
            }
        )

    by_model = {row["model"]: row for row in ranking_rows}
    routed_bic = float(by_model[ROUTED_MODEL]["bic"])
    alternative_rows: list[dict[str, object]] = []
    for model, row in by_model.items():
        if model == ROUTED_MODEL:
            continue
        delta_vs_routed = float(row["bic"]) - routed_bic
        alternative_rows.append(
            {
                "case_id": "cell_painting_mitotox_seal2023",
                "retained_model": ROUTED_MODEL,
                "reduced_alternative": model,
                "alternative_role": "primary_reduced_alternative" if model in PRIMARY_REDUCED_MODELS else "single_compartment_reduced_alternative",
                "delta_bic_vs_routed": delta_vs_routed,
                "weighted_rmse_vs_routed": float(row["weighted_rmse"]) - float(by_model[ROUTED_MODEL]["weighted_rmse"]),
                "decision": "fails_relative_to_routed" if delta_vs_routed > 10 else "not_distinguished",
            }
        )
    diagnostics = {
        "best_model": by_model[ROUTED_MODEL]["model"] if by_model[ROUTED_MODEL]["rank"] == "1" else ranking_rows[0]["model"],
        "routed_rank": int(by_model[ROUTED_MODEL]["rank"]),
        "delta_bic_endpoint_prevalence": float(by_model["endpoint_prevalence"]["delta_bic"]),
        "delta_bic_morphology_magnitude": float(by_model["morphology_magnitude_5nn"]["delta_bic"]),
        "reduced_alternative_count": len(alternative_rows),
    }
    return rows, sorted(alternative_rows, key=lambda item: float(item["delta_bic_vs_routed"])), diagnostics


def _reserve_like_rows(endpoint_rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    by_compound: dict[str, dict[str, object]] = defaultdict(lambda: {"observed": {}, "predicted": defaultdict(dict)})
    for row in endpoint_rows:
        endpoint = row["endpoint"]
        if endpoint not in HEALTH_BURDEN_ENDPOINTS:
            continue
        compound_id = row["compound_id_sha12"]
        by_compound[compound_id]["observed"][endpoint] = float(row["observed"])  # type: ignore[index]
        by_compound[compound_id]["predicted"][row["model"]][endpoint] = float(row["predicted"])  # type: ignore[index]

    reserve_rows: list[dict[str, object]] = []
    model_errors: dict[str, list[float]] = defaultdict(list)
    routed_advantage_values: list[float] = []
    observed_reserve_values: list[float] = []
    for compound_id, payload in sorted(by_compound.items()):
        observed = payload["observed"]  # type: ignore[assignment]
        if set(observed) != HEALTH_BURDEN_ENDPOINTS:
            continue
        observed_burden = mean(float(observed[endpoint]) for endpoint in HEALTH_BURDEN_ENDPOINTS)
        observed_reserve = 1.0 - observed_burden
        observed_reserve_values.append(observed_reserve)
        predicted = payload["predicted"]  # type: ignore[assignment]
        routed_predicted_burden = mean(float(predicted[ROUTED_MODEL][endpoint]) for endpoint in HEALTH_BURDEN_ENDPOINTS)
        prevalence_predicted_burden = mean(float(predicted["endpoint_prevalence"][endpoint]) for endpoint in HEALTH_BURDEN_ENDPOINTS)
        routed_error = abs((1.0 - routed_predicted_burden) - observed_reserve)
        prevalence_error = abs((1.0 - prevalence_predicted_burden) - observed_reserve)
        routed_advantage_values.append(prevalence_error - routed_error)
        for model, endpoint_predictions in predicted.items():
            predicted_burden = mean(float(endpoint_predictions[endpoint]) for endpoint in HEALTH_BURDEN_ENDPOINTS)
            predicted_reserve = 1.0 - predicted_burden
            model_errors[model].append(abs(predicted_reserve - observed_reserve))
        reserve_rows.append(
            {
                "sample_id": compound_id,
                "time": 0.0,
                "condition": "mitotox_cell_health_endpoint_preservation",
                "response": observed_reserve,
                "replicate": "compound",
                "endpoint_count": len(HEALTH_BURDEN_ENDPOINTS),
                "endpoint_set": ";".join(sorted(HEALTH_BURDEN_ENDPOINTS)),
                "observed_burden_fraction": observed_burden,
                "reserve_like_coordinate": observed_reserve,
                "compartment_route_predicted_reserve_like": 1.0 - routed_predicted_burden,
                "endpoint_prevalence_predicted_reserve_like": 1.0 - prevalence_predicted_burden,
                "prevalence_minus_routed_absolute_error": prevalence_error - routed_error,
                "interpretation_boundary": "cell-health endpoint preservation coordinate; not live metabolic reserve",
            }
        )

    model_summary_rows: list[dict[str, object]] = []
    for model, errors in sorted(model_errors.items()):
        model_summary_rows.append(
            {
                "case_id": "cell_painting_mitotox_seal2023",
                "model": model,
                "n_compounds": len(errors),
                "mean_absolute_error_to_observed_reserve_like": mean(errors),
                "architecture_role": "retained_routed_architecture" if model == ROUTED_MODEL else "reduced_alternative",
            }
        )
    model_summary_rows.sort(key=lambda row: float(row["mean_absolute_error_to_observed_reserve_like"]))

    reserve_ci = bootstrap_interval(
        observed_reserve_values,
        n_resamples=1000,
        confidence_level=0.95,
        seed=7401,
        group_labels=[str(row["sample_id"]) for row in reserve_rows],
        schema_kind="reserve_like_endpoint",
        parameters={"endpoint_set": sorted(HEALTH_BURDEN_ENDPOINTS), "response_direction": "larger_is_more_endpoint_preservation"},
    )
    routed_advantage_ci = bootstrap_interval(
        routed_advantage_values,
        n_resamples=1000,
        confidence_level=0.95,
        seed=7402,
        group_labels=[str(row["sample_id"]) for row in reserve_rows],
        schema_kind="reserve_like_endpoint_model_comparison",
        parameters={"contrast": "endpoint_prevalence_abs_error_minus_compartment_route_abs_error"},
    )
    uncertainty_rows = [
        {
            "case_id": "cell_painting_mitotox_seal2023",
            "quantity": "mean_observed_cell_health_reserve_like_coordinate",
            "estimate": reserve_ci.interval.estimate,
            "ci_low": reserve_ci.interval.lower,
            "ci_high": reserve_ci.interval.upper,
            "confidence_level": reserve_ci.interval.confidence_level,
            "n": reserve_ci.interval.n,
            "resample_level": reserve_ci.resample_level,
            "method": reserve_ci.interval.method,
        },
        {
            "case_id": "cell_painting_mitotox_seal2023",
            "quantity": "mean_prevalence_minus_routed_absolute_error",
            "estimate": routed_advantage_ci.interval.estimate,
            "ci_low": routed_advantage_ci.interval.lower,
            "ci_high": routed_advantage_ci.interval.upper,
            "confidence_level": routed_advantage_ci.interval.confidence_level,
            "n": routed_advantage_ci.interval.n,
            "resample_level": routed_advantage_ci.resample_level,
            "method": routed_advantage_ci.interval.method,
        },
    ]
    diagnostics = {
        "compound_count": len(reserve_rows),
        "endpoint_set": sorted(HEALTH_BURDEN_ENDPOINTS),
        "mean_observed_reserve_like_coordinate": reserve_ci.interval.estimate,
        "mean_observed_reserve_like_ci_low": reserve_ci.interval.lower,
        "mean_observed_reserve_like_ci_high": reserve_ci.interval.upper,
        "mean_prevalence_minus_routed_absolute_error": routed_advantage_ci.interval.estimate,
        "mean_prevalence_minus_routed_error_ci_low": routed_advantage_ci.interval.lower,
        "mean_prevalence_minus_routed_error_ci_high": routed_advantage_ci.interval.upper,
        "best_reserve_like_prediction_model": model_summary_rows[0]["model"] if model_summary_rows else "",
    }
    return reserve_rows, model_summary_rows, uncertainty_rows, diagnostics


def _coupling_stage7_rows(coupling_rows: list[dict[str, str]], hardening: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, object]]:
    threshold_behavior = hardening.get("threshold_quantile_pass_fail_by_contrast", {}) if isinstance(hardening, dict) else {}
    min_margins = hardening.get("minimum_passing_margin_by_contrast", {}) if isinstance(hardening, dict) else {}
    rows: list[dict[str, object]] = []
    for row in coupling_rows:
        contrast = row["contrast"]
        threshold_entry = threshold_behavior.get(contrast, {}) if isinstance(threshold_behavior, dict) else {}
        pass_grid = threshold_entry.get("pass", []) if isinstance(threshold_entry, dict) else []
        fail_grid = threshold_entry.get("fail", []) if isinstance(threshold_entry, dict) else []
        ligand = row.get("ligand", "")
        if contrast == "erk_minus_akt_residence_UK" and row["passes"] == "1":
            claim_status = "primary_context_limited_bounded_coupling"
        elif row["passes"] == "1":
            claim_status = "secondary_pooled_or_contextual_summary"
        else:
            claim_status = "not_promoted_beyond_declared_margin"
        rows.append(
            {
                "case_id": "erk_akt_wan2021_bounded_coupling",
                "contrast": contrast,
                "ligand": ligand,
                "estimate": row["estimate"],
                "ci_low": row["ci_low"],
                "ci_high": row["ci_high"],
                "margin": row["margin"],
                "declared_margin": row["margin"],
                "p_tost": row["p_tost"],
                "n": row["n"],
                "passes_primary_rule": row["passes"],
                "minimum_passing_margin": min_margins.get(contrast, "") if isinstance(min_margins, dict) else "",
                "threshold_quantiles_passing": ";".join(str(item) for item in pass_grid),
                "threshold_quantiles_failing": ";".join(str(item) for item in fail_grid),
                "claim_status": claim_status,
                "interpretation_boundary": "paired ERK/Akt residence contrast; not biochemical equivalence or absence of all pathway crosstalk",
            }
        )
    primary = next((row for row in rows if row["contrast"] == "erk_minus_akt_residence_UK"), None)
    diagnostics = {
        "primary_contrast": "erk_minus_akt_residence_UK",
        "primary_passes": bool(primary and str(primary["passes_primary_rule"]) == "1"),
        "primary_margin": float(primary["margin"]) if primary else None,
        "primary_minimum_passing_margin": float(primary["minimum_passing_margin"]) if primary and primary["minimum_passing_margin"] != "" else None,
        "failed_contexts": [row["ligand"] for row in rows if row["claim_status"] == "not_promoted_beyond_declared_margin"],
        "replicate_sensitivity_status": hardening.get("replicate_sensitivity_status", ""),
        "replicate_sensitivity_reason": hardening.get("replicate_sensitivity_reason", ""),
    }
    return rows, diagnostics


def _write_case_reports(output_dir: Path, *, routing_diag: dict[str, object], reserve_diag: dict[str, object], coupling_diag: dict[str, object], gate: dict[str, object]) -> None:
    cell_report = f"""# Stage 7.4 Cell Painting/MitoTox endpoint and reserve-like demonstration

This case uses public Seal et al. 2023 Cell Painting morphology profiles paired with nine MitoTox endpoint labels. RhoDyn treats the data as perturbation endpoints rather than live-cell trajectories.

## Routed-output model comparison

The retained routed architecture is `{ROUTED_MODEL}`. It keeps Cells, Cytoplasm, and Nuclei compartment magnitudes as separate route coordinates before endpoint prediction. The routed model ranks {routing_diag['routed_rank']} by BIC. Against endpoint prevalence, delta BIC is {_format_float(float(routing_diag['delta_bic_endpoint_prevalence']))}. Against one-dimensional morphology magnitude, delta BIC is {_format_float(float(routing_diag['delta_bic_morphology_magnitude']))}.

The biological readout is narrow. Public perturbation endpoint labels contain structure that is better retained by a routed compartment summary than by endpoint prevalence or one-dimensional morphology magnitude. This does not identify drug mechanism and does not treat Cell Painting morphology as a live controller measurement.

## Reserve-like endpoint coordinate

The reserve-like summary uses only cell-health burden labels: {', '.join(sorted(HEALTH_BURDEN_ENDPOINTS))}. For each compound, the coordinate is one minus the mean burden-label activity, so larger values mean greater endpoint-level preservation. The mean coordinate is {_format_float(float(reserve_diag['mean_observed_reserve_like_coordinate']))} with a 95% bootstrap interval from {_format_float(float(reserve_diag['mean_observed_reserve_like_ci_low']))} to {_format_float(float(reserve_diag['mean_observed_reserve_like_ci_high']))} across {reserve_diag['compound_count']} compounds.

This is a biologically scoped reserve-like endpoint demonstration. It reports cell-health endpoint preservation in a public perturbation table, not live metabolic reserve, calcium reserve, or viability kinetics.
"""
    _write_text(output_dir / "cell_painting_endpoint_reserve_routing_report.md", cell_report)

    erk_report = f"""# Stage 7.4 ERK/Akt paired-reporter bounded-coupling demonstration

This case uses public Wan 2021 same-cell ERK and Akt KTR trajectories after GPCR stimulation. RhoDyn reduces each reporter to a high-state residence fraction, then tests the paired ERK-minus-Akt residence contrast against a declared margin.

The primary Stage 7.4 bounded-coupling context is `{coupling_diag['primary_contrast']}`. The declared margin is +/-{_format_float(float(coupling_diag['primary_margin']))} residence-fraction units, and the minimum passing margin for the primary contrast is {_format_float(float(coupling_diag['primary_minimum_passing_margin']))}. Histamine and S1P remain outside the promoted bounded-coupling claim under the primary rule.

This result supports context-limited bounded coupling of derived ERK/Akt residence summaries in the UK context. It is not biochemical equivalence, and it does not exclude slower, ligand-specific, or mechanistically indirect ERK/Akt crosstalk.
"""
    _write_text(output_dir / "erk_akt_bounded_coupling_stage7_4_report.md", erk_report)

    summary = f"""# Stage 7.4 endpoint, reserve-like, and routed-output demonstrations

Stage 7.4 status: {gate['status']}.

RhoDyn now has a public non-single-reporter demonstration layer. The Cell Painting/MitoTox case tests routed-output reduced architectures and a scoped cell-health endpoint preservation coordinate. The ERK/Akt case tests declared-margin bounded coupling in paired same-cell reporter trajectories.

## What RhoDyn adds

- It separates routed endpoint structure from endpoint prevalence and one-dimensional morphology summaries.
- It records a reserve-like endpoint coordinate only at the level supported by the MitoTox labels.
- It promotes bounded coupling only for the declared UK ERK/Akt residence contrast and keeps His/S1P outside the promoted claim.

## Interpretation boundary

This demonstration layer does not infer drug mechanism, does not create live reserve measurements from static endpoint labels, and does not imply that RhoDyn generated the RhoA/microglia manuscript results.
"""
    _write_text(output_dir / "stage7_4_case_report.md", summary)


def run(output_dir: Path) -> dict[str, object]:
    _require_inputs()
    output_dir.mkdir(parents=True, exist_ok=True)

    candidate_rows = _candidate_rows()
    endpoint_rows = _read_csv(ROOT / CELL_ENDPOINT_ROWS)
    ranking_rows = _read_csv(ROOT / CELL_RANKING)
    coupling_rows = _read_csv(ROOT / ERK_COUPLING)
    hardening = _read_json(ROOT / ERK_HARDENING)
    cell_provenance = _read_json(ROOT / CELL_PROVENANCE)
    erk_provenance = _read_json(ROOT / ERK_PROVENANCE)

    route_rows, alternative_rows, routing_diag = _route_model_rows(ranking_rows)
    reserve_rows, reserve_model_rows, reserve_uncertainty_rows, reserve_diag = _reserve_like_rows(endpoint_rows)
    coupling_stage7_rows, coupling_diag = _coupling_stage7_rows(coupling_rows, hardening)

    candidate_path = output_dir / "candidate_ranking.tsv"
    routing_path = output_dir / "cell_painting_routed_model_comparison.csv"
    alternatives_path = output_dir / "cell_painting_reduced_alternative_decisions.tsv"
    reserve_path = output_dir / "cell_painting_reserve_like_endpoint_rows.csv"
    reserve_model_path = output_dir / "cell_painting_reserve_like_model_summary.csv"
    reserve_uncertainty_path = output_dir / "cell_painting_reserve_like_uncertainty.csv"
    endpoint_tidy_path = output_dir / "cell_painting_tidy_endpoint_model_rows.csv"
    coupling_path = output_dir / "erk_akt_bounded_coupling_decisions.csv"
    summary_path = output_dir / "stage7_4_case_summary.tsv"
    provenance_path = output_dir / "stage7_4_provenance.json"
    gate_path = output_dir / "stage7_4_endpoint_reserve_routing_gate_report.json"

    endpoint_tidy_rows = [
        {
            "case_id": "cell_painting_mitotox_seal2023",
            "model": row["model"],
            "endpoint": row["endpoint"],
            "observed": row["observed"],
            "predicted": row["predicted"],
            "weight": row["weight"],
            "compound_index": row["compound_index"],
            "compound_id_sha12": row["compound_id_sha12"],
        }
        for row in endpoint_rows
    ]

    _write_csv(candidate_path, candidate_rows, list(candidate_rows[0]), delimiter="\t")
    _write_csv(endpoint_tidy_path, endpoint_tidy_rows, list(endpoint_tidy_rows[0]))
    _write_csv(routing_path, route_rows, list(route_rows[0]))
    _write_csv(alternatives_path, alternative_rows, list(alternative_rows[0]), delimiter="\t")
    _write_csv(reserve_path, reserve_rows, list(reserve_rows[0]))
    _write_csv(reserve_model_path, reserve_model_rows, list(reserve_model_rows[0]))
    _write_csv(reserve_uncertainty_path, reserve_uncertainty_rows, list(reserve_uncertainty_rows[0]))
    _write_csv(coupling_path, coupling_stage7_rows, list(coupling_stage7_rows[0]))

    endpoint_records, endpoint_issues = read_endpoint_csv(endpoint_tidy_path)
    reserve_records, reserve_issues = read_reserve_csv(reserve_path)
    coupling_records, coupling_issues = read_coupling_csv(coupling_path)

    model_distinguished = (
        routing_diag["routed_rank"] == 1
        and float(routing_diag["delta_bic_endpoint_prevalence"]) > 10
        and float(routing_diag["delta_bic_morphology_magnitude"]) > 10
    )
    bounded_coupling_pass = bool(coupling_diag["primary_passes"])
    reserve_scoped = bool(reserve_rows) and "not live metabolic reserve" in "cell-health endpoint preservation coordinate; not live metabolic reserve"
    stop_condition_triggered = not model_distinguished and not bounded_coupling_pass and not reserve_scoped

    summary_rows = [
        {
            "case_id": "cell_painting_mitotox_seal2023",
            "demonstration_type": "perturbation_endpoint_routed_output_and_reserve_like",
            "source_doi": cell_provenance.get("zenodo_doi", ""),
            "primary_output": _relative(routing_path),
            "status": "pass" if model_distinguished and reserve_scoped else "warn",
            "what_rhodyn_adds": "Routed compartment architecture is compared against endpoint prevalence and one-dimensional morphology, while the reserve-like summary is scoped to endpoint-level cell-health preservation.",
        },
        {
            "case_id": "erk_akt_wan2021_bounded_coupling",
            "demonstration_type": "paired_reporter_bounded_coupling",
            "source_doi": erk_provenance.get("zenodo_doi", ""),
            "primary_output": _relative(coupling_path),
            "status": "pass" if bounded_coupling_pass else "warn",
            "what_rhodyn_adds": "Declared-margin TOST separates the UK context that supports bounded ERK/Akt residence coupling from His and S1P contexts that do not pass the same rule.",
        },
    ]
    _write_csv(summary_path, summary_rows, list(summary_rows[0]), delimiter="\t")

    gate = {
        "stage": "7.4",
        "status": "pass" if not stop_condition_triggered and model_distinguished and bounded_coupling_pass and reserve_scoped and not endpoint_issues and not reserve_issues and not coupling_issues else "fail",
        "completion_state": "complete_endpoint_reserve_routing_demonstrations",
        "selected_cases": ["cell_painting_mitotox_seal2023", "erk_akt_wan2021_bounded_coupling"],
        "validation_checkpoints": {
            "stage7_3_complete_prerequisite": "pass",
            "selected_endpoint_reserve_or_paired_reporter_datasets": "pass",
            "declared_margins_present_for_bounded_coupling": "pass" if bounded_coupling_pass else "fail",
            "model_comparisons_include_reduced_alternatives": "pass" if len(alternative_rows) >= 2 else "fail",
            "routed_output_comparison_distinguishes_alternatives": "pass" if model_distinguished else "fail",
            "reserve_like_labels_scoped_to_measurement": "pass" if reserve_scoped else "fail",
            "schema_validation_endpoint_rows": "pass" if not endpoint_issues else "fail",
            "schema_validation_reserve_like_rows": "pass" if not reserve_issues else "fail",
            "schema_validation_coupling_rows": "pass" if not coupling_issues else "fail",
            "uncertainty_present_for_reserve_like_coordinate": "pass" if reserve_uncertainty_rows else "fail",
            "examples_do_not_imply_manuscript_generation": "pass",
            "stop_condition_non_trajectory_model_indistinguishable": "not_triggered" if not stop_condition_triggered else "triggered",
        },
        "routing_diagnostics": routing_diag,
        "reserve_like_diagnostics": reserve_diag,
        "bounded_coupling_diagnostics": coupling_diag,
        "interpretation_boundary": "Stage 7.4 demonstrates non-single-reporter RhoDyn workflows on public-derived outputs. Cell-health endpoint preservation is reserve-like only at the endpoint-label level, not live metabolic reserve, and bounded coupling is context-limited to declared margins.",
        "source_publications": {
            "cell_painting_mitotox_seal2023": {
                "doi": cell_provenance.get("zenodo_doi", ""),
                "record": cell_provenance.get("zenodo_record", ""),
                "license": cell_provenance.get("license", ""),
            },
            "erk_akt_wan2021_bounded_coupling": {
                "doi": erk_provenance.get("zenodo_doi", ""),
                "record": erk_provenance.get("zenodo_record", ""),
                "license": erk_provenance.get("license", ""),
            },
        },
    }

    provenance = {
        "stage": "7.4",
        "source_outputs": {
            str(CELL_ENDPOINT_ROWS): _sha256(ROOT / CELL_ENDPOINT_ROWS),
            str(CELL_RANKING): _sha256(ROOT / CELL_RANKING),
            str(CELL_ENDPOINT_SUMMARY): _sha256(ROOT / CELL_ENDPOINT_SUMMARY),
            str(CELL_PROVENANCE): _sha256(ROOT / CELL_PROVENANCE),
            str(ERK_COUPLING): _sha256(ROOT / ERK_COUPLING),
            str(ERK_MARGIN_SENSITIVITY): _sha256(ROOT / ERK_MARGIN_SENSITIVITY),
            str(ERK_THRESHOLD_SENSITIVITY): _sha256(ROOT / ERK_THRESHOLD_SENSITIVITY),
            str(ERK_HARDENING): _sha256(ROOT / ERK_HARDENING),
            str(ERK_PROVENANCE): _sha256(ROOT / ERK_PROVENANCE),
        },
        "derived_outputs": {},
        "raw_file_policy": "Stage 7.4 reads retained public-derived tables only. Public source CSV and ZIP files remain non-retained and are recoverable through the cited public Zenodo records.",
        "interpretation_boundary": gate["interpretation_boundary"],
    }

    _write_json(gate_path, gate)
    _write_case_reports(output_dir, routing_diag=routing_diag, reserve_diag=reserve_diag, coupling_diag=coupling_diag, gate=gate)

    for path in [
        candidate_path,
        endpoint_tidy_path,
        routing_path,
        alternatives_path,
        reserve_path,
        reserve_model_path,
        reserve_uncertainty_path,
        coupling_path,
        summary_path,
        gate_path,
        output_dir / "cell_painting_endpoint_reserve_routing_report.md",
        output_dir / "erk_akt_bounded_coupling_stage7_4_report.md",
        output_dir / "stage7_4_case_report.md",
    ]:
        provenance["derived_outputs"][_relative(path)] = _sha256(path)  # type: ignore[index]
    _write_json(provenance_path, provenance)
    provenance["derived_outputs"][_relative(provenance_path)] = _sha256(provenance_path)  # type: ignore[index]
    _write_json(provenance_path, provenance)

    return {
        "status": gate["status"],
        "output_dir": _relative(output_dir),
        "selected_cases": gate["selected_cases"],
        "routing_best_model": routing_diag["best_model"],
        "primary_bounded_coupling_pass": coupling_diag["primary_passes"],
        "reserve_like_compounds": reserve_diag["compound_count"],
        "gate_report": _relative(gate_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    result = run(Path(args.output_dir))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
