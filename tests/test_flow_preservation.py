import unittest

import torch

from kavi.flow_preservation import learn_with_rehearsal, project_displacement
from kavi.pathway_trials import TrialLearner
from kavi.wave_core import WaveConfig


class FlowPreservationTests(unittest.TestCase):
    def test_harmful_component_is_removed_without_freezing_other_directions(self):
        corrected, event = project_displacement([torch.tensor([2.0, 3.0])], [torch.tensor([1.0, 0.0])])
        self.assertTrue(event["projected"])
        self.assertTrue(torch.equal(corrected[0], torch.tensor([0.0, 3.0])))
        self.assertLessEqual(event["reference_dot_after"], 1e-7)

    def test_helpful_change_is_left_unchanged(self):
        delta = torch.tensor([-2.0, 3.0])
        corrected, event = project_displacement([delta], [torch.tensor([1.0, 0.0])])
        self.assertFalse(event["projected"])
        self.assertTrue(torch.equal(delta, corrected[0]))

    def test_zero_reference_gradient_does_not_divide_by_zero(self):
        corrected, event = project_displacement([torch.ones(2)], [torch.zeros(2)])
        self.assertFalse(event["projected"])
        self.assertTrue(torch.equal(corrected[0], torch.ones(2)))

    def test_serial_and_parallel_rehearsal_have_one_equivalent_update(self):
        focus = [("First ab => ", "a"), ("Last ab => ", "b"), ("Copy ab => ", "ab"), ("Join a b => ", "ab")]
        reference = [("Copy a => ", "a"), ("Copy b => ", "b"), ("Copy c => ", "c"), ("Copy d => ", "d")]
        a, b = [TrialLearner(WaveConfig(nodes=8, hops=1, threads=1)) for _ in range(2)]
        b.parallel_rows = 1
        first = learn_with_rehearsal(a, focus, reference, project=True)
        second = learn_with_rehearsal(b, focus, reference, project=True)
        self.assertEqual(a.updates, 1)
        self.assertEqual(b.updates, 1)
        self.assertAlmostEqual(first["loss"], second["loss"], places=5)
        self.assertEqual(first["presentations"], 8)
        for p, q in zip(a.network.parameters(), b.network.parameters()):
            self.assertTrue(torch.allclose(p, q, atol=2e-6, rtol=2e-5))


if __name__ == "__main__":
    unittest.main()
