"""Interpreter and annotation regressions; these fixtures do not teach a model."""

import json
from pathlib import Path
import unittest

from kavi.composable_configurations import Work
from kavi.english_configurations import ConnectionTree,Input,OPS,numeric
from kavi.published_english import (
    PredicateTree,RelevanceReasoner,bind_expression,formula_tree,project,
)
from kavi.published_learning import load_science

ROOT=Path(__file__).resolve().parents[1]


class PublishedEnglishTests(unittest.TestCase):
    def setUp(self):
        self.registry=load_science(ROOT/'experiments/science-20260907-published-model.json',
            ROOT/'experiments/library-20260907-compiled.json',extended=True).registry

    def test_linear_annotation_retains_variable_inputs(self):
        expression,linear=formula_tree('x:unknown;2x-12=20')
        inp=Input('',[],[0,1,2],[2.,12.,20.],[])
        ids,program,_=bind_expression(inp,expression)
        self.assertTrue(linear)
        self.assertEqual(numeric(program,project(inp,ids).numbers),16)
        changed=Input('',[],[0,1,2],[4.,12.,20.],[])
        self.assertEqual(numeric(program,project(changed,ids).numbers),8)

    def test_annotation_identifies_unused_quantity(self):
        expression,_=formula_tree('8+10=18')
        inp=Input('',[],[0,1,2],[5.,8.,10.],[])
        ids,program,_=bind_expression(inp,expression)
        self.assertEqual(ids,[1,2])
        self.assertEqual(numeric(program,project(inp,ids).numbers),18)

    def test_nonlinear_and_unknown_literals_rejected(self):
        with self.assertRaises(ValueError):formula_tree('x*x=25')
        with self.assertRaises(ValueError):
            bind_expression(Input('',[],[0,1],[2.,3.],[]),('+',('c',2),('c',17)))

    def reasoner(self,ambiguous=False):
        return RelevanceReasoner(PredicateTree(nodes=[{'ports':['keep']}]),
            ConnectionTree([{'ports':list(OPS)}]),
            PredicateTree(labels=('sum','difference'),nodes=[{'ports':['sum','difference'] if ambiguous else ['sum']}]),
            {'sum':{'arity':2,'program':['+',0,1]},'difference':{'arity':2,'program':['-',0,1]}})

    def test_existing_program_avoids_candidate_construction(self):
        reasoner=self.reasoner()
        before=json.dumps(reasoner.record(),sort_keys=True)
        work=Work()
        result=reasoner.answer('2 3',self.registry,work)
        self.assertEqual(result['value'],5)
        self.assertEqual(work.counts['reused_program_answers'],1)
        self.assertNotIn('candidate_configurations',work.counts)
        self.assertEqual(json.dumps(reasoner.record(),sort_keys=True),before)

    def test_unresolved_route_uses_existing_operations(self):
        work=Work()
        result=self.reasoner(ambiguous=True).answer('2 3',self.registry,work)
        self.assertEqual(result['value'],5)
        self.assertEqual(work.counts['composition_searches'],1)
        self.assertGreater(work.counts['candidate_configurations'],0)

    def test_work_budget_remains_interruptible(self):
        with self.assertRaises(InterruptedError):
            self.reasoner().answer('2 3',self.registry,Work(limit=1))


if __name__=='__main__':unittest.main()
