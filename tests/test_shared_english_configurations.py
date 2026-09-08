"""Preservation checks on the acquired English artifact; no new teaching."""

import json
from pathlib import Path
import unittest

from kavi.composable_configurations import Work,encoded
from kavi.shared_english_configurations import (
    SharedEnglishReasoner,share_configuration,verify_representation,
)
from kavi.published_english import RelevanceReasoner
from kavi.published_learning import load_science

ROOT=Path(__file__).resolve().parents[1]


class SharedEnglishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((ROOT/'experiments/english-20260907-expanded-model.json').read_text())
        cls.shared=share_configuration(cls.original,Work())

    def test_every_acquired_predicate_and_program_is_preserved(self):
        self.assertTrue(verify_representation(self.original,self.shared,Work()))
        self.assertEqual(len(self.shared['programs']),588)

    def test_sharing_reduces_same_format_nodes_and_bytes(self):
        unshared=share_configuration(self.original,Work(),share=False)
        self.assertLess(len(self.shared['nodes']),len(unshared['nodes']))
        self.assertLess(len(self.shared['program_nodes']),len(unshared['program_nodes']))
        self.assertLess(len(encoded(self.shared)),len(encoded(unshared)))

    def test_changed_operator_fails_full_preservation_check(self):
        damaged=json.loads(json.dumps(self.shared))
        call=next(n for n in damaged['program_nodes'] if n[0]=='call')
        call[1]='-' if call[1]=='+' else '+'
        self.assertFalse(verify_representation(self.original,damaged,Work()))

    def test_cyclic_shared_definition_is_rejected(self):
        damaged=json.loads(json.dumps(self.shared))
        index=next(i for i,n in enumerate(damaged['nodes']) if n[0]=='branch')
        damaged['nodes'][index][2]=index
        with self.assertRaises(ValueError):SharedEnglishReasoner(damaged)

    def test_compact_runtime_matches_acquired_answers_and_search_work(self):
        original=RelevanceReasoner.load(ROOT/'experiments/english-20260907-expanded-model.json')
        shared=SharedEnglishReasoner(self.shared)
        registry=load_science(ROOT/'experiments/science-20260907-published-model.json',
            ROOT/'experiments/library-20260907-compiled.json',extended=True).registry
        for text in ('2 3','5 8 13','1 2 3 4'):
            a,b=Work(),Work()
            old=original.answer(text,registry,a)
            new=shared.answer(text,registry,b)
            self.assertEqual(old['value'],new['value'])
            self.assertEqual(old['program'],new['program'])
            self.assertEqual(a.counts,b.counts)


if __name__=='__main__':unittest.main()
