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
    read_ctc_feature_csv,
    read_ctc_lineage,
)
from rhodyn.plots import plot_residence_trace
from rhodyn.report import to_plain
from rhodyn.residence import ResidenceWindow, score_records
from rhodyn.sensitivity import residence_window_grid, score_records_window_sensitivity
from rhodyn.uncertainty import bootstrap_interval


ROOT = Path(__file__).resolve().parent


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

    plot_status = "matplotlib_not_installed"
    if find_spec("matplotlib") is not None:
        os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp())
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt

        first_track = [row for row in trajectories if row.cell_id == "track_1"]
        fig, _ = plot_residence_trace(first_track, ResidenceWindow(low=3.0, high=5.0))
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
                    "plot_status": plot_status,
                    "interpretation_boundary": "fixture validates workflow only; it is not a biological result",
                }
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
