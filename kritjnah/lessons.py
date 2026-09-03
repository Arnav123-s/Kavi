"""Trusted, structured explanations for the first learning curriculum.

The learner does not treat arbitrary prose as proof. A lesson carries a
machine-checkable rule identifier, its verified target, and the explanatory
parameters that the small arithmetic domain can safely use.
"""

from __future__ import annotations

from dataclasses import dataclass

from .types import ArithmeticEvent, Operation


@dataclass(frozen=True, slots=True)
class VerifiedLesson:
    """One exact correction plus a scoped explanation of why it is correct."""

    event: ArithmeticEvent
    rule_id: str
    explanation: str
    target_weights: tuple[float, float, float]

    @classmethod
    def for_event(cls, event: ArithmeticEvent) -> "VerifiedLesson":
        """Create a lesson from a locally checked arithmetic rule."""

        if event.operation is Operation.ADD:
            explanation = (
                "Addition combines the first quantity with the second quantity. "
                "The relation path marks the second quantity as positive."
            )
            rule_id = "quantity-plus-positive-relation"
        else:
            explanation = (
                "Subtraction starts with the first quantity and removes the "
                "second quantity. The relation path marks the second quantity "
                "as negative."
            )
            rule_id = "quantity-plus-signed-relation"
        return cls(
            event=event,
            rule_id=rule_id,
            explanation=explanation,
            target_weights=(1.0, 1.0, 0.0),
        )

    def is_valid(self) -> bool:
        """Check that this small-domain explanation matches its exact target."""

        left, signed_right, bias = (
            float(self.event.left),
            float(self.event.operation.sign * self.event.right),
            1.0,
        )
        reconstructed = (
            self.target_weights[0] * left
            + self.target_weights[1] * signed_right
            + self.target_weights[2] * bias
        )
        return reconstructed == float(self.event.target)
