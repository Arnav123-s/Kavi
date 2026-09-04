"""Controller correctness tests are not evidence of learner intelligence."""

from dataclasses import asdict
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from kavi.language_curriculum import STAGES, allowed, inventory, varied, letters_case, quantity_case
from kavi.language_teacher import LanguageFirstTeacher, school_stages
from kavi.wave_core import WaveConfig, WaveLearner


class LanguageCurriculumTests(unittest.TestCase):
    def test_order_cannot_skip_prerequisites(self):
        passed = []
        for stage in school_stages():
            self.assertTrue(all(p in passed for p in stage.prerequisites))
            if stage in STAGES:
                self.assertTrue(allowed(stage.stage_id, passed))
            passed.append(stage.stage_id)
        self.assertFalse(allowed(STAGES[1].stage_id, []))
        self.assertEqual(school_stages()[5].prerequisites, (STAGES[4].stage_id,))

    def test_expected_answers_are_exact_and_freshness_is_enforced(self):
        for stage in STAGES:
            known = inventory(stage.stage_id)
            first = varied(stage.stage_id, 31, 16, exclude={q.key for q in known})
            harder = varied(stage.stage_id, 41, 16, harder=True, exclude={q.key for q in known + first})
            self.assertEqual(len({q.key for q in known + first + harder}), len(known + first + harder))
            for q in known + first + harder:
                self.assertTrue(q.correct(q.answer))
                self.assertFalse(q.correct("probably " + q.answer))
                self.assertFalse(q.correct(q.answer + " another answer"))
        self.assertFalse(letters_case("a").correct("A"))
        self.assertEqual(quantity_case((0, 3)).answer, "zero | three")
        self.assertEqual(quantity_case((0, 3), True).answer, "empty | xxx")


class AnswerLearningTests(unittest.TestCase):
    def core(self):
        return WaveLearner(WaveConfig(nodes=16, fan_in=3, hops=1, threads=1))

    def test_answer_objective_changes_internal_connections_without_growth(self):
        import torch
        core = self.core()
        phase = core.network.phase.detach().clone()
        count = core.ledger()["parameters"]
        examples = [("Copy a => ", "a"), ("Copy b => ", "b")]
        initial = core.learn_answers(examples)["loss"]
        for _ in range(30):
            result = core.learn_answers(examples)
        self.assertLess(result["loss"], initial)
        self.assertFalse(torch.equal(phase, core.network.phase))
        self.assertEqual(core.ledger()["parameters"], count)
        self.assertEqual(result["tokens"], 4)  # a/newline + b/newline; no prefix loss
        self.assertEqual(result["objective"], "balanced-answer-only")
        self.assertGreater(core.network.embedding.weight.grad[ord("C")].abs().sum().item(), 0)

    def test_independent_rows_and_read_only_inference(self):
        import torch
        core = self.core()
        tokens = torch.tensor([list(b"Copy a => "), list(b"Copy b => ")])
        with torch.no_grad():
            batch, _ = core.network(tokens)
            for i in range(2):
                single, _ = core.network(tokens[i:i+1])
                self.assertTrue(torch.allclose(batch[i], single[0], atol=1e-6))
        before = core.fingerprint()
        core.generate("Copy a => ", max_bytes=4)
        self.assertEqual(core.fingerprint(), before)

    def test_budget_and_checkpoint(self):
        core = self.core()
        for invalid in ([], [("p", "x")] * 5, [("", "x")], [("p" * 256, "x")]):
            with self.assertRaises(ValueError):
                core.learn_answers(invalid)
        self.assertTrue(core.learn_answers([("p", "x")], callback=lambda _: False)["interrupted"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "core.pt"
            core.save(path)
            restored = WaveLearner.load(path)
            core.learn_answers([("p", "x")])
            restored.learn_answers([("p", "x")])
            self.assertEqual(core.fingerprint(), restored.fingerprint())


class TeacherControlTests(unittest.TestCase):
    def teacher(self):
        teacher = object.__new__(LanguageFirstTeacher)
        teacher.emit = Mock()
        teacher.core = Mock()
        teacher.core.fingerprint.return_value = "unchanged"
        teacher.seen = set()
        teacher.stopping = False
        teacher.control = Mock(return_value=True)
        teacher.school = {"passed": [], "letter_count": 4, "retention": {}, "stage_index": 0}
        teacher.stages = school_stages()
        return teacher

    def test_grader_does_not_supply_answer_or_train(self):
        teacher = self.teacher()
        teacher.core.generate.return_value = "wrong"
        score, errors, correct = teacher.check(STAGES[0], [letters_case("a")], "unseen")
        self.assertEqual(score, 0)
        self.assertEqual(len(errors), 1)
        self.assertFalse(correct)
        teacher.core.generate.assert_called_once_with("Copy a => ", max_bytes=96)
        teacher.core.learn.assert_not_called()
        teacher.core.learn_answers.assert_not_called()
        self.assertIn(letters_case("a").key, teacher.seen)

    def test_fresh_pool_exhaustion_blocks_pass_without_crashing(self):
        teacher = self.teacher()
        teacher.new_examples = Mock(side_effect=ValueError("Unseen exercise space exhausted"))
        self.assertIsNone(teacher.fresh_check(STAGES[0]))
        self.assertEqual(teacher.school["passed"], [])
        self.assertEqual(teacher.emit.call_args.args[1], "fresh-pool-exhausted")

    def test_interrupted_check_cannot_pass(self):
        teacher = self.teacher()
        teacher.control.return_value = False
        score, _, _ = teacher.check(STAGES[0], [letters_case("a")], "unseen")
        self.assertEqual(score, 0)

    def test_frozen_grader_detects_illicit_update(self):
        teacher = self.teacher()
        teacher.core.fingerprint.side_effect = ["before", "after"]
        with self.assertRaises(AssertionError):
            teacher.check(STAGES[0], [letters_case("a")], "unseen")

    def test_unmet_prerequisite_does_not_start_teaching(self):
        teacher = self.teacher()
        teacher.source_lesson = Mock()
        with self.assertRaises(ValueError):
            teacher.run_round(STAGES[1])
        teacher.source_lesson.assert_not_called()

    def test_retention_protects_previous_correct_answers(self):
        teacher = self.teacher()
        teacher.school["retention"] = {STAGES[0].stage_id: [asdict(letters_case("a"))]}
        teacher.core.generate.return_value = "b"
        self.assertFalse(teacher.retained_skills_pass())


if __name__ == "__main__":
    unittest.main()
