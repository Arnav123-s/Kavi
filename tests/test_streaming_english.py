"""Current-activity and execution regressions; these checks perform no teaching."""

import itertools
import json
from pathlib import Path
import unittest

from kavi.composable_configurations import Work
from kavi.english_configurations import EnglishReasoner,WORD,features,read_input
from kavi.published_learning import load_science
from kavi.streaming_english import StreamingEnglishReasoner

ROOT=Path(__file__).resolve().parents[1]


class StreamingEnglishTests(unittest.TestCase):
    def setUp(self):
        self.path=ROOT/'experiments/english-20260907-initial-model.json'
        self.model=StreamingEnglishReasoner.load(self.path)

    def test_feature_activity_matches_batch_predicates(self):
        for text in ('There are 8 red books and 3 blue books. How many books are there?',
                     'What is shared? Two groups have five books. How many remain from nine?',
                     'A has 10.25 and B has 10.25. Calculate the total.'):
            state=self.model.begin(Work())
            for token in WORD.findall(text):state.consume(token)
            expected=read_input(text)
            for i,j in itertools.combinations(range(len(state.numbers)),2):
                self.assertEqual(state.features(i,j),features(expected,i,j)&self.model.vocabulary)
            self.assertFalse(hasattr(state,'text'))
            self.assertFalse(hasattr(state,'words'))
            self.assertLessEqual(len(state.recent),5)

    def test_completion_rejects_more_input(self):
        state=self.model.begin(Work());state.consume('two');state.close()
        with self.assertRaises(ValueError):state.consume('three')

    def test_streaming_answer_preserves_the_original_calculation(self):
        registry=load_science(ROOT/'experiments/science-20260907-published-model.json',
            ROOT/'experiments/library-20260907-compiled.json',extended=True).registry
        original=EnglishReasoner.load(self.path)
        before=json.dumps(self.model.record(),sort_keys=True)
        events=[]
        for text in ('There are 8 red books and 3 blue books. How many books are there?',
                     'Two groups have five books. How many books are there?'):
            first=original.answer(text,registry,Work())
            second=self.model.answer(text,registry,Work(),observe=events.append)
            self.assertEqual(first['program'],second['program'])
            self.assertEqual(first['value'],second['value'])
            self.assertTrue(second['input_activity']['input_complete'])
            self.assertTrue(second['signal_activity']['output_available'])
        self.assertTrue(events)
        self.assertTrue(all(not e['answer_released'] for e in events))
        self.assertEqual(before,json.dumps(self.model.record(),sort_keys=True))
