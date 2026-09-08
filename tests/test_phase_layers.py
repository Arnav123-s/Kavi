"""Two-layer reconstruction checks; no source-based training claims."""

import unittest
from kavi.composable_configurations import Work
from kavi.phase import PhaseConfiguration
from kavi.phase.layers import CircuitTemplate, CircuitGeneration, reconstruct
from kavi.phase.evaluation import evaluate


class LayerTests(unittest.TestCase):
    def test_whole_reconstruction_retains_template_and_acquires_fixture_rule(self):
        template = CircuitTemplate((2,), max_couplings=0)
        old = CircuitGeneration(template, PhaseConfiguration((2,), (('x', 0, 0),)))
        successor, stats = reconstruct(old, [('x', 1), ('xx', 0)], [], Work(), candidates=32)
        self.assertTrue(stats['accepted'])
        self.assertIs(successor.template, old.template)
        self.assertEqual(successor.generation, 1)
        self.assertEqual(old.circuit.outputs, ())
        self.assertNotIn('parent', successor.record())
        for length in range(3, 100):
            self.assertEqual(successor.circuit.predict('x'*length, Work()), length % 2)
        again, _ = reconstruct(old, [('x', 1), ('xx', 0)], [], Work(), candidates=32)
        self.assertEqual(again, successor)

    def test_impossible_correction_is_not_admitted(self):
        old = CircuitGeneration(CircuitTemplate((2,), max_couplings=0),
                                PhaseConfiguration((2,), (('x', 0, 1),), outputs=(((1,), 1),)))
        successor, stats = reconstruct(old, [('x', 0)], [('x', 1)], Work(), candidates=8)
        self.assertIs(successor, old)
        self.assertFalse(stats['accepted'])

    def test_template_change_is_explicit_and_interruption_is_transactional(self):
        with self.assertRaises(ValueError):
            CircuitGeneration(CircuitTemplate((2,)), PhaseConfiguration((3,)))
        old = CircuitGeneration(CircuitTemplate((2,)), PhaseConfiguration((2,)))
        with self.assertRaises(InterruptedError):
            reconstruct(old, [('x', 1)], [], Work(limit=1))
        self.assertEqual(old.generation, 0)

    def test_frozen_evaluation_distinguishes_wrong_and_unknown(self):
        model = CircuitGeneration(CircuitTemplate((2,)),
                                  PhaseConfiguration((2,), (('x', 0, 1),), outputs=(((1,), 1),)))
        result = evaluate(model, [('x', 1), ('x', 0), ('?', 1)], Work())
        self.assertEqual((result['correct'], result['wrong'], result['unresolved']), (1, 1, 1))
        self.assertTrue(result['frozen_unchanged'])


if __name__ == '__main__':
    unittest.main()
