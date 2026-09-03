"""Live runtime for the explanation-learning follow-up experiment."""

from __future__ import annotations

import time

from .explanation_learning import ExplanationGatedLearner
from .learning import IndependentEvaluator
from .lessons import VerifiedLesson
from .runtime import LiveRuntime, RunSummary


class ExplanationRuntime(LiveRuntime):
    """Keep the original controls while adding a verified explanation path."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.learner = ExplanationGatedLearner(self.evaluator)

    def run(self) -> RunSummary:
        """Run a finite, user-stoppable lesson stream."""

        self.emit("Kavi explanation-learning live pathway trace")
        self.emit(f"  profile: {self.device_profile}")
        self.emit(
            "  boundary: lessons are locally verified arithmetic rules; no "
            "network, source rewrite, background persistence, or device-limit changes."
        )
        completed = promoted = correct = abstentions = 0
        for step in range(1, self.config.steps + 1):
            if self._stop_requested() or not self._wait_if_paused():
                self.emit("[control] stop requested; preserving the current in-memory parent.")
                return RunSummary(completed, True, promoted, correct, abstentions)
            event = self.curriculum.event_at(step)
            lesson = VerifiedLesson.for_event(event)
            inference = self.fabric.infer(
                event,
                max_active_routes=self.config.max_active_routes,
            )
            feedback = self.learner.observe(self.fabric, inference, lesson)
            self._emit_event(step, inference, feedback)
            self.emit(f"  verified explanation: {lesson.explanation}")
            completed += 1
            promoted += int(feedback.promoted)
            correct += int(inference.answer == event.target)
            abstentions += int(inference.answer is None)
            if self.config.interval_ms:
                time.sleep(self.config.interval_ms / 1000.0)
        return RunSummary(completed, False, promoted, correct, abstentions)
