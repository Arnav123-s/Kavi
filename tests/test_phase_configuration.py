"""Interpreter fixtures, not language teaching data or intelligence benchmarks."""

import unittest
from kavi.composable_configurations import Work
from kavi.phase_configuration import PhaseConfiguration, PhaseActivity, select_correction


class PhaseTests(unittest.TestCase):
    def model(self, kick=1):
        return PhaseConfiguration((2, 3), (('a', 0, 1), ('b', 0, 0)),
                                  ((0, 1, 1, kick),), (((1, 1), 7), ((1, 2), 8)))

    def test_later_input_changes_joint_result_and_order_matters(self):
        m = self.model()
        r = PhaseActivity(m, Work())
        self.assertIsNone(r.accept('a'))
        self.assertEqual(r.phases, (1, 1))
        self.assertIsNone(r.accept('b'))
        self.assertEqual(r.finish(), 8)
        self.assertEqual(m.predict('ba', Work()), 7)
        with self.assertRaises(ValueError):
            r.accept('a')

    def test_couplings_use_snapshot_and_not_list_order(self):
        c = ((0, 1, 1, 1), (1, 1, 0, 1))
        a = PhaseConfiguration((3, 3), (('x', 0, 1),), c)
        b = PhaseConfiguration(a.moduli, a.impulses, tuple(reversed(c)))
        ra, rb = PhaseActivity(a, Work()), PhaseActivity(b, Work())
        ra.accept('x'); rb.accept('x')
        self.assertEqual(ra.phases, (1, 1))
        self.assertEqual(ra.phases, rb.phases)

    def test_unknown_and_interrupt_cannot_release_stale_output(self):
        r = PhaseActivity(self.model(), Work())
        r.accept('a'); r.accept('unrecognized')
        self.assertIsNone(r.finish())
        r = PhaseActivity(self.model(), Work(limit=1))
        with self.assertRaises(InterruptedError):
            r.accept('a')
        self.assertIsNone(r.finish())

    def test_only_current_phases_are_retained(self):
        m = self.model()
        r = PhaseActivity(m, Work())
        for _ in range(1000):
            r.accept('a')
        self.assertEqual(r.phases, (0, 2))
        self.assertEqual(set(vars(r)), {'configuration', 'work', 'phases', 'closed', 'failed'})
        self.assertEqual(PhaseActivity(m, Work()).phases, (0, 0))

    def test_correction_selects_shared_dynamics_without_storing_lessons(self):
        before, after = self.model(0), self.model(1)
        chosen, stats = select_correction(before, [after], [('a', 7)], [], Work())
        self.assertTrue(stats['accepted'])
        self.assertEqual(chosen.predict('ab', Work()), 8)
        self.assertEqual(chosen.record(), after.record())
        # Protection can block a correction; it must not silently disappear.
        chosen, stats = select_correction(after, [before], [('a', None)], [('a', 7)], Work())
        self.assertEqual(chosen, after)
        self.assertEqual(stats['errors'], 1)

    def test_schema_and_search_budget(self):
        with self.assertRaises(ValueError):
            PhaseConfiguration((1,))
        with self.assertRaises(ValueError):
            PhaseConfiguration((2,), outputs=(((0,), 1), ((0,), 2)))
        with self.assertRaises(InterruptedError):
            select_correction(self.model(), [self.model(), self.model()], [('a', 7)], [], Work(), max_candidates=1)


if __name__ == '__main__':
    unittest.main()
