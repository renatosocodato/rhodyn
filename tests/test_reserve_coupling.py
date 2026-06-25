from unittest import TestCase

from rhodyn.coupling import equivalence_from_interval, one_sample_tost, rope_decision, rope_mass, two_sample_welch_tost
from rhodyn.reserve import ff_over_f0, reserve_coordinate


class ReserveCouplingTests(TestCase):
    def test_ff_over_f0(self):
        values = ff_over_f0([2.0, 2.0, 4.0], baseline_points=2)
        self.assertEqual(values, [1.0, 1.0, 2.0])

    def test_reserve_coordinate(self):
        self.assertAlmostEqual(reserve_coordinate([0.2, 0.4], floor=0.0, ceiling=1.0), 0.6)

    def test_equivalence_interval(self):
        decision = equivalence_from_interval(0.01, -0.05, 0.04, 0.10, rope_mass=0.99)
        self.assertTrue(decision.passes)
        self.assertAlmostEqual(rope_mass([-0.01, 0.02, 0.20], 0.05), 2 / 3)

    def test_one_sample_tost_from_raw_array(self):
        decision = one_sample_tost(
            [-0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03],
            margin=0.20,
            prefer_scipy=False,
        )
        self.assertTrue(decision.passes)
        self.assertLess(decision.p_tost, 0.05)
        self.assertTrue(-0.20 <= decision.ci_low <= decision.ci_high <= 0.20)
        self.assertEqual(decision.method, "normal_approximation")

    def test_two_sample_welch_tost_from_raw_arrays_with_rope(self):
        a = [0.10, 0.11, 0.09, 0.10, 0.12, 0.08]
        b = [0.12, 0.11, 0.13, 0.12, 0.10, 0.14]
        decision = two_sample_welch_tost(
            a,
            b,
            margin=0.15,
            rope_samples=[-0.04, -0.03, -0.02, -0.01, 0.00, 0.01],
            prefer_scipy=False,
        )
        self.assertTrue(decision.passes)
        self.assertEqual(decision.n_a, len(a))
        self.assertEqual(decision.n_b, len(b))
        self.assertAlmostEqual(decision.rope_mass, 1.0)

    def test_rope_only_decision(self):
        decision = rope_decision([-0.02, -0.01, 0.00, 0.01, 0.02], margin=0.05)
        self.assertTrue(decision.passes)
        self.assertAlmostEqual(decision.rope_mass, 1.0)
