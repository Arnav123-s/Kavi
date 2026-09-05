import unittest

import torch

from kavi.consolidation_trials import interpolate_candidate, lost_correct_answers
from kavi.pathway_trials import TrialLearner
from kavi.repair_trials import RepairLearner
from kavi.wave_core import WaveConfig


class ConsolidationTests(unittest.TestCase):
    def test_smaller_change_keeps_base_trainable_and_does_not_mutate_parent(self):
        parent = TrialLearner(WaveConfig(nodes=8, hops=1, threads=1))
        proposal = RepairLearner.from_parent(parent, mode="adapter_joint")
        proposal.learn_answers([("Copy a => ", "a")])
        fingerprint = parent.fingerprint()
        child = interpolate_candidate(parent, proposal, 0.5)
        initial = RepairLearner.from_parent(parent, mode="adapter_joint")
        for p, a, b in zip(child.network.parameters(), initial.network.parameters(), proposal.network.parameters()):
            self.assertTrue(torch.allclose(p, (a+b)*0.5, atol=1e-6))
            self.assertTrue(p.requires_grad)
        self.assertEqual(parent.fingerprint(), fingerprint)
        self.assertEqual(len(child.optimizer.state), 0)

    def test_zero_fraction_has_original_forward_map(self):
        parent = TrialLearner(WaveConfig(nodes=8, hops=1, threads=1))
        proposal = RepairLearner.from_parent(parent, mode="adapter_joint")
        proposal.learn_answers([("Copy a => ", "a")])
        child = interpolate_candidate(parent, proposal, 0)
        x = torch.tensor([list(b"Last abc => ")])
        self.assertTrue(torch.equal(parent.network(x)[0], child.network(x)[0]))

    def test_protection_includes_primary_and_transfer_not_only_old_copying(self):
        old = {"primary_3": {"outputs": [{"key": "p", "correct": True}]},
               "script_transfer": {"outputs": [{"key": "s", "correct": True}]},
               "retention_characters": {"outputs": [{"key": "r", "correct": True}]}}
        now = {"anything": {"outputs": [{"key": "p", "correct": False},
                                         {"key": "s", "correct": False},
                                         {"key": "r", "correct": True}]}}
        self.assertEqual(lost_correct_answers(old, now), ["p", "s"])


if __name__ == "__main__":
    unittest.main()
