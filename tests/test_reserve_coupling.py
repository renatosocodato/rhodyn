from unittest import TestCase

from rhodyn.coupling import equivalence_from_interval, rope_mass
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
