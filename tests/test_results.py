import json
from unittest import TestCase

from rhodyn.compare import rank_model_fits
from rhodyn.coupling import equivalence_from_interval, two_sample_welch_tost
from rhodyn.report import to_plain
from rhodyn.residence import ResidenceWindow, score_records
from rhodyn.results import (
    GroupMetadata,
    coupling_result_from_decision,
    coupling_result_from_tost,
    model_comparison_result_from_fits,
    residence_result_from_summary,
)
from rhodyn.schema import read_endpoint_csv, read_trajectory_csv


class TypedResultTests(TestCase):
    def test_residence_result_serialization_keeps_group_and_parameters(self):
        rows, issues = read_trajectory_csv("examples/synthetic_trajectory.csv")
        self.assertEqual(issues, [])
        summary = score_records(rows, ResidenceWindow(low=0.3, high=0.7))[0]
        result = residence_result_from_summary(summary, parameters={"low": 0.3, "high": 0.7}, source="fixture")

        plain = to_plain(result)
        encoded = json.dumps(plain, sort_keys=True)

        self.assertIn('"schema_kind": "trajectory"', encoded)
        self.assertEqual(plain["group"]["condition"], summary.condition)
        self.assertEqual(plain["group"]["cell_id"], summary.cell_id)
        self.assertEqual(plain["provenance"]["parameters"]["low"], 0.3)
        self.assertEqual(plain["value_kind"], "derived_summary")

    def test_coupling_result_separates_decision_rule_from_input_group(self):
        decision = equivalence_from_interval(0.01, -0.03, 0.04, 0.10, rope_mass=0.98)
        result = coupling_result_from_decision(
            "rock_src",
            decision,
            group=GroupMetadata(condition="Y27632", replicate="rep1"),
            parameters={"alpha": 0.05},
        )
        plain = to_plain(result)

        self.assertTrue(plain["passes"])
        self.assertEqual(plain["decision_rule"], "interval_inside_margin_and_rope")
        self.assertEqual(plain["group"]["condition"], "Y27632")
        self.assertEqual(plain["group"]["grouping_levels"], ["condition", "replicate"])
        self.assertEqual(plain["value_kind"], "decision_rule")

    def test_model_comparison_result_reports_best_model_and_provenance(self):
        rows, issues = read_endpoint_csv("examples/synthetic_endpoints.csv")
        self.assertEqual(issues, [])
        fits = rank_model_fits(rows)
        result = model_comparison_result_from_fits(fits, parameters={"parameter_count": 1})
        plain = to_plain(result)

        self.assertEqual(plain["best_model"], "residence_gated")
        self.assertEqual(plain["ranking_metric"], "bic")
        self.assertEqual(plain["provenance"]["schema_kind"], "endpoint")
        self.assertEqual(plain["value_kind"], "model_comparison")

    def test_tost_result_serialization_carries_margin_and_p_values(self):
        decision = two_sample_welch_tost(
            [0.10, 0.11, 0.09, 0.10, 0.12, 0.08],
            [0.12, 0.11, 0.13, 0.12, 0.10, 0.14],
            margin=0.15,
            prefer_scipy=False,
        )
        result = coupling_result_from_tost("rock_src", decision, parameters={"alpha": 0.05})
        plain = to_plain(result)

        self.assertTrue(plain["passes"])
        self.assertEqual(plain["decision_rule"], "welch_tost_interval_rope")
        self.assertEqual(plain["margin"], 0.15)
        self.assertIsNotNone(plain["p_tost"])
        self.assertEqual(plain["n"], 12)
