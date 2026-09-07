import itertools
import math
import unittest

from kavi.configuration_repair import acceptance_probability, assess, redirect, repair
from kavi.finite_state_audit import compare
from kavi.recurrent_configuration import Configuration


class ConfigurationRepairTests(unittest.TestCase):
    def setUp(self):
        self.original = Configuration(('a', 'b'), ((1, 0), (0, 1)), (0, 1))
        self.damaged = redirect(self.original, 0, 1, 1)
        self.examples = [(seq, seq.count('a') % 2) for n in range(5)
                         for seq in itertools.product(('a', 'b'), repeat=n)]

    def test_exhaustive_repair_preserves_old_domain(self):
        graph, stats = repair(self.damaged, self.examples, self.original, ('a',),
                              budget=4, exhaustive=True)
        self.assertTrue(compare(graph, self.original, ('a', 'b'))['equivalent'])
        self.assertEqual(stats['proposals'], 4)
        self.assertGreater(stats['retention_rejections'], 0)
        self.assertEqual(stats['best_errors'], 0)

    def test_zero_budget_never_mutates_and_stop_interrupts(self):
        graph, stats = repair(self.damaged, self.examples, self.original, ('a',), budget=0)
        self.assertEqual(graph, self.damaged)
        self.assertEqual(stats['proposals'], 0)
        def stop():
            raise InterruptedError('stop')
        with self.assertRaises(InterruptedError):
            repair(self.damaged, self.examples, self.original, ('a',), check=stop)

    def test_temperature_cannot_override_retention(self):
        graph, stats = repair(self.damaged, self.examples, self.original, ('a',),
                              seed=43, budget=100, heated=True, priority=True)
        self.assertTrue(compare(graph, self.original, ('a',))['equivalent'])
        self.assertLessEqual(stats['proposals'], 100)
        with self.assertRaisesRegex(ValueError, 'old-domain'):
            repair(self.damaged, self.examples, self.original, ('a', 'b'))

    def test_asymmetric_acceptance_uses_reverse_proposal_probability(self):
        self.assertAlmostEqual(acceptance_probability(-.1, .1, .25), math.exp(-1) * .25)
        self.assertEqual(acceptance_probability(.1, .1, 4), 1)
        self.assertEqual(acceptance_probability(-1000, .001), 0)

    def test_priority_counts_failed_traversals_without_reexecuting_graph(self):
        result = assess(self.damaged, [(('b', 'a'), 1)])
        self.assertEqual(result['token_steps'], 2)
        self.assertEqual(result['priority_steps'], 2)
        self.assertEqual(result['weights'], [1, 2, 2, 1])


if __name__ == '__main__':
    unittest.main()
