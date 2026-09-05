from pathlib import Path
import random
import tempfile
import unittest

import torch

from kavi.forward_repair import (ForwardLearner, choose_jump, feedback_batch,
                                 jump_pool, preservation)
from kavi.language_curriculum import letters_case
from kavi.pathway_trials import TrialLearner
from kavi.repair_trials import RepairLearner
from kavi.wave_core import WaveConfig


class ForwardRepairTests(unittest.TestCase):
    def latest(self):
        old = TrialLearner(WaveConfig(nodes=16, hops=1, threads=1))
        latest = RepairLearner.from_parent(old, mode="adapter_joint")
        latest.learn_answers([("Last ab => ", "b"), ("Copy ab => ", "ab")])
        return latest

    def test_zero_effect_jump_preserves_full_latest_state_and_moments(self):
        latest = self.latest()
        fingerprint = latest.fingerprint()
        child = ForwardLearner.from_latest(latest, [jump_pool(latest)[0]])
        x = torch.tensor([list(b"First abc => ")])
        a, state = latest.network(x)
        b, other = child.network(x)
        self.assertTrue(torch.equal(a, b))
        self.assertTrue(torch.equal(state, other))
        self.assertEqual(latest.fingerprint(), fingerprint)
        self.assertEqual(child.ledger()["parameters"]-latest.ledger()["parameters"], 7)
        for name, parameter in child.network.named_parameters():
            self.assertTrue(parameter.requires_grad)
            old = dict(latest.network.named_parameters())[name]
            a = latest.optimizer.state[old]["exp_avg"]
            b = child.optimizer.state[parameter]["exp_avg"]
            self.assertTrue(torch.equal(a, b if a.shape == b.shape else b[:8]))
        self.assertEqual(float(child.network.repair_gain[-1]), 0)

    def test_route_selection_is_read_only_and_bounded(self):
        latest = self.latest()
        fingerprint, updates = latest.fingerprint(), latest.updates
        rows = [("Copy a => ", "a")] * 4
        chosen, event = choose_jump(latest, rows, rows)
        self.assertIn(chosen, jump_pool(latest))
        self.assertLessEqual(len(event["candidates"]), 8)
        self.assertEqual(event["probe_presentations"], 8)
        self.assertEqual(latest.fingerprint(), fingerprint)
        self.assertEqual(latest.updates, updates)

    def test_round_trip_and_no_growth_control(self):
        latest = self.latest()
        for jumps in ([], [jump_pool(latest)[0]]):
            child = ForwardLearner.from_latest(latest, jumps)
            child.learn_answers([("Copy c => ", "c")])
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder)/"forward.pt"
                child.save(path)
                restored = ForwardLearner.load(path)
                self.assertEqual(child.fingerprint(), restored.fingerprint())
                self.assertEqual(child.ledger(), restored.ledger())
                self.assertEqual(child.generate("Copy a => ", max_bytes=4),
                                 restored.generate("Copy a => ", max_bytes=4))

    def test_growth_and_endpoints_are_bounded(self):
        latest = self.latest()
        for jumps in ([(-1, 0)], [(0, 16)], [(0, 1), (0, 1)], [(i, i) for i in range(9)]):
            with self.assertRaises(ValueError):
                ForwardLearner.from_latest(latest, jumps)

    def test_protection_includes_latest_successes_and_deduplicates_union(self):
        def scores(keys):
            return {"g": {"outputs": [{"key": k, "correct": True} for k in keys]}}
        value = preservation(scores(["old", "both"]), scores(["new", "both"]), scores(["old", "new"]))
        self.assertEqual(value["union_correct"], 3)
        self.assertEqual(value["union_lost"], 1)
        self.assertEqual(value["old_regressions_repaired"], 1)

    def test_feedback_contains_new_and_old_successes(self):
        questions = [letters_case(c) for c in "abcd"]
        old, latest = {questions[0].key}, {questions[1].key}
        focus, reference = feedback_batch(random.Random(3), questions, old, latest, latest)
        self.assertEqual(len(focus), 4)
        self.assertEqual(len(reference), 4)
        self.assertEqual([q.key for q in focus[:2]], [questions[0].key]*2)
        self.assertEqual({q.key for q in reference}, old | latest)


if __name__ == "__main__":
    unittest.main()
