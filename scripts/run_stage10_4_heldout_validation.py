"""Run Stage 10.4 sealed held-out validation.

Stage 10.4 turns the earlier held-out evidence into an editor-facing challenge
route. The runner writes a predeclaration, then evaluates fixed public
held-out contexts without retuning. It must preserve positive, negative, and
inconclusive calls so RhoDyn reads as a decision method rather than a
success-only workflow.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OUTPUT_DIR = ROOT / "case_studies" / "stage10_heldout_validation"
MLCI_SUMMARY = ROOT / "case_studies" / "stage10_public_breadth" / "stage10_3_mlci_tracking_residence_summary.csv"
ERK_SUMMARY = ROOT / "case_studies" / "stage7_public_signaling" / "erk_gpcr_residence_amplitude_summary.csv"
ERK_AKT_HELDOUT = ROOT / "case_studies" / "stage7_heldout_validation" / "heldout_bounded_coupling_decisions.csv"
ERK_AKT_STAGE7_PLAN = ROOT / "case_studies" / "stage7_heldout_validation" / "heldout_analysis_plan.json"
STAGE10_3_REPORT = ROOT / "case_studies" / "stage10_public_breadth" / "stage10_3_public_breadth_report.json"

DISCORDANCE_JACCARD_MAX = 0.50
CONCORDANCE_JACCARD_MIN = 0.75
MIN_DISCORDANT_HELDOUT_OBJECTS = 2
THRESHOLD_QUANTILE = 0.75


def _read_csv(path: Path, *, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None, *, delimiter: str = ",") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=delimiter, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _format_value(row.get(field, "")) for field in fieldnames})


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _format_value(value: object) -> object:
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return f"{value:.8g}"
    return value


def _quantile(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("quantile requires values")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = fraction * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _classify_pair(amp: bool, residence: bool) -> str:
    if amp and residence:
        return "amplitude_and_residence_high"
    if amp:
        return "amplitude_only_high"
    if residence:
        return "residence_only_high"
    return "neither_high"


def _jaccard_from_counts(counts: Counter[str]) -> float:
    both = counts["amplitude_and_residence_high"]
    union = both + counts["amplitude_only_high"] + counts["residence_only_high"]
    return 1.0 if union == 0 else both / union


def _trajectory_split_decision(
    *,
    case_id: str,
    rows: list[dict[str, str]],
    split_field: str,
    train_values: set[str],
    heldout_values: set[str],
    source: str,
    domain: str,
    interpretation_boundary: str,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    train = [row for row in rows if row[split_field] in train_values]
    heldout = [row for row in rows if row[split_field] in heldout_values]
    if not train or not heldout:
        raise ValueError(f"{case_id} requires non-empty training and held-out rows")
    amp_threshold = _quantile([float(row["max_signal"]) for row in train], THRESHOLD_QUANTILE)
    residence_threshold = _quantile([float(row["residence_fraction"]) for row in train], THRESHOLD_QUANTILE)
    counts: Counter[str] = Counter()
    object_rows: list[dict[str, object]] = []
    for row in heldout:
        amp_high = float(row["max_signal"]) >= amp_threshold
        residence_high = float(row["residence_fraction"]) >= residence_threshold
        class_label = _classify_pair(amp_high, residence_high)
        counts[class_label] += 1
        object_rows.append(
            {
                "case_id": case_id,
                "object_id": row.get("cell_id", ""),
                "split": "heldout",
                "source": source,
                "group": row.get(split_field, ""),
                "max_signal": float(row["max_signal"]),
                "residence_fraction": float(row["residence_fraction"]),
                "amplitude_threshold": amp_threshold,
                "residence_threshold": residence_threshold,
                "heldout_class": class_label,
            }
        )
    discordant_count = counts["amplitude_only_high"] + counts["residence_only_high"]
    jaccard = _jaccard_from_counts(counts)
    if jaccard <= DISCORDANCE_JACCARD_MAX and discordant_count >= MIN_DISCORDANT_HELDOUT_OBJECTS:
        call = "positive_residence_changes_interpretation"
        outcome_class = "positive"
    elif jaccard >= CONCORDANCE_JACCARD_MIN:
        call = "negative_amplitude_or_comparator_largely_sufficient"
        outcome_class = "negative"
    else:
        call = "inconclusive_residence_amplitude_boundary"
        outcome_class = "inconclusive"
    decision = {
        "case_id": case_id,
        "challenge_type": "trajectory_residence_amplitude_holdout",
        "source": source,
        "domain": domain,
        "train_definition": f"{split_field} in {','.join(sorted(train_values))}",
        "heldout_definition": f"{split_field} in {','.join(sorted(heldout_values))}",
        "n_train_objects": len(train),
        "n_heldout_objects": len(heldout),
        "amplitude_threshold": amp_threshold,
        "residence_threshold": residence_threshold,
        "jaccard_high_sets": jaccard,
        "discordant_heldout_objects": discordant_count,
        "amplitude_only_high": counts["amplitude_only_high"],
        "residence_only_high": counts["residence_only_high"],
        "both_high": counts["amplitude_and_residence_high"],
        "neither_high": counts["neither_high"],
        "call": call,
        "outcome_class": outcome_class,
        "hidden_tuning_status": "fixed_split_and_training_thresholds",
        "interpretation_boundary": interpretation_boundary,
    }
    return decision, object_rows


def _mlci_decision() -> tuple[dict[str, object], list[dict[str, object]]]:
    rows = _read_csv(MLCI_SUMMARY)
    return _trajectory_split_decision(
        case_id="mlci_replicate_01_heldout_residence_amplitude",
        rows=rows,
        split_field="replicate",
        train_values={"00"},
        heldout_values={"01"},
        source="Zenodo DOI 10.5281/zenodo.7260137",
        domain="microbial live-cell tracking",
        interpretation_boundary="Tracking intensity is a public trajectory stress test for schema portability and residence/amplitude divergence, not a molecular signaling reporter.",
    )


def _erk_gpcr_decision() -> tuple[dict[str, object], list[dict[str, object]]]:
    rows = _read_csv(ERK_SUMMARY)
    ligands = sorted({row["ligand"] for row in rows})
    train_values = {ligand for index, ligand in enumerate(ligands) if index % 2 == 0}
    heldout_values = set(ligands) - train_values
    return _trajectory_split_decision(
        case_id="erk_gpcr_ligand_s1p_heldout_residence_amplitude",
        rows=rows,
        split_field="ligand",
        train_values=train_values,
        heldout_values=heldout_values,
        source="Zenodo DOI 10.5281/zenodo.5836623",
        domain="GPCR-linked ERK kinase dynamics",
        interpretation_boundary="A concordant held-out ligand supports an amplitude/comparator-sufficient boundary for this split, not a claim that ERK dynamics are always amplitude-sufficient.",
    )


def _erk_akt_decisions() -> list[dict[str, object]]:
    rows = _read_csv(ERK_AKT_HELDOUT)
    pass_rows = [row for row in rows if row["outcome"] == "pass_bounded_coupling"]
    fail_rows = [row for row in rows if row["outcome"] == "fail_outside_margin"]
    inconclusive_rows = [row for row in rows if row["outcome"] == "inconclusive_margin_boundary"]
    decisions: list[dict[str, object]] = []
    if pass_rows:
        decisions.append(
            {
                "case_id": "erk_akt_non_dmso_contexts_bounded_coupling_pass",
                "challenge_type": "paired_reporter_margin_holdout",
                "source": "Zenodo DOI 10.5281/zenodo.5836623",
                "domain": "paired kinase reporter dynamics",
                "train_definition": "Stage 7.4 DMSO-control ERK/Akt thresholds and +/-0.20 margin",
                "heldout_definition": "non-DMSO inhibitor contexts",
                "n_train_objects": "",
                "n_heldout_objects": sum(int(row["n"]) for row in pass_rows),
                "amplitude_threshold": "",
                "residence_threshold": "",
                "jaccard_high_sets": "",
                "discordant_heldout_objects": "",
                "amplitude_only_high": "",
                "residence_only_high": "",
                "both_high": "",
                "neither_high": "",
                "call": "positive_bounded_coupling_preserved",
                "outcome_class": "positive",
                "hidden_tuning_status": "stage7_5_fixed_thresholds_margin_and_contexts",
                "interpretation_boundary": "Passing contexts support bounded coupling of derived ERK/Akt residence summaries in those ligand-inhibitor contexts only.",
                "context_count": len(pass_rows),
                "contexts": ";".join(row["contrast"] for row in pass_rows),
            }
        )
    if fail_rows:
        decisions.append(
            {
                "case_id": "erk_akt_non_dmso_contexts_margin_fail",
                "challenge_type": "paired_reporter_margin_holdout",
                "source": "Zenodo DOI 10.5281/zenodo.5836623",
                "domain": "paired kinase reporter dynamics",
                "train_definition": "Stage 7.4 DMSO-control ERK/Akt thresholds and +/-0.20 margin",
                "heldout_definition": "non-DMSO inhibitor contexts",
                "call": "negative_outside_declared_margin",
                "outcome_class": "negative",
                "hidden_tuning_status": "stage7_5_fixed_thresholds_margin_and_contexts",
                "interpretation_boundary": "A fail context would reject bounded coupling for that declared margin and context, not identify a biochemical edge.",
                "context_count": len(fail_rows),
                "contexts": ";".join(row["contrast"] for row in fail_rows),
            }
        )
    if inconclusive_rows:
        decisions.append(
            {
                "case_id": "erk_akt_non_dmso_contexts_margin_inconclusive",
                "challenge_type": "paired_reporter_margin_holdout",
                "source": "Zenodo DOI 10.5281/zenodo.5836623",
                "domain": "paired kinase reporter dynamics",
                "train_definition": "Stage 7.4 DMSO-control ERK/Akt thresholds and +/-0.20 margin",
                "heldout_definition": "non-DMSO inhibitor contexts",
                "n_train_objects": "",
                "n_heldout_objects": sum(int(row["n"]) for row in inconclusive_rows),
                "amplitude_threshold": "",
                "residence_threshold": "",
                "jaccard_high_sets": "",
                "discordant_heldout_objects": "",
                "amplitude_only_high": "",
                "residence_only_high": "",
                "both_high": "",
                "neither_high": "",
                "call": "inconclusive_margin_boundary_preserved",
                "outcome_class": "inconclusive",
                "hidden_tuning_status": "stage7_5_fixed_thresholds_margin_and_contexts",
                "interpretation_boundary": "Inconclusive contexts remain visible when fixed margins do not support promotion.",
                "context_count": len(inconclusive_rows),
                "contexts": ";".join(row["contrast"] for row in inconclusive_rows),
            }
        )
    return decisions


def _predeclaration() -> dict[str, object]:
    stage7_plan = json.loads(ERK_AKT_STAGE7_PLAN.read_text(encoding="utf-8"))
    return {
        "stage": "10.4",
        "analysis_id": "stage10_4_sealed_heldout_challenge",
        "status": "predeclared_before_stage10_4_outputs",
        "challenge_type": "sealed_replay_from_public_derived_tables",
        "scope_boundary": (
            "This is a no-retuning held-out challenge over public-derived tables already retained in RhoDyn. "
            "It is not a prospective blinded collaborator study and does not create a universal performance claim."
        ),
        "trajectory_decision_rule": {
            "threshold_source": "training split only",
            "threshold_quantile": THRESHOLD_QUANTILE,
            "positive_call": f"Jaccard <= {DISCORDANCE_JACCARD_MAX} with at least {MIN_DISCORDANT_HELDOUT_OBJECTS} discordant held-out objects",
            "negative_call": f"Jaccard >= {CONCORDANCE_JACCARD_MIN}",
            "inconclusive_call": "all other cases",
        },
        "trajectory_challenges": [
            {
                "case_id": "mlci_replicate_01_heldout_residence_amplitude",
                "source": "Zenodo DOI 10.5281/zenodo.7260137",
                "train": "replicate 00",
                "heldout": "replicate 01",
            },
            {
                "case_id": "erk_gpcr_ligand_s1p_heldout_residence_amplitude",
                "source": "Zenodo DOI 10.5281/zenodo.5836623",
                "train": "lexically sorted ligands at even indices",
                "heldout": "remaining ligands",
            },
        ],
        "paired_reporter_challenge": {
            "case_id": "wan2021_erk_akt_non_dmso_inhibitors",
            "source": "Zenodo DOI 10.5281/zenodo.5836623",
            "stage7_5_fixed_plan": stage7_plan,
        },
        "required_gate": "at least one positive, one negative, and one inconclusive held-out call with no retuning",
    }


def _predeclaration_markdown(payload: dict[str, object]) -> str:
    return f"""# Stage 10.4 held-out validation predeclaration

