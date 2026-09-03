"""Independent verification and candidate-only pathway updates."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Iterable, Sequence

from .graph import PathwayFabric
from .types import (
    ArithmeticEvent,
    Feedback,
    FeedbackValence,
    Inference,
    Metrics,
    Operation,
)


def protected_manifest() -> tuple[ArithmeticEvent, ...]:
    """Small fixed tests that candidates may not silently regress."""

    return (
        ArithmeticEvent("protected-01", 1, 1, Operation.ADD, "p01"),
        ArithmeticEvent("protected-02", 2, 5, Operation.ADD, "p02"),
        ArithmeticEvent("protected-03", 9, 3, Operation.SUBTRACT, "p03"),
        ArithmeticEvent("protected-04", 8, 6, Operation.SUBTRACT, "p04"),
    )


def held_out_manifest() -> tuple[ArithmeticEvent, ...]:
    """Unseen combinations that distinguish a rule from mere replay."""

    return (
        ArithmeticEvent("held-01", 13, 7, Operation.ADD, "h01"),
        ArithmeticEvent("held-02", 17, 4, Operation.ADD, "h02"),
        ArithmeticEvent("held-03", 15, 9, Operation.SUBTRACT, "h03"),
        ArithmeticEvent("held-04", 20, 11, Operation.SUBTRACT, "h04"),
    )


@dataclass(frozen=True, slots=True)
class CandidateAssessment:
    """A complete before/after decision record for one proposed update."""

    parent_protected: Metrics
    candidate_protected: Metrics
    parent_held_out: Metrics
    candidate_held_out: Metrics
    current_parent_error: float
    current_candidate_error: float
    accepted: bool


class IndependentEvaluator:
    """Evaluates a proposed readout without changing the learning fabric."""

    def __init__(
        self,
        *,
        protected: Sequence[ArithmeticEvent] | None = None,
        held_out: Sequence[ArithmeticEvent] | None = None,
        workers: int = 1,
    ) -> None:
        self.protected = tuple(protected or protected_manifest())
        self.held_out = tuple(held_out or held_out_manifest())
        self.workers = max(1, min(workers, 2))

    @staticmethod
    def _measure(
        fabric: PathwayFabric,
        event: ArithmeticEvent,
        weights: tuple[float, float, float] | None,
    ) -> tuple[int, int, float]:
        inference = fabric.infer(event, readout_weights=weights)
        if inference.answer is None:
            return (0, 0, float(abs(event.target)))
        return (
            1,
            int(inference.answer == event.target),
            float(abs(inference.answer - event.target)),
        )

    def evaluate(
        self,
        fabric: PathwayFabric,
        events: Iterable[ArithmeticEvent],
        weights: tuple[float, float, float] | None = None,
    ) -> Metrics:
        """Measure a fixed manifest, optionally with at most two workers.

        Inference microsteps remain serial within each event. Parallel workers
        are only for independent evaluator cases, so users can compare the two
        forms of work rather than unknowingly overloading the device.
        """

        cases = tuple(events)
        if self.workers == 1:
            measurements = [self._measure(fabric, event, weights) for event in cases]
        else:
            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                measurements = list(
                    executor.map(
                        lambda event: self._measure(fabric, event, weights),
                        cases,
                    )
                )
        answered = sum(item[0] for item in measurements)
        correct = sum(item[1] for item in measurements)
        error = sum(item[2] for item in measurements)
        return Metrics(
            cases=len(cases),
            answered=answered,
            correct=correct,
            total_absolute_error=error,
        )

    def assess(
        self,
        fabric: PathwayFabric,
        event: ArithmeticEvent,
        candidate_weights: tuple[float, float, float],
        parent_inference: Inference,
    ) -> CandidateAssessment:
        """Decide a candidate with a fixed, external policy."""

        parent_protected = self.evaluate(fabric, self.protected)
        candidate_protected = self.evaluate(fabric, self.protected, candidate_weights)
        parent_held_out = self.evaluate(fabric, self.held_out)
        candidate_held_out = self.evaluate(fabric, self.held_out, candidate_weights)
        parent_raw = parent_inference.raw_value
        if parent_raw is None:
            parent_error = float(abs(event.target))
        else:
            parent_error = abs(parent_raw - event.target)
        candidate_raw = fabric.readout.raw_value(event, candidate_weights)
        candidate_error = abs(candidate_raw - event.target)
        accepted = (
            candidate_error < parent_error
            and candidate_protected.exact_accuracy >= parent_protected.exact_accuracy
            and candidate_protected.mean_absolute_error
            <= parent_protected.mean_absolute_error
            and candidate_held_out.mean_absolute_error
            <= parent_held_out.mean_absolute_error
        )
        return CandidateAssessment(
            parent_protected=parent_protected,
            candidate_protected=candidate_protected,
            parent_held_out=parent_held_out,
            candidate_held_out=candidate_held_out,
            current_parent_error=parent_error,
            current_candidate_error=candidate_error,
            accepted=accepted,
        )


class VerifierGatedLearner:
    """Turns exact arithmetic feedback into safe, tested path updates."""

    def __init__(self, evaluator: IndependentEvaluator, learning_rate: float = 0.20) -> None:
        self.evaluator = evaluator
        self.learning_rate = learning_rate

    def observe(self, fabric: PathwayFabric, inference: Inference) -> Feedback:
        """Apply one external verifier result without mutating the evaluator."""

        trace_strength = fabric.record_eligibility(inference)
        if inference.answer is None:
            return Feedback(
                valence=FeedbackValence.NEUTRAL,
                verdict="abstained; no answer was claimed",
                candidate_action="no update; preserve uncertainty",
                promoted=False,
                parent_protected=None,
                candidate_protected=None,
                parent_held_out=None,
                candidate_held_out=None,
            )

        if inference.answer == inference.event.target:
            fabric.confirm_positive(inference)
            return Feedback(
                valence=FeedbackValence.POSITIVE,
                verdict=f"verified correct: {inference.answer}",
                candidate_action="increase support on the active paths",
                promoted=False,
                parent_protected=None,
                candidate_protected=None,
                parent_held_out=None,
                candidate_held_out=None,
            )

        candidate_weights = fabric.readout.candidate_weights(
            inference.event,
            inference.event.target,
            trace_strength,
            self.learning_rate * fabric.readout.plasticity,
        )
        assessment = self.evaluator.assess(
            fabric,
            inference.event,
            candidate_weights,
            inference,
        )
        if assessment.accepted:
            fabric.readout.promote(candidate_weights)
            action = "candidate readout path promoted after protected + held-out checks"
        else:
            action = "candidate rejected; parent paths remain unchanged"
        return Feedback(
            valence=FeedbackValence.NEGATIVE,
            verdict=(
                f"verified incorrect: predicted {inference.answer}, "
                f"target {inference.event.target}"
            ),
            candidate_action=action,
            promoted=assessment.accepted,
            parent_protected=assessment.parent_protected,
            candidate_protected=assessment.candidate_protected,
            parent_held_out=assessment.parent_held_out,
            candidate_held_out=assessment.candidate_held_out,
        )
