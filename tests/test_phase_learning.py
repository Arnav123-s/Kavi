"""Algorithm fixtures only; no fixture is admitted as a curriculum result."""

import json
import unittest
from kavi.composable_configurations import Work
from kavi.phase import PhaseConfiguration
from kavi.phase.encoding import text_events, gray_events
from kavi.phase.learning import teach


class PhaseLearningTests(unittest.TestCase):
    def test_acquires_recurrent_impulse_and_generalizes_fixture_lengths(self):
        original = PhaseConfiguration((2,), (('x', 0, 0),))
        model, result = teach(original, [('x', 1), ('xx', 0)], [], Work())
        self.assertTrue(result['accepted'])
        self.assertEqual(result['errors'], 0)
        for length in range(3, 100):
            self.assertEqual(model.predict('x'*length, Work()), length % 2)
        self.assertEqual(original.outputs, ())
        self.assertEqual(PhaseConfiguration.from_record(json.loads(json.dumps(model.record()))), model)

    def test_conflicting_correction_does_not_destroy_protection(self):
        model = PhaseConfiguration((2,), (('x', 0, 1),), outputs=(((1,), 1),))
        successor, result = teach(model, [('x', 0)], [('x', 1)], Work())
        self.assertEqual(successor, model)
        self.assertFalse(result['accepted'])

    def test_encoding_distinguishes_modalities_and_unicode(self):
        self.assertNotEqual(list(text_events('a')), list(text_events('α')))
        self.assertNotEqual(list(text_events('A')), list(text_events('a')))
        self.assertTrue(set(text_events('12')).isdisjoint(gray_events(2, 1, [1, 2])))
        with self.assertRaises(ValueError):
            list(gray_events(1, 1, [256]))
        with self.assertRaises(ValueError):
            list(gray_events(1, 2, [0]))
        with self.assertRaises(ValueError):
            list(gray_events(1, 1, [0, 1]))

    def test_interrupt_discards_partial_successor(self):
        model = PhaseConfiguration((2,), (('x', 0, 0),))
        with self.assertRaises(InterruptedError):
            teach(model, [('x', 1)], [], Work(limit=1))
        self.assertEqual(model.outputs, ())


if __name__ == '__main__':
    unittest.main()
