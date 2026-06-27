"""Audit the Stage 3 public case-study evidence bank.

The audit is intentionally deterministic and standard-library only. It checks
the retained derived tables, public-source provenance, notebook surfaces, and
the manuscript-independence boundary that keeps RhoDyn separate from the
RhoA/microglia paper.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

DRG_TABLE = Path("case_studies/drg_calcium_residence_amplitude_benchmark.csv")
ERK_TABLE = Path("case_studies/erk_gpcr_residence_amplitude_benchmark.csv")
CELL_PAINTING_RANKING = Path("case_studies/cell_painting_mitotox_model_ranking.csv")
ERK_AKT_COUPLING = Path("case_studies/erk_gpcr_erk_akt_bounded_coupling.csv")
ERK_AKT_HARDENING = Path("case_studies/erk_gpcr_erk_akt_hardening_report.json")
PUBLIC_CANDIDATES = Path("case_studies/public_data_candidates.tsv")

NOTEBOOKS = [
    Path("notebooks/01_synthetic_residence_primer.ipynb"),
    Path("notebooks/02_public_signaling_benchmarks.ipynb"),
    Path("notebooks/03_public_endpoint_and_coupling_benchmarks.ipynb"),
]

PUBLIC_ADAPTERS = [
    Path("scripts/fetch_drg_calcium_benchmark.py"),
    Path("scripts/fetch_erk_gpcr_benchmark.py"),
    Path("scripts/fetch_cell_painting_endpoint_benchmark.py"),
    Path("scripts/fetch_erk_akt_bounded_coupling.py"),
    Path("scripts/fetch_mlci_feature_subset.py"),
]

DOCS = [
    Path("docs/drg_calcium_public_benchmark.md"),
    Path("docs/erk_gpcr_public_benchmark.md"),
    Path("docs/cell_painting_endpoint_benchmark.md"),
    Path("docs/erk_akt_bounded_coupling_benchmark.md"),
    Path("docs/stage3_case_study_bank.md"),
]


def _read_csv(root: Path, rel: Path) -> list[dict[str, str]]:
    with (root / rel).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _read_json(root: Path, rel: Path) -> dict[str, Any]:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def _exists(root: Path, rel: Path) -> bool:
    return (root / rel).exists()


def _pass(value: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"status": "pass" if value else "fail", **evidence}


def _class_counts(rows: list[dict[str, str]]) -> Counter[str]:
    return Counter(row.get("amplitude_residence_class", "") for row in rows)


def _audit_drg(root: Path) -> dict[str, Any]:
    rows = _read_csv(root, DRG_TABLE)
    classes = _class_counts(rows)
    cells = {row["cell_id"] for row in rows}
    conditions = Counter(row["condition"] for row in rows)
    return _pass(
        len(rows) == 360
        and len(cells) == 120
        and classes["amplitude_only_top_quartile"] > 0
        and classes["residence_only_top_quartile"] > 0,
        {
            "dataset": "public DRG calcium traces",
            "table": DRG_TABLE.as_posix(),
            "rows": len(rows),
            "cell_count": len(cells),
            "condition_counts": dict(sorted(conditions.items())),
            "class_counts": dict(sorted(classes.items())),
            "residence_amplitude_distinction": classes["amplitude_only_top_quartile"] > 0
            and classes["residence_only_top_quartile"] > 0,
        },
    )


def _audit_erk(root: Path) -> dict[str, Any]:
    rows = _read_csv(root, ERK_TABLE)
    classes = _class_counts(rows)
    ligands = Counter(row["ligand"] for row in rows)
    return _pass(
        len(rows) == 180
        and set(ligands) == {"His", "S1P", "UK"}
        and classes["amplitude_only_top_quartile"] > 0
        and classes["residence_only_top_quartile"] > 0,
        {
            "dataset": "public ERK KTR GPCR traces",
            "table": ERK_TABLE.as_posix(),
            "rows": len(rows),
            "ligand_counts": dict(sorted(ligands.items())),
            "class_counts": dict(sorted(classes.items())),
            "residence_amplitude_distinction": classes["amplitude_only_top_quartile"] > 0
            and classes["residence_only_top_quartile"] > 0,
        },
    )


def _audit_cell_painting(root: Path) -> dict[str, Any]:
    ranking = _read_csv(root, CELL_PAINTING_RANKING)
    best = ranking[0] if ranking else {}
    next_best = ranking[1] if len(ranking) > 1 else {}
    return _pass(
        bool(best)
        and best.get("model") == "compartment_route_5nn"
        and float(next_best.get("delta_bic", "0")) > 200,
        {
            "dataset": "public Cell Painting morphology and MitoTox endpoints",
            "table": CELL_PAINTING_RANKING.as_posix(),
            "model_count": len(ranking),
            "best_model": best.get("model"),
            "runner_up_delta_bic": float(next_best.get("delta_bic", "nan")) if next_best else None,
            "role": "public perturbation endpoint/model-comparison benchmark",
        },
    )


def _audit_erk_akt(root: Path) -> dict[str, Any]:
    rows = _read_csv(root, ERK_AKT_COUPLING)
    by_contrast = {row["contrast"]: row for row in rows}
    hardening = _read_json(root, ERK_AKT_HARDENING)
    uk = by_contrast.get("erk_minus_akt_residence_UK", {})
    his = by_contrast.get("erk_minus_akt_residence_His", {})
    s1p = by_contrast.get("erk_minus_akt_residence_S1P", {})
    return _pass(
        uk.get("passes") == "1"
        and his.get("passes") == "0"
        and s1p.get("passes") == "0"
        and hardening.get("status") == "pass",
        {
            "dataset": "paired public ERK and Akt KTR GPCR traces",
            "table": ERK_AKT_COUPLING.as_posix(),
            "passed_contexts": [key for key, row in by_contrast.items() if row.get("passes") == "1"],
            "failed_contexts": [key for key, row in by_contrast.items() if row.get("passes") == "0"],
            "primary_margin": float(uk.get("margin", "nan")) if uk else None,
            "minimum_passing_margin_UK": hardening.get("minimum_passing_margin_by_contrast", {}).get(
                "erk_minus_akt_residence_UK"
            ),
            "replicate_sensitivity_status": hardening.get("replicate_sensitivity_status"),
            "role": "context-limited public bounded-coupling benchmark",
        },
    )


def _audit_deliverables(root: Path) -> dict[str, Any]:
    notebooks = {path.as_posix(): _exists(root, path) for path in NOTEBOOKS}
    adapters = {path.as_posix(): _exists(root, path) for path in PUBLIC_ADAPTERS}
    docs = {path.as_posix(): _exists(root, path) for path in DOCS}
    benchmark_tables = {
        path.as_posix(): _exists(root, path)
        for path in [DRG_TABLE, ERK_TABLE, CELL_PAINTING_RANKING, ERK_AKT_COUPLING, PUBLIC_CANDIDATES]
    }
    readme = (root / "README.md").read_text(encoding="utf-8")
    manuscript_boundary = (
        "The manuscript was not generated with RhoDyn" in readme
        and "optional reference case study" in readme
    )
    return {
        "tutorial_notebooks": _pass(all(notebooks.values()), {"files": notebooks}),
        "reproducible_case_study_docs": _pass(all(docs.values()), {"files": docs}),
        "public_data_adapters": _pass(all(adapters.values()), {"files": adapters}),
        "benchmark_tables": _pass(all(benchmark_tables.values()), {"files": benchmark_tables}),
        "manuscript_independence_boundary": _pass(
            manuscript_boundary,
            {
                "source": "README.md",
                "required_phrases": [
                    "The manuscript was not generated with RhoDyn",
                    "optional reference case study",
                ],
            },
        ),
    }


def audit_stage3(root: Path = ROOT) -> dict[str, Any]:
    """Return a deterministic Stage 3 gate report."""

    drg = _audit_drg(root)
    erk = _audit_erk(root)
    cell_painting = _audit_cell_painting(root)
    erk_akt = _audit_erk_akt(root)
    deliverables = _audit_deliverables(root)
    signaling_systems = [
        key
        for key, result in {
            "public_drg_calcium": drg,
            "public_erk_gpcr": erk,
        }.items()
        if result["status"] == "pass" and result["residence_amplitude_distinction"]
    ]
    gates = {
        "two_biological_systems_show_residence_amplitude_distinction": _pass(
            len(signaling_systems) >= 2,
            {"passing_systems": signaling_systems},
        ),
        "one_public_endpoint_case_shows_model_comparison": _pass(
            cell_painting["status"] == "pass",
            {"case": "cell_painting_mitotox", "best_model": cell_painting.get("best_model")},
        ),
        "one_case_shows_bounded_coupling_or_reserve_logic": _pass(
            erk_akt["status"] == "pass",
            {
                "case": "erk_gpcr_erk_akt",
                "role": "bounded coupling",
                "passed_contexts": erk_akt.get("passed_contexts", []),
            },
        ),
        "examples_do_not_imply_manuscript_generated_original_results": deliverables[
            "manuscript_independence_boundary"
        ],
    }
    all_checks = [
        drg,
        erk,
        cell_painting,
        erk_akt,
        *deliverables.values(),
        *gates.values(),
    ]
    status = "pass" if all(item["status"] == "pass" for item in all_checks) else "fail"
    return {
        "report_format": "rhodyn.stage3_case_study_bank_gate_report.v1",
        "status": status,
        "roadmap_scope": "Stage 3 case-study evidence bank",
        "current_position": (
            "Stage 3 evidence bank is satisfied for v0.3 if all gates pass. "
            "Additional public systems are Stage 7 evidence-expansion work, not prerequisites for Stage 4."
        ),
        "case_studies": {
            "public_drg_calcium": drg,
            "public_erk_gpcr": erk,
            "public_cell_painting_mitotox": cell_painting,
            "public_erk_akt_bounded_coupling": erk_akt,
        },
        "deliverables": deliverables,
        "gates": gates,
        "interpretation_boundary": (
            "The public case studies demonstrate RhoDyn analysis behavior on retained derived public tables. "
            "They do not imply that RhoDyn generated the original RhoA/microglia manuscript results."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", type=Path, default=None)
    args = parser.parse_args(argv)

    report = audit_stage3(args.root)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write is not None:
        output = args.write if args.write.is_absolute() else args.root / args.write
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