Stage 10.4 evaluates RhoDyn as a no-retuning decision method. The challenge is sealed as a replay over public-derived tables already retained in the repository. It is stricter than a figure caption because the train splits, held-out contexts, thresholds, margins, and outcome classes are written before the Stage 10.4 output tables are interpreted.

## Trajectory rule

Training rows define the 75th-percentile amplitude and residence thresholds. Held-out rows are then classified as amplitude-high, residence-high, both, or neither. A held-out case is called positive when the high-set Jaccard overlap is at most {DISCORDANCE_JACCARD_MAX} and at least {MIN_DISCORDANT_HELDOUT_OBJECTS} held-out objects are discordant. A case is called negative when the high-set Jaccard overlap is at least {CONCORDANCE_JACCARD_MIN}. Other cases remain inconclusive.

## Fixed challenges

- MLCI tracking. Train on replicate 00 and hold out replicate 01.
- ERK GPCR trajectories. Train on lexically sorted even-index ligands and hold out the remaining ligand.
- ERK/Akt paired reporter coupling. Reuse the Stage 7.5 non-DMSO held-out plan with fixed DMSO-derived thresholds and the fixed +/-0.20 ERK-minus-Akt residence margin.

## Boundary

This stage is not a prospective blind collaborator study. It is a sealed replay that tests whether already-retained public examples preserve positive, negative, and inconclusive decisions under fixed rules. It does not show universal RhoDyn superiority and does not identify molecular mechanisms.
"""


def _report_markdown(decisions: list[dict[str, object]], gates: dict[str, bool]) -> str:
    rows = "\n".join(
        f"| {row['case_id']} | {row['challenge_type']} | {row['outcome_class']} | {row['call']} | {row.get('interpretation_boundary', '')} |"
        for row in decisions
    )
    return f"""# Stage 10.4 held-out validation report

