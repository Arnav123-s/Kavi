from pathlib import Path
import math
import unittest

from kavi.composable_configurations import (Configuration, Registry, Work, Unresolved,
    StaleConfiguration, agrees, candidates, differentiate, fit)
from kavi.equation_kernels import make_registry
from kavi.procedure_core import ProcedureLibrary

ROOT = Path(__file__).resolve().parents[1]


class HierarchyTests(unittest.TestCase):
    def setUp(self):
        self.registry = make_registry(ProcedureLibrary.load(ROOT / 'experiments/library-20260907-compiled.json'))

    def test_nested_definition_and_expansion_share_intermediate(self):
        r = self.registry
        r.install('square_sum', Configuration(2, (('add', (0, 1)), ('multiply', (2, 2))), 3))
        r.install('nested', Configuration(3, (('square_sum', (0, 1)), ('add', (3, 2))), 4))
        plan = r.expand('nested', Work())
        work = Work()
        self.assertEqual(plan.execute((4, 5, 7), r, work), 88)
        self.assertEqual(work.counts['kernel_add'], 2)
        self.assertEqual(work.counts['kernel_multiply'], 1)
        self.assertEqual(r.execute('nested', (4, 5, 7), Work()), 88)
        self.assertEqual(Configuration.decode(r.definitions['nested'].record()), r.definitions['nested'])

    def test_unknown_component_and_local_learning(self):
        r = self.registry
        r.install('outer', Configuration(4, (('add', (0, 1)), ('missing', (4, 2)), ('add', (5, 3))), 6))
        with self.assertRaises(Unresolved):
            r.execute('outer', (1, 2, 3, 4), Work())
        examples = [((1, 1, 3, 2), 27), ((1, 2, 4, 1), 50), ((0, 2, 1, 3), 12)]
        works = [Work(), Work()]
        graphs = [fit(r, 'missing', examples, ('add', 'subtract', 'multiply'), w,
                      outer='outer', local=local) for w, local in zip(works, (False, True))]
        self.assertEqual(graphs[0], graphs[1])
        self.assertIsNotNone(graphs[0])
        self.assertEqual(works[0].counts['candidate_proposals'], 338)
        self.assertLess(works[1].counts['kernel_add'], works[0].counts['kernel_add'])
        r.install('missing', graphs[1])
        self.assertEqual(r.execute('outer', (7, 8, 9, 4), Work()), 580)

    def test_correction_invalidates_dependent_but_not_unrelated_expansion(self):
        r = self.registry
        r.install('rule', Configuration(2, (('add', (0, 1)),), 2))
        r.install('outer', Configuration(2, (('rule', (0, 1)),), 2))
        stale = r.expand('outer', Work())
        unrelated = r.expand('multiply', Work())
        repaired = fit(r, 'rule', [((2, 3), 6), ((3, 4), 12), ((1, 5), 5)],
                       ('add', 'subtract', 'multiply'), Work())
        r.install('rule', repaired)
        with self.assertRaises(StaleConfiguration):
            stale.execute((11, 13), r, Work())
        self.assertEqual(stale.execute((11, 13), r, Work(), verify=False), 24)
        self.assertEqual(r.expand('outer', Work()).execute((11, 13), r, Work()), 143)
        self.assertEqual(unrelated.execute((11, 13), r, Work()), 143)

    def test_differentiation_produces_an_executable_configuration(self):
        r = self.registry
        r.install('f', Configuration(2, (('add', (0, 1)), ('multiply', (2, 2))), 3))
        r.install('df', differentiate(r, 'f', 0, Work()))
        for x, y in ((0, 0), (3, 7), (101, 39)):
            self.assertEqual(r.execute('df', (x, y), Work()), 2*(x+y))

    def test_physical_kernels_compose_and_preserve_invariants(self):
        r = self.registry
        for kernel, state in (('heat', (1., 4., 7.)), ('schrodinger', (1+0j, 0j))):
            r.install('twice', Configuration(2, ((kernel, (0, 1)), (kernel, (2, 1))), 3))
            r.install('combined', Configuration(2, (('real_add', (1, 1)), (kernel, (0, 2))), 3))
            for t in (0, .1, .7, 3):
                self.assertTrue(agrees(r.execute('twice', (state, t), Work()),
                                       r.execute('combined', (state, t), Work())))
        out = r.execute('heat', ((0., 0., 9.), .3), Work())
        self.assertAlmostEqual(sum(out), 9)
        self.assertGreater(out[0], 0)
        a = 1/math.sqrt(2)
        destructive = r.execute('schrodinger', ((a, 1j*a), math.pi/4), Work())
        constructive = r.execute('schrodinger', ((a, -1j*a), math.pi/4), Work())
        self.assertAlmostEqual(abs(destructive[1])**2, 0)
        self.assertAlmostEqual(abs(constructive[1])**2, 1)

    def test_limits_and_invalid_interfaces_are_enforced(self):
        r = self.registry
        with self.assertRaises(ValueError):
            Configuration(2, (('add', (0, 2)),), 2)
        r.install('cycle', Configuration(1, (('cycle', (0,)),), 1))
        with self.assertRaises(ValueError):
            r.expand('cycle', Work())
        with self.assertRaises(InterruptedError):
            fit(r, 'x', [((2, 3), 6)], ('add',), Work(limit=1))
        with self.assertRaises(ValueError):
            r.execute('heat', ((0, 1, 2), -.1), Work())


if __name__ == '__main__':
    unittest.main()
