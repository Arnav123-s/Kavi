from collections import Counter
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

import torch

from kavi.language_curriculum import letters_case
from kavi.mixed_quizzes import OPERATIONS, exercise, task_name
from kavi.pathway_trials import TrialLearner
from kavi.strategy_trials import STRATEGIES, TeachingRecipe, make_plan, rank_results
from kavi.teaching_comparison import written_sequence
from kavi.trial_resources import parallel_rows
from kavi.wave_core import WaveConfig, WaveLearner


def fixture_plan():
    progress = {"seen_questions": [], "multilingual_bridge": {"lanes": {"x": {"correct_characters": ["\u0905", "\u0628"]}}}}
    return make_plan(progress, {"xyz", "ABC"})


class StrategyTests(unittest.TestCase):
    def test_partitions_and_rehearsal_respect_protected_strings(self):
        plan = fixture_plan()
        sets = []
        for bank in plan["partitions"].values():
            strings = {written_sequence(q) for name, rows in bank.items() if name != "retention_characters" for q in rows}
            sets.append(strings | {s[::-1] for s in strings})
        for i, first in enumerate(sets):
            for second in sets[i+1:]:
                self.assertFalse(first & second)
        for q in plan["rehearsal"]:
            if len(q.answer) > 1:
                self.assertNotIn(q.answer, plan["forbidden_sequences"])

    def test_teacher_recipes_match_task_and_length_budgets(self):
        class WrongProbe:
            updates = 0
            def fingerprint(self): return "fixed"
            def generate(self, prompt, max_bytes): return ""
        plan, totals, reviews = fixture_plan(), [], []
        for strategy in STRATEGIES:
            recipe, count, review = TeachingRecipe(strategy, 41, plan, 180), Counter(), []
            for step in range(180):
                rows, metadata = recipe.batch(step, WrongProbe())
                if metadata["kind"] == "shared_review":
                    review.append(rows)
                else:
                    count.update((task_name(q), len(written_sequence(q))) for q in rows)
                    self.assertFalse({written_sequence(q) for q in rows} & set(plan["forbidden_sequences"]))
            totals.append(count)
            reviews.append(review)
        self.assertTrue(all(x == totals[0] for x in totals))
        self.assertTrue(all(x == reviews[0] for x in reviews))

    def test_blocked_and_mixed_use_identical_example_multisets(self):
        plan = fixture_plan()
        one, two = TeachingRecipe("mixed", 43, plan, 180), TeachingRecipe("blocked", 43, plan, 180)
        self.assertEqual(Counter(q.key for q in one.rows), Counter(q.key for q in two.rows))
        self.assertNotEqual(one.rows, two.rows)

    def test_boundary_groups_include_append_and_prepend_relations(self):
        recipe = TeachingRecipe("boundary", 4, fixture_plan(), 180)
        strings = [written_sequence(q) for q in recipe.rows[:24:4]]
        self.assertEqual(list(map(len, strings)), [2, 2, 3, 3, 4, 4])
        self.assertTrue(strings[4].startswith(strings[2]) and strings[2].startswith(strings[0]))
        self.assertTrue(strings[5].endswith(strings[3]) and strings[3].endswith(strings[1]))

    def test_ranking_does_not_trade_retention_for_score_silently(self):
        def row(name, correct, losses):
            return {"state": "complete", "strategy": name, "scores": {"primary_3": {"correct": correct, "total": 10}}, "retention_losses": losses}
        result = rank_results([row("high_score", 10, ["old"]), row("retained", 8, [])], "strategy")
        self.assertEqual(result[0]["name"], "retained")

    def test_parallelism_falls_back_with_less_memory_or_unknown_telemetry(self):
        self.assertEqual(parallel_rows({}), 1)
        for gib, expected in ((8, 4), (5, 2), (3, 1)):
            self.assertEqual(parallel_rows({"available_bytes": gib * 1024**3, "working_set_bytes": 500 * 1024**2}), expected)


class PathwayTrialTests(unittest.TestCase):
    def core(self):
        return TrialLearner(WaveConfig(nodes=16, fan_in=4, hops=1, threads=1))

    def test_microbatches_preserve_objective_and_single_update(self):
        batch = [(exercise(op, "AbC").prefix, exercise(op, "AbC").answer) for op in OPERATIONS]
        reference, serial = self.core(), self.core()
        serial.parallel_rows = 1
        reference.learn_answers(batch)
        serial.learn_answers(batch)
        self.assertEqual(reference.updates, 1)
        self.assertEqual(serial.updates, 1)
        for a, b in zip(reference.network.parameters(), serial.network.parameters()):
            self.assertTrue(torch.allclose(a, b, atol=2e-6, rtol=2e-5))

    def test_standard_matches_original_answer_objective(self):
        trial = self.core()
        original = WaveLearner(trial.config)
        batch = [("Last Ab => ", "b"), ("Copy x => ", "x")]
        a, b = trial.learn_answers(batch), original.learn_answers(batch)
        self.assertAlmostEqual(a["loss"], b["loss"], places=6)
        for p, q in zip(trial.network.parameters(), original.network.parameters()):
            self.assertTrue(torch.allclose(p, q, atol=1e-6))

    def test_unperturbed_split_preserves_function_and_old_moments(self):
        core = self.core()
        core.learn_answers([("Copy a => ", "a")])
        x = torch.tensor([list(b"Last Ab => ")])
        before, _ = core.network(x)
        moments = core.optimizer.state[core.network.phase]["exp_avg"].clone()
        old_size = core.ledger()["parameters"]
        core.grow_split_routes(perturbation=0)
        after, _ = core.network(x)
        self.assertTrue(torch.allclose(before, after, atol=2e-6, rtol=2e-5))
        self.assertEqual(core.ledger()["parameters"] - old_size, 16 * 4)
        self.assertTrue(torch.equal(core.optimizer.state[core.network.phase]["exp_avg"][:, :4], moments))
        with self.assertRaises(ValueError):
            core.grow_split_routes()

    def test_rewire_changes_sources_without_growing_and_roundtrips(self):
        core = self.core()
        core.learn_answers([("Copy a => ", "a")])
        before, size = core.network.sources.clone(), core.ledger()["parameters"]
        core.rewire_weak_routes()
        self.assertEqual(int((before != core.network.sources).sum()), core.config.nodes)
        self.assertEqual(core.ledger()["parameters"], size)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "model.pt"
            core.save(path)
            restored = TrialLearner.load(path)
            self.assertEqual(core.fingerprint(), restored.fingerprint())

    def test_damping_reduces_route_displacement_without_freezing(self):
        normal, damped = self.core(), self.core()
        old = normal.network.phase.detach().clone()
        damped.variant = "damped_routes"
        batch = [("Last ab => ", "b")]
        normal.learn_answers(batch)
        damped.learn_answers(batch)
        expected = old + 0.25 * (normal.network.phase.detach() - old)
        self.assertTrue(torch.allclose(damped.network.phase, expected, atol=1e-7))
        self.assertFalse(torch.equal(damped.network.phase, old))


if __name__ == "__main__":
    unittest.main()
