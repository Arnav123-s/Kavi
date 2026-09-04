import json
from pathlib import Path
import tempfile
import unittest
from collections import Counter

from kavi.language_curriculum import letters_case
from kavi.mixed_quizzes import OPERATIONS, exercise, task_name
from kavi.teaching_comparison import (ComparisonConfig, LessonSchedule, build_plan,
                                     checkpoint, contrast_group, evaluate,
                                     retention_losses, written_sequence)


def small_progress():
    return {"seen_questions": [letters_case(a + b).key for a in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                               for b in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"],
            "multilingual_bridge": {"banks": {"3": [{"answer": "xyz"}]},
                                    "lanes": {"one": {"correct_characters": ["\u0905", "\u0628", "\u00f1"]}}}}


class ComparisonTests(unittest.TestCase):
    def test_contrast_changes_operation_and_reverses_order(self):
        rows = contrast_group("AB")
        self.assertEqual({q.prompt: q.answer for q in rows if q.prompt.startswith(("First", "Last"))},
                         {"First AB": "A", "Last AB": "B", "First BA": "B", "Last BA": "A"})
        self.assertEqual(Counter(task_name(q) for q in rows), {k: 2 for k in OPERATIONS})
        with self.assertRaises(ValueError):
            contrast_group("ABA")

    def test_plan_handles_exhausted_two_letter_pool_and_preserves_novelty(self):
        progress = small_progress()
        plan = build_plan(progress)
        seen = set(progress["seen_questions"])
        self.assertEqual(len(plan["development"]["2"]), 24)
        for name, rows in plan["final"].items():
            if name.startswith("retention"):
                continue
            for q in rows:
                seq = written_sequence(q)
                self.assertTrue(all(exercise(op, s).key not in seen for op in OPERATIONS for s in (seq, seq[::-1])))
        partitions = [set(written_sequence(q) for q in rows) for rows in
                      list(plan["development"].values()) + [v for k, v in plan["final"].items() if k != "retention_characters"]]
        for i, first in enumerate(partitions):
            for second in partitions[i+1:]:
                self.assertFalse(first & second)

    def test_identical_budgets_rehearsal_and_no_assessment_leakage(self):
        plan = build_plan(small_progress())
        first, second = LessonSchedule("random_mixed", 42, plan), LessonSchedule("contrast", 42, plan)
        counts = [Counter(), Counter()]
        for step in range(384):
            pairs = [first.batch(step), second.batch(step)]
            for i, (rows, label) in enumerate(pairs):
                self.assertEqual(len(rows), 4)
                counts[i].update(task_name(q) for q in rows)
                if label != "shared_rehearsal":
                    self.assertFalse({written_sequence(q) for q in rows} & set(plan["forbidden_sequences"]))
            if step % 5 == 4:
                self.assertEqual(pairs[0], pairs[1])
            self.assertEqual(counts[0], counts[1])
        self.assertEqual(counts[0], counts[1])

    def test_development_gate_cannot_be_replaced_by_final_scores(self):
        plan = build_plan(small_progress())
        schedule = LessonSchedule("contrast", 42, plan)
        scores = {"2": {"per_task": {"first": {"accuracy": 1.0}, "last": {"accuracy": 0.5}}}}
        self.assertFalse(schedule.observe_development(scores))
        self.assertEqual(schedule.stage, 2)
        scores["2"]["per_task"]["last"]["accuracy"] = 1.0
        self.assertTrue(schedule.observe_development(scores))
        self.assertEqual(schedule.stage, 3)

    def test_evaluation_only_sends_question_and_preserves_state(self):
        class DummyCore:
            updates = 8
            def fingerprint(self):
                return "unchanged"
            def generate(self, prompt, max_bytes):
                self.last_prompt = prompt
                return "A"
        core = DummyCore()
        result = evaluate(core, {"position": [exercise("first", "AB"), exercise("last", "AB")]})
        self.assertEqual(result["position"]["correct"], 1)
        self.assertEqual(core.last_prompt, "Last AB => ")
        self.assertEqual(core.updates, 8)

    def test_retention_counts_only_formerly_correct_answers(self):
        before = {"retention_characters": {"outputs": [{"key": "a", "correct": True}, {"key": "b", "correct": False}]}}
        after = {"retention_characters": {"outputs": [{"key": "a", "correct": False}, {"key": "b", "correct": False}]}}
        self.assertEqual(retention_losses(before, after), ["a"])

    def test_checkpoint_rejects_escape_and_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "current.json").write_text(json.dumps({"snapshot": "../escaped", "sha256": "wrong"}))
            with self.assertRaises(ValueError):
                checkpoint(root)
            folder = root / "snapshots" / "one"
            folder.mkdir(parents=True)
            (folder / "learner.pt").write_bytes(b"test fixture, not a model")
            (root / "current.json").write_text(json.dumps({"snapshot": "snapshots/one", "sha256": "wrong"}))
            with self.assertRaises(ValueError):
                checkpoint(root)

    def test_invalid_budgets_rejected(self):
        for steps in (0, 63, 769):
            with self.assertRaises(ValueError):
                ComparisonConfig(steps=steps)
        with self.assertRaises(ValueError):
            ComparisonConfig(seeds=(4, 4))


if __name__ == "__main__":
    unittest.main()
