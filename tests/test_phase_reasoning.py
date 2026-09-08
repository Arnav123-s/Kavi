"""Reasoning and clause-mask fixtures; not teaching examples."""

import unittest
from kavi.composable_configurations import Work
from kavi.phase.model import PhaseConfiguration
from kavi.phase.reasoning import models
from kavi.phase.english_logic import events, interpret


class ReasoningTests(unittest.TestCase):
    def test_missing_semantics_does_not_assert_a_solution(self):
        result = models(PhaseConfiguration((2,)), [('not','P')], ['P'], Work())
        self.assertFalse(result['complete'])
        self.assertEqual(result['solutions'], [])
        self.assertEqual(result['unresolved_assignments'], 2)

    def test_variable_premise_constrains_assignments(self):
        result = models(PhaseConfiguration((2,)), ['P'], ['P','Q'], Work())
        self.assertEqual(result['solutions'], [{'P':1,'Q':0},{'P':1,'Q':1}])
        self.assertTrue(result['complete'])

    def test_assignment_search_respects_domain_and_work_limits(self):
        with self.assertRaises(ValueError):
            models(PhaseConfiguration((2,)), [], ['P','P'], Work())
        with self.assertRaises(InterruptedError):
            models(PhaseConfiguration((2,)), [], ['P'], Work(limit=0))

    def test_masking_preserves_connector_order_and_not_clause_content(self):
        self.assertEqual(events('If Alice runs, then Bob waits.',('Alice runs','Bob waits')),
                         ('if','@clause','then','@clause'))
        self.assertNotEqual(events('A if B',('A','B')),events('A only if B',('A','B')))
        with self.assertRaises(ValueError): events('A and A',('A','A'))
        with self.assertRaises(ValueError): events('abc',('ab','bc'))

    def test_phrase_meaning_is_taken_from_circuit_output(self):
        class Circuit:
            def predict(self, sequence, work): return 3
        self.assertEqual(interpret(Circuit(),'A and B',('A','B'),Work()),('implies','Q','P'))
        self.assertIsNone(interpret(PhaseConfiguration((2,)),'A and B',('A','B'),Work()))


if __name__ == '__main__': unittest.main()