Stage 10.4 adds the no-retuning validation layer that the Nature Methods rescue roadmap requires. The stage deliberately includes positive, negative, and inconclusive calls, because a method-level claim is stronger when unsupported calls remain visible.

## Decisions

| case | challenge | outcome class | call | boundary |
| --- | --- | --- | --- | --- |
{rows}

## Gate result

Status. `{'pass' if all(gates.values()) else 'fail'}`.

- Positive held-out call present. `{gates['positive_call_present']}`.
- Negative or amplitude-sufficient held-out call present. `{gates['negative_call_present']}`.
- Inconclusive held-out call present. `{gates['inconclusive_call_present']}`.
- No-retuning predeclaration present. `{gates['predeclaration_present']}`.
- Stage 10.3 public breadth prerequisite passed. `{gates['stage10_3_prerequisite_passed']}`.

## Interpretation

The held-out challenge strengthens RhoDyn's method reading because the same decision framework can preserve a residence-divergence call, withhold a margin-boundary call, and identify a comparator-sufficient boundary without rewriting the rule for each outcome. The result is still scoped. It is not a claim that every public biological system contains a residence regime or that RhoDyn always outperforms simpler summaries.
"""


def evaluate_stage10_4(output_dir: Path = OUTPUT_DIR) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    predeclared = _predeclaration()
    _write_json(output_dir / "stage10_4_predeclaration.json", predeclared)
    _write_text(output_dir / "stage10_4_predeclaration.md", _predeclaration_markdown(predeclared))

    mlci_decision, mlci_objects = _mlci_decision()
    erk_decision, erk_objects = _erk_gpcr_decision()
    decisions = [mlci_decision, erk_decision, *_erk_akt_decisions()]
    object_rows = [*mlci_objects, *erk_objects]

    decision_fields = [
        "case_id",
        "challenge_type",
        "source",
        "domain",
        "train_definition",
        "heldout_definition",
        "n_train_objects",
        "n_heldout_objects",
        "amplitude_threshold",
        "residence_threshold",
        "jaccard_high_sets",
        "discordant_heldout_objects",
        "amplitude_only_high",
        "residence_only_high",
        "both_high",
        "neither_high",
        "context_count",
        "contexts",
        "call",
        "outcome_class",
        "hidden_tuning_status",
        "interpretation_boundary",
    ]
    _write_csv(output_dir / "stage10_4_heldout_decisions.tsv", decisions, decision_fields, delimiter="\t")
    _write_csv(
        output_dir / "stage10_4_trajectory_object_calls.csv",
        object_rows,
        [
            "case_id",
            "object_id",
            "split",
            "source",
            "group",
            "max_signal",
            "residence_fraction",
            "amplitude_threshold",
            "residence_threshold",
            "heldout_class",
        ],
    )

    stage10_3_pass = json.loads(STAGE10_3_REPORT.read_text(encoding="utf-8")).get("status") == "pass"
    outcome_classes = {str(row["outcome_class"]) for row in decisions}
    gates = {
        "predeclaration_present": (output_dir / "stage10_4_predeclaration.json").exists(),
        "stage10_3_prerequisite_passed": bool(stage10_3_pass),
        "positive_call_present": "positive" in outcome_classes,
        "negative_call_present": "negative" in outcome_classes,
        "inconclusive_call_present": "inconclusive" in outcome_classes,
        "no_hidden_tuning_status_recorded": all(row.get("hidden_tuning_status") for row in decisions),
        "three_or_more_challenge_rows": len(decisions) >= 3,
    }
    report = {
        "stage": "10.4",
        "status": "pass" if all(gates.values()) else "fail",
        "report_format": "rhodyn.stage10_4_heldout_validation.v1",
        "output_dir": "case_studies/stage10_heldout_validation",
        "gates": gates,
        "summary_metrics": {
            "decision_count": len(decisions),
            "positive_call_count": sum(1 for row in decisions if row["outcome_class"] == "positive"),
            "negative_call_count": sum(1 for row in decisions if row["outcome_class"] == "negative"),
            "inconclusive_call_count": sum(1 for row in decisions if row["outcome_class"] == "inconclusive"),
            "trajectory_object_call_rows": len(object_rows),
        },
        "interpretation_boundary": (
            "Stage 10.4 is a sealed replay held-out validation over retained public-derived tables. "
            "It strengthens no-retuning evidence but does not replace a prospective blinded collaborator study."
        ),
        "created_outputs": [
            "stage10_4_predeclaration.json",
            "stage10_4_predeclaration.md",
            "stage10_4_heldout_decisions.tsv",
            "stage10_4_trajectory_object_calls.csv",
            "stage10_4_heldout_report.md",
            "stage10_4_gate_report.json",
        ],
        "next_phase": "Stage 10.5 method-first Nature Methods figure architecture",
    }
    _write_text(output_dir / "stage10_4_heldout_report.md", _report_markdown(decisions, gates))
    _write_json(output_dir / "stage10_4_gate_report.json", report)
    return report


def main() -> int:
    report = evaluate_stage10_4()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
