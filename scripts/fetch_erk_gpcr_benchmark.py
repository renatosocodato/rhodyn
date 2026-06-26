"""Build a derived ERK/KTR residence-versus-amplitude benchmark.

The source dataset is the public Zenodo source-data archive from Wan et al.
2021, containing single-cell ERK and Akt KTR trajectories after GPCR ligand
stimulation. This script downloads the selected Figure 3 source archive in
memory, extracts a bounded subset of ERK KTR traces, scores a declared high-ERK
residence threshold, and writes only derived benchmark/provenance outputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from math import ceil
from pathlib import Path
from statistics import mean
import sys
from urllib.request import urlopen
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhodyn.residence import ResidenceWindow, score_records
from rhodyn.schema import TrajectoryRecord


ZENODO_RECORD = "https://zenodo.org/records/5836623"
ZENODO_DOI = "10.5281/zenodo.5836623"
ARCHIVE_FILE = "Figure_3.zip"
ARCHIVE_URL = f"https://zenodo.org/api/records/5836623/files/{ARCHIVE_FILE}/content"
TRACE_MEMBERS = (
    "Figure_3/Data/ALL_UK.csv",
    "Figure_3/Data/ALL_S1P.csv",
    "Figure_3/Data/ALL_His.csv",
)


def _download_bytes(url: str) -> tuple[bytes, str]:
    with urlopen(url, timeout=90) as response:
        payload = response.read()
    return payload, hashlib.sha256(payload).hexdigest()


def _safe_id(value: str) -> str:
    return value.strip().replace(" ", "_").replace("/", "_").replace("|", "_")


def _quantile(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("quantile requires at least one value")
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("quantile fraction must be between 0 and 1")
    ordered = sorted(values)
    index = round((len(ordered) - 1) * fraction)
    return ordered[index]


def _read_member_records(
    member_bytes: bytes,
    *,
    max_cells_per_ligand: int,
) -> tuple[list[TrajectoryRecord], dict[str, dict[str, str]], str]:
    reader = csv.DictReader(io.StringIO(member_bytes.decode("utf-8", errors="replace")))
    selected: set[str] = set()
    records: list[TrajectoryRecord] = []
    metadata: dict[str, dict[str, str]] = {}
    member_sha = hashlib.sha256(member_bytes).hexdigest()
    for row in reader:
        if (row.get("Inhibitor") or "").strip() != "DMSO":
            continue
        ligand = (row.get("Ligand") or "").strip()
        experiment = (row.get("Experiment") or "").strip()
        source_object = (row.get("Unique_Unique_Object") or "").strip()
        if not ligand or not experiment or not source_object:
            continue
        source_key = "|".join([ligand, experiment, source_object])
        if source_key not in selected:
            if len(selected) >= max_cells_per_ligand:
                continue
            selected.add(source_key)
        if source_key not in selected:
            continue
        concentration = (row.get("Condition") or "").strip()
        inhibitor = (row.get("Inhibitor") or "").strip()
        cell_id = f"erk_ktr_{_safe_id(ligand)}_{_safe_id(experiment)}_{_safe_id(source_object)}"
        condition = f"erk_ktr_{_safe_id(ligand)}_{_safe_id(inhibitor)}_{_safe_id(concentration)}"
        records.append(
            TrajectoryRecord(
                cell_id=cell_id,
                time=float(row["Time_in_min"]),
                condition=condition,
                signal=float(row["CN_ERK"]),
                replicate=experiment,
            )
        )
        metadata[cell_id] = {
            "ligand": ligand,
            "concentration": concentration,
            "inhibitor": inhibitor,
            "experiment": experiment,
            "date": (row.get("Date") or "").strip(),
            "slide": (row.get("Slide") or "").strip(),
            "position": (row.get("Position") or "").strip(),
            "source_object": source_object,
        }
    return records, metadata, member_sha


def _archive_to_records(
    archive_bytes: bytes,
    *,
    max_cells_per_ligand: int,
) -> tuple[list[TrajectoryRecord], dict[str, dict[str, str]], dict[str, str]]:
    records: list[TrajectoryRecord] = []
    metadata: dict[str, dict[str, str]] = {}
    member_hashes: dict[str, str] = {}
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        for member in TRACE_MEMBERS:
            member_bytes = archive.read(member)
            member_records, member_metadata, member_sha = _read_member_records(
                member_bytes,
                max_cells_per_ligand=max_cells_per_ligand,
            )
            records.extend(member_records)
            metadata.update(member_metadata)
            member_hashes[member] = member_sha
    return records, metadata, member_hashes


def _rank_by_value(rows: list[dict[str, object]], field: str) -> dict[tuple[str, str], int]:
    ranked = sorted(
        rows,
        key=lambda row: (-float(row[field]), str(row["condition"]), str(row["cell_id"])),
    )
    return {
        (str(row["condition"]), str(row["cell_id"])): rank
        for rank, row in enumerate(ranked, start=1)
    }


def _benchmark_rows(
    records: list[TrajectoryRecord],
    *,
    window: ResidenceWindow,
    metadata: dict[str, dict[str, str]],
) -> tuple[list[dict[str, object]], dict[str, int]]:
    summaries = score_records(records, window)
    rows: list[dict[str, object]] = []
    for summary in summaries:
        trace = [
            record
            for record in records
            if record.cell_id == summary.cell_id and record.condition == summary.condition
        ]
        if not trace:
            continue
        meta = metadata.get(summary.cell_id, {})
        values = [record.signal for record in trace]
        times = [record.time for record in trace]
        rows.append(
            {
                "dataset": "erk_gpcr_ktr_wan2021",
                "condition": summary.condition,
                "cell_id": summary.cell_id,
                "replicate": trace[0].replicate,
                "ligand": meta.get("ligand", ""),
                "concentration": meta.get("concentration", ""),
                "inhibitor": meta.get("inhibitor", ""),
                "experiment": meta.get("experiment", ""),
                "date": meta.get("date", ""),
                "slide": meta.get("slide", ""),
                "position": meta.get("position", ""),
                "source_object": meta.get("source_object", ""),
                "n_points": summary.n_points,
                "time_start_min": min(times),
                "time_end_min": max(times),
                "mean_signal": mean(values),
                "max_signal": summary.max_signal,
                "min_signal": summary.min_signal,
                "residence_fraction": summary.residence_fraction,
                "residence_time_min": summary.residence_time,
                "total_time_min": summary.total_time,
                "high_erk_threshold": window.low,
            }
        )

    amplitude_ranks = _rank_by_value(rows, "max_signal")
    residence_ranks = _rank_by_value(rows, "residence_fraction")
    top_n = ceil(len(rows) * 0.25)
    class_counts = {
        "amplitude_and_residence_top_quartile": 0,
        "amplitude_only_top_quartile": 0,
        "residence_only_top_quartile": 0,
        "neither_top_quartile": 0,
    }
    for row in rows:
        key = (str(row["condition"]), str(row["cell_id"]))
        amplitude_rank = amplitude_ranks[key]
        residence_rank = residence_ranks[key]
        amplitude_top = amplitude_rank <= top_n
        residence_top = residence_rank <= top_n
        if amplitude_top and residence_top:
            category = "amplitude_and_residence_top_quartile"
        elif amplitude_top:
            category = "amplitude_only_top_quartile"
        elif residence_top:
            category = "residence_only_top_quartile"
        else:
            category = "neither_top_quartile"
        class_counts[category] += 1
        row["amplitude_rank"] = amplitude_rank
        row["residence_rank"] = residence_rank
        row["residence_minus_amplitude_rank"] = residence_rank - amplitude_rank
        row["amplitude_top_quartile"] = int(amplitude_top)
        row["residence_top_quartile"] = int(residence_top)
        row["amplitude_residence_class"] = category
    return sorted(rows, key=lambda row: (str(row["condition"]), int(row["amplitude_rank"]))), class_counts


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "dataset",
        "condition",
        "cell_id",
        "replicate",
        "ligand",
        "concentration",
        "inhibitor",
        "experiment",
        "date",
        "slide",
        "position",
        "source_object",
        "n_points",
        "time_start_min",
        "time_end_min",
        "mean_signal",
        "max_signal",
        "min_signal",
        "residence_fraction",
        "residence_time_min",
        "total_time_min",
        "high_erk_threshold",
        "amplitude_rank",
        "residence_rank",
        "residence_minus_amplitude_rank",
        "amplitude_top_quartile",
        "residence_top_quartile",
        "amplitude_residence_class",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            formatted = dict(row)
            for key in [
                "time_start_min",
                "time_end_min",
                "mean_signal",
                "max_signal",
                "min_signal",
                "residence_fraction",
                "residence_time_min",
                "total_time_min",
                "high_erk_threshold",
            ]:
                formatted[key] = f"{float(formatted[key]):.6g}"
            writer.writerow(formatted)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-cells-per-ligand", type=int, default=60)
    parser.add_argument("--threshold-quantile", type=float, default=0.75)
    parser.add_argument("--output", default="case_studies/erk_gpcr_residence_amplitude_benchmark.csv")
    parser.add_argument(
        "--provenance",
        default="case_studies/erk_gpcr_residence_amplitude_benchmark.provenance.json",
    )
    args = parser.parse_args()

    if args.max_cells_per_ligand <= 0:
        raise ValueError("max-cells-per-ligand must be positive")
    if not 0.0 < args.threshold_quantile < 1.0:
        raise ValueError("threshold-quantile must be between 0 and 1")

    archive_bytes, archive_sha = _download_bytes(ARCHIVE_URL)
    records, metadata, member_hashes = _archive_to_records(
        archive_bytes,
        max_cells_per_ligand=args.max_cells_per_ligand,
    )
    if not records:
        raise ValueError("No ERK/KTR records were extracted from the source archive")

    threshold = _quantile([record.signal for record in records], args.threshold_quantile)
    window = ResidenceWindow(low=threshold, high=1.0e12)
    benchmark, class_counts = _benchmark_rows(records, window=window, metadata=metadata)

    output = Path(args.output)
    _write_csv(output, benchmark)
    provenance = {
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
        "zenodo_record": ZENODO_RECORD,
        "zenodo_doi": ZENODO_DOI,
        "license": "CC-BY-4.0",
        "archive_file": ARCHIVE_FILE,
        "archive_url": ARCHIVE_URL,
        "archive_sha256": archive_sha,
        "source_members": list(TRACE_MEMBERS),
        "source_member_sha256": member_hashes,
        "selected_cell_count": len({record.cell_id for record in records}),
        "selected_ligands": sorted({metadata[cell_id]["ligand"] for cell_id in metadata}),
        "max_cells_per_ligand": args.max_cells_per_ligand,
        "threshold_rule": "high ERK KTR residence threshold is the selected-record CN_ERK quantile",
        "threshold_quantile": args.threshold_quantile,
        "residence_window": {"low": threshold, "high": 1.0e12},
        "benchmark_rows": len(benchmark),
        "class_counts": class_counts,
        "derived_output": str(output),
        "derived_output_sha256": _sha256(output),
        "raw_file_policy": "The Figure 3 source archive and member CSV files were downloaded into memory and converted to derived benchmark rows only; source ZIP and CSV files are not retained in the repository.",
        "interpretation_boundary": "The retained table benchmarks amplitude and high-ERK residence summaries for a public ERK/KTR live-cell signaling dataset. The quantile threshold is analytical, not a calibrated biological activation boundary, and the table does not infer GPCR mechanism.",
    }
    provenance_path = Path(args.provenance)
    provenance_path.parent.mkdir(parents=True, exist_ok=True)
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "pass",
                "benchmark_rows": len(benchmark),
                "selected_cell_count": provenance["selected_cell_count"],
                "class_counts": class_counts,
                "threshold": threshold,
                "output": str(output),
                "provenance": str(provenance_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
