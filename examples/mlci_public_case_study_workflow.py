"""Minimal public-case-study workflow for CTC-style live-cell tracks."""

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
    public_features, public_feature_issues = read_ctc_feature_csv(CASE_STUDIES / "mlci_public_track_features_subset.csv")
    if public_feature_issues:
        raise SystemExit(json.dumps(to_plain({"public_feature_issues": public_feature_issues}), indent=2))

    public_intensity_trajectories = ctc_features_to_trajectory_records(
        public_features,
        signal="intensity",
        condition="mlci_public_segmentation_features",
        replicate="zenodo_7260137",
    )
    public_speed_trajectories = ctc_features_to_trajectory_records(
        public_features,
        signal="speed",
        condition="mlci_public_segmentation_features",
        replicate="zenodo_7260137",
    )
    public_residence = score_records(public_intensity_trajectories, ResidenceWindow(low=13.0, high=14.5))
    public_sensitivity = score_records_window_sensitivity(
        public_intensity_trajectories,
        residence_window_grid(low_min=12.8, low_max=13.2, high_min=14.2, high_max=14.6, steps=2),
        min_residence_fraction=0.25,
    )
    public_uncertainty = bootstrap_interval(
        [summary.residence_fraction for summary in public_residence],
        n_resamples=50,
        seed=17,
        schema_kind="trajectory",
        parameters={"source": "Zenodo 7260137 tracking label mean intensities"},
    )

    public_lineage_trajectories = ctc_lineage_to_trajectory_records(
        public_lineage,
        signal="normalized_track_age",
        condition="mlci_public_lineage_subset",
        replicate="zenodo_7260137",
        max_tracks=10,
    )

    plot_status = "matplotlib_not_installed"
    if find_spec("matplotlib") is not None:
        os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp())
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt

        first_cell_id = public_intensity_trajectories[0].cell_id
        first_track = [row for row in public_intensity_trajectories if row.cell_id == first_cell_id]
        fig, _ = plot_residence_trace(first_track, ResidenceWindow(low=13.0, high=14.5))
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
                        "source": "Zenodo 7260137 ctc_format.zip tracking masks plus raw frames",
                        "feature_rows": len(public_features),
                        "intensity_trajectory_rows": len(public_intensity_trajectories),
                        "speed_trajectory_rows": len(public_speed_trajectories),
                        "residence_summaries": public_residence,
                        "sensitivity_curves": public_sensitivity,
                        "bootstrap_interval": public_uncertainty.interval,
                    },
                    "public_lineage_fallback": {
                        "source": "Zenodo 7260137 ctc_format.zip 00_GT/TRA/man_track.txt",
                        "lineage_rows": len(public_lineage),
                        "trajectory_rows": len(public_lineage_trajectories),
                    },
                    "plot_status": plot_status,
                    "interpretation_boundary": "public segmentation-derived features demonstrate centroid, area, and intensity ingestion; biological interpretation still requires a declared signal, window, grouping structure, and uncertainty rule",
                }
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
