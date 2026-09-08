"""Finite-state and coupled-runtime checks, not a language teaching corpus."""

from pathlib import Path
import unittest

from kavi.composable_configurations import Work
from kavi.event_learning import EventConfiguration, learn
from kavi.event_english import EventEnglish, events
from kavi.published_learning import load_science
from kavi.recurrent_configuration import learn as dense_learn

ROOT = Path(__file__).resolve().parents[1]


class EventTests(unittest.TestCase):
    def test_sparse_learning_preserves_constraints_and_matches_old_learner(self):
        examples = [((), 0), (('a',), 1), (('a', 'a'), 0), (('a', 'a', 'a'), 1)]
        sparse, _ = learn(examples, Work())
        dense, _ = dense_learn(examples)
        for length in range(20):
            self.assertEqual(sparse.predict(('a',)*length, Work()), dense.predict(('a',)*length))
        self.assertLess(len(sparse.outputs), 5)

    def test_contradiction_is_not_silently_removed(self):
        with self.assertRaises(ValueError):
            learn([(('a',), 0), (('a',), 1)], Work())

    def test_signal_execution_holds_input_and_respects_event_order(self):
        text = 'Two groups have three books.'
        vocabulary = {'group', 'have', 'book'}
        tokens = [token for token, _ in events(text, vocabulary)]
        graph = EventConfiguration([{token:i+1} for i, token in enumerate(tokens)]+[{}],
            [None]*len(tokens)+[3])
        model = EventEnglish(graph, vocabulary)
        registry = load_science(ROOT/'experiments/science-20260907-published-model.json',
            ROOT/'experiments/library-20260907-compiled.json', extended=True).registry
        observed = []
        answer = model.answer(text, registry, Work(), observed.append)
        self.assertEqual(answer['value'], 6)
        self.assertEqual(answer['live_values'], 4)
        self.assertFalse(any(row['released'] for row in observed))
        self.assertEqual(model.answer('Three books have two groups.', registry, Work())['state'], 'unresolved')
        self.assertEqual(EventEnglish.from_record(model.record()).record(), model.record())
