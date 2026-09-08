"""Readout semantics and acquisition fixtures; not curriculum data."""

import json
import unittest
from kavi.composable_configurations import Work
from kavi.phase import PhaseConfiguration
from kavi.phase.regions import bind_regions


class RegionTests(unittest.TestCase):
    def test_interval_rule_reaches_unshown_state(self):
        raw = PhaseConfiguration((10,), (('x', 0, 1),))
        learned = bind_regions(raw, [('xx', 1), ('xxxx', 1), ('xxxxxx', 2)], Work())
        self.assertEqual(learned.predict('xxx', Work()), 1)
        self.assertIsNone(learned.predict('xxxxx', Work()))
        self.assertEqual(PhaseConfiguration.from_record(json.loads(json.dumps(learned.record()))), learned)

    def test_disagreement_is_not_resolved_by_rule_order(self):
        rules = ((((1, 4),), 1), (((3, 5),), 2))
        for ordering in (rules, tuple(reversed(rules))):
            model = PhaseConfiguration((10,), (('x', 0, 1),), outputs=ordering)
            self.assertIsNone(model.predict('xxx', Work()))
            self.assertEqual(model.predict('x', Work()), 1)

    def test_opposite_class_blocks_expansion(self):
        raw = PhaseConfiguration((10,), (('x', 0, 1),))
        learned = bind_regions(raw, [('x', 1), ('xxx', 2), ('xxxxx', 1)], Work())
        self.assertEqual(learned.predict('xxx', Work()), 2)
        self.assertIsNone(learned.predict('xx', Work()))
        self.assertIsNone(bind_regions(raw, [('x', 1), ('x', 2)], Work()))

    def test_invalid_interval_and_work_budget(self):
        for interval in ((4, 1), (0, 10), (False, 1)):
            with self.assertRaises(ValueError):
                PhaseConfiguration((10,), outputs=(((interval,), 1),))
        with self.assertRaises(InterruptedError):
            bind_regions(PhaseConfiguration((10,), (('x', 0, 1),)), [('x', 1)], Work(limit=1))


if __name__ == '__main__':
    unittest.main()
