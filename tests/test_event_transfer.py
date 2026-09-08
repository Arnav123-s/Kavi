"""Small implementation fixtures; these are not psychology teaching material."""

import unittest

from kavi.composable_configurations import Work, encoded
from kavi.event_learning import EventConfiguration
from kavi.event_transfer import ENTRY, graft, preserves
from kavi.text_choice_events import TextChoice, events


class TransferTests(unittest.TestCase):
    def test_reuses_old_loop_without_changing_any_old_defined_execution(self):
        base = EventConfiguration([{'x': 1}, {'x': 0}], [0, 1])
        original = encoded(base.record())
        examples = [(('x',)*length+('#',), 6+length % 2) for length in range(8)]
        transferred, embedding, stats = graft(base, examples, Work(limit=5_000_000))
        self.assertTrue(preserves(base, transferred, embedding, Work()))
        self.assertGreater(stats['old_state_merges'], 0)
        self.assertEqual(encoded(base.record()), original)
        for length in range(100):
            self.assertEqual(transferred.predict(('x',)*length, Work()), length % 2)
        for sequence, label in examples:
            self.assertEqual(transferred.predict((ENTRY,)+sequence, Work()), label)
        control, _, no_reuse = graft(base, examples, Work(), reuse=False)
        self.assertEqual(no_reuse['shared_reachable_states'], 0)
        for sequence, label in examples:
            self.assertEqual(control.predict((ENTRY,)+sequence, Work()), label)

    def test_bad_preservation_map_and_output_change_are_rejected(self):
        old = EventConfiguration([{'x': 0}], [0])
        self.assertFalse(preserves(old, EventConfiguration([{'x': 0}], [1]), [0], Work()))
        self.assertFalse(preserves(old, EventConfiguration([{}], [0]), [0], Work()))
        self.assertFalse(preserves(old, old, [], Work()))

    def test_correction_cannot_silently_drop_a_contradictory_lesson(self):
        old = EventConfiguration([{}], [None])
        with self.assertRaises(ValueError):
            graft(old, [(('x',), 6), (('x',), 7)], Work())
        with self.assertRaises(InterruptedError):
            graft(old, [(('x', 'y'), 7)], Work(limit=1))

    def test_all_options_must_finish_and_unknown_is_not_rejection(self):
        same = 'same'
        self.assertEqual(list(events(same, same, {'same'})),
                         ['same', '<option>', 'same', '<choice-end>'])
        old = EventConfiguration([{}], [None])
        choices = ['first', 'second', 'third', 'fourth']
        vocabulary = {'q', *choices}
        samples = [(tuple(events('q', option, vocabulary)), 7 if i == 2 else 6)
                   for i, option in enumerate(choices)]
        graph, embedding, _ = graft(old, samples, Work(), reuse=False)
        model = TextChoice(graph, vocabulary, embedding)
        self.assertEqual(model.answer('q', choices, Work())['answer'], 2)
        self.assertEqual(TextChoice.from_record(model.record()).record(), model.record())
        # Remove the gate: a supported prefix must not escape as a final answer.
        damaged = EventConfiguration([{key: value for key, value in row.items() if key != '<choice-end>'}
                                     for row in graph.transitions], list(graph.outputs))
        result = TextChoice(damaged, vocabulary, embedding).answer('q', choices, Work())
        self.assertIsNone(result['answer'])


if __name__ == '__main__':
    unittest.main()
