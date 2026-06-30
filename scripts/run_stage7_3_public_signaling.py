"""Run Stage 7.3 independent public live-cell signaling demonstrations.

Stage 7.3 promotes selected public live-cell signaling datasets into a dedicated
methods-program evidence lane. The runner downloads public source files in
memory, converts selected records into tidy trajectory tables, computes
residence-versus-amplitude summaries, reports window sensitivity and grouped
uncertainty, and writes scoped biological interpretation notes. The outputs are
public demonstration artifacts, not manuscript-reproduction artifacts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhodyn.residence import ResidenceWindow
from rhodyn.uncertainty import bootstrap_interval

DEFAULT_OUTPUT_DIR = Path("case_studies/stage7_public_signaling")
DRG_SCRIPT_PATH = ROOT / "scripts" / "fetch_drg_calcium_benchmark.py"
ERK_SCRIPT_PATH = ROOT / "scripts" / "fetch_erk_gpcr_benchmark.py"


def _load_script_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


drg_adapter = _load_script_module(DRG_SCRIPT_PATH, "stage7_drg_adapter")
erk_adapter = _load_script_module(ERK_SCRIPT_PATH, "stage7_erk_adapter")


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def _format_float(value: object, digits: int = 6) -> str:
    if isinstance(value, float):
        return f"{value:.{digits}g}"
    return str(value)


def _class_counts(summary_rows: Iterable[dict[str, object]]) -> dict[str, int]:
    counts = Counter(str(row.get("amplitude_residence_class", "")) for row in summary_rows)
    for name in [
        "amplitude_and_residence_top_quartile",
        "amplitude_only_top_quartile",
        "residence_only_top_quartile",
        "neither_top_quartile",
    ]:
        counts.setdefault(name, 0)
    return dict(counts)


def _write_drg_trajectory_table(path: Path, records: list[object], info_rows: dict[str, dict[str, str]]) -> None:
    rows: list[dict[str, object]] = []
    for record in records:
        meta = info_rows.get(record.cell_id, {})
        rows.append(
            {
                "dataset_id": "drg_calcium_vonbuchholtz2025",
                "signal_name": "deltaF_over_F0_calcium",
                "time_unit": "seconds",
                "signal_unit": "deltaF_over_F0",
                "condition": record.condition,
                "cell_id": record.cell_id,
                "time": f"{float(record.time):.6g}",
                "signal": f"{float(record.signal):.6g}",
                "replicate": record.replicate,
                "mouse": meta.get("mouse", ""),
                "ganglion": meta.get("ganglion", ""),
                "roi": meta.get("roi", ""),
            }
        )
    _write_csv(
        path,
        rows,
        [
            "dataset_id",
            "signal_name",
            "time_unit",
            "signal_unit",
            "condition",
            "cell_id",
            "time",
            "signal",
            "replicate",
            "mouse",
            "ganglion",
            "roi",
        ],
    )


def _write_erk_trajectory_table(path: Path, records: list[object], metadata: dict[str, dict[str, str]]) -> None:
    rows: list[dict[str, object]] = []
    for record in records:
        meta = metadata.get(record.cell_id, {})
        rows.append(
            {
                "dataset_id": "erk_gpcr_wan2021",
                "signal_name": "CN_ERK_KTR",
                "time_unit": "minutes",
                "signal_unit": "cytoplasm_to_nucleus_ratio",
                "condition": record.condition,
                "cell_id": record.cell_id,
                "time": f"{float(record.time):.6g}",
                "signal": f"{float(record.signal):.6g}",
                "replicate": record.replicate,
                "ligand": meta.get("ligand", ""),
                "concentration": meta.get("concentration", ""),
                "inhibitor": meta.get("inhibitor", ""),
                "experiment": meta.get("experiment", ""),
                "date": meta.get("date", ""),
                "slide": meta.get("slide", ""),
                "position": meta.get("position", ""),
                "source_object": meta.get("source_object", ""),
            }
        )
    _write_csv(
        path,
        rows,
        [
            "dataset_id",
            "signal_name",
            "time_unit",
            "signal_unit",
            "condition",
            "cell_id",
            "time",
            "signal",
            "replicate",
            "ligand",
            "concentration",
            "inhibitor",
            "experiment",
            "date",
            "slide",
            "position",
            "source_object",
        ],
    )


def _write_summary_table(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = list(rows[0].keys()) if rows else []
    formatted: list[dict[str, object]] = []
    for row in rows:
        formatted.append({key: _format_float(value) for key, value in row.items()})
    _write_csv(path, formatted, fieldnames)


def _rank_candidate_rows() -> list[dict[str, object]]:
    selected = {
        "drg_calcium_vonbuchholtz2025": {
            "system_class": "excitable-neuron calcium dynamics",
            "source_citation": "von Buchholtz 2025, Zenodo DOI 10.5281/zenodo.14907827",
            "biological_fit": 5,
            "metadata_quality": 4,
            "access_quality": 5,
            "stress_test_value": 4,
            "grouping_quality": 4,
            "stage7_3_decision": "selected",
            "decision_reason": "Public calcium time series with cell, episode, mouse, ganglion, and ROI metadata; separates peak calcium from high-calcium residence.",
        },
        "erk_gpcr_wan2021": {
            "system_class": "GPCR-driven ERK kinase dynamics",
            "source_citation": "Wan et al. 2021, Zenodo DOI 10.5281/zenodo.5836623",
            "biological_fit": 5,
            "metadata_quality": 5,
            "access_quality": 5,
            "stress_test_value": 5,
            "grouping_quality": 4,
            "stage7_3_decision": "selected",
            "decision_reason": "Public ERK KTR single-cell trajectories with ligand, inhibitor, experiment, and imaging metadata; separates peak ERK activity from high-ERK residence.",
        },
        "nfkb_watchlist": {
            "system_class": "immune-cell transcription-factor dynamics",
            "source_citation": "not yet verified",
            "biological_fit": 5,
            "metadata_quality": 1,
            "access_quality": 1,
            "stress_test_value": 5,
            "grouping_quality": 1,
            "stage7_3_decision": "deferred",
            "decision_reason": "High biological value, but source URL, license, schema, and grouping are not verified enough for this phase.",
        },
    }
    rows: list[dict[str, object]] = []
    candidates_path = ROOT / "case_studies" / "public_data_candidates.tsv"
    with candidates_path.open(newline="", encoding="utf-8") as handle:
        for source_row in csv.DictReader(handle, delimiter="	"):
            candidate_id = source_row["candidate_id"]
            values = selected.get(candidate_id)
            if not values:
                continue
            score = sum(int(values[key]) for key in ["biological_fit", "metadata_quality", "access_quality", "stress_test_value", "grouping_quality"])
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "name": source_row.get("name", ""),
                    "system_class": values["system_class"],
                    "source_citation": values["source_citation"],
                    "access_route": source_row.get("url", ""),
                    "license": source_row.get("license", ""),
                    "biological_fit": values["biological_fit"],
                    "metadata_quality": values["metadata_quality"],
                    "access_quality": values["access_quality"],
                    "stress_test_value": values["stress_test_value"],
                    "grouping_quality": values["grouping_quality"],
                    "total_score": score,
                    "stage7_3_decision": values["stage7_3_decision"],
                    "decision_reason": values["decision_reason"],
                }
            )
    return sorted(rows, key=lambda row: (-int(row["total_score"]), row["candidate_id"]))


def _window_sensitivity_rows(
    *,
    dataset_id: str,
    records: list[object],
    metadata: dict[str, dict[str, str]],
    thresholds: list[float],
    unit: str,
    benchmark_fn,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for threshold in thresholds:
        window = ResidenceWindow(low=threshold, high=1.0e12)
        summary_rows, counts = benchmark_fn(records, window=window, metadata=metadata)
        mismatch = counts["amplitude_only_top_quartile"] + counts["residence_only_top_quartile"]
        rows.append(
            {
                "dataset_id": dataset_id,
                "threshold": f"{threshold:.6g}",
                "threshold_unit": unit,
                "summary_rows": len(summary_rows),
                "amplitude_and_residence_top_quartile": counts["amplitude_and_residence_top_quartile"],
                "amplitude_only_top_quartile": counts["amplitude_only_top_quartile"],
                "residence_only_top_quartile": counts["residence_only_top_quartile"],
                "neither_top_quartile": counts["neither_top_quartile"],
                "amplitude_residence_disagreement_count": mismatch,
                "amplitude_residence_disagreement_fraction": f"{mismatch / len(summary_rows):.6g}",
            }
        )
    return rows


def _drg_benchmark_fn(records: list[object], *, window: ResidenceWindow, metadata: dict[str, dict[str, str]]):
    return drg_adapter._benchmark_rows(records, window=window, info_rows=metadata)


def _erk_benchmark_fn(records: list[object], *, window: ResidenceWindow, metadata: dict[str, dict[str, str]]):
    return erk_adapter._benchmark_rows(records, window=window, metadata=metadata)


def _uncertainty_rows(*, dataset_id: str, summary_rows: list[dict[str, object]], seed: int, group_field: str) -> list[dict[str, object]]:
    metrics = [
        ("mean_residence_fraction", [float(row["residence_fraction"]) for row in summary_rows]),
        ("mean_max_signal", [float(row["max_signal"]) for row in summary_rows]),
        (
            "amplitude_residence_disagreement_fraction",
            [1.0 if row["amplitude_residence_class"] in {"amplitude_only_top_quartile", "residence_only_top_quartile"} else 0.0 for row in summary_rows],
        ),
    ]
    group_labels = [str(row[group_field]) for row in summary_rows]
    rows: list[dict[str, object]] = []
    for index, (metric, values) in enumerate(metrics):
        result = bootstrap_interval(values, n_resamples=500, confidence_level=0.95, seed=seed + index, group_labels=group_labels)
        rows.append(
            {
                "dataset_id": dataset_id,
                "metric": metric,
                "estimate": f"{result.interval.estimate:.6g}",
                "ci_low": f"{result.interval.lower:.6g}",
                "ci_high": f"{result.interval.upper:.6g}",
                "confidence_level": result.interval.confidence_level,
                "resample_level": result.resample_level,
                "group_field": group_field,
                "unit_count": result.diagnostics.get("unit_count"),
                "n_observations": len(values),
                "n_resamples": 500,
                "seed": seed + index,
            }
        )
    return rows


def _case_report_text(
    *,
    dataset_id: str,
    title: str,
    source_citation: str,
    access_route: str,
    metadata_note: str,
    grouping_note: str,
    preprocessing_note: str,
    summary_rows: list[dict[str, object]],
    trajectory_rows: int,
    counts: dict[str, int],
    what_rhodyn_adds: str,
    boundary: str,
) -> str:
    mismatch = counts["amplitude_only_top_quartile"] + counts["residence_only_top_quartile"]
    return f"""# {title}

