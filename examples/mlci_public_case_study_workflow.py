"""Minimal public-case-study workflow for CTC-style live-cell tracks.

The bundled CSV is a tiny schema fixture. For a real public tutorial, replace
the fixture with features extracted from the MLCI benchmark CTC archives.
"""

from __future__ import annotations

import json
import os
import tempfile
from importlib.util import find_spec
from pathlib import Path

from rhodyn.ctc import (
    ctc_features_to_trajectory_records,
    ctc_lineage_coverage_issues,
    ctc_lineage_to_trajectory_records,
    read_ctc_feature_csv,
    read_ctc_lineage,
)
from rhodyn.plots import plot_residence_trace
from rhodyn.report import to_plain
from rhodyn.residence import ResidenceWindow, score_records
from rhodyn.sensitivity import residence_window_grid, score_records_window_sensitivity
from rhodyn.uncertainty import bootstrap_interval


ROOT = Path(__file__).resolve().parent
CASE_STUDIES = ROOT.parent / "case_studies"


def main() -> None:
    features, feature_issues = read_ctc_feature_csv(ROOT / "mlci_ctc_features.csv")
    lineage, lineage_issues = read_ctc_lineage(ROOT / "mlci_man_track.txt")
    coverage_issues = ctc_lineage_coverage_issues(features, lineage)
    if feature_issues or lineage_issues or coverage_issues:
        raise SystemExit(
            json.dumps(
                to_plain({"feature_issues": feature_issues, "lineage_issues": lineage_issues, "coverage": coverage_issues}),
                indent=2,
            )
        )

    trajectories = ctc_features_to_trajectory_records(
        features,
        signal="speed",
        condition="mlci_fixture",
        replicate="schema_fixture",
    )
    residence = score_records(trajectories, ResidenceWindow(low=3.0, high=5.0))
    windows = residence_window_grid(low_min=2.0, low_max=3.0, high_min=5.0, high_max=6.0, steps=2)
    sensitivity = score_records_window_sensitivity(trajectories, windows, min_residence_fraction=0.5)
    uncertainty = bootstrap_interval(
        [summary.residence_fraction for summary in residence],
        n_resamples=50,
        seed=13,
        schema_kind="trajectory",
        parameters={"statistic": "mean residence_fraction"},
    )

    public_lineage, public_lineage_issues = read_ctc_lineage(CASE_STUDIES / "mlci_public_man_track_subset.txt")
    if public_lineage_issues:
        raise SystemExit(json.dumps(to_plain({"public_lineage_issues": public_lineage_issues}), indent=2))
    public_trajectories = ctc_lineage_to_trajectory_records(
        public_lineage,
        signal="normalized_track_age",
        condition="mlci_public_lineage_subset",
        replicate="zenodo_7260137",
        max_tracks=10,
    )
    public_residence = score_records(public_trajectories, ResidenceWindow(low=0.25, high=0.75))
    public_sensitivity = score_records_window_sensitivity(
        public_trajectories,
        residence_window_grid(low_min=0.2, low_max=0.3, high_min=0.7, high_max=0.8, steps=2),
        min_residence_fraction=0.25,
    )
    public_uncertainty = bootstrap_interval(
        [summary.residence_fraction for summary in public_residence],
        n_resamples=50,
        seed=17,
        schema_kind="trajectory",
        parameters={"source": "Zenodo 7260137 00_GT/TRA/man_track.txt subset"},
    )

    plot_status = "matplotlib_not_installed"
    if find_spec("matplotlib") is not None:
        os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp())
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt

        first_cell_id = public_trajectories[0].cell_id
        first_track = [row for row in public_trajectories if row.cell_id == first_cell_id]
        fig, _ = plot_residence_trace(first_track, ResidenceWindow(low=0.25, high=0.75))
        plt.close(fig)
        plot_status = "plot_constructed_without_display"

    print(
        json.dumps(
            to_plain(
                {
                    "status": "pass",
                    "source": "ctc-style schema fixture for MLCI public tutorial",
                    "trajectory_rows": len(trajectories),
                    "residence_summaries": residence,
                    "sensitivity_curves": sensitivity,
                    "bootstrap_interval": uncertainty.interval,
                    "public_subset": {
                        "source": "Zenodo 7260137 ctc_format.zip 00_GT/TRA/man_track.txt",
                        "lineage_rows": len(public_lineage),
                        "trajectory_rows": len(public_trajectories),
                        "residence_summaries": public_residence,
                        "sensitivity_curves": public_sensitivity,
                        "bootstrap_interval": public_uncertainty.interval,
                    },
                    "plot_status": plot_status,
                    "interpretation_boundary": "public lineage subset demonstrates software flow only; segmentation-derived features are needed for centroid or intensity biology",
                }
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
