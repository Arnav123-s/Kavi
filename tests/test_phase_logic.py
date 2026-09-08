"""Composition and source-reader fixtures, not training data."""

import unittest
from kavi.composable_configurations import Work
from kavi.phase.logic import evaluate_formula, gate_events
from kavi.phase.model import PhaseConfiguration
from scripts.pcl_discrete_source import Tables, rows


class LogicTests(unittest.TestCase):
    def test_untrained_circuit_does_not_inherit_python_logic(self):
        empty = PhaseConfiguration((2,))
        self.assertIsNone(evaluate_formula(empty, ('and', 'P', 'Q'), {'P': 1, 'Q': 1}, Work()))

    def test_postorder_uses_circuit_outputs_in_operand_order(self):
        class Circuit:
            calls = []
            def predict(self, events, work):
                self.calls.append(events)
                return 0 if len(self.calls) == 1 else 1
        circuit = Circuit()
        self.assertEqual(evaluate_formula(circuit, ('implies', ('not', 'P'), 'Q'),
                                          {'P': 1, 'Q': 1}, Work()), 1)
        self.assertEqual(circuit.calls, [('not', 'true'), ('false', 'implies', 'true')])

    def test_missing_values_and_invalid_syntax(self):
        empty = PhaseConfiguration((2,))
        self.assertIsNone(evaluate_formula(empty, 'P', {}, Work()))
        for expression in [('and', 'P'), ('unknown', 'P'), [], 1]:
            with self.assertRaises(ValueError):
                evaluate_formula(empty, expression, {}, Work())
        with self.assertRaises(ValueError):
            evaluate_formula(empty, 'P', {'P': True}, Work())

    def test_depth_and_work_limits(self):
        expression = 'P'
        for _ in range(1200):
            expression = ('not', expression)
        with self.assertRaises(InterruptedError):
            evaluate_formula(PhaseConfiguration((2,)), expression, {'P': 1}, Work(), max_nodes=100)
        with self.assertRaises(InterruptedError):
            evaluate_formula(PhaseConfiguration((2,)), 'P', {'P': 1}, Work(limit=0))

    def test_nonboolean_model_output_rejected(self):
        class Circuit:
            def predict(self, events, work): return 7
        with self.assertRaises(ValueError):
            evaluate_formula(Circuit(), ('not', 'P'), {'P': 1}, Work())

    def test_source_table_ignores_layout_padding_not_truth_cells(self):
        parser = Tables()
        parser.feed('<table><tr><th>P</th><th>out</th></tr><tr><td>T</td><td>F</td></tr><tr><td></td></tr></table>')
        self.assertEqual(rows(parser.tables[0]), [[1, 0]])
        self.assertEqual(gate_events('implies', (1, 0)), ('true', 'implies', 'false'))


if __name__ == '__main__':
    unittest.main()