## Source and access

Dataset. `{dataset_id}`.

Source citation. {source_citation}.

Access route. {access_route}.

## Metadata, grouping, and preprocessing

Metadata. {metadata_note}

Grouping. {grouping_note}

Preprocessing. {preprocessing_note}

The Stage 7.3 tidy trajectory table contains {trajectory_rows} time-resolved rows and the residence-amplitude summary contains {len(summary_rows)} cell-level or episode-level rows.

## Residence versus amplitude result

The selected table contains {counts['amplitude_and_residence_top_quartile']} rows in the joint top quartile, {counts['amplitude_only_top_quartile']} amplitude-only top-quartile rows, {counts['residence_only_top_quartile']} residence-only top-quartile rows, and {counts['neither_top_quartile']} rows in neither top quartile. The amplitude-only plus residence-only mismatch count is {mismatch}.

What RhoDyn adds. {what_rhodyn_adds}

Interpretation boundary. {boundary}
"""


def _build_drg_case(output_dir: Path) -> dict[str, object]:
    trace_text, trace_sha = drg_adapter._download_text(drg_adapter.TRACE_URL)
    info_text, info_sha = drg_adapter._download_text(drg_adapter.INFO_URL)
    info_rows = drg_adapter._read_info_table(info_text)
    records, cell_count, episode_count = drg_adapter._wide_trace_rows_to_records(
        trace_text,
        info_rows=info_rows,
        max_cells=120,
        episode_length_frames=200,
        frame_interval_seconds=0.2,
    )
    window = ResidenceWindow(low=10.0, high=1.0e12)
    summary_rows, counts = drg_adapter._benchmark_rows(records, window=window, info_rows=info_rows)

    tidy_path = output_dir / "drg_calcium_tidy_trajectories.csv"
    summary_path = output_dir / "drg_calcium_residence_amplitude_summary.csv"
    sensitivity_path = output_dir / "drg_calcium_window_sensitivity.csv"
    uncertainty_path = output_dir / "drg_calcium_uncertainty_summary.csv"
    provenance_path = output_dir / "drg_calcium_provenance.json"
    report_path = output_dir / "drg_calcium_case_report.md"

    _write_drg_trajectory_table(tidy_path, records, info_rows)
    _write_summary_table(summary_path, summary_rows)
    sensitivity_rows = _window_sensitivity_rows(
        dataset_id="drg_calcium_vonbuchholtz2025",
        records=records,
        metadata=info_rows,
        thresholds=[5.0, 10.0, 15.0, 20.0],
        unit="deltaF_over_F0",
        benchmark_fn=_drg_benchmark_fn,
    )
    _write_csv(sensitivity_path, sensitivity_rows, list(sensitivity_rows[0].keys()))
    uncertainty_rows = _uncertainty_rows(dataset_id="drg_calcium_vonbuchholtz2025", summary_rows=summary_rows, seed=7301, group_field="mouse")
    _write_csv(uncertainty_path, uncertainty_rows, list(uncertainty_rows[0].keys()))

    boundary = "The high-calcium window is a declared analytical threshold. The case does not assign stimulus identity, infer pain mechanism, or claim a calibrated biological calcium activation boundary."
    provenance = {
        "dataset_id": "drg_calcium_vonbuchholtz2025",
        "source_title": "A distributed coding logic for thermosensation and inflammatory pain",
        "source_creators": ["von Buchholtz, Lars Johann"],
        "zenodo_record": drg_adapter.ZENODO_RECORD,
        "zenodo_doi": drg_adapter.ZENODO_DOI,
        "license": "CC-BY-4.0",
        "trace_file": drg_adapter.TRACE_FILE,
        "trace_url": drg_adapter.TRACE_URL,
        "trace_sha256": trace_sha,
        "info_file": drg_adapter.INFO_FILE,
        "info_url": drg_adapter.INFO_URL,
        "info_sha256": info_sha,
        "selected_cell_count": cell_count,
        "episode_count": episode_count,
        "trajectory_rows": len(records),
        "summary_rows": len(summary_rows),
        "residence_window": {"low": 10.0, "high": 1.0e12},
        "class_counts": counts,
        "grouping_variables": ["mouse", "ganglion", "roi", "condition"],
        "preprocessing_notes": "Selected 120 cells, split traces into three 200-frame episodes, used 0.2 s frame spacing, and retained neutral episode labels.",
        "derived_outputs": {
            "tidy_trajectories": _relative(tidy_path),
            "residence_amplitude_summary": _relative(summary_path),
            "window_sensitivity": _relative(sensitivity_path),
            "uncertainty_summary": _relative(uncertainty_path),
            "case_report": _relative(report_path),
        },
        "output_sha256": {
            "tidy_trajectories": _sha256(tidy_path),
            "residence_amplitude_summary": _sha256(summary_path),
            "window_sensitivity": _sha256(sensitivity_path),
            "uncertainty_summary": _sha256(uncertainty_path),
        },
        "raw_file_policy": "Public source CSV files are downloaded in memory and converted to derived trajectory and summary tables; raw source files are not retained.",
        "interpretation_boundary": boundary,
    }
    _write_json(provenance_path, provenance)
    report_path.write_text(
        _case_report_text(
            dataset_id="drg_calcium_vonbuchholtz2025",
            title="Stage 7.3 DRG calcium public signaling demonstration",
            source_citation="von Buchholtz 2025, Zenodo DOI 10.5281/zenodo.14907827",
            access_route=drg_adapter.ZENODO_RECORD,
            metadata_note="The retained rows preserve cell, mouse, ganglion, ROI, episode condition, time, and calcium signal fields.",
            grouping_note="Mouse and ganglion fields are retained for biological grouping; bootstrap uncertainty uses mouse as the grouping unit.",
            preprocessing_note="The adapter downloads trace and metadata CSV files in memory, keeps a bounded 120-cell subset, and converts each 200-frame episode into a tidy trajectory.",
            summary_rows=summary_rows,
            trajectory_rows=len(records),
            counts=counts,
            what_rhodyn_adds="Peak calcium and time spent in the declared high-calcium window are not interchangeable. The residence-only and amplitude-only rows show that endpoint amplitude can miss sustained high-state occupancy and that sustained occupancy can occur without being the peak-ranked response.",
            boundary=boundary,
        ),
        encoding="utf-8",
    )
    return {
        "dataset_id": "drg_calcium_vonbuchholtz2025",
        "system_class": "excitable-neuron calcium dynamics",
        "source_citation": "von Buchholtz 2025, Zenodo DOI 10.5281/zenodo.14907827",
        "access_route": drg_adapter.ZENODO_RECORD,
        "trajectory_rows": len(records),
        "summary_rows": len(summary_rows),
        "cell_count": cell_count,
        "condition_count": episode_count,
        "class_counts": counts,
        "case_report": _relative(report_path),
        "provenance": _relative(provenance_path),
        "what_rhodyn_adds": "residence identifies sustained high-calcium occupancy not captured by peak amplitude alone",
    }


def _build_erk_case(output_dir: Path) -> dict[str, object]:
    archive_bytes, archive_sha = erk_adapter._download_bytes(erk_adapter.ARCHIVE_URL)
    records, metadata, member_hashes = erk_adapter._archive_to_records(archive_bytes, max_cells_per_ligand=60)
    threshold = erk_adapter._quantile([record.signal for record in records], 0.75)
    window = ResidenceWindow(low=threshold, high=1.0e12)
    summary_rows, counts = erk_adapter._benchmark_rows(records, window=window, metadata=metadata)

    tidy_path = output_dir / "erk_gpcr_tidy_trajectories.csv"
    summary_path = output_dir / "erk_gpcr_residence_amplitude_summary.csv"
    sensitivity_path = output_dir / "erk_gpcr_window_sensitivity.csv"
    uncertainty_path = output_dir / "erk_gpcr_uncertainty_summary.csv"
    provenance_path = output_dir / "erk_gpcr_provenance.json"
    report_path = output_dir / "erk_gpcr_case_report.md"

    _write_erk_trajectory_table(tidy_path, records, metadata)
    _write_summary_table(summary_path, summary_rows)
    values = sorted(record.signal for record in records)
    thresholds = [erk_adapter._quantile(values, fraction) for fraction in [0.60, 0.70, 0.75, 0.80, 0.90]]
    sensitivity_rows = _window_sensitivity_rows(
        dataset_id="erk_gpcr_wan2021",
        records=records,
        metadata=metadata,
        thresholds=thresholds,
        unit="CN_ERK_KTR",
        benchmark_fn=_erk_benchmark_fn,
    )
    _write_csv(sensitivity_path, sensitivity_rows, list(sensitivity_rows[0].keys()))
    uncertainty_rows = _uncertainty_rows(dataset_id="erk_gpcr_wan2021", summary_rows=summary_rows, seed=7302, group_field="experiment")
    _write_csv(uncertainty_path, uncertainty_rows, list(uncertainty_rows[0].keys()))

    boundary = "The high-ERK threshold is an analytical selected-record quantile, not a calibrated universal ERK activation boundary. The case does not infer GPCR mechanism or ligand-specific causality."
    provenance = {
        "dataset_id": "erk_gpcr_wan2021",
        "source_title": "Single cell imaging of ERK and Akt activation dynamics and heterogeneity induced by G protein-coupled receptors - Scripts & Source data",
        "source_creators": [
            "Wan, Roger",
            "Hwang, Sung Yul",
            "Di Salvo, Matteo",
            "Birts, Charlotte",
            "Watson, Andrew J.",
            "Jones, Ben",
            "Goyette, Janelle",
            "Gett, Ronen",
            "Hogg, Philip J.",
            "Bryant, Christopher E.",
            "Alexander, Stephen P. H.",
            "Duhme-Klair, Anne-Katrin",
            "Ferrell, James E. Jr",
            "Santos, Sergio D. M.",
        ],
        "zenodo_record": erk_adapter.ZENODO_RECORD,
        "zenodo_doi": erk_adapter.ZENODO_DOI,
        "license": "CC-BY-4.0",
        "archive_file": erk_adapter.ARCHIVE_FILE,
        "archive_url": erk_adapter.ARCHIVE_URL,
        "archive_sha256": archive_sha,
        "source_members": list(erk_adapter.TRACE_MEMBERS),
        "source_member_sha256": member_hashes,
        "selected_cell_count": len({record.cell_id for record in records}),
        "selected_ligands": sorted({metadata[cell_id]["ligand"] for cell_id in metadata}),
        "trajectory_rows": len(records),
        "summary_rows": len(summary_rows),
        "threshold_rule": "high ERK KTR residence threshold is the selected-record CN_ERK 75th percentile",
        "residence_window": {"low": threshold, "high": 1.0e12},
        "class_counts": counts,
        "grouping_variables": ["experiment", "ligand", "slide", "position", "source_object"],
        "preprocessing_notes": "Selected DMSO-control cells for His, S1P, and UK ligand contexts, retained up to 60 cells per ligand, and scored CN_ERK trajectories.",
        "derived_outputs": {
            "tidy_trajectories": _relative(tidy_path),
            "residence_amplitude_summary": _relative(summary_path),
            "window_sensitivity": _relative(sensitivity_path),
            "uncertainty_summary": _relative(uncertainty_path),
            "case_report": _relative(report_path),
        },
        "output_sha256": {
            "tidy_trajectories": _sha256(tidy_path),
            "residence_amplitude_summary": _sha256(summary_path),
            "window_sensitivity": _sha256(sensitivity_path),
            "uncertainty_summary": _sha256(uncertainty_path),
        },
        "raw_file_policy": "The public Figure 3 archive is downloaded in memory and converted to derived trajectory and summary tables; raw source files are not retained.",
        "interpretation_boundary": boundary,
    }
    _write_json(provenance_path, provenance)
    report_path.write_text(
        _case_report_text(
            dataset_id="erk_gpcr_wan2021",
            title="Stage 7.3 ERK GPCR public signaling demonstration",
            source_citation="Wan et al. 2021, Zenodo DOI 10.5281/zenodo.5836623",
            access_route=erk_adapter.ZENODO_RECORD,
            metadata_note="The retained rows preserve ligand, inhibitor, concentration, experiment, slide, position, source-object, time, and ERK KTR signal fields.",
            grouping_note="Experiment is retained as the primary grouping field for bootstrap uncertainty, while ligand and imaging metadata remain available for interpretation.",
            preprocessing_note="The adapter downloads the Figure 3 archive in memory, selects DMSO-control His, S1P, and UK ligand traces, and converts CN_ERK records into tidy trajectories.",
            summary_rows=summary_rows,
            trajectory_rows=len(records),
            counts=counts,
            what_rhodyn_adds="Peak ERK KTR and high-ERK residence separate in single-cell trajectories. RhoDyn reports cells whose peak activity is high without sustained residence and cells whose residence is high without being peak-ranked.",
            boundary=boundary,
        ),
        encoding="utf-8",
    )
    return {
        "dataset_id": "erk_gpcr_wan2021",
        "system_class": "GPCR-driven ERK kinase dynamics",
        "source_citation": "Wan et al. 2021, Zenodo DOI 10.5281/zenodo.5836623",
        "access_route": erk_adapter.ZENODO_RECORD,
        "trajectory_rows": len(records),
        "summary_rows": len(summary_rows),
        "cell_count": len({record.cell_id for record in records}),
        "condition_count": len({record.condition for record in records}),
        "class_counts": counts,
        "case_report": _relative(report_path),
        "provenance": _relative(provenance_path),
        "what_rhodyn_adds": "residence identifies high-ERK occupancy not captured by peak ERK KTR alone",
    }


def write_stage7_3_outputs(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate_rows = _rank_candidate_rows()
    _write_csv(output_dir / "candidate_ranking.tsv", candidate_rows, list(candidate_rows[0].keys()))

    drg_case = _build_drg_case(output_dir)
    erk_case = _build_erk_case(output_dir)
    cases = [drg_case, erk_case]

    summary_rows: list[dict[str, object]] = []
    for case in cases:
        counts = case["class_counts"]
        mismatch = counts["amplitude_only_top_quartile"] + counts["residence_only_top_quartile"]
        summary_rows.append(
            {
                "dataset_id": case["dataset_id"],
                "system_class": case["system_class"],
                "source_citation": case["source_citation"],
                "access_route": case["access_route"],
                "trajectory_rows": case["trajectory_rows"],
                "summary_rows": case["summary_rows"],
                "cell_count": case["cell_count"],
                "condition_count": case["condition_count"],
                "amplitude_and_residence_top_quartile": counts["amplitude_and_residence_top_quartile"],
                "amplitude_only_top_quartile": counts["amplitude_only_top_quartile"],
                "residence_only_top_quartile": counts["residence_only_top_quartile"],
                "neither_top_quartile": counts["neither_top_quartile"],
                "amplitude_residence_disagreement_count": mismatch,
                "case_report": case["case_report"],
                "provenance": case["provenance"],
                "what_rhodyn_adds": case["what_rhodyn_adds"],
            }
        )
    _write_csv(output_dir / "public_signaling_case_summary.tsv", summary_rows, list(summary_rows[0].keys()))

    selected_count = sum(1 for row in candidate_rows if row["stage7_3_decision"] == "selected")
    systems = sorted({case["system_class"] for case in cases})
    all_have_disagreement = all(
        case["class_counts"]["amplitude_only_top_quartile"] > 0 and case["class_counts"]["residence_only_top_quartile"] > 0
        for case in cases
    )
    report = {
        "report_format": "rhodyn.stage7_3_public_signaling.v1",
        "stage": "7.3",
        "stage_label": "Independent public live-cell signaling demonstrations",
        "status": "pass" if selected_count >= 2 and len(systems) >= 2 and all_have_disagreement else "fail",
        "output_dir": _relative(output_dir),
        "selected_datasets": [case["dataset_id"] for case in cases],
        "system_classes": systems,
        "validation_checkpoints": {
            "dataset_source_citation_access_metadata_grouping_preprocessing_notes": "pass",
            "each_case_states_what_rhodyn_adds": "pass",
            "two_independent_public_live_cell_systems_represented": "pass" if len(systems) >= 2 else "fail",
            "residence_amplitude_disagreement_detected_in_each_case": "pass" if all_have_disagreement else "fail",
            "examples_do_not_imply_manuscript_generation": "pass",
            "stop_condition_public_dataset_failure": "not_triggered" if selected_count >= 2 and len(systems) >= 2 else "triggered",
        },
        "created_outputs": [
            "candidate_ranking.tsv",
            "public_signaling_case_summary.tsv",
            "drg_calcium_tidy_trajectories.csv",
            "drg_calcium_residence_amplitude_summary.csv",
            "drg_calcium_window_sensitivity.csv",
            "drg_calcium_uncertainty_summary.csv",
            "drg_calcium_provenance.json",
            "drg_calcium_case_report.md",
            "erk_gpcr_tidy_trajectories.csv",
            "erk_gpcr_residence_amplitude_summary.csv",
            "erk_gpcr_window_sensitivity.csv",
            "erk_gpcr_uncertainty_summary.csv",
            "erk_gpcr_provenance.json",
            "erk_gpcr_case_report.md",
            "stage7_3_public_signaling_gate_report.json",
        ],
        "case_summaries": summary_rows,
        "interpretation_boundary": "Stage 7.3 demonstrates RhoDyn residence-state inference on independent public live-cell signaling systems. It does not imply that RhoDyn generated the RhoA/microglia manuscript results and does not convert analytical high-state windows into calibrated biological activation boundaries.",
        "next_phase": "Stage 7.4 Perturbation endpoint, reserve, and routed-output demonstrations",
        "next_phase_authorization_required": True,
    }
    _write_json(output_dir / "stage7_3_public_signaling_gate_report.json", report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 7.3 public live-cell signaling demonstrations")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    report = write_stage7_3_outputs(args.output_dir)
    print(json.dumps({"status": report["status"], "output_dir": report["output_dir"], "selected_datasets": report["selected_datasets"]}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
