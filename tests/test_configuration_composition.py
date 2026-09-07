import json
from pathlib import Path
import unittest

from kavi.configuration_composition import (ArithmeticBridge, GraphCatalog, ProgramGraph,
    candidate_graphs, fit_bridge, fit_graph)
from kavi.procedure_core import Limits, ProcedureLibrary
from kavi.recurrent_configuration import Configuration

ROOT = Path(__file__).resolve().parents[1]


class CompositionTests(unittest.TestCase):
    def setUp(self):
        self.library = ProcedureLibrary.load(ROOT / 'experiments/library-20260907-compiled.json')
        self.controller = Configuration(('a',), ((1,), (0,)), (0, 1))

    def test_uncertain_feedback_does_not_choose_arbitrary_route(self):
        examples = [((), (2, 2), 4), (('a',), (2, 2), 4)]
        bridge, _ = fit_bridge(self.controller, examples, self.library)
        self.assertEqual(bridge.answer((), (2, 3), self.library)['state'], 'ambiguous')
        bridge, _ = fit_bridge(self.controller, examples + [((), (2, 3), 5), (('a',), (2, 3), 6)], self.library)
        loaded = ArithmeticBridge.decode(bridge.encoded())
        self.assertEqual(loaded.answer(('a',) * 101, (4, 7), self.library)['value'], 28)
        self.assertEqual(loaded.answer(('a',) * 100, (4, 7), self.library)['value'], 11)
        self.assertEqual(loaded.answer(('unknown',), (4, 7), self.library)['state'], 'unresolved')
        self.assertNotIn('examples', json.loads(bridge.encoded()))

    def test_new_shared_computation_is_selected_from_numerical_examples(self):
        graph, stats = fit_graph([((2, 3), 25), ((1, 4), 25), ((0, 3), 9), ((4, 2), 36)], self.library)
        self.assertEqual(stats['candidates'], 338)
        self.assertEqual(len(list(candidate_graphs())), 338)
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(graph.nodes[1][1:], (2, 2))
        result = graph.execute((17, 19), self.library)
        first = self.library.execute('add', (17, 19))
        second = self.library.execute('multiply', (36, 36))
        self.assertEqual(result.value, 1296)
        self.assertEqual(result.calls, first.calls + second.calls)
        with self.assertRaisesRegex(ValueError, 'budget'):
            graph.execute((17, 19), self.library, limits=Limits(max_calls=1))

    def test_supervised_merge_is_immutable_and_preserves_dependencies(self):
        catalog = GraphCatalog(self.library.digest)
        graph = ProgramGraph((('add', 0, 1), ('multiply', 2, 2)), 3)
        with self.assertRaisesRegex(ValueError, 'promotion'):
            catalog.admit('novel', graph, [((2, 3), 24)], self.library)
        self.assertEqual(catalog.entries, ())
        merged, _ = catalog.admit('novel', graph, [((2, 3), 25)], self.library)
        loaded = GraphCatalog.decode(merged.encoded())
        self.assertEqual(loaded.execute('novel', (7, 5), self.library).value, 144)
        self.assertEqual(loaded.execute('add', (7, 5), self.library).value, 12)
        with self.assertRaisesRegex(ValueError, 'replace'):
            merged.admit('add', graph, [((2, 3), 25)], self.library)
        with self.assertRaisesRegex(ValueError, 'changed'):
            merged.execute('novel', (7, 5), ProcedureLibrary())

    def test_cycles_and_unbounded_inputs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'earlier'):
            ProgramGraph((('add', 0, 2),), 2)
        with self.assertRaises(ValueError):
            ProgramGraph((), 0).execute((-1, 3), self.library)
        def stop():
            raise InterruptedError('stop')
        with self.assertRaises(InterruptedError):
            fit_graph([((2, 3), 25)], self.library, check=stop)


if __name__ == '__main__':
    unittest.main()
