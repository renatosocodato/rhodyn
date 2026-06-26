"""Build a public Cell Painting endpoint model-comparison benchmark.

The source dataset is the public Zenodo record from Seal et al. 2023, which
pairs scaled Cell Painting morphology profiles with nine MitoTox biological
activity endpoints for the same 658 compounds. The script downloads source CSV
files in memory, builds leave-one-compound-out endpoint predictions from
reduced morphology architectures, and writes only derived benchmark/provenance
outputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from math import dist, isfinite, log
from pathlib import Path
import sys
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhodyn.compare import fit_model_rows
from rhodyn.schema import EndpointRecord


ZENODO_RECORD = "https://zenodo.org/records/10011861"
ZENODO_DOI = "10.5281/zenodo.10011861"
ENDPOINT_FILE = "Endpoints_9_Mitotox_biological_activities_658_compounds.csv"
FEATURE_FILE = "Cell_Painting_data_658_compounds_827_Features_scaled.csv"
ENDPOINT_URL = f"https://zenodo.org/api/records/10011861/files/{ENDPOINT_FILE}/content"
FEATURE_URL = f"https://zenodo.org/api/records/10011861/files/{FEATURE_FILE}/content"
K_NEIGHBORS = 5


def _download_text(url: str) -> tuple[str, str]:
    with urlopen(url, timeout=90) as response:
        payload = response.read()
    return payload.decode("utf-8"), hashlib.sha256(payload).hexdigest()


def _read_tables(endpoint_text: str, feature_text: str) -> tuple[list[str], list[str], list[list[int]], list[str], list[list[float]]]:
    endpoint_rows = list(csv.DictReader(io.StringIO(endpoint_text)))
    feature_rows = list(csv.DictReader(io.StringIO(feature_text)))
    if not endpoint_rows or not feature_rows:
        raise ValueError("source endpoint and feature tables must both contain rows")

    endpoints = [field for field in endpoint_rows[0] if field != "InChICode_standardised"]
    feature_fields = [field for field in feature_rows[0] if field != "InChICode_standardised"]
    feature_by_id = {row["InChICode_standardised"]: row for row in feature_rows}
    endpoint_by_id = {row["InChICode_standardised"]: row for row in endpoint_rows}
    compound_ids = [row["InChICode_standardised"] for row in endpoint_rows if row["InChICode_standardised"] in feature_by_id]
    if len(compound_ids) < 2:
        raise ValueError("at least two matched compounds are required for leave-one-out comparison")

    endpoint_matrix = [[int(endpoint_by_id[compound_id][endpoint]) for endpoint in endpoints] for compound_id in compound_ids]
    feature_matrix = [
        [float(feature_by_id[compound_id][field]) for field in feature_fields]
        for compound_id in compound_ids
    ]
    return compound_ids, endpoints, endpoint_matrix, feature_fields, feature_matrix


def _feature_groups(feature_fields: list[str]) -> dict[str, list[int]]:
    groups: dict[str, list[int]] = {}
    for index, field in enumerate(feature_fields):
        prefix = field.split("_", 1)[0]
        groups.setdefault(prefix, []).append(index)
    for required in ("Cells", "Cytoplasm", "Nuclei"):
        if required not in groups:
            raise ValueError(f"missing expected Cell Painting feature group: {required}")
    return groups


def _norm(values: list[float]) -> float:
    return (sum(value * value for value in values) / len(values)) ** 0.5


def _architecture_spaces(feature_fields: list[str], feature_matrix: list[list[float]]) -> dict[str, list[tuple[float, ...]]]:
    groups = _feature_groups(feature_fields)
    spaces: dict[str, list[tuple[float, ...]]] = {
        "endpoint_prevalence": [tuple() for _ in feature_matrix],
        "morphology_magnitude_5nn": [],
        "cells_block_5nn": [],
        "cytoplasm_block_5nn": [],
        "nuclei_block_5nn": [],
        "compartment_route_5nn": [],
    }
    for row in feature_matrix:
        spaces["morphology_magnitude_5nn"].append((_norm(row),))
        for group_name, model_name in [
            ("Cells", "cells_block_5nn"),
            ("Cytoplasm", "cytoplasm_block_5nn"),
            ("Nuclei", "nuclei_block_5nn"),
        ]:
            spaces[model_name].append(tuple(row[index] for index in groups[group_name]))
        spaces["compartment_route_5nn"].append(
            tuple(_norm([row[index] for index in groups[group_name]]) for group_name in ("Cells", "Cytoplasm", "Nuclei"))
        )
    return spaces


def _nearest_neighbors(vectors: list[tuple[float, ...]], *, k: int) -> list[list[int]]:
    if len(vectors) <= k:
        raise ValueError("number of vectors must be greater than k")
    neighbors: list[list[int]] = []
    for i, vector in enumerate(vectors):
        distances: list[tuple[float, int]] = []
        for j, other in enumerate(vectors):
            if i == j:
                continue
            if len(vector) == 1:
                distance = abs(vector[0] - other[0])
            else:
                distance = dist(vector, other)
            distances.append((distance, j))
        distances.sort(key=lambda item: (item[0], item[1]))
        neighbors.append([index for _, index in distances[:k]])
    return neighbors


def _endpoint_weights(endpoint_matrix: list[list[int]], endpoints: list[str]) -> dict[str, tuple[float, float]]:
    weights: dict[str, tuple[float, float]] = {}
    for endpoint_index, endpoint in enumerate(endpoints):
        positive_count = sum(row[endpoint_index] for row in endpoint_matrix)
        negative_count = len(endpoint_matrix) - positive_count
        positive_weight = 0.5 / positive_count if positive_count else 0.0
        negative_weight = 0.5 / negative_count if negative_count else 0.0
        weights[endpoint] = (positive_weight, negative_weight)
    return weights


def _prediction_rows(
    compound_ids: list[str],
    endpoints: list[str],
    endpoint_matrix: list[list[int]],
    feature_fields: list[str],
    feature_matrix: list[list[float]],
    *,
    k_neighbors: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    spaces = _architecture_spaces(feature_fields, feature_matrix)
    neighbor_indexes = {
        model: _nearest_neighbors(vectors, k=k_neighbors)
        for model, vectors in spaces.items()
        if model != "endpoint_prevalence"
    }
    endpoint_sums = [sum(row[index] for row in endpoint_matrix) for index in range(len(endpoints))]
    weights = _endpoint_weights(endpoint_matrix, endpoints)
    prediction_rows: list[dict[str, object]] = []
    endpoint_stats: dict[str, dict[str, dict[str, float]]] = {}
    model_positive_probability: dict[str, float] = {model: 0.0 for model in spaces}
    positive_total = 0

    for compound_index, compound_id in enumerate(compound_ids):
        observed_row = endpoint_matrix[compound_index]
        for endpoint_index, endpoint in enumerate(endpoints):
            observed = observed_row[endpoint_index]
            endpoint_stats.setdefault(endpoint, {})
            predictions: dict[str, float] = {
                "endpoint_prevalence": (endpoint_sums[endpoint_index] - observed) / (len(compound_ids) - 1)
            }
            for model, neighbors in neighbor_indexes.items():
                predictions[model] = sum(endpoint_matrix[index][endpoint_index] for index in neighbors[compound_index]) / k_neighbors
            weight = weights[endpoint][0 if observed else 1]
            if observed:
                positive_total += 1
            for model, predicted in predictions.items():
                error = observed - predicted
                stats = endpoint_stats[endpoint].setdefault(
                    model,
                    {"rss": 0.0, "weighted_n": 0.0, "positive_probability_sum": 0.0, "positive_n": 0.0},
                )
                stats["rss"] += weight * error * error
                stats["weighted_n"] += weight
                if observed:
                    stats["positive_probability_sum"] += predicted
                    stats["positive_n"] += 1.0
                    model_positive_probability[model] += predicted
                prediction_rows.append(
                    {
                        "model": model,
                        "endpoint": endpoint,
                        "observed": observed,
                        "predicted": predicted,
                        "weight": weight,
                        "compound_index": compound_index,
                        "compound_id_sha12": hashlib.sha256(compound_id.encode("utf-8")).hexdigest()[:12],
                    }
                )

    ranking_rows: list[dict[str, object]] = []
    parameter_counts = {
        "endpoint_prevalence": len(endpoints),
        "morphology_magnitude_5nn": 1,
        "cells_block_5nn": sum(1 for field in feature_fields if field.startswith("Cells_")),
        "cytoplasm_block_5nn": sum(1 for field in feature_fields if field.startswith("Cytoplasm_")),
        "nuclei_block_5nn": sum(1 for field in feature_fields if field.startswith("Nuclei_")),
        "compartment_route_5nn": 3,
    }
    for model in spaces:
        rows = [
            EndpointRecord(
                model=model,
                endpoint=str(row["endpoint"]),
                observed=float(row["observed"]),
                predicted=float(row["predicted"]),
                weight=float(row["weight"]),
            )
            for row in prediction_rows
            if row["model"] == model
        ]
        fit = fit_model_rows(rows, parameter_count=parameter_counts[model])
        weighted_n = sum(float(row["weight"]) for row in prediction_rows if row["model"] == model)
        weighted_rmse = (fit.rss / weighted_n) ** 0.5
        positive_probability = model_positive_probability[model] / positive_total if positive_total else 0.0
        ranking_rows.append(
            {
                "model": model,
                "n_endpoint_rows": fit.n,
                "weighted_n": weighted_n,
                "rss": fit.rss,
                "weighted_rmse": weighted_rmse,
                "aic": fit.aic,
                "bic": fit.bic,
                "parameter_count": parameter_counts[model],
                "mean_predicted_probability_on_active_endpoints": positive_probability,
            }
        )
    ranking_rows.sort(key=lambda row: (float(row["bic"]), float(row["rss"])))
    best_bic = float(ranking_rows[0]["bic"])
    for rank, row in enumerate(ranking_rows, start=1):
        row["rank"] = rank
        row["delta_bic"] = float(row["bic"]) - best_bic

    endpoint_summary_rows: list[dict[str, object]] = []
    for endpoint, model_stats in endpoint_stats.items():
        for model, stats in model_stats.items():
            positive_probability = (
                stats["positive_probability_sum"] / stats["positive_n"]
                if stats["positive_n"]
                else 0.0
            )
            endpoint_summary_rows.append(
                {
                    "endpoint": endpoint,
                    "model": model,
                    "weighted_n": stats["weighted_n"],
                    "rss": stats["rss"],
                    "weighted_rmse": (stats["rss"] / stats["weighted_n"]) ** 0.5,
                    "mean_predicted_probability_on_active_endpoints": positive_probability,
                }
            )
    endpoint_summary_rows.sort(key=lambda row: (str(row["endpoint"]), float(row["weighted_rmse"]), str(row["model"])))

    diagnostics = {
        "compound_count": len(compound_ids),
        "endpoint_count": len(endpoints),
        "feature_count": len(feature_fields),
        "k_neighbors": k_neighbors,
        "endpoint_positive_counts": {
            endpoint: endpoint_sums[index] for index, endpoint in enumerate(endpoints)
        },
        "best_model_by_bic": ranking_rows[0]["model"],
        "best_model_by_weighted_rmse": min(ranking_rows, key=lambda row: float(row["weighted_rmse"]))["model"],
    }
    return prediction_rows, ranking_rows, {"endpoint_summary": endpoint_summary_rows, "diagnostics": diagnostics}


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            formatted = dict(row)
            for key, value in list(formatted.items()):
                if isinstance(value, float):
                    formatted[key] = f"{value:.8g}" if isfinite(value) else str(value)
            writer.writerow(formatted)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k-neighbors", type=int, default=K_NEIGHBORS)
    parser.add_argument(
        "--endpoint-rows-output",
        default="case_studies/cell_painting_mitotox_endpoint_model_rows.csv",
    )
    parser.add_argument(
        "--ranking-output",
        default="case_studies/cell_painting_mitotox_model_ranking.csv",
    )
    parser.add_argument(
        "--endpoint-summary-output",
        default="case_studies/cell_painting_mitotox_endpoint_summary.csv",
    )
    parser.add_argument(
        "--provenance",
        default="case_studies/cell_painting_mitotox_model_comparison.provenance.json",
    )
    args = parser.parse_args()
    if args.k_neighbors <= 0:
        raise ValueError("k-neighbors must be positive")

    endpoint_text, endpoint_sha = _download_text(ENDPOINT_URL)
    feature_text, feature_sha = _download_text(FEATURE_URL)
    compound_ids, endpoints, endpoint_matrix, feature_fields, feature_matrix = _read_tables(endpoint_text, feature_text)
    prediction_rows, ranking_rows, payload = _prediction_rows(
        compound_ids,
        endpoints,
        endpoint_matrix,
        feature_fields,
        feature_matrix,
        k_neighbors=args.k_neighbors,
    )

    endpoint_rows_output = Path(args.endpoint_rows_output)
    ranking_output = Path(args.ranking_output)
    endpoint_summary_output = Path(args.endpoint_summary_output)
    _write_csv(
        endpoint_rows_output,
        prediction_rows,
        [
            "model",
            "endpoint",
            "observed",
            "predicted",
            "weight",
            "compound_index",
            "compound_id_sha12",
        ],
    )
    _write_csv(
        ranking_output,
        ranking_rows,
        [
            "rank",
            "model",
            "n_endpoint_rows",
            "weighted_n",
            "rss",
            "weighted_rmse",
            "aic",
            "bic",
            "delta_bic",
            "parameter_count",
            "mean_predicted_probability_on_active_endpoints",
        ],
    )
    _write_csv(
        endpoint_summary_output,
        payload["endpoint_summary"],
        [
            "endpoint",
            "model",
            "weighted_n",
            "rss",
            "weighted_rmse",
            "mean_predicted_probability_on_active_endpoints",
        ],
    )

    provenance = {
        "source_title": "From Pixels to Phenotypes: Integrating Image-Based Profiling with Cell Health Data Improves Interpretability",
        "source_creators": [
            "Srijit Seal",
            "Jordi Carreras-Puigvert",
            "Anne E. Carpenter",
            "Ola Spjuth",
            "Andreas Bender",
        ],
        "zenodo_record": ZENODO_RECORD,
        "zenodo_doi": ZENODO_DOI,
        "license": "CC-BY-4.0",
        "endpoint_file": ENDPOINT_FILE,
        "endpoint_url": ENDPOINT_URL,
        "endpoint_sha256": endpoint_sha,
        "feature_file": FEATURE_FILE,
        "feature_url": FEATURE_URL,
        "feature_sha256": feature_sha,
        "model_architectures": [
            "endpoint_prevalence",
            "morphology_magnitude_5nn",
            "cells_block_5nn",
            "cytoplasm_block_5nn",
            "nuclei_block_5nn",
            "compartment_route_5nn",
        ],
        "prediction_rule": "leave-one-compound-out nearest-neighbor endpoint prediction for morphology architectures; leave-one-compound-out endpoint prevalence for endpoint_prevalence",
        "weighting_rule": "within each endpoint, positive and negative labels each receive total weight 0.5",
        "diagnostics": payload["diagnostics"],
        "derived_outputs": {
            str(endpoint_rows_output): _sha256(endpoint_rows_output),
            str(ranking_output): _sha256(ranking_output),
            str(endpoint_summary_output): _sha256(endpoint_summary_output),
        },
        "raw_file_policy": "Source endpoint and Cell Painting feature CSV files were downloaded into memory and converted to derived benchmark rows only; source CSV files are not retained in the repository.",
        "interpretation_boundary": "This benchmark compares endpoint compatibility among declared reduced morphology architectures. It does not infer drug mechanism, does not train a production classifier, and does not treat Cell Painting morphology as a direct dynamic-state measurement.",
    }
    provenance_path = Path(args.provenance)
    provenance_path.parent.mkdir(parents=True, exist_ok=True)
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "pass",
                "endpoint_rows": len(prediction_rows),
                "ranking_rows": len(ranking_rows),
                "best_model_by_bic": payload["diagnostics"]["best_model_by_bic"],
                "best_model_by_weighted_rmse": payload["diagnostics"]["best_model_by_weighted_rmse"],
                "endpoint_rows_output": str(endpoint_rows_output),
                "ranking_output": str(ranking_output),
                "endpoint_summary_output": str(endpoint_summary_output),
                "provenance": str(provenance_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
