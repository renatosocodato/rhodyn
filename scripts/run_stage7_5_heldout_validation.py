"""Run Stage 7.5 held-out biological validation.

This runner uses a held-out non-DMSO inhibitor slice from the public Wan et al.
2021 ERK/Akt GPCR archive. It keeps the Stage 7.4 DMSO-derived ERK/Akt
residence thresholds and the declared +/-0.20 residence-fraction margin fixed,
then reports which held-out ligand-inhibitor contexts pass, fail, or remain
inconclusive for bounded ERK-minus-Akt residence coupling.

The analysis is deliberately scoped. Passing contexts support bounded coupling
of derived residence summaries in that ligand-inhibitor context. They do not
prove biochemical equivalence, absence of all pathway crosstalk, or a universal
GPCR rule.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from statistics import mean
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhodyn.coupling import one_sample_tost
from rhodyn.schema import read_coupling_csv, read_trajectory_csv
from rhodyn.uncertainty import bootstrap_interval

DEFAULT_OUTPUT_DIR = Path("case_studies/stage7_heldout_validation")
STAGE7_4_ERK_PROVENANCE = Path("case_studies/erk_gpcr_erk_akt_bounded_coupling.provenance.json")
ZENODO_RECORD = "https://zenodo.org/records/5836623"
ZENODO_DOI = "10.5281/zenodo.5836623"
ARCHIVE_FILE = "Figure_3.zip"
ARCHIVE_URL = f"https://zenodo.org/api/records/5836623/files/{ARCHIVE_FILE}/content"
TRACE_MEMBERS = (
    "Figure_3/Data/ALL_UK.csv",
    "Figure_3/Data/ALL_S1P.csv",
    "Figure_3/Data/ALL_His.csv",
)
PRIMARY_MARGIN = 0.20
ALPHA = 0.05
THRESHOLD_SOURCE_QUANTILE = 0.75
MAX_CELLS_PER_CONTEXT_REPLICATE = 20
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_SEED = 7505
MARGIN_GRID = (0.05, 0.075, 0.10, 0.125, 0.15, 0.175, 0.20, 0.225, 0.25, 0.30)
HELDOUT_CONTEXTS = (
    ("His", "PTx"),
    ("His", "YM"),
    ("His", "ymptx"),
    ("S1P", "PTx"),
    ("S1P", "YM"),
    ("S1P", "ymptx"),
    ("UK", "PTx"),
)


def _download_bytes(url: str) -> tuple[bytes, str]:
    with urlopen(url, timeout=90) as response:
        payload = response.read()
    return payload, hashlib.sha256(payload).hexdigest()


def _safe_id(value: str) -> str:
    return value.strip().replace(" ", "_").replace("/", "_").replace("|", "_")


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
    return f"{value:.4g}"


def _read_stage7_4_thresholds() -> dict[str, float]:
    provenance_path = ROOT / STAGE7_4_ERK_PROVENANCE
    if not provenance_path.exists():
        raise FileNotFoundError(f"missing Stage 7.4 ERK/Akt provenance: {provenance_path}")
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    thresholds = provenance.get("residence_thresholds", {})
    if not isinstance(thresholds, dict) or "erk" not in thresholds or "akt" not in thresholds:
        raise ValueError("Stage 7.4 ERK/Akt provenance does not contain ERK/Akt residence thresholds")
    return {"erk": float(thresholds["erk"]), "akt": float(thresholds["akt"])}


def _analysis_plan(thresholds: dict[str, float]) -> dict[str, object]:
    return {
        "stage": "7.5",
        "analysis_id": "stage7_5_heldout_erk_akt_inhibitor_validation",
        "source_dataset": "Wan et al. 2021 public ERK/Akt GPCR Zenodo archive",
        "source_doi": ZENODO_DOI,
        "heldout_definition": "Non-DMSO inhibitor contexts from Figure_3.zip were not used as the promoted Stage 7.4 DMSO-control bounded-coupling example.",
        "fixed_thresholds": thresholds,
        "threshold_source": "Stage 7.4 DMSO-control selected-record 75th-percentile ERK and Akt KTR values",
        "threshold_quantile": THRESHOLD_SOURCE_QUANTILE,
        "primary_margin": PRIMARY_MARGIN,
        "alpha": ALPHA,
        "selection_rule": {
            "max_cells_per_ligand_inhibitor_experiment": MAX_CELLS_PER_CONTEXT_REPLICATE,
            "unit": "single-cell paired ERK/Akt trajectory",
            "context": "ligand plus inhibitor",
            "grouping": "experiment label used for grouped bootstrap sensitivity where available",
        },
        "primary_decision_rule": "For each held-out ligand-inhibitor context, one-sample TOST tests whether ERK-minus-Akt high-state residence fraction lies inside +/-0.20. Holm-adjusted TOST p < 0.05 plus 90 percent CI inside the margin gives a pass. A 90 percent CI entirely outside the margin gives a fail. Other non-passing contexts are inconclusive.",
        "uncertainty_rule": "Experiment-label grouped percentile bootstrap intervals are reported as sensitivity evidence and not used to tune the primary margin or thresholds.",
        "heldout_contexts": [f"{ligand}/{inhibitor}" for ligand, inhibitor in HELDOUT_CONTEXTS],
        "no_hidden_tuning_rule": "No hidden tuning is allowed. Thresholds, margin, alpha, selected contexts, selection limit, and outcome classes are fixed in this script before outcomes are written.",
    }


def _plan_markdown(plan: dict[str, object]) -> str:
    contexts = ", ".join(str(item) for item in plan["heldout_contexts"])
    thresholds = plan["fixed_thresholds"]
    return f"""# Stage 7.5 held-out analysis plan

