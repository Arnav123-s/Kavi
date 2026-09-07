"""Known routes avoid search; contradictions trigger bounded repair."""

from pathlib import Path
import unittest
from unittest.mock import patch

from kavi.experience_router import ExperienceRouter
from kavi.procedure_core import ProcedureLibrary
from kavi.procedure_search import ProgramExample
from kavi.route_memory import RouteMemory


class RouteMemoryTests(unittest.TestCase):
    def memory(self):
        root=Path(__file__).resolve().parents[1]
        library=ProcedureLibrary.load(root/'experiments/library-20260907-compiled.json')
        key=(1,-1,-1,2,0,0)
        router=ExperienceRouter.fit([(key,('add','multiply','square'))])
        return RouteMemory(library,router),key

    def test_valid_primary_route_never_searches(self):
        memory,key=self.memory()
        memory.routes=[{'features':list(key),'arity':1,'body':('call','square',('arg',0))}]
        with patch('kavi.route_memory.ProgramSearch.learn',side_effect=AssertionError('Unexpected search')):
            observed=memory.acquire(key,1,[ProgramExample((7,),49),ProgramExample((11,),121)])
        self.assertTrue(observed['reused'])
        self.assertEqual(observed['attempts'],[])
        self.assertEqual(observed['route_checks'],2)

    def test_correction_rejects_identity_and_preserves_stored_route(self):
        memory,key=self.memory()
        memory.routes=[{'features':list(key),'arity':1,'body':('arg',0)}]
        observed=memory.acquire(key,1,[ProgramExample((0,),0),ProgramExample((1,),1),ProgramExample((2,),8)])
        self.assertFalse(observed['reused'])
        self.assertEqual(memory.library.execute_expr(observed['body'],(9,)).value,729)
        self.assertEqual(memory.routes[0]['body'],('arg',0))
        self.assertEqual(len(memory.routes),2)


if __name__=='__main__': unittest.main()
