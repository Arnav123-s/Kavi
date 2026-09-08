"""Structural-transfer regressions using small interface fixtures."""

import json
import unittest

from kavi.composable_configurations import Work
from kavi.english_configurations import ConnectionTree, OPS
from kavi.pathway_transfer import refine


class TransferTests(unittest.TestCase):
    def test_correction_preserves_unvisited_route_and_parent(self):
        teacher = ConnectionTree([
            {'feature':'visited', 'yes':1, 'no':2},
            {'ports':list(OPS)},
            {'ports':['*']+[op for op in OPS if op != '*']},
        ])
        before = json.dumps(teacher.nodes, sort_keys=True)
        student = refine(teacher, [(frozenset({'visited'}), '-')], Work())
        self.assertEqual(before, json.dumps(teacher.nodes, sort_keys=True))
        for values, expected in ((frozenset({'visited'}), '-'), (frozenset(), '*')):
            ports, _ = student.activate(values, Work())
            self.assertEqual(max(ports, key=ports.get), expected)

    def test_refinement_retains_distinct_inputs_at_same_old_destination(self):
        teacher = ConnectionTree([{'ports':list(OPS)}])
        student = refine(teacher, [(frozenset(), '+'), (frozenset({'scale'}), '*')], Work())
        for values, expected in ((frozenset(), '+'), (frozenset({'scale'}), '*')):
            ports, _ = student.activate(values, Work())
            self.assertEqual(max(ports, key=ports.get), expected)
        self.assertFalse({'counts', 'examples', 'answers'} & {k for n in student.nodes for k in n})