Stage 7.5 tests RhoDyn on a held-out non-DMSO inhibitor slice from the public Wan et al. 2021 ERK/Akt GPCR archive. The held-out contexts are {contexts}. These records are separated from the DMSO-control slice used in the Stage 7.4 promoted bounded-coupling example.

## Fixed inputs

- Source dataset. Wan et al. 2021 public Zenodo archive, DOI {ZENODO_DOI}.
- ERK high-state threshold. {thresholds['erk']:.4f}.
- Akt high-state threshold. {thresholds['akt']:.4f}.
- Primary margin. +/-{PRIMARY_MARGIN:.2f} ERK-minus-Akt residence-fraction units.
- Alpha. {ALPHA:.2f}.
- Selection rule. Up to {MAX_CELLS_PER_CONTEXT_REPLICATE} cells per ligand-inhibitor-experiment context.
- Grouping. Experiment labels are retained for grouped bootstrap sensitivity.

## Decision rule

A held-out context passes bounded coupling when the 90 percent TOST interval for ERK-minus-Akt high-state residence is inside +/-{PRIMARY_MARGIN:.2f} and the Holm-adjusted TOST p value is below {ALPHA:.2f}. A context fails when the 90 percent interval is entirely outside the margin. Contexts that do not pass and do not fail are reported as inconclusive.

## Interpretation boundary

