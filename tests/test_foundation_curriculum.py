"""Verify separation of teaching, correction and final examples."""

import unittest
import tempfile
from kavi.foundation_curriculum import LESSONS,banks,language_packet
from kavi.grounded_language import LanguageModel
from kavi.procedure_core import ProcedureLibrary,Procedure
from kavi.procedure_search import ProgramSearch,ProgramExample
from pathlib import Path


class FoundationProtocolTests(unittest.TestCase):
    def test_specific_sentence_rule_preserves_prior_interpretation(self):
        specific=[{'text':'the paper claims that '+claim,'source':'authored',
                   'target':{'kind':'relation','label':'reported_research_claim','slots':{'claim':claim}}}
                  for claim in ('search takes time','circuits can share work')]
        general=[{'text':speaker+' claims that '+claim,'source':'authored',
                  'target':{'kind':'relation','label':'attribution','slots':{'speaker':speaker,'claim':claim}}}
                 for speaker,claim in [('a narrator','the journey ended'),('a critic','an image repeats')]]
        model=LanguageModel(prefer_specific=True)
        model.teach(specific+general)
        self.assertEqual(model.interpret('the paper claims that storage has a cost')['meaning']['label'],'reported_research_claim')
        self.assertEqual(model.interpret('a witness claims that rain fell')['meaning']['label'],'attribution')
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'language.json'
            path.write_bytes(model.encoded())
            self.assertEqual(LanguageModel.load(path).encoded(),model.encoded())
        model.prefer_specific=False
        self.assertEqual(model.interpret('the paper claims that storage has a cost')['state'],'ambiguous')
    def test_explicit_call_only_search(self):
        source=ProcedureLibrary.load(Path(__file__).resolve().parents[1]/'experiments/library-20260907-compiled.json')
        lib=source.closure('multiply')
        search=ProgramSearch(lib,max_nodes=1,allowed_tags=('call',))
        body=search.learn(1,[ProgramExample((x,),x*x) for x in (0,1,2,3)])
        self.assertEqual(lib.execute_expr(body,(13,)).value,169)
        with self.assertRaises(ValueError):
            ProgramSearch(lib,allowed_tags=('arbitrary',)).learn(1,[ProgramExample((2,),4)])
        search=ProgramSearch(lib,max_nodes=1,allowed_tags=('call',),allowed_names=('multiply',))
        body=search.learn(1,[ProgramExample((x,),x*x) for x in (0,1,2,3)])
        self.assertEqual(lib.execute_expr(body,(19,)).value,361)
        with self.assertRaises(ValueError):
            ProgramSearch(lib,allowed_names=('missing',)).learn(1,[ProgramExample((2,),4)])
    def test_partitions_do_not_overlap(self):
        for seed in (17,41):
            for lesson in LESSONS:
                train,correction,final=banks(lesson,seed)
                self.assertFalse(set(train)&set(correction))
                self.assertFalse(set(train)&set(final))
                self.assertFalse(set(correction)&set(final))
                self.assertTrue(all(all(x>=6 for x in xs) for xs in final))

    def test_language_slots_generalize_without_final_teaching(self):
        teaching,final=language_packet()
        self.assertFalse({x['text'] for x in teaching}&{x['text'] for x in final})
        language=LanguageModel()
        language.teach(teaching)
        for case in final:
            self.assertEqual(language.interpret(case['text']).get('meaning'),case['target'])


if __name__=='__main__': unittest.main()
