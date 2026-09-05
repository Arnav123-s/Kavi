from pathlib import Path
import tempfile
import unittest

import torch

from kavi.pathway_trials import TrialLearner
from kavi.repair_trials import RepairLearner
from kavi.wave_core import WaveConfig


class SmallRepairTests(unittest.TestCase):
    def parent(self):
        parent = TrialLearner(WaveConfig(nodes=16, hops=2, threads=1))
        parent.learn_answers([("Copy a => ", "a")])
        return parent

    def test_zero_gain_preserves_logits_and_base_exactly(self):
        parent = self.parent()
        for mode in ("adapter_only", "adapter_joint"):
            child = RepairLearner.from_parent(parent, mode=mode)
            x = torch.tensor([list(b"Last abcd => ")])
            first, state = parent.network(x)
            second, other_state = child.network(x)
            self.assertTrue(torch.equal(first, second))
            self.assertTrue(torch.equal(state, other_state))
            self.assertEqual(child.base_fingerprint(), parent.fingerprint())
            self.assertEqual(child.ledger()["parameters"] - parent.ledger()["parameters"], 56)

    def test_adapter_updates_without_changing_any_base_weight(self):
        child = RepairLearner.from_parent(self.parent())
        base, whole = child.base_fingerprint(), child.fingerprint()
        child.learn_answers([("Last abc => ", "c"), ("First abc => ", "a")])
        self.assertEqual(base, child.base_fingerprint())
        self.assertNotEqual(whole, child.fingerprint())
        self.assertGreater(float(child.network.repair_gain.abs().sum()), 0)
        self.assertEqual(child.ledger()["trainable_parameters"], 56)

    def test_joint_mode_preserves_old_optimizer_moments_then_learns(self):
        parent = self.parent()
        child = RepairLearner.from_parent(parent, mode="adapter_joint")
        self.assertTrue(torch.equal(parent.optimizer.state[parent.network.phase]["exp_avg"],
                                    child.optimizer.state[child.network.phase]["exp_avg"]))
        base = child.base_fingerprint()
        child.learn_answers([("Last xyz => ", "z")])
        self.assertNotEqual(base, child.base_fingerprint())

    def test_save_load_keeps_freeze_policy_predictions_and_state(self):
        for mode in ("adapter_only", "adapter_joint"):
            child = RepairLearner.from_parent(self.parent(), mode=mode)
            child.learn_answers([("Last xyz => ", "z")])
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "repair.pt"
                child.save(path)
                restored = RepairLearner.load(path)
                self.assertEqual(child.fingerprint(), restored.fingerprint())
                self.assertEqual(child.ledger(), restored.ledger())
                self.assertEqual(child.generate("First abc => ", max_bytes=4),
                                 restored.generate("First abc => ", max_bytes=4))

    def test_capacity_is_bounded(self):
        with self.assertRaises(ValueError):
            RepairLearner.from_parent(self.parent(), slots=9)


if __name__ == "__main__":
    unittest.main()