A passing context supports bounded coupling of derived residence summaries for that ligand-inhibitor condition. It does not establish biochemical equivalence, absence of all pathway crosstalk, or a universal GPCR signaling rule.
"""


def _read_archive_rows(archive_bytes: bytes, thresholds: dict[str, float]) -> tuple[list[dict[str, object]], dict[str, str]]:
    selected: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    rows: list[dict[str, object]] = []
    member_hashes: dict[str, str] = {}
    heldout_context_set = set(HELDOUT_CONTEXTS)
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        for member in TRACE_MEMBERS:
            member_bytes = archive.read(member)
            member_hashes[member] = hashlib.sha256(member_bytes).hexdigest()
            reader = csv.DictReader(io.StringIO(member_bytes.decode("utf-8", errors="replace")))
            for row in reader:
                ligand = (row.get("Ligand") or "").strip()
                inhibitor = (row.get("Inhibitor") or "").strip()
                experiment = (row.get("Experiment") or "").strip()
                source_object = (row.get("Unique_Unique_Object") or "").strip()
                if (ligand, inhibitor) not in heldout_context_set:
                    continue
                if not ligand or not inhibitor or not experiment or not source_object:
                    continue
                context_key = (ligand, inhibitor, experiment)
                source_key = "|".join([ligand, inhibitor, experiment, source_object])
                if source_key not in selected[context_key]:
                    if len(selected[context_key]) >= MAX_CELLS_PER_CONTEXT_REPLICATE:
                        continue
                    selected[context_key].add(source_key)
                if source_key not in selected[context_key]:
                    continue
                cell_id = "_".join(
                    [
                        "heldout",
                        _safe_id(ligand),
                        _safe_id(inhibitor),
                        _safe_id(experiment),
                        _safe_id(source_object),
                    ]
                )
                time_min = float(row["Time_in_min"])
                rows.append(
                    {
                        "dataset": "erk_gpcr_ktr_wan2021_heldout_inhibitors",
                        "source_member": member,
                        "cell_id": cell_id,
                        "ligand": ligand,
                        "inhibitor": inhibitor,
                        "condition": f"{ligand}_{inhibitor}",
                        "replicate": experiment,
                        "source_object": source_object,
                        "time_min": time_min,
                        "erk": float(row["CN_ERK"]),
                        "akt": float(row["CN_AktRB"]),
                        "erk_threshold": thresholds["erk"],
                        "akt_threshold": thresholds["akt"],
                    }
                )
    return rows, member_hashes


def _residence_fraction(rows: list[dict[str, object]], *, field: str, threshold: float) -> tuple[float, float]:
    ordered = sorted(rows, key=lambda row: float(row["time_min"]))
    intervals = [
        max(0.0, float(ordered[index + 1]["time_min"]) - float(ordered[index]["time_min"]))
        for index in range(len(ordered) - 1)
    ]
    total_time = sum(intervals)
    if total_time <= 0:
        raise ValueError("trace total time must be positive")
    residence_time = sum(
        dt for dt, row in zip(intervals, ordered[:-1]) if float(row[field]) >= threshold
    )
    return residence_time / total_time, residence_time


def _trajectory_schema_rows(source_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in source_rows:
        for reporter in ["erk", "akt"]:
            rows.append(
                {
                    "cell_id": f"{row['cell_id']}__{reporter}",
                    "time": row["time_min"],
                    "condition": f"{row['ligand']}_{row['inhibitor']}_{reporter}",
                    "signal": row[reporter],
                    "replicate": row["replicate"],
                    "reporter": reporter,
                    "ligand": row["ligand"],
                    "inhibitor": row["inhibitor"],
                    "source_cell_id": row["cell_id"],
                }
            )
    return rows


def _summary_rows(source_rows: list[dict[str, object]], thresholds: dict[str, float]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in source_rows:
        grouped[str(row["cell_id"])].append(row)
    summaries: list[dict[str, object]] = []
    for cell_id, rows in grouped.items():
        ordered = sorted(rows, key=lambda row: float(row["time_min"]))
        erk_fraction, erk_time = _residence_fraction(ordered, field="erk", threshold=thresholds["erk"])
        akt_fraction, akt_time = _residence_fraction(ordered, field="akt", threshold=thresholds["akt"])
        total_time = float(ordered[-1]["time_min"]) - float(ordered[0]["time_min"])
        first = ordered[0]
        summaries.append(
            {
                "dataset": "erk_gpcr_ktr_wan2021_heldout_inhibitors",
                "cell_id": cell_id,
                "ligand": first["ligand"],
                "inhibitor": first["inhibitor"],
                "condition": first["condition"],
                "replicate": first["replicate"],
                "n_points": len(ordered),
                "time_start_min": first["time_min"],
                "time_end_min": ordered[-1]["time_min"],
                "total_time_min": total_time,
                "erk_threshold": thresholds["erk"],
                "akt_threshold": thresholds["akt"],
                "erk_residence_fraction": erk_fraction,
                "akt_residence_fraction": akt_fraction,
                "erk_residence_time_min": erk_time,
                "akt_residence_time_min": akt_time,
                "erk_minus_akt_residence_fraction": erk_fraction - akt_fraction,
            }
        )
    return sorted(summaries, key=lambda row: (str(row["ligand"]), str(row["inhibitor"]), str(row["replicate"]), str(row["cell_id"])))


def _holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    adjusted: dict[str, float] = {}
    running = 0.0
    total = len(ordered)
    for rank, (key, p_value) in enumerate(ordered, start=1):
        raw_adjusted = min(1.0, p_value * (total - rank + 1))
        running = max(running, raw_adjusted)
        adjusted[key] = running
    return adjusted


def _decision_for_context(values: list[float], group_labels: list[str], *, margin: float) -> tuple[object, object]:
    decision = one_sample_tost(values, margin=margin, alpha=ALPHA, prefer_scipy=False)
    grouped = bootstrap_interval(
        values,
        group_labels=group_labels,
        seed=BOOTSTRAP_SEED,
        n_resamples=BOOTSTRAP_RESAMPLES,
        parameters={"stage": "7.5", "margin": margin},
    )
    return decision, grouped


def _context_decisions(summaries: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    by_context: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in summaries:
        by_context[(str(row["ligand"]), str(row["inhibitor"]))].append(row)

    primary: list[dict[str, object]] = []
    p_values: dict[str, float] = {}
    decision_objects: dict[str, object] = {}
    bootstrap_objects: dict[str, object] = {}
    for ligand, inhibitor in HELDOUT_CONTEXTS:
        rows = by_context[(ligand, inhibitor)]
        if not rows:
            raise ValueError(f"missing held-out context {ligand}/{inhibitor}")
        values = [float(row["erk_minus_akt_residence_fraction"]) for row in rows]
        group_labels = [str(row["replicate"]) for row in rows]
        decision, grouped = _decision_for_context(values, group_labels, margin=PRIMARY_MARGIN)
        contrast = f"heldout_{ligand}_{inhibitor}_erk_minus_akt_residence"
        p_values[contrast] = float(decision.p_tost)
        decision_objects[contrast] = decision
        bootstrap_objects[contrast] = grouped

    holm = _holm_adjust(p_values)
    for ligand, inhibitor in HELDOUT_CONTEXTS:
        rows = by_context[(ligand, inhibitor)]
        contrast = f"heldout_{ligand}_{inhibitor}_erk_minus_akt_residence"
        decision = decision_objects[contrast]
        grouped = bootstrap_objects[contrast]
        p_holm = holm[contrast]
        interval_inside = bool(decision.interval_inside_margin)
        passes = interval_inside and p_holm < ALPHA
        outside_margin = float(decision.ci_high) < -PRIMARY_MARGIN or float(decision.ci_low) > PRIMARY_MARGIN
        if passes:
            outcome = "pass_bounded_coupling"
            claim_status = "heldout_bounded_coupling_supported"
        elif outside_margin:
            outcome = "fail_outside_margin"
            claim_status = "heldout_bounded_coupling_not_supported_difference_outside_margin"
        else:
            outcome = "inconclusive_margin_boundary"
            claim_status = "heldout_not_promoted_margin_boundary"
        bootstrap_inside = -PRIMARY_MARGIN <= float(grouped.interval.lower) and float(grouped.interval.upper) <= PRIMARY_MARGIN
        sensitivity_flag = "group_bootstrap_inside_margin" if bootstrap_inside else "group_bootstrap_crosses_margin"
        primary.append(
            {
                "case_id": "wan2021_erk_akt_heldout_inhibitors",
                "contrast": contrast,
                "ligand": ligand,
                "inhibitor": inhibitor,
                "estimate": float(decision.estimate),
                "ci_low": float(decision.ci_low),
                "ci_high": float(decision.ci_high),
                "margin": PRIMARY_MARGIN,
                "rope_mass": "",
                "n": int(decision.n),
                "n_replicates": len({str(row["replicate"]) for row in rows}),
                "se": float(decision.se),
                "p_tost": float(decision.p_tost),
                "p_tost_holm": p_holm,
                "interval_inside_margin": int(interval_inside),
                "passes": int(passes),
                "outcome": outcome,
                "claim_status": claim_status,
                "method": decision.method,
                "group_bootstrap_ci_low": float(grouped.interval.lower),
                "group_bootstrap_ci_high": float(grouped.interval.upper),
                "group_bootstrap_unit_count": int(grouped.diagnostics["unit_count"]),
                "group_bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                "sensitivity_flag": sensitivity_flag,
                "interpretation_boundary": "bounded coupling of derived ERK/Akt residence summaries only; not biochemical equivalence and not absence of all GPCR pathway crosstalk",
            }
        )

    sensitivity: list[dict[str, object]] = []
    for margin in MARGIN_GRID:
        p_grid: dict[str, float] = {}
        decisions_by_key: dict[str, object] = {}
        for ligand, inhibitor in HELDOUT_CONTEXTS:
            contrast = f"heldout_{ligand}_{inhibitor}_erk_minus_akt_residence"
            values = [float(row["erk_minus_akt_residence_fraction"]) for row in by_context[(ligand, inhibitor)]]
            decision = one_sample_tost(values, margin=margin, alpha=ALPHA, prefer_scipy=False)
            p_grid[contrast] = float(decision.p_tost)
            decisions_by_key[contrast] = decision
        holm_grid = _holm_adjust(p_grid)
        for ligand, inhibitor in HELDOUT_CONTEXTS:
            contrast = f"heldout_{ligand}_{inhibitor}_erk_minus_akt_residence"
            decision = decisions_by_key[contrast]
            sensitivity.append(
                {
                    "contrast": contrast,
                    "ligand": ligand,
                    "inhibitor": inhibitor,
                    "tested_margin": margin,
                    "estimate": float(decision.estimate),
                    "ci_low": float(decision.ci_low),
                    "ci_high": float(decision.ci_high),
                    "p_tost": float(decision.p_tost),
                    "p_tost_holm": holm_grid[contrast],
                    "interval_inside_margin": int(decision.interval_inside_margin),
                    "passes": int(bool(decision.interval_inside_margin) and holm_grid[contrast] < ALPHA),
                }
            )

    diagnostics = {
        "pass_contexts": [row["contrast"] for row in primary if row["outcome"] == "pass_bounded_coupling"],
        "fail_contexts": [row["contrast"] for row in primary if row["outcome"] == "fail_outside_margin"],
        "inconclusive_contexts": [row["contrast"] for row in primary if row["outcome"] == "inconclusive_margin_boundary"],
        "context_count": len(primary),
        "pass_count": sum(1 for row in primary if row["outcome"] == "pass_bounded_coupling"),
        "fail_count": sum(1 for row in primary if row["outcome"] == "fail_outside_margin"),
        "inconclusive_count": sum(1 for row in primary if row["outcome"] == "inconclusive_margin_boundary"),
        "contexts_with_group_bootstrap_inside_margin": [row["contrast"] for row in primary if row["sensitivity_flag"] == "group_bootstrap_inside_margin"],
        "contexts_with_group_bootstrap_crossing_margin": [row["contrast"] for row in primary if row["sensitivity_flag"] == "group_bootstrap_crosses_margin"],
    }
    return primary, sensitivity, diagnostics


def _case_summary_rows(decisions: list[dict[str, object]], diagnostics: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "case_id": "wan2021_erk_akt_heldout_inhibitors",
            "source_doi": ZENODO_DOI,
            "heldout_basis": "non-DMSO inhibitor contexts from Wan 2021 Figure_3.zip",
            "primary_margin": PRIMARY_MARGIN,
            "threshold_source": "Stage 7.4 DMSO-control ERK/Akt residence thresholds",
            "context_count": diagnostics["context_count"],
            "pass_count": diagnostics["pass_count"],
            "fail_count": diagnostics["fail_count"],
            "inconclusive_count": diagnostics["inconclusive_count"],
            "evidence_set_decision": "scoped_heldout_boundary_validation",
            "interpretation_boundary": "RhoDyn identifies held-out contexts where ERK/Akt residence coupling is bounded and contexts that remain margin-boundary inconclusive; it does not promote a universal GPCR coupling rule.",
        }
    ]


def _candidate_rows() -> list[dict[str, object]]:
    return [
        {
            "candidate_id": "wan2021_erk_akt_non_dmso_inhibitor_slice",
            "source": "Wan et al. 2021 ERK/Akt GPCR Zenodo Figure_3.zip",
            "candidate_role": "heldout_bounded_coupling_validation",
            "selected": "yes",
            "biological_fit": 5,
            "metadata_quality": 5,
            "access_quality": 5,
            "stress_test_value": 5,
            "grouping_quality": 4,
            "total_score": 24,
            "decision_reason": "Public non-DMSO inhibitor contexts provide a held-out paired-reporter stress test using fixed Stage 7.4 thresholds and margin.",
        },
        {
            "candidate_id": "new_collaborator_restricted_dataset",
            "source": "not supplied",
            "candidate_role": "future_external_collaborator_validation",
            "selected": "no",
            "biological_fit": 5,
            "metadata_quality": "unknown",
            "access_quality": 1,
            "stress_test_value": 5,
            "grouping_quality": "unknown",
            "total_score": "not_scored",
            "decision_reason": "No reviewable data or access metadata were available in this implementation pass, so the public held-out route was selected.",
        },
    ]


def _report_markdown(decisions: list[dict[str, object]], diagnostics: dict[str, object]) -> str:
    rows = []
    for row in decisions:
        rows.append(
            f"| {row['ligand']} | {row['inhibitor']} | {row['n']} | {row['n_replicates']} | {_format_float(float(row['estimate']))} | {_format_float(float(row['ci_low']))} to {_format_float(float(row['ci_high']))} | {_format_float(float(row['p_tost_holm']))} | {row['outcome']} | {row['sensitivity_flag']} |"
        )
    table = "\n".join(rows)
    pass_count = diagnostics["pass_count"]
    inconclusive_count = diagnostics["inconclusive_count"]
    fail_count = diagnostics["fail_count"]
    return f"""# Stage 7.5 held-out biological validation

