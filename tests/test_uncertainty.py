from unittest import TestCase

from rhodyn.report import to_plain
from rhodyn.uncertainty import bootstrap_interval, mean_difference, permutation_test


class UncertaintyTests(TestCase):
    def test_bootstrap_interval_is_seed_reproducible(self):
        first = bootstrap_interval([1, 2, 3, 4, 5], n_resamples=50, seed=7)
        second = bootstrap_interval([1, 2, 3, 4, 5], n_resamples=50, seed=7)

        self.assertEqual(first.distribution, second.distribution)
        self.assertEqual(first.resample_level, "observation")
        self.assertEqual(first.interval.n, 5)
        self.assertLessEqual(first.interval.lower, first.interval.estimate)
        self.assertGreaterEqual(first.interval.upper, first.interval.estimate)

    def test_group_bootstrap_resamples_declared_units(self):
        result = bootstrap_interval(
            [1.0, 1.2, 2.0, 2.2],
            n_resamples=20,
            seed=3,
            group_labels=["rep1", "rep1", "rep2", "rep2"],
        )
        plain = to_plain(result)

        self.assertEqual(plain["resample_level"], "group")
        self.assertEqual(plain["diagnostics"]["unit_count"], 2)

    def test_permutation_test_is_seed_reproducible(self):
        first = permutation_test([1, 2, 3], [4, 5, 6], n_resamples=40, seed=11)
        second = permutation_test([1, 2, 3], [4, 5, 6], n_resamples=40, seed=11)

        self.assertEqual(first.null_distribution, second.null_distribution)
        self.assertEqual(first.exchangeability_level, "observation")
        self.assertGreaterEqual(first.p_value, 0.0)
        self.assertLessEqual(first.p_value, 1.0)
        self.assertEqual(first.observed, mean_difference([1, 2, 3], [4, 5, 6]))

    def test_group_permutation_uses_group_means(self):
        result = permutation_test(
            [1.0, 1.2, 2.0, 2.2],
            [3.0, 3.2, 4.0, 4.2],
            n_resamples=20,
            seed=5,
            group_labels_a=["a1", "a1", "a2", "a2"],
            group_labels_b=["b1", "b1", "b2", "b2"],
        )

        self.assertEqual(result.exchangeability_level, "group")
        self.assertEqual(result.n_units_a, 2)
        self.assertEqual(result.n_units_b, 2)
