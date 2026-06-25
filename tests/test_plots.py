import os
import tempfile
from importlib.util import find_spec
from unittest import TestCase, skipUnless
from unittest.mock import patch

from rhodyn.compare import rank_model_fits
from rhodyn.coupling import equivalence_from_interval
from rhodyn.extras import MissingOptionalDependency
from rhodyn.plots import (
    plot_coupling_interval,
    plot_model_residuals,
    plot_reserve_summary,
    plot_residence_trace,
    plot_sensitivity_curve,
)
from rhodyn.residence import ResidenceWindow
from rhodyn.schema import TrajectoryRecord, read_endpoint_csv
from rhodyn.sensitivity import residence_window_grid, score_trace_window_sensitivity


class PlotTests(TestCase):
    def test_missing_matplotlib_message_is_actionable(self):
        with patch("rhodyn.extras.find_spec", return_value=None):
            with self.assertRaises(MissingOptionalDependency):
                plot_reserve_summary(["a"], [0.5])

    @skipUnless(find_spec("matplotlib") is not None, "matplotlib not installed")
    def test_plot_helpers_return_fig_and_axis(self):
        os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp())
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt

        records = [
            TrajectoryRecord("cell", 0, "control", 0.2),
            TrajectoryRecord("cell", 1, "control", 0.5),
            TrajectoryRecord("cell", 2, "control", 0.8),
        ]
        curve = score_trace_window_sensitivity(
            records,
            residence_window_grid(low_min=0.3, low_max=0.4, high_min=0.6, high_max=0.7, steps=2),
        )
        fits, issues = read_endpoint_csv("examples/synthetic_endpoints.csv")
        self.assertEqual(issues, [])

        plot_calls = [
            lambda: plot_residence_trace(records, ResidenceWindow(0.3, 0.7)),
            lambda: plot_coupling_interval(equivalence_from_interval(0.0, -0.05, 0.05, 0.1)),
            lambda: plot_reserve_summary(["control"], [0.8]),
            lambda: plot_sensitivity_curve(curve),
            lambda: plot_model_residuals(rank_model_fits(fits)),
        ]
        for call in plot_calls:
            fig, ax = call()
            self.assertIs(ax.figure, fig)
            plt.close(fig)
