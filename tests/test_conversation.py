"""Engineering regressions, not teaching data or a language benchmark."""

import unittest
from fractions import Fraction
from pathlib import Path

from kavi.composable_configurations import Configuration,Work
from kavi.equation_kernels import make_registry
from kavi.procedure_core import ProcedureLibrary
from kavi.conversation import Arithmetic,parse_science
from kavi.source_curation import BodyParagraphs,curate_html
from kavi.passage_answering import PassageAnswerer
from kavi.inequality_pathway import answer


ROOT=Path(__file__).resolve().parents[1]


class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.registry=make_registry(ProcedureLibrary.load(ROOT/'experiments/library-20260907-compiled.json'))
        self.arithmetic=Arithmetic(self.registry)

    def test_arithmetic_acquired_programs_and_exact_fraction(self):
        w=Work()
        self.assertEqual(self.arithmetic.answer('(17+19)*(17+19)',w),1296)
        self.assertGreater(w.counts.get('arithmetic_gates',0),0)
        self.assertEqual(self.arithmetic.answer('1/3+1/6',Work()),Fraction(1,2))
        self.assertEqual(self.arithmetic.answer('what is two plus two?',Work()),4)

    def test_untrusted_expression_and_expensive_input(self):
        self.assertIsNone(self.arithmetic.answer('__import__("os").getcwd()',Work()))
        with self.assertRaises(ValueError): self.arithmetic.answer('2**1000000',Work())
        with self.assertRaises(ZeroDivisionError): self.arithmetic.answer('1/0',Work())
        with self.assertRaises(InterruptedError): self.arithmetic.answer('123+456',Work(limit=1))

    def test_quantities_units_and_bad_domains(self):
        values,target=parse_science('Kinetic energy for mass 800 g and speed 36 km/h')
        self.assertEqual(target,'kinetic_energy')
        self.assertEqual(values['mass'],.8)
        self.assertEqual(values['speed'],10)
        with self.assertRaises(ValueError): parse_science('kinetic energy mass 2 lb speed 3 m/s')
        with self.assertRaises(ValueError): parse_science('kinetic energy mass -2 kg speed 3 m/s')
        self.assertIsNone(parse_science('What is energy?'))

    def test_html_active_content_and_utf8(self):
        parser=BodyParagraphs()
        parser.feed('<nav><p>Navigation is not expository source knowledge and should be omitted.</p></nav><h2>Definition</h2><p>A real source sentence can contain a line<br/>break and remain valid text.</p><script>execute()</script>')
        parser.flush()
        self.assertEqual(len(parser.rows),1)
        self.assertIn('line break',parser.rows[0]['text'])
        self.assertNotIn('execute',str(parser.rows))
        rows=curate_html('<h2>Definition</h2><p>Text preserves the source’s original punctuation without corruption.</p>'.encode(),{'id':'nhgri-test','url':'https://example.org'})
        self.assertIn('source’s',rows[0]['text'])

    def test_retrieval_prefers_definition_and_abstains(self):
        records=[{'id':'one','title':'Alpha','passages':[{'heading':'Definition','text':'Alpha is the object described by this source definition.'},
                  {'heading':'Narration','text':'Is Alpha an amazing thing?'}]},
                 {'id':'two','title':'Beta','passages':[{'heading':'Definition','text':'Beta is a different object that sometimes mentions Alpha in passing.'}]}]
        search=PassageAnswerer(records)
        hit=search.search('What is Alpha?')[0]
        self.assertEqual(hit['source']['id'],'one')
        self.assertFalse(search.search('Unrelated zymurgy'))

    def test_inequality_requires_all_supplied_premises(self):
        self.registry.install('radius_bound',Configuration(3,output=0))
        with self.assertRaises(ValueError): answer(self.registry,35,23,2/3,Work(),positive_friction=False,starts_at_rest=True,crest=True)
        with self.assertRaises(ValueError): answer(self.registry,35,23,1,Work(),positive_friction=True,starts_at_rest=True,crest=True)


if __name__=='__main__': unittest.main()
