"""Build a public ERK/Akt bounded-coupling benchmark.

The source dataset is the public Zenodo source-data archive from Wan et al.
2021, containing paired ERK and Akt KTR trajectories after GPCR ligand
stimulation. The script downloads the selected Figure 3 source archive in
memory, extracts a bounded DMSO-control subset, summarizes high-state residence
for ERK and Akt in the same cells, and runs one-sample TOST on the paired
ERK-minus-Akt residence contrast.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import defaultdict
from pathlib import Path
import sys
from urllib.request import urlopen
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhodyn.coupling import one_sample_tost


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
    ordered = sorted(values)
    index = round((len(ordered) - 1) * fraction)
    return ordered[index]


def _read_member_rows(member_bytes: bytes, *, max_cells_per_ligand: int) -> tuple[list[dict[str, object]], str]:
    reader = csv.DictReader(io.StringIO(member_bytes.decode("utf-8", errors="replace")))
    selected: set[str] = set()
    rows: list[dict[str, object]] = []
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
        cell_id = f"erk_akt_{_safe_id(ligand)}_{_safe_id(experiment)}_{_safe_id(source_object)}"
        rows.append(
            {
                "cell_id": cell_id,
                "ligand": ligand,
                "concentration": concentration,
                "experiment": experiment,
                "time_min": float(row["Time_in_min"]),
                "erk": float(row["CN_ERK"]),
                "akt": float(row["CN_AktRB"]),
            }
        )
    return rows, member_sha


def _archive_to_rows(
    archive_bytes: bytes,
    *,
    max_cells_per_ligand: int,
) -> tuple[list[dict[str, object]], dict[str, str]]:
    rows: list[dict[str, object]] = []
    member_hashes: dict[str, str] = {}
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        for member in TRACE_MEMBERS:
            member_rows, member_sha = _read_member_rows(
                archive.read(member),
                max_cells_per_ligand=max_cells_per_ligand,
            )
            rows.extend(member_rows)
            member_hashes[member] = member_sha
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
        dt
        for dt, row in zip(intervals, ordered[:-1])
        if float(row[field]) >= threshold
    )
    return residence_time / total_time, residence_time


def _summary_rows(
    source_rows: list[dict[str, object]],
    *,
    threshold_quantile: float,
) -> tuple[list[dict[str, object]], dict[str, float]]:
    thresholds = {
        "erk": _quantile([float(row["erk"]) for row in source_rows], threshold_quantile),
        "akt": _quantile([float(row["akt"]) for row in source_rows], threshold_quantile),
    }
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in source_rows:
        grouped[str(row["cell_id"])].append(row)

    summaries: list[dict[str, object]] = []
    for cell_id, rows in grouped.items():
        ordered = sorted(rows, key=lambda row: float(row["time_min"]))
        erk_fraction, erk_time = _residence_fraction(ordered, field="erk", threshold=thresholds["erk"])
        akt_fraction, akt_time = _residence_fraction(ordered, field="akt", threshold=thresholds["akt"])
        total_time = float(ordered[-1]["time_min"]) - float(ordered[0]["time_min"])
        summaries.append(
            {
                "dataset": "erk_gpcr_ktr_wan2021",
                "cell_id": cell_id,
                "ligand": ordered[0]["ligand"],
                "concentration": ordered[0]["concentration"],
                "replicate": ordered[0]["experiment"],
                "n_points": len(ordered),
                "time_start_min": ordered[0]["time_min"],
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
    return sorted(summaries, key=lambda row: (str(row["ligand"]), str(row["cell_id"]))), thresholds


def _coupling_rows(
    summaries: list[dict[str, object]],
    *,
    margin: float,
    alpha: float,
) -> list[dict[str, object]]:
    contrasts = ["all"] + sorted({str(row["ligand"]) for row in summaries})
    rows: list[dict[str, object]] = []
    for contrast in contrasts:
        selected = summaries if contrast == "all" else [row for row in summaries if row["ligand"] == contrast]
        values = [float(row["erk_minus_akt_residence_fraction"]) for row in selected]
        decision = one_sample_tost(values, margin=margin, alpha=alpha, prefer_scipy=False)
        rows.append(
            {
                "contrast": f"erk_minus_akt_residence_{contrast}",
                "estimate": decision.estimate,
                "ci_low": decision.ci_low,
                "ci_high": decision.ci_high,
                "margin": decision.margin,
                "rope_mass": "",
                "n": decision.n,
                "se": decision.se,
                "p_tost": decision.p_tost,
                "interval_inside_margin": int(decision.interval_inside_margin),
                "passes": int(decision.passes),
                "method": decision.method,
                "ligand": contrast,
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            formatted = dict(row)
            for key, value in list(formatted.items()):
                if isinstance(value, float):
                    formatted[key] = f"{value:.8g}"
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
    parser.add_argument("--margin", type=float, default=0.20)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument(
        "--summary-output",
        default="case_studies/erk_gpcr_erk_akt_residence_summary.csv",
    )
    parser.add_argument(
        "--coupling-output",
        default="case_studies/erk_gpcr_erk_akt_bounded_coupling.csv",
    )
    parser.add_argument(
        "--provenance",
        default="case_studies/erk_gpcr_erk_akt_bounded_coupling.provenance.json",
    )
    args = parser.parse_args()

    if args.max_cells_per_ligand <= 0:
        raise ValueError("max-cells-per-ligand must be positive")
    if not 0.0 < args.threshold_quantile < 1.0:
        raise ValueError("threshold-quantile must be between 0 and 1")
    if args.margin <= 0:
        raise ValueError("margin must be positive")

    archive_bytes, archive_sha = _download_bytes(ARCHIVE_URL)
    source_rows, member_hashes = _archive_to_rows(
        archive_bytes,
        max_cells_per_ligand=args.max_cells_per_ligand,
    )
    summaries, thresholds = _summary_rows(source_rows, threshold_quantile=args.threshold_quantile)
    coupling = _coupling_rows(summaries, margin=args.margin, alpha=args.alpha)

    summary_output = Path(args.summary_output)
    coupling_output = Path(args.coupling_output)
    _write_csv(
        summary_output,
        summaries,
        [
            "dataset",
            "cell_id",
            "ligand",
            "concentration",
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
        coupling_output,
        coupling,
        [
            "contrast",
            "estimate",
            "ci_low",
            "ci_high",
            "margin",
            "rope_mass",
            "n",
            "se",
            "p_tost",
            "interval_inside_margin",
            "passes",
            "method",
            "ligand",
        ],
    )

    passed = [row["contrast"] for row in coupling if int(row["passes"]) == 1]
    failed = [row["contrast"] for row in coupling if int(row["passes"]) == 0]
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
        "selected_cell_count": len(summaries),
        "selected_ligands": sorted({str(row["ligand"]) for row in summaries}),
        "max_cells_per_ligand": args.max_cells_per_ligand,
        "threshold_rule": "ERK and Akt residence thresholds are separate selected-record 75th-percentile KTR values by default",
        "threshold_quantile": args.threshold_quantile,
        "residence_thresholds": thresholds,
        "margin": args.margin,
        "alpha": args.alpha,
        "passed_contrasts": passed,
        "failed_contrasts": failed,
        "derived_outputs": {
            str(summary_output): _sha256(summary_output),
            str(coupling_output): _sha256(coupling_output),
        },
        "raw_file_policy": "The Figure 3 source archive and member CSV files were downloaded into memory and converted to derived benchmark rows only; source ZIP and CSV files are not retained in the repository.",
        "interpretation_boundary": "This benchmark tests whether paired ERK-minus-Akt high-state residence differences fall inside a declared +/-0.20 residence-fraction margin. Passing contrasts support context-limited bounded coupling of derived residence summaries, not biochemical equivalence and not absence of all GPCR pathway crosstalk.",
    }
    provenance_path = Path(args.provenance)
    provenance_path.parent.mkdir(parents=True, exist_ok=True)
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "pass",
                "summary_rows": len(summaries),
                "coupling_rows": len(coupling),
                "passed_contrasts": passed,
                "failed_contrasts": failed,
                "summary_output": str(summary_output),
                "coupling_output": str(coupling_output),
                "provenance": str(provenance_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