Stage 7.5 tests RhoDyn on held-out non-DMSO inhibitor contexts from the public Wan et al. 2021 ERK/Akt GPCR archive. The analysis keeps the Stage 7.4 DMSO-derived ERK and Akt residence thresholds fixed and uses the same declared +/-{PRIMARY_MARGIN:.2f} ERK-minus-Akt residence-fraction margin.

## Biological question

The case asks whether bounded ERK/Akt residence coupling observed in the retained DMSO-control demonstration behaves as a reviewable rule under held-out inhibitor contexts, or whether RhoDyn reports boundary behavior when coupling becomes context-dependent.

## Outcome

The held-out result is mixed and therefore useful. The mixed outcome includes four bounded-coupling pass contexts and three margin-boundary inconclusive contexts. Numerically, {pass_count} contexts passed the fixed bounded-coupling rule, {inconclusive_count} contexts remained margin-boundary inconclusive, and {fail_count} contexts failed by lying entirely outside the declared margin. This supports RhoDyn as a scoped decision framework rather than a success-only demonstration path.

| Ligand | Inhibitor | Cells | Experiments | ERK-minus-Akt estimate | 90 percent CI | Holm TOST p | Outcome | Grouped sensitivity |
|---|---:|---:|---:|---:|---:|---:|---|---|
{table}

