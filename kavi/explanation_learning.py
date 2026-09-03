"""Verifier-gated learning from structured explanations.

This is a separate experiment from the original target-only stage. It keeps
the independent evaluator and frozen-parent rule, but a trusted lesson can
teach the scope-specific transformation rather than only a single answer.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .graph import PathwayFabric
from .learning import CandidateAssessment, IndependentEvaluator
from .lessons import VerifiedLesson
from .types import Feedback, FeedbackValence, Inference


@dataclass(frozen=True, slots=True)
class ExplanationAssessment:
    """Candidate result under the predeclared explanation-learning policy."""

    candidate: CandidateAssessment
    promoted: bool


class ExplanationGatedLearner:
    """Use a verified rule explanation to guide, but never force, a candidate."""

    def __init__(
        self,
        evaluator: IndependentEvaluator,
        *,
        learning_rate: float = 0.20,
        rule_blend: float = 0.35,
        established_accuracy_floor: float = 0.50,
    ) -> None:
        if not 0.0 < rule_blend < 1.0:
            raise ValueError("rule_blend must be between zero and one")
        if not 0.0 <= established_accuracy_floor <= 1.0:
            raise ValueError("established_accuracy_floor must be in [0, 1]")
        self.evaluator = evaluator
        self.learning_rate = learning_rate
        self.rule_blend = rule_blend
        self.established_accuracy_floor = established_accuracy_floor

    def _candidate_from_lesson(
        self,
        fabric: PathwayFabric,
        lesson: VerifiedLesson,
        trace_strength: float,
    ) -> tuple[float, float, float]:
        """Blend local error credit with the verified scoped rule."""

        local_candidate = fabric.readout.candidate_weights(
            lesson.event,
            lesson.event.target,
            trace_strength,
            self.learning_rate * fabric.readout.plasticity,
        )
        explanation_strength = min(
            0.60,
            self.rule_blend * (1.0 + 0.02 * min(trace_strength, 10.0)),
        )
        return tuple(
            local + explanation_strength * (rule - local)
            for local, rule in zip(local_candidate, lesson.target_weights)
        )

    def _approve(self, assessment: CandidateAssessment) -> bool:
        """Protect mature exact skills while allowing early continuous learning.

        A lone rounded exact answer early in learning can be accidental. Before
        the protected manifest reaches the declared floor, continuous protected
        and held-out error are the retention signal. After that, exact protected
        accuracy may not fall.
        """

        parent = assessment.parent_protected
        candidate = assessment.candidate_protected
        established = parent.exact_accuracy >= self.established_accuracy_floor
        preserves_exact = not established or (
            candidate.exact_accuracy >= parent.exact_accuracy
        )
        return (
            assessment.current_candidate_error < assessment.current_parent_error
            and candidate.mean_absolute_error <= parent.mean_absolute_error
            and assessment.candidate_held_out.mean_absolute_error
            <= assessment.parent_held_out.mean_absolute_error
            and preserves_exact
        )

    def observe(
        self,
        fabric: PathwayFabric,
        inference: Inference,
        lesson: VerifiedLesson,
    ) -> Feedback:
        """Learn from a valid explanation even when the model abstains.

        An abstention remains an honest output. It does not block a trusted,
        independent teacher from proposing a candidate for the active paths.
        """

        if lesson.event != inference.event:
            raise ValueError("The lesson must refer to the inferred event.")
        if not lesson.is_valid():
            raise ValueError("Refusing an explanation that fails its local verifier.")

        trace_strength = fabric.record_eligibility(inference)
        if inference.answer == inference.event.target:
            fabric.confirm_positive(inference)
            return Feedback(
                valence=FeedbackValence.POSITIVE,
                verdict=f"verified correct: {inference.answer}",
                candidate_action=(
                    f"{lesson.rule_id}: verified rule match; "
                    "increase support on the active paths"
                ),
                promoted=False,
                parent_protected=None,
                candidate_protected=None,
                parent_held_out=None,
                candidate_held_out=None,
            )

        parent_raw = (
            inference.raw_value
            if inference.raw_value is not None
            else fabric.readout.raw_value(inference.event)
        )
        assessment_inference = replace(inference, raw_value=parent_raw)
        candidate_weights = self._candidate_from_lesson(
            fabric,
            lesson,
            trace_strength,
        )
        candidate = self.evaluator.assess(
            fabric,
            inference.event,
            candidate_weights,
            assessment_inference,
        )
        promoted = self._approve(candidate)
        if promoted:
            fabric.readout.promote(candidate_weights)
            action = (
                f"{lesson.rule_id}: explanation-guided candidate promoted "
                "after protected and held-out checks"
            )
        else:
            action = (
                f"{lesson.rule_id}: candidate rejected; parent paths remain unchanged"
            )
        valence = (
            FeedbackValence.NEUTRAL
            if inference.answer is None
            else FeedbackValence.NEGATIVE
        )
        prediction = "abstain" if inference.answer is None else str(inference.answer)
        return Feedback(
            valence=valence,
            verdict=(
                f"verified lesson: predicted {prediction}, "
                f"target {inference.event.target}"
            ),
            candidate_action=action,
            promoted=promoted,
            parent_protected=candidate.parent_protected,
            candidate_protected=candidate.candidate_protected,
            parent_held_out=candidate.parent_held_out,
            candidate_held_out=candidate.candidate_held_out,
        )
