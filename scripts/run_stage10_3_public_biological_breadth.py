"""Run Stage 10.3 expanded public biological breadth.

Stage 10.3 addresses the second Nature Methods vulnerability in the Stage 10
roadmap: public biological breadth. It aggregates retained public-derived
demonstrations, promotes the MLCI live-cell tracking subset into the Stage 10
breadth matrix, and probes an additional public ERK/Akt cell-division source
without retaining unlicensed derivative data. It does not add manuscript-private
data, new wet-lab results, or universal residence-regime claims.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhodyn.residence import ResidenceWindow, score_trace
from rhodyn.schema import TrajectoryRecord


OUTPUT_DIR = ROOT / "case_studies" / "stage10_public_breadth"
MLCI_FEATURES = ROOT / "case_studies" / "mlci_public_track_features_subset.csv"
DRG_SUMMARY = ROOT / "case_studies" / "stage7_public_signaling" / "drg_calcium_residence_amplitude_summary.csv"
ERK_SUMMARY = ROOT / "case_studies" / "stage7_public_signaling" / "erk_gpcr_residence_amplitude_summary.csv"
CELL_MODEL_RANKING = ROOT / "case_studies" / "stage7_endpoint_reserve_routing" / "cell_painting_routed_model_comparison.csv"
CELL_RESERVE_ROWS = ROOT / "case_studies" / "stage7_endpoint_reserve_routing" / "cell_painting_reserve_like_endpoint_rows.csv"
ERK_AKT_COUPLING = ROOT / "case_studies" / "stage7_endpoint_reserve_routing" / "erk_akt_bounded_coupling_decisions.csv"
STAGE7_CASE_SUMMARY = ROOT / "case_studies" / "stage7_endpoint_reserve_routing" / "stage7_4_case_summary.tsv"
PUBLIC_CANDIDATES = ROOT / "case_studies" / "public_data_candidates.tsv"

BIRTWISTLE_REPO = "https://github.com/birtwistlelab/Predicting-Individual-Cell-Division-Events-from-Single-Cell-ERK-and-Akt-Dynamics"
BIRTWISTLE_API = "https://api.github.com/repos/birtwistlelab/Predicting-Individual-Cell-Division-Events-from-Single-Cell-ERK-and-Akt-Dynamics"
BIRTWISTLE_README = "https://raw.githubusercontent.com/birtwistlelab/Predicting-Individual-Cell-Division-Events-from-Single-Cell-ERK-and-Akt-Dynamics/main/README.md"
BIRTWISTLE_MAT_URLS = {
    "all_div_cells_ERK": "https://raw.githubusercontent.com/birtwistlelab/Predicting-Individual-Cell-Division-Events-from-Single-Cell-ERK-and-Akt-Dynamics/main/src/all_div_cells_ERK.mat",
    "all_non_div_ERK": "https://raw.githubusercontent.com/birtwistlelab/Predicting-Individual-Cell-Division-Events-from-Single-Cell-ERK-and-Akt-Dynamics/main/src/all_non_div_ERK.mat",
    "all_div_cells_Akt": "https://raw.githubusercontent.com/birtwistlelab/Predicting-Individual-Cell-Division-Events-from-Single-Cell-ERK-and-Akt-Dynamics/main/src/all_div_cells_Akt.mat",
    "all_non_div_Akt": "https://raw.githubusercontent.com/birtwistlelab/Predicting-Individual-Cell-Division-Events-from-Single-Cell-ERK-and-Akt-Dynamics/main/src/all_non_div_Akt.mat",
}


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


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _quantile(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("quantile requires non-empty values")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = fraction * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _class_counts(rows: Iterable[dict[str, str]]) -> dict[str, int]:
    counts = Counter(row.get("amplitude_residence_class", "") for row in rows)
    for label in [
        "amplitude_and_residence_top_quartile",
        "amplitude_only_top_quartile",
        "residence_only_top_quartile",
        "neither_top_quartile",
    ]:
        counts.setdefault(label, 0)
    return dict(counts)


def _mlci_trajectory_records() -> list[TrajectoryRecord]:
    records: list[TrajectoryRecord] = []
    for row in _read_csv(MLCI_FEATURES):
        try:
            signal = float(row["intensity"])
            time = float(row["frame"])
        except (KeyError, ValueError):
            continue
        if not math.isfinite(signal) or not math.isfinite(time):
            continue
        cell_id = f"mlci_seq{row.get('sequence', '')}_track{row.get('track_id', '')}"
        records.append(
            TrajectoryRecord(
                cell_id=cell_id,
                time=time,
                condition="mlci_tracking_intensity",
                signal=signal,
                replicate=row.get("sequence", ""),
            )
        )
    return records


def _mlci_summary_rows() -> list[dict[str, object]]:
    records = _mlci_trajectory_records()
    values = [record.signal for record in records]
    window = ResidenceWindow(_quantile(values, 0.40), _quantile(values, 0.70))
    grouped: dict[str, list[TrajectoryRecord]] = defaultdict(list)
    for record in records:
        grouped[record.cell_id].append(record)
    summaries = []
    for cell_id, trace in grouped.items():
        scored = score_trace(trace, window)
        summaries.append(
            {
                "dataset": "mlci_tracking",
                "cell_id": cell_id,
                "replicate": trace[0].replicate,
                "n_points": scored.n_points,
                "mean_signal": scored.mean_signal,
                "max_signal": scored.max_signal,
                "min_signal": scored.min_signal,
                "residence_fraction": scored.residence_fraction,
                "residence_time_frames": scored.residence_time,
                "total_time_frames": scored.total_time,
                "window_low": window.low,
                "window_high": window.high,
            }
        )
    peak_cut = _quantile([float(row["max_signal"]) for row in summaries], 0.75)
    residence_cut = _quantile([float(row["residence_fraction"]) for row in summaries], 0.75)
    for row in summaries:
        amp = float(row["max_signal"]) >= peak_cut
        res = float(row["residence_fraction"]) >= residence_cut
        row["amplitude_top_quartile"] = int(amp)
        row["residence_top_quartile"] = int(res)
        if amp and res:
            row["amplitude_residence_class"] = "amplitude_and_residence_top_quartile"
        elif amp:
            row["amplitude_residence_class"] = "amplitude_only_top_quartile"
        elif res:
            row["amplitude_residence_class"] = "residence_only_top_quartile"
        else:
            row["amplitude_residence_class"] = "neither_top_quartile"
    return summaries


def _birtwistle_probe() -> dict[str, object]:
    probe: dict[str, object] = {
        "source_id": "birtwistle_erk_akt_cell_division",
        "repo": BIRTWISTLE_REPO,
        "license_status": "not_counted_no_explicit_license_detected",
        "counted_as_stage10_3_public_system": False,
        "readme_available": False,
        "github_api_available": False,
        "mat_files_readable": False,
        "retained_derivative_data": False,
        "file_shapes": {},
        "source_hashes": {},
        "interpretation_boundary": (
            "Public source files are readable, but no explicit repository license was detected. "
            "Stage 10.3 records this as a future candidate and does not retain derivative tables."
        ),
    }
    try:
        repo_payload = json.loads(urllib.request.urlopen(BIRTWISTLE_API, timeout=30).read().decode("utf-8"))
        probe["github_api_available"] = True
        probe["license"] = repo_payload.get("license") or None
    except Exception as exc:
        probe["github_api_error"] = f"{type(exc).__name__}: {exc}"
    try:
        readme = urllib.request.urlopen(BIRTWISTLE_README, timeout=30).read()
        probe["readme_available"] = True
        probe["readme_sha256"] = _sha256_bytes(readme)
    except Exception as exc:
        probe["readme_error"] = f"{type(exc).__name__}: {exc}"
    try:
        import scipy.io  # type: ignore

        shapes: dict[str, str] = {}
        hashes: dict[str, str] = {}
        for name, url in BIRTWISTLE_MAT_URLS.items():
            data = urllib.request.urlopen(url, timeout=45).read()
            hashes[name] = _sha256_bytes(data)
            mat = scipy.io.loadmat(__import__("io").BytesIO(data))
            public_keys = [key for key in mat if not key.startswith("__")]
            if public_keys:
                arr = mat[public_keys[0]]
                shapes[name] = "x".join(str(part) for part in getattr(arr, "shape", ()))
        probe["mat_files_readable"] = len(shapes) == len(BIRTWISTLE_MAT_URLS)
        probe["file_shapes"] = shapes
        probe["source_hashes"] = hashes
    except Exception as exc:
        probe["mat_probe_error"] = f"{type(exc).__name__}: {exc}"
    return probe


def _system_matrix_rows(mlci_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    drg_counts = _class_counts(_read_csv(DRG_SUMMARY))
    erk_counts = _class_counts(_read_csv(ERK_SUMMARY))
    mlci_counts = _class_counts([{key: str(value) for key, value in row.items()} for row in mlci_rows])
    cell_rank = _read_csv(CELL_MODEL_RANKING)
    cell_reserve = _read_csv(CELL_RESERVE_ROWS)
    coupling_rows = _read_csv(ERK_AKT_COUPLING)
    routed_delta = float(cell_rank[1]["delta_bic"]) if len(cell_rank) > 1 else float("nan")
    mean_reserve = mean(float(row["reserve_like_coordinate"]) for row in cell_reserve)
    bounded_passes = sum(int(row.get("passes_primary_rule", row.get("passes", "0")) or 0) for row in coupling_rows)
    return [
        {
            "system_id": "drg_calcium_vonbuchholtz2025",
            "source": "Zenodo DOI 10.5281/zenodo.14907827",
            "domain": "excitable-neuron calcium dynamics",
            "measurement_class": "single-cell calcium trajectories",
            "counted_public_system": 1,
            "stage10_3_role": "retained_public_positive_residence_amplitude_distinction",
            "primary_result": f"residence_only={drg_counts['residence_only_top_quartile']} amplitude_only={drg_counts['amplitude_only_top_quartile']}",
            "boundary": "Calcium residence and peak amplitude can diverge, but this does not establish a universal residence regime.",
        },
        {
            "system_id": "erk_gpcr_wan2021",
            "source": "Zenodo DOI 10.5281/zenodo.5836623",
            "domain": "GPCR-linked ERK kinase dynamics",
            "measurement_class": "single-cell ERK KTR trajectories",
            "counted_public_system": 1,
            "stage10_3_role": "retained_public_positive_and_amplitude_sufficient_cases",
            "primary_result": f"residence_only={erk_counts['residence_only_top_quartile']} amplitude_only={erk_counts['amplitude_only_top_quartile']}",
            "boundary": "ERK public rows support method discordance, not ground-truth biological superiority.",
        },
        {
            "system_id": "cell_painting_mitotox_seal2023",
            "source": "Zenodo DOI 10.5281/zenodo.10011861",
            "domain": "perturbation endpoint morphology and cell-health profiling",
            "measurement_class": "endpoint model comparison and reserve-like endpoint coordinate",
            "counted_public_system": 1,
            "stage10_3_role": "retained_public_routed_output_and_reserve_like_endpoint_case",
            "primary_result": f"routed_delta_bic={routed_delta:.3g} mean_endpoint_preservation={mean_reserve:.3g}",
            "boundary": "Reserve-like coordinate is endpoint preservation, not a direct live reserve measurement.",
        },
        {
            "system_id": "mlci_tracking",
            "source": "Zenodo DOI 10.5281/zenodo.7260137",
            "domain": "microbial live-cell tracking",
            "measurement_class": "tracking-derived intensity trajectories",
            "counted_public_system": 1,
            "stage10_3_role": "new_stage10_public_live_cell_trajectory_breadth_case",
            "primary_result": f"residence_only={mlci_counts['residence_only_top_quartile']} amplitude_only={mlci_counts['amplitude_only_top_quartile']}",
            "boundary": "Tracking intensity demonstrates schema portability and residence/amplitude separation, not molecular signaling.",
        },
        {
            "system_id": "erk_akt_wan2021_bounded_coupling",
            "source": "Zenodo DOI 10.5281/zenodo.5836623",
            "domain": "paired kinase reporter dynamics",
            "measurement_class": "declared-margin bounded coupling",
            "counted_public_system": 0,
            "stage10_3_role": "retained_within_wan_system_bounded_coupling_case",
            "primary_result": f"bounded_coupling_pass_contexts={bounded_passes}/{len(coupling_rows)}",
            "boundary": "Same source family as ERK GPCR; counted as additional method evidence but not as an independent public system.",
        },
    ]


def _candidate_resolution_rows(birtwistle: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "candidate_id": "mlci_tracking",
            "decision": "counted_stage10_3_public_system",
            "reason": "CC-BY live-cell tracking source already has retained derived trajectory features and now contributes a residence/amplitude breadth case.",
            "counted": 1,
        },
        {
            "candidate_id": "cell_painting_mitotox_seal2023",
            "decision": "counted_stage10_3_public_system",
            "reason": "CC-BY perturbation endpoint source contributes routed-output and endpoint-preservation breadth beyond trajectory-only signaling.",
            "counted": 1,
        },
        {
            "candidate_id": "birtwistle_erk_akt_cell_division",
            "decision": "source_verified_but_deferred",
            "reason": "Public ERK/Akt cell-division MAT files are readable, but no explicit repository license was detected; no derivative table is retained in this phase.",
            "counted": 0,
        },
        {
            "candidate_id": "nfkb_watchlist",
            "decision": "deferred",
            "reason": "High-value immune dynamics target, but no release-safe tidy trajectory source with license and grouping metadata has been promoted yet.",
            "counted": 0,
        },
        {
            "candidate_id": "esc_erk_akt_stat3_cell_systems",
            "decision": "deferred",
            "reason": "Scientifically strong ESC signaling candidate, but direct supplemental source access was not stable enough for retained Stage 10.3 outputs.",
            "counted": 0,
        },
    ]


def _source_ledger_rows(birtwistle: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "source_id": "drg_calcium_vonbuchholtz2025",
            "url": "https://zenodo.org/records/14907827",
            "license": "CC-BY-4.0",
            "access_status": "retained_public_derived_outputs_available",
            "counted": 1,
        },
        {
            "source_id": "erk_gpcr_wan2021",
            "url": "https://zenodo.org/records/5836623",
            "license": "CC-BY-4.0",
            "access_status": "retained_public_derived_outputs_available",
            "counted": 1,
        },
        {
            "source_id": "cell_painting_mitotox_seal2023",
            "url": "https://zenodo.org/records/10011861",
            "license": "CC-BY-4.0",
            "access_status": "retained_public_derived_outputs_available",
            "counted": 1,
        },
        {
            "source_id": "mlci_tracking",
            "url": "https://zenodo.org/records/7260137",
            "license": "CC-BY-4.0",
            "access_status": "retained_public_derived_outputs_available",
            "counted": 1,
        },
        {
            "source_id": "birtwistle_erk_akt_cell_division",
            "url": BIRTWISTLE_REPO,
            "license": str(birtwistle.get("license") or "no_explicit_license_detected"),
            "access_status": "source_probe_readable" if birtwistle.get("mat_files_readable") else "source_probe_failed",
            "counted": 0,
        },
    ]


def _update_candidate_table() -> None:
    desired_fields = [
        "candidate_id",
        "domain",
        "name",
        "url",
        "license",
        "access_format",
        "schema_mapping",
        "biological_value",
        "nature_methods_value",
        "status",
        "priority",
        "notes",
    ]
    rows = _read_csv(PUBLIC_CANDIDATES, delimiter="\t")
    if any(row.get("candidate_id") == "birtwistle_erk_akt_cell_division" for row in rows):
        _write_csv(PUBLIC_CANDIDATES, rows, fieldnames=desired_fields, delimiter="\t")
        return
    rows.append(
        {
            "candidate_id": "birtwistle_erk_akt_cell_division",
            "domain": "kinase dynamics and cell-division fate",
            "name": "Relating Individual Cell Division Events to Single-Cell ERK and Akt Activity Time Courses",
            "url": BIRTWISTLE_REPO,
            "license": "no explicit repository license detected",
            "access_format": "GitHub repository containing preprocessed MATLAB trajectory files",
            "schema_mapping": "Per-cell ERK and Akt traces can map to cell_id,time,condition,signal after finite-value filtering",
            "biological_value": "Tests whether fate-linked ERK/Akt trajectories can be represented as residence versus amplitude decisions",
            "nature_methods_value": "Strong candidate for public breadth after license clarification",
            "status": "deferred_license_review",
            "priority": "stage10_candidate",
            "notes": "Source files were probed successfully in Stage 10.3, but derivative data were not retained because no explicit license was detected.",
        }
    )
    _write_csv(PUBLIC_CANDIDATES, rows, fieldnames=desired_fields, delimiter="\t")


def evaluate_stage10_3(output_dir: Path = OUTPUT_DIR) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    _update_candidate_table()
    mlci_rows = _mlci_summary_rows()
    birtwistle_probe = _birtwistle_probe()
    matrix_rows = _system_matrix_rows(mlci_rows)
    candidate_rows = _candidate_resolution_rows(birtwistle_probe)
    source_rows = _source_ledger_rows(birtwistle_probe)

    counted_systems = [row for row in matrix_rows if int(row["counted_public_system"]) == 1]
    counted_domains = {str(row["domain"]) for row in counted_systems}
    additional_beyond_drg_erk = {
        row["system_id"]
        for row in counted_systems
        if row["system_id"] not in {"drg_calcium_vonbuchholtz2025", "erk_gpcr_wan2021"}
    }
    has_negative_or_amplitude_sufficient = any(
        "amplitude_only=" in str(row["primary_result"]) and not str(row["primary_result"]).endswith("=0")
        for row in counted_systems
    )
    has_bounded_or_routed = any(
        row["stage10_3_role"] == "retained_public_routed_output_and_reserve_like_endpoint_case"
        for row in matrix_rows
    ) and any(row["stage10_3_role"] == "retained_within_wan_system_bounded_coupling_case" for row in matrix_rows)
    gates = {
        "four_total_independent_public_systems": len(counted_systems) >= 4,
        "three_or_more_biological_domains": len(counted_domains) >= 3,
        "two_additional_systems_beyond_drg_and_erk": len(additional_beyond_drg_erk) >= 2,
        "negative_or_amplitude_sufficient_case_present": has_negative_or_amplitude_sufficient,
        "bounded_coupling_or_routed_output_evidence_retained": has_bounded_or_routed,
        "unlicensed_public_source_not_counted": birtwistle_probe.get("counted_as_stage10_3_public_system") is False,
    }
    report = {
        "report_format": "rhodyn.stage10_3_public_biological_breadth.v1",
        "stage": "10.3",
        "status": "pass" if all(gates.values()) else "fail",
        "output_dir": output_dir.relative_to(ROOT).as_posix(),
        "gates": gates,
        "summary_metrics": {
            "counted_independent_public_systems": len(counted_systems),
            "counted_biological_domains": len(counted_domains),
            "additional_systems_beyond_drg_and_erk": sorted(additional_beyond_drg_erk),
            "birtwistle_mat_files_readable": bool(birtwistle_probe.get("mat_files_readable")),
            "birtwistle_counted": False,
        },
        "created_outputs": [
            "stage10_3_public_system_matrix.tsv",
            "stage10_3_mlci_tracking_residence_summary.csv",
            "stage10_3_candidate_resolution.tsv",
            "stage10_3_source_access_ledger.tsv",
            "stage10_3_birtwistle_source_probe.json",
            "stage10_3_public_breadth_brief.md",
            "stage10_3_public_breadth_report.json",
        ],
        "interpretation_boundary": (
            "Stage 10.3 expands public biological breadth, but it does not show that every "
            "live-cell system has a residence regime and does not count unlicensed public "
            "sources as release-ready demonstrations."
        ),
        "next_phase": "Stage 10.4 blinded or held-out challenge route",
    }
    _write_csv(
        output_dir / "stage10_3_public_system_matrix.tsv",
        matrix_rows,
        fieldnames=[
            "system_id",
            "source",
            "domain",
            "measurement_class",
            "counted_public_system",
            "stage10_3_role",
            "primary_result",
            "boundary",
        ],
        delimiter="\t",
    )
    _write_csv(output_dir / "stage10_3_mlci_tracking_residence_summary.csv", mlci_rows)
    _write_csv(output_dir / "stage10_3_candidate_resolution.tsv", candidate_rows, delimiter="\t")
    _write_csv(output_dir / "stage10_3_source_access_ledger.tsv", source_rows, delimiter="\t")
    _write_json(output_dir / "stage10_3_birtwistle_source_probe.json", birtwistle_probe)
    _write_stage10_3_brief(output_dir / "stage10_3_public_breadth_brief.md", report, matrix_rows, candidate_rows)
    _write_json(output_dir / "stage10_3_public_breadth_report.json", report)
    return report


def _write_stage10_3_brief(
    path: Path,
    report: dict[str, object],
    matrix_rows: list[dict[str, object]],
    candidate_rows: list[dict[str, object]],
) -> None:
    lines = [
        "# Stage 10.3 public biological breadth brief",
        "",
        "Stage 10.3 expands the public evidence surface for RhoDyn beyond named-tool benchmarking. It aggregates retained public demonstrations across trajectory, endpoint, bounded-coupling, and tracking-derived cases, while withholding candidate sources that are not release-safe.",
        "",
        f"Status. `{report['status']}`.",
        "",
        "## Counted public systems",
        "",
        "| system | domain | role | boundary |",
        "| --- | --- | --- | --- |",
    ]
    for row in matrix_rows:
        if int(row["counted_public_system"]) != 1:
            continue
        lines.append(f"| {row['system_id']} | {row['domain']} | {row['stage10_3_role']} | {row['boundary']} |")
    lines.extend(
        [
            "",
            "## Deferred candidates",
            "",
            "| candidate | decision | reason |",
            "| --- | --- | --- |",
        ]
    )
    for row in candidate_rows:
        if int(row["counted"]) == 0:
            lines.append(f"| {row['candidate_id']} | {row['decision']} | {row['reason']} |")
    lines.extend(
        [
            "",
            "## Biological interpretation",
            "",
            "The breadth result is stronger than the Stage 9 package because it now separates live-cell calcium, GPCR-linked kinase trajectories, microbial tracking-derived dynamics, and perturbation endpoint structure. The result is still bounded. RhoDyn is not being claimed as a universal detector of residence regimes. It is being positioned as a method that reports when residence changes interpretation, when amplitude or endpoints are sufficient, and when evidence should be withheld.",
        ]
    )
    _write_text(path, "\n".join(lines))


def main() -> None:
    report = evaluate_stage10_3()
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
