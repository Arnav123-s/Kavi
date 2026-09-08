"""Interface, non-leakage and feedback-state regressions; no source teaching."""

import json
from pathlib import Path
import unittest

from kavi.composable_configurations import Work
from kavi.english_configurations import ConnectionTree, OPS
from kavi.learned_inquiry import InquiryModel, relations
from kavi.published_english import PredicateTree
from kavi.published_learning import load_science

ROOT = Path(__file__).resolve().parents[1]


class InquiryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_science(ROOT/'experiments/science-20260907-published-model.json',
            ROOT/'experiments/library-20260907-compiled.json', extended=True).registry

    def model(self, ask=True):
        return InquiryModel(ConnectionTree([{'ports':list(OPS)}]),
            PredicateTree(('answer', 'ask'), [{'ports':['ask' if ask else 'answer']}]))

    def test_question_has_no_correct_answer_and_blocks_release(self):
        model = self.model()
        turn = model.begin('Two groups hold three books each.', Work())
        question = turn.ask(Work())
        self.assertEqual(question['pair'], [0, 1])
        self.assertNotIn('answer', question)
        self.assertNotIn('expected', question)
        self.assertEqual(question, turn.ask(Work()))
        with self.assertRaises(ValueError):
            turn.answer(self.registry, Work())

    def test_requested_relation_changes_only_current_computation(self):
        model = self.model()
        before = json.dumps(model.record(), sort_keys=True)
        turn = model.begin('Two groups hold three books each.', Work())
        self.assertEqual(turn.best.value, 5)
        turn.ask(Work())
        turn.clarify('*', Work())
        self.assertEqual(turn.answer(self.registry, Work())['value'], 6)
        self.assertIsNone(turn.ask(Work()))
        self.assertEqual(before, json.dumps(model.record(), sort_keys=True))
        fresh = model.begin('Two groups hold three books each.', Work())
        self.assertEqual(fresh.best.value, 5)
        self.assertFalse(fresh.replies)

    def test_no_unrequested_or_malformed_feedback(self):
        turn = self.model().begin('Two groups hold three books each.', Work())
        with self.assertRaises(ValueError):
            turn.clarify('*', Work())
        turn.ask(Work())
        with self.assertRaises(ValueError):
            turn.clarify('the answer is six', Work())
        self.assertFalse(turn.replies)
        self.assertIsNotNone(turn.pending)

    def test_pair_relation_refers_to_branch_join_and_orientation(self):
        self.assertEqual(relations(('-', 2, ('+', 0, 1))),
            {(0, 1):'+', (0, 2):'r-', (1, 2):'r-'})

    def test_untrained_decision_does_not_invent_a_question(self):
        model = InquiryModel(ConnectionTree([{'ports':list(OPS)}]))
        turn = model.begin('Two groups hold three books each.', Work())
        self.assertIsNone(turn.ask(Work()))
        self.assertEqual(turn.answer(self.registry, Work())['value'], 5)
        self.assertTrue(turn.activity.complete)
        self.assertFalse(hasattr(turn.activity, 'text'))
        self.assertFalse(hasattr(turn.activity, 'words'))
