"""Build a derived DRG calcium residence-versus-amplitude benchmark.

The source dataset is a public Zenodo calcium-imaging table from von Buchholtz
2025. The script downloads the selected trace and metadata CSV files in memory,
maps a bounded cell subset into RhoDyn trajectory records, scores a declared
high-calcium residence window, and writes only derived benchmark/provenance
outputs.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhodyn.residence import ResidenceWindow, score_records
from rhodyn.schema import TrajectoryRecord


ZENODO_RECORD = "https://zenodo.org/records/14907827"
ZENODO_DOI = "10.5281/zenodo.14907827"
TRACE_FILE = "sstlineage_ly_drg_traces.csv"
INFO_FILE = "sstlineage_ly_drg_info.csv"
TRACE_URL = f"https://zenodo.org/api/records/14907827/files/{TRACE_FILE}/content"
INFO_URL = f"https://zenodo.org/api/records/14907827/files/{INFO_FILE}/content"


def _download_text(url: str) -> tuple[str, str]:
    with urlopen(url, timeout=60) as response:
        payload = response.read()
    return payload.decode("utf-8"), hashlib.sha256(payload).hexdigest()


def _read_info_table(text: str) -> dict[str, dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text))
    rows: dict[str, dict[str, str]] = {}
    for row in reader:
        cell_id = (row.get("") or "").strip()
        if cell_id:
            rows[cell_id] = {key: (value or "").strip() for key, value in row.items()}
    return rows


def _wide_trace_rows_to_records(
    text: str,
    *,
    info_rows: dict[str, dict[str, str]],
    max_cells: int,
    episode_length_frames: int,
    frame_interval_seconds: float,
) -> tuple[list[TrajectoryRecord], int, int]:
    reader = csv.DictReader(io.StringIO(text))
    records: list[TrajectoryRecord] = []
    cell_count = 0
    episode_count = 0
    for row in reader:
        if cell_count >= max_cells:
            break
        source_cell_id = (row.get("") or "").strip()
        if not source_cell_id:
            continue
        frame_columns = [field for field in (reader.fieldnames or []) if field and field.isdigit()]
        frame_count = len(frame_columns)
        if frame_count < episode_length_frames:
            continue
        episodes = frame_count // episode_length_frames
        metadata = info_rows.get(source_cell_id, {})
        replicate = metadata.get("mouse") or metadata.get("ganglion") or "unknown_mouse"
        cell_count += 1
        for episode_index in range(episodes):
            episode_count = max(episode_count, episode_index + 1)
            condition = f"drg_calcium_episode_{episode_index + 1}"
            for frame in range(episode_index * episode_length_frames, (episode_index + 1) * episode_length_frames):
                value = row.get(str(frame))
                if value is None or value == "":
                    continue
                records.append(
                    TrajectoryRecord(
                        cell_id=source_cell_id,
                        time=(frame - episode_index * episode_length_frames) * frame_interval_seconds,
                        condition=condition,
                        signal=float(value),
                        replicate=replicate,
                    )
                )
    return records, cell_count, episode_count


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
    info_rows: dict[str, dict[str, str]],
) -> tuple[list[dict[str, object]], dict[str, int]]:
    summaries = score_records(records, window)
    rows: list[dict[str, object]] = []
    for summary in summaries:
        trace = [record for record in records if record.cell_id == summary.cell_id and record.condition == summary.condition]
        metadata = info_rows.get(summary.cell_id, {})
        values = [record.signal for record in trace]
        rows.append(
            {
                "dataset": "drg_calcium_sstlineage_ly",
                "condition": summary.condition,
                "cell_id": summary.cell_id,
                "replicate": trace[0].replicate if trace else "",
                "mouse": metadata.get("mouse", ""),
                "ganglion": metadata.get("ganglion", ""),
                "roi": metadata.get("roi", ""),
                "n_points": summary.n_points,
                "mean_signal": mean(values),
                "max_signal": summary.max_signal,
                "min_signal": summary.min_signal,
                "residence_fraction": summary.residence_fraction,
                "residence_time_seconds": summary.residence_time,
                "total_time_seconds": summary.total_time,
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
        "mouse",
        "ganglion",
        "roi",
        "n_points",
        "mean_signal",
        "max_signal",
        "min_signal",
        "residence_fraction",
        "residence_time_seconds",
        "total_time_seconds",
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
                "mean_signal",
                "max_signal",
                "min_signal",
                "residence_fraction",
                "residence_time_seconds",
                "total_time_seconds",
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
    parser.add_argument("--max-cells", type=int, default=120)
    parser.add_argument("--episode-length-frames", type=int, default=200)
    parser.add_argument("--frame-interval-seconds", type=float, default=0.2)
    parser.add_argument("--residence-low", type=float, default=10.0)
    parser.add_argument("--residence-high", type=float, default=1.0e12)
    parser.add_argument("--output", default="case_studies/drg_calcium_residence_amplitude_benchmark.csv")
    parser.add_argument("--provenance", default="case_studies/drg_calcium_residence_amplitude_benchmark.provenance.json")
    args = parser.parse_args()

    if args.max_cells <= 0:
        raise ValueError("max-cells must be positive")
    if args.episode_length_frames <= 0:
        raise ValueError("episode-length-frames must be positive")
    if args.frame_interval_seconds <= 0:
        raise ValueError("frame-interval-seconds must be positive")
    if args.residence_high < args.residence_low:
        raise ValueError("residence-high must be greater than or equal to residence-low")

    trace_text, trace_sha = _download_text(TRACE_URL)
    info_text, info_sha = _download_text(INFO_URL)
    info_rows = _read_info_table(info_text)
    records, cell_count, episode_count = _wide_trace_rows_to_records(
        trace_text,
        info_rows=info_rows,
        max_cells=args.max_cells,
        episode_length_frames=args.episode_length_frames,
        frame_interval_seconds=args.frame_interval_seconds,
    )
    window = ResidenceWindow(low=args.residence_low, high=args.residence_high)
    benchmark, class_counts = _benchmark_rows(records, window=window, info_rows=info_rows)

    output = Path(args.output)
    _write_csv(output, benchmark)
    provenance = {
        "source_title": "A distributed coding logic for thermosensation and inflammatory pain",
        "source_creators": ["von Buchholtz, Lars Johann"],
        "zenodo_record": ZENODO_RECORD,
        "zenodo_doi": ZENODO_DOI,
        "license": "CC-BY-4.0",
        "trace_file": TRACE_FILE,
        "trace_url": TRACE_URL,
        "trace_sha256": trace_sha,
        "info_file": INFO_FILE,
        "info_url": INFO_URL,
        "info_sha256": info_sha,
        "selected_cell_count": cell_count,
        "episode_count": episode_count,
        "episode_length_frames": args.episode_length_frames,
        "frame_interval_seconds": args.frame_interval_seconds,
        "residence_window": {"low": args.residence_low, "high": args.residence_high},
        "benchmark_rows": len(benchmark),
        "class_counts": class_counts,
        "derived_output": str(output),
        "derived_output_sha256": _sha256(output),
        "raw_file_policy": "Source trace and metadata CSV files were downloaded into memory and converted to derived benchmark rows only; source CSV files are not retained in the repository.",
        "interpretation_boundary": "The retained table benchmarks amplitude and high-calcium residence summaries for a public calcium-imaging trace dataset. It does not assign stimulus identity or claim a calibrated biological calcium threshold.",
    }
    provenance_path = Path(args.provenance)
    provenance_path.parent.mkdir(parents=True, exist_ok=True)
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "pass",
                "benchmark_rows": len(benchmark),
                "selected_cell_count": cell_count,
                "class_counts": class_counts,
                "output": str(output),
                "provenance": str(provenance_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
