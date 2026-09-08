"""Learned-boundary and transactional replacement fixtures; not curriculum."""

from itertools import product
import unittest
from kavi.composable_configurations import Work
from kavi.phase.habitat import Habitat,WorldGeneration,infer_habitat,teach_world
from kavi.phase.layers import CircuitTemplate,CircuitGeneration
from kavi.phase.model import PhaseConfiguration


class HabitatTests(unittest.TestCase):
    def base(self):
        return WorldGeneration(Habitat(),CircuitGeneration(CircuitTemplate((2,),max_couplings=0),
                               PhaseConfiguration((2,),(('x',0,1),))))

    def test_roles_inferred_without_semantic_labels_and_language_exact(self):
        words=[(a,op,b) for a,b in product(('t','f'),repeat=2) for op in ('u','v')]
        h=infer_habitat(words,Work())
        self.assertEqual(set(h.roles),{('f','t'),('u','v')})
        self.assertEqual(set(h.language(Work())),set(words))
        self.assertFalse(h.accepts(('u','t','f'),Work()))

    def test_context_refinement_does_not_overgeneralize(self):
        words=[('a','a'),('a','b'),('b','a')]
        h=infer_habitat(words,Work())
        self.assertFalse(h.accepts(('b','b'),Work()))
        self.assertEqual(set(h.language(Work())),set(words))

    def test_new_context_can_split_an_old_role_without_erasing_boundary(self):
        old=infer_habitat([('a',),('b',)],Work())
        new=infer_habitat([*old.language(Work()),('a','c')],Work())
        self.assertEqual(old.roles,(('a','b'),))
        self.assertEqual(len(new.roles),3)
        for word in old.language(Work()):self.assertTrue(new.accepts(word,Work()))

    def test_successor_replays_old_shape_without_retaining_lessons(self):
        old=self.base()
        first,s=teach_world(old,[(('x',),1)],Work(),candidates=8)
        self.assertTrue(s['accepted'])
        second,s=teach_world(first,[(('x','x'),0)],Work(),candidates=8)
        self.assertTrue(s['accepted'])
        self.assertEqual(s['protected_cases'],1)
        self.assertEqual(second.predict(('x',),Work()),1)
        self.assertEqual(second.predict(('x','x'),Work()),0)
        self.assertEqual(old.habitat,Habitat())
        self.assertEqual(set(second.record()),{'habitat','inner'})

    def test_explicit_correction_not_falsely_protected(self):
        first,_=teach_world(self.base(),[(('x',),1)],Work(),candidates=8)
        changed,s=teach_world(first,[(('x',),0)],Work(),candidates=8)
        self.assertEqual(s['explicit_corrections'],1)
        self.assertEqual(changed.predict(('x',),Work()),0)

    def test_failed_replacement_and_interruption_leave_old_available(self):
        old=self.base()
        with self.assertRaises(InterruptedError):
            teach_world(old,[(('x',),1)],Work(limit=0))
        self.assertEqual(old.habitat,Habitat())
        with self.assertRaises(ValueError):
            teach_world(old,[(('x',),1),(('x',),0)],Work())
        # With one component and no coupling, xy and yx cannot differ.
        unchanged,s=teach_world(old,[(('x','y'),1),(('y','x'),0)],Work(),candidates=8)
        self.assertFalse(s['accepted']);self.assertIs(unchanged,old)

    def test_expansion_is_bounded_and_duplicate_symbols_rejected(self):
        h=Habitat((('a','b'),),((0,0),))
        with self.assertRaises(InterruptedError):tuple(h.language(Work(),limit=2))
        with self.assertRaises(ValueError):Habitat((('a',),('a',)),((0,),))

    def test_factorization_preserves_every_small_finite_language(self):
        words=[('a',),('b',),('a','a'),('a','b'),('b','a'),('b','b')]
        for mask in range(1<<len(words)):
            language={word for i,word in enumerate(words) if mask & (1<<i)}
            h=infer_habitat(language,Work())
            self.assertEqual(set(h.language(Work())),language)


if __name__=='__main__':unittest.main()
