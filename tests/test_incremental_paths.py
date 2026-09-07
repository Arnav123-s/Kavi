"""Incremental ambiguity, shared continuation and original token identity."""

import unittest
from kavi.grounded_language import LanguageModel
from kavi.incremental_paths import IncrementalPaths
from scripts.run_incremental_paths import lessons,trace


class IncrementalPathTests(unittest.TestCase):
    def setUp(self):
        self.language=LanguageModel()
        self.language.teach(lessons())
        self.graph=IncrementalPaths(self.language.rules)

    def test_prefix_stays_open_and_unlabelled_continuation_resolves(self):
        state=self.graph.feed('a')
        self.assertEqual(state['possible_roles'],['add','description','notation_mapping'])
        self.assertEqual(state['complete'],[])
        row=trace(self.graph,'a equals 12 plus 13')
        self.assertEqual(row['final']['complete'],[{'kind':'calculation','label':'add','inputs':[12,13]}])
        self.assertEqual(row['states'][1]['possible_roles'],['add','description'])
        # The unrestricted text slot can stay viable until end-of-input.
        self.assertEqual(trace(self.graph,'a fox is alert')['final']['complete'],
                         [self.language.interpret('a fox is alert')['meaning']])

    def test_symbol_variants_share_math_states_without_erasing_form(self):
        a=trace(self.graph,'a equals 12 plus 13')
        alpha=trace(self.graph,'α equals 12 plus 13')
        self.assertEqual(a['final']['complete'],alpha['final']['complete'])
        self.assertNotEqual(a['final']['original_tokens'],alpha['final']['original_tokens'])
        self.assertTrue(set(a['states'][1]['active_nodes']) & set(alpha['states'][1]['active_nodes']))
        self.assertEqual(trace(self.graph,'alpha fox is alert')['final']['state'],'unsupported')

    def test_no_new_path_is_invented_by_inference(self):
        before=self.graph.encoded()
        self.assertEqual(trace(self.graph,'a multiplies 12 by 13')['final']['state'],'unsupported')
        self.assertEqual(before,self.graph.encoded())


if __name__=='__main__': unittest.main()
