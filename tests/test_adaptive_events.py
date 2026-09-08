"""Provisional-structure and conditional preservation checks."""

import unittest

from kavi.adaptive_events import AdaptiveActivity
from kavi.composable_configurations import Work
from kavi.event_learning import EventConfiguration


class AdaptiveTests(unittest.TestCase):
    def test_missing_connection_can_be_proposed_without_changing_parent(self):
        graph = EventConfiguration([{'a':1}, {'end':1}], [None, 0])
        activity = AdaptiveActivity(graph, Work())
        activity.feed('b')
        with self.assertRaises(ValueError):
            activity.proposals()
        activity.feed('end')
        activity.close()
        chosen = next(candidate for candidate, label in activity.proposals() if label == 0)
        successor = activity.commit(chosen, graph)
        self.assertNotIn('b', graph.transitions[0])
        self.assertEqual(successor.predict(('b', 'end'), Work()), 0)
        for size in range(20):
            old = ('a',)+('end',)*size
            self.assertEqual(successor.predict(old, Work()), graph.predict(old, Work()))

    def test_known_execution_does_not_branch_or_override_an_old_answer(self):
        graph = EventConfiguration([{'a':0}], [1])
        activity = AdaptiveActivity(graph, Work())
        for _ in range(40):
            activity.feed('a')
        activity.close()
        self.assertEqual(activity.maximum_active, 1)
        self.assertEqual(activity.proposals()[0][1], 1)
        self.assertEqual(activity.proposals()[0][0].links, ())
        with self.assertRaises(ValueError):
            activity.feed('b')

    def test_changed_parent_invalidates_candidate(self):
        graph = EventConfiguration([{}], [0])
        activity = AdaptiveActivity(graph, Work())
        activity.feed('a')
        activity.close()
        with self.assertRaises(ValueError):
            activity.commit(activity.proposals()[0][0], EventConfiguration([{'b':0}], [0]))