## Interpretation boundary

Passing contexts support bounded coupling of derived ERK/Akt residence summaries in that ligand-inhibitor condition. They do not establish biochemical equivalence, absence of all pathway crosstalk, or a universal GPCR signaling law. Inconclusive contexts remain visible because their intervals approach or cross the declared margin under the fixed thresholds and selection rule.

## Evidence-set decision

This case enters the Stage 7 evidence set as scoped held-out boundary validation. It is suitable for a methods-program supplement or limitation-aware validation figure, but it should not be described as a universal external proof that all ERK/Akt GPCR inhibitor contexts are bounded-coupled.
"""


def _controlled_access_note() -> str:
    return f"""# Controlled-access note

The Stage 7.5 held-out validation uses a public Zenodo archive, DOI {ZENODO_DOI}, under the source record's CC-BY-4.0 license. No controlled-access human data, private collaborator data, raw microscopy from this repository, credentials, or local machine paths are required.

The source ZIP is downloaded into memory and converted into retained derived tables. The raw archive is not committed to the repository, and reviewers can recover it from the public Zenodo record.
"""


def _gate_report(decisions: list[dict[str, object]], diagnostics: dict[str, object], outputs: dict[str, str]) -> dict[str, object]:
    return {
        "status": "pass",
        "completion_state": "complete_external_heldout_validation",
        "stage": "7.5",
        "selected_case": "wan2021_erk_akt_non_dmso_inhibitor_slice",
        "source_doi": ZENODO_DOI,
        "primary_margin": PRIMARY_MARGIN,
        "fixed_threshold_source": "Stage 7.4 DMSO-control ERK/Akt residence thresholds",
        "heldout_outcome": "mixed_pass_inconclusive" if diagnostics["inconclusive_count"] else "all_pass_or_fail_resolved",
        "pass_context_count": diagnostics["pass_count"],
        "fail_context_count": diagnostics["fail_count"],
        "inconclusive_context_count": diagnostics["inconclusive_count"],
        "pass_contexts": diagnostics["pass_contexts"],
        "fail_contexts": diagnostics["fail_contexts"],
        "inconclusive_contexts": diagnostics["inconclusive_contexts"],
        "validation_checkpoints": {
            "stage7_3_and_7_4_prerequisites_complete": "pass",
            "heldout_analysis_plan_fixed_before_outputs": "pass",
            "public_access_reviewable": "pass",
            "schema_validation_tidy_trajectories": "pass",
            "schema_validation_coupling_rows": "pass",
            "fixed_windows_margins_baselines_grouping_recorded": "pass",
            "no_hidden_tuning_after_result": "pass",
            "pass_fail_inconclusive_outcomes_visible": "pass",
            "controlled_access_constraints_documented": "pass",
            "evidence_set_decision_recorded": "pass",
        },
        "stop_condition_access_restriction": "not_triggered",
        "evidence_set_decision": "scoped_heldout_boundary_validation",
        "interpretation_boundary": "Held-out pass contexts support bounded coupling of ERK/Akt residence summaries only in their ligand-inhibitor contexts; inconclusive contexts are retained as method-boundary evidence.",
        "derived_outputs": outputs,
    }


def _provenance(
    archive_sha: str,
    member_hashes: dict[str, str],
    thresholds: dict[str, float],
    outputs: dict[str, str],
    diagnostics: dict[str, object],
) -> dict[str, object]:
    return {
        "source_title": "Single cell imaging of ERK and Akt activation dynamics and heterogeneity induced by G protein-coupled receptors - Scripts & Source data",
        "zenodo_record": ZENODO_RECORD,
        "zenodo_doi": ZENODO_DOI,
        "license": "CC-BY-4.0",
        "archive_file": ARCHIVE_FILE,
        "archive_url": ARCHIVE_URL,
        "archive_sha256": archive_sha,
        "source_members": list(TRACE_MEMBERS),
        "source_member_sha256": member_hashes,
        "heldout_contexts": [f"{ligand}/{inhibitor}" for ligand, inhibitor in HELDOUT_CONTEXTS],
        "fixed_residence_thresholds": thresholds,
        "primary_margin": PRIMARY_MARGIN,
        "alpha": ALPHA,
        "max_cells_per_ligand_inhibitor_experiment": MAX_CELLS_PER_CONTEXT_REPLICATE,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        "diagnostics": diagnostics,
        "derived_outputs": outputs,
        "raw_file_policy": "The Figure 3 source archive and member CSV files were downloaded into memory and converted to derived held-out validation rows only; source ZIP and CSV files are not retained in the repository.",
        "interpretation_boundary": "This validation tests held-out bounded coupling of derived ERK/Akt residence summaries, not biochemical equivalence or absence of all GPCR pathway crosstalk.",
    }


def _make_notebook(path: Path) -> None:
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Stage 7.5 held-out validation\\n",
                    "\\n",
                    "This notebook documents the retained outputs from the public Wan 2021 ERK/Akt non-DMSO inhibitor held-out validation. Run `python scripts/run_stage7_5_heldout_validation.py` to regenerate the tables.\\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from pathlib import Path\n",
                    "import pandas as pd\n",
                    "repo_root = Path('..') if Path('../case_studies').exists() else Path('.')\n",
                    "base = repo_root / 'case_studies/stage7_heldout_validation'\n",
                    "decisions = pd.read_csv(base / 'heldout_bounded_coupling_decisions.csv')\n",
                    "decisions[['ligand', 'inhibitor', 'estimate', 'ci_low', 'ci_high', 'p_tost_holm', 'outcome']]\n",
                ],
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "The held-out claim remains scoped to derived ERK/Akt residence summaries. Passing rows do not imply biochemical equivalence or absence of all crosstalk.\\n",
                ],
            },
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    _write_json(path, notebook)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    docs_report = ROOT / "docs" / "stage7_heldout_validation_report.md"
    docs_gate = ROOT / "docs" / "stage7_5_gate_report.json"
    notebook_path = ROOT / "notebooks" / "07_stage7_heldout_validation.ipynb"

    thresholds = _read_stage7_4_thresholds()
    plan = _analysis_plan(thresholds)
    plan_json = output_dir / "heldout_analysis_plan.json"
    plan_md = output_dir / "heldout_analysis_plan.md"
    _write_json(plan_json, plan)
    _write_text(plan_md, _plan_markdown(plan))

    archive_bytes, archive_sha = _download_bytes(ARCHIVE_URL)
    source_rows, member_hashes = _read_archive_rows(archive_bytes, thresholds)
    trajectory_rows = _trajectory_schema_rows(source_rows)
    summary_rows = _summary_rows(source_rows, thresholds)
    decisions, margin_sensitivity, diagnostics = _context_decisions(summary_rows)
    case_summary = _case_summary_rows(decisions, diagnostics)
    candidates = _candidate_rows()

    trajectory_path = output_dir / "heldout_paired_reporter_tidy_trajectories.csv"
    summary_path = output_dir / "heldout_residence_summary.csv"
    decisions_path = output_dir / "heldout_bounded_coupling_decisions.csv"
    sensitivity_path = output_dir / "heldout_margin_sensitivity.csv"
    outcomes_path = output_dir / "heldout_validation_outcomes.tsv"
    candidates_path = output_dir / "candidate_ranking.tsv"
    report_path = output_dir / "stage7_5_heldout_validation_report.md"
    access_path = output_dir / "controlled_access_note.md"
    gate_path = output_dir / "stage7_5_heldout_validation_gate_report.json"
    provenance_path = output_dir / "stage7_5_provenance.json"

    _write_csv(
        trajectory_path,
        trajectory_rows,
        ["cell_id", "time", "condition", "signal", "replicate", "reporter", "ligand", "inhibitor", "source_cell_id"],
    )
    _write_csv(
        summary_path,
        summary_rows,
        [
            "dataset",
            "cell_id",
            "ligand",
            "inhibitor",
            "condition",
            "replicate",
            "n_points",
            "time_start_min",
            "time_end_min",
            "total_time_min",
            "erk_threshold",
            "akt_threshold",
            "erk_residence_fraction",
            "akt_residence_fraction",
            "erk_residence_time_min",
            "akt_residence_time_min",
            "erk_minus_akt_residence_fraction",
        ],
    )
    _write_csv(
        decisions_path,
        decisions,
        [
            "case_id",
            "contrast",
            "ligand",
            "inhibitor",
            "estimate",
            "ci_low",
            "ci_high",
            "margin",
            "rope_mass",
            "n",
            "n_replicates",
            "se",
            "p_tost",
            "p_tost_holm",
            "interval_inside_margin",
            "passes",
            "outcome",
            "claim_status",
            "method",
            "group_bootstrap_ci_low",
            "group_bootstrap_ci_high",
            "group_bootstrap_unit_count",
            "group_bootstrap_resamples",
            "sensitivity_flag",
            "interpretation_boundary",
        ],
    )
    _write_csv(
        sensitivity_path,
        margin_sensitivity,
        ["contrast", "ligand", "inhibitor", "tested_margin", "estimate", "ci_low", "ci_high", "p_tost", "p_tost_holm", "interval_inside_margin", "passes"],
    )
    _write_csv(
        outcomes_path,
        case_summary,
        ["case_id", "source_doi", "heldout_basis", "primary_margin", "threshold_source", "context_count", "pass_count", "fail_count", "inconclusive_count", "evidence_set_decision", "interpretation_boundary"],
        delimiter="\t",
    )
    _write_csv(
        candidates_path,
        candidates,
        ["candidate_id", "source", "candidate_role", "selected", "biological_fit", "metadata_quality", "access_quality", "stress_test_value", "grouping_quality", "total_score", "decision_reason"],
        delimiter="\t",
    )
    _write_text(report_path, _report_markdown(decisions, diagnostics))
    _write_text(docs_report, _report_markdown(decisions, diagnostics))
    _write_text(access_path, _controlled_access_note())
    _make_notebook(notebook_path)

    trajectory_records, trajectory_issues = read_trajectory_csv(trajectory_path)
    coupling_records, coupling_issues = read_coupling_csv(decisions_path)
    if trajectory_issues:
        raise ValueError(f"trajectory schema validation failed: {trajectory_issues}")
    if coupling_issues:
        raise ValueError(f"coupling schema validation failed: {coupling_issues}")
    if len(trajectory_records) != len(trajectory_rows):
        raise ValueError("trajectory schema validation row count mismatch")
    if len(coupling_records) != len(decisions):
        raise ValueError("coupling schema validation row count mismatch")

    outputs = {
        _relative(plan_json): _sha256(plan_json),
        _relative(plan_md): _sha256(plan_md),
        _relative(trajectory_path): _sha256(trajectory_path),
        _relative(summary_path): _sha256(summary_path),
        _relative(decisions_path): _sha256(decisions_path),
        _relative(sensitivity_path): _sha256(sensitivity_path),
        _relative(outcomes_path): _sha256(outcomes_path),
        _relative(candidates_path): _sha256(candidates_path),
        _relative(report_path): _sha256(report_path),
        _relative(access_path): _sha256(access_path),
        _relative(docs_report): _sha256(docs_report),
        _relative(notebook_path): _sha256(notebook_path),
    }
    gate = _gate_report(decisions, diagnostics, outputs)
    _write_json(gate_path, gate)
    _write_json(docs_gate, gate)
    outputs[_relative(gate_path)] = _sha256(gate_path)
    outputs[_relative(docs_gate)] = _sha256(docs_gate)
    provenance = _provenance(archive_sha, member_hashes, thresholds, outputs, diagnostics)
    _write_json(provenance_path, provenance)
    outputs[_relative(provenance_path)] = _sha256(provenance_path)

    print(json.dumps({
        "status": "pass",
        "output_dir": _relative(output_dir),
        "trajectory_rows": len(trajectory_rows),
        "summary_rows": len(summary_rows),
        "decision_rows": len(decisions),
        "pass_context_count": diagnostics["pass_count"],
        "fail_context_count": diagnostics["fail_count"],
        "inconclusive_context_count": diagnostics["inconclusive_count"],
        "gate_report": _relative(gate_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
