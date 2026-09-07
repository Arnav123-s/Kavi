"""Probe invariance, learned routing and ambiguous evidence checks."""

import unittest
from kavi.experience_router import ExperienceRouter, probe_inputs, signature, called_components


class ExperienceRouterTests(unittest.TestCase):
    def test_permuted_inputs_have_same_component_signature(self):
        def features(fn):
            return signature(2, {xs: fn(*xs) for xs in probe_inputs(2)})
        self.assertEqual(features(lambda a,b: a*b*b), features(lambda a,b: b*a*a))
        self.assertNotEqual(features(lambda a,b: a*a+b*b), features(lambda a,b: (a+b)**2))

    def test_discrete_rules_come_from_labels(self):
        a, b = (1,-1,-1,2,0,0), (1,-1,-1,3,0,0)
        router = ExperienceRouter.fit([(a, ('square',)), (b, ('multiply','square'))])
        self.assertEqual(router.select(a), ('square',))
        self.assertEqual(router.select(b), ('multiply','square'))
        changed = ExperienceRouter.fit([(a, ('multiply',)), (b, ('square',))])
        self.assertEqual(changed.select(a), ('multiply',))
        self.assertEqual(router.select((1,-1,-1,4,0,0)), ('multiply','square'))

    def test_conflicts_keep_both_routes_and_calls_are_extracted(self):
        key = (1,-1,-1,2,0,0)
        router = ExperienceRouter.fit([(key, ('add',)), (key, ('multiply',))])
        self.assertEqual(router.select(key), ('add','multiply'))
        self.assertEqual(called_components(('call','add',('arg',0),('call','square',('arg',1)))),
                         ('add','square'))
        with self.assertRaises(ValueError): signature(2, {})


if __name__ == '__main__': unittest.main()
