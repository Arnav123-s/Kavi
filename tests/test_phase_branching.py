"""Branching interpreter fixtures; these are not a teaching dataset."""

import unittest

from kavi.composable_configurations import Work
from kavi.phase.model import PhaseConfiguration
from kavi.phase.runtime import PhaseActivity


class BranchingTests(unittest.TestCase):
    def activity(self, work=None):
        circuit = PhaseConfiguration(
            (2, 3), (('a', 0, 1), ('b', 0, 0)),
            ((0, 1, 1, 1),), (((1, 1), 7), ((1, 2), 8)))
        activity = PhaseActivity(circuit, work or Work())
        activity.accept('a')
        return activity

    def test_questions_share_situation_without_changing_parent(self):
        parent = self.activity()
        first, second = parent.fork(), parent.fork()
        self.assertIsNone(first.accept('b'))
        self.assertEqual(first.finish(), 8)
        self.assertEqual(second.finish(), 7)
        self.assertEqual(parent.phases, (1, 1))
        self.assertFalse(parent.closed)
        self.assertEqual(parent.finish(), 7)

    def test_branch_matches_replay_for_all_short_suffixes(self):
        from itertools import product
        for length in range(5):
            for suffix in product('ab', repeat=length):
                parent = self.activity()
                child = parent.fork()
                for event in suffix:
                    child.accept(event)
                self.assertEqual(child.finish(),
                                 parent.configuration.predict(('a',)+suffix, Work()))

    def test_failure_is_isolated_and_cannot_be_branched(self):
        parent = self.activity()
        child = parent.fork()
        child.accept('unknown')
        with self.assertRaises(ValueError):
            child.fork()
        self.assertIsNone(child.finish())
        self.assertEqual(parent.fork().finish(), 7)
        parent.finish()
        with self.assertRaises(ValueError):
            parent.fork()

    def test_no_history_or_parent_and_no_new_budget(self):
        parent = self.activity()
        child = parent.fork()
        self.assertEqual(set(vars(child)),
                         {'configuration', 'work', 'phases', 'closed', 'failed'})
        self.assertIs(child.work, parent.work)
        self.assertIs(child.configuration, parent.configuration)
        self.assertEqual(parent.work.counts['phase_branch_coordinates'], 2)
        parent.work.limit = sum(parent.work.counts.values())
        before = parent.phases
        with self.assertRaises(InterruptedError):
            parent.fork()
        self.assertEqual(parent.phases, before)
        self.assertFalse(parent.failed)
        with self.assertRaises(InterruptedError):
            child.accept('b')
        self.assertIsNone(child.finish())


if __name__ == '__main__':
    unittest.main()
