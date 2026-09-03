"""Tests for verified explanation-guided candidate learning."""

from __future__ import annotations

import unittest

from kavi.explanation_learning import ExplanationGatedLearner
from kavi.graph import PathwayFabric
from kavi.learning import IndependentEvaluator
from kavi.lesson_runtime import ExplanationRuntime
from kavi.lessons import VerifiedLesson
from kavi.runtime import RuntimeConfig
from kavi.types import ArithmeticEvent, Operation


class VerifiedLessonTests(unittest.TestCase):
    def test_generated_lesson_is_locally_valid(self) -> None:
        event = ArithmeticEvent("lesson", 7, 5, Operation.ADD, "lesson")
        lesson = VerifiedLesson.for_event(event)
        self.assertTrue(lesson.is_valid())
        self.assertEqual(lesson.target_weights, (1.0, 1.0, 0.0))

    def test_abstention_can_still_receive_a_verified_lesson(self) -> None:
        fabric = PathwayFabric()
        event = ArithmeticEvent(
            "conflict",
            4,
            2,
            Operation.ADD,
            "conflict",
            conflicted=True,
        )
        inference = fabric.infer(event)
        feedback = ExplanationGatedLearner(IndependentEvaluator()).observe(
            fabric,
            inference,
            VerifiedLesson.for_event(event),
        )
        self.assertEqual(feedback.valence.value, "neutral")
        self.assertTrue(feedback.promoted)

    def test_short_verified_curriculum_learns_unseen_addition(self) -> None:
        runtime = ExplanationRuntime(
            RuntimeConfig(steps=12, seed=7, conflict_every=0, interval_ms=0),
            emit=lambda _: None,
        )
        runtime.run()
        result = runtime.ask(7, 5, Operation.ADD)
        self.assertEqual(result.answer, 12)


if __name__ == "__main__":
    unittest.main()
