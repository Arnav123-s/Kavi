"""A small textbook-backed concept pathway core for Kavi.

This is deliberately not a general language model.  It learns two compact
concept prototypes from a reviewed local lesson: whether a mathematical
notation is an expression or a relation.  Source examples live only in an
ignored local lesson workspace.  The persistent model stores numeric feature
centroids and support counts, never the source extract or its example strings.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
import math
import re
from typing import Iterable, Sequence


class ConceptKind(str, Enum):
    """The two textbook concepts in the first bounded source lesson."""

    EXPRESSION = "expression"
    RELATION = "relation"


_FEATURE_COUNT = 5
_ALLOWED_NOTATION = re.compile(r"[0-9A-Za-z+\-*/=<>()[\]·÷\s]+\Z")


def _compact_notation(notation: str) -> str:
    """Validate a small algebraic notation subset without interpreting prose."""

    if not isinstance(notation, str) or not notation.strip():
        raise ValueError("A textbook event needs non-empty mathematical notation.")
    if not _ALLOWED_NOTATION.fullmatch(notation):
        raise ValueError("Notation contains a character outside the first lesson subset.")
    return notation.replace("·", "*").replace("÷", "/").replace(" ", "")


def notation_kind(notation: str) -> ConceptKind:
    """Return the independently verifiable structural kind of a notation input."""

    compact = _compact_notation(notation)
    relation_count = sum(compact.count(symbol) for symbol in ("=", "<", ">"))
    if relation_count > 1:
        raise ValueError("The first lesson accepts at most one relation sign.")
    return ConceptKind.RELATION if relation_count else ConceptKind.EXPRESSION


def notation_features(notation: str) -> tuple[float, ...]:
    """Produce bounded structural facets without retaining source words."""

    compact = _compact_notation(notation)
    relation_count = sum(compact.count(symbol) for symbol in ("=", "<", ">"))
    arithmetic_count = sum(compact.count(symbol) for symbol in ("+", "-", "*", "/"))
    variable_count = sum(character.isalpha() for character in compact)
    digit_count = sum(character.isdigit() for character in compact)
    return (
        float(relation_count),
        min(arithmetic_count, 4) / 4.0,
        min(variable_count, 4) / 4.0,
        min(digit_count, 4) / 4.0,
        min(len(compact), 16) / 16.0,
    )


def _numeric_value(expression: str) -> Fraction:
    """Safely evaluate a variable-free arithmetic expression exactly."""

    compact = _compact_notation(expression)
    if any(character.isalpha() for character in compact):
        raise ValueError("A variable-free value cannot contain a variable.")
    if any(symbol in compact for symbol in ("=", "<", ">")):
        raise ValueError("A numeric expression cannot contain a relation sign.")
    tree = ast.parse(compact, mode="eval")

    def visit(node: ast.AST) -> Fraction:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return Fraction(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
            return visit(node.operand)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -visit(node.operand)
        if isinstance(node, ast.BinOp):
            left = visit(node.left)
            right = visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise ValueError("Division by zero is undefined.")
                return left / right
        raise ValueError("Unsupported arithmetic form in the first lesson subset.")

    return visit(tree)


def _format_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def semantic_outcome(notation: str) -> str:
    """Independently verify a limited exact result for the source notation."""

    compact = _compact_notation(notation)
    kind = notation_kind(compact)
    if kind is ConceptKind.EXPRESSION:
        if any(character.isalpha() for character in compact):
            return "value is unknown without variable values"
        try:
            return f"value={_format_fraction(_numeric_value(compact))}"
        except (SyntaxError, ValueError):
            return "value is outside the first exact evaluator"

    relation_match = re.search(r"[=<>]", compact)
    assert relation_match is not None
    operator = relation_match.group(0)
    left = compact[: relation_match.start()]
    right = compact[relation_match.end() :]
    if not left or not right:
        return "truth is outside the first exact evaluator"
    if any(character.isalpha() for character in compact):
        return "truth is unknown without variable values"
    try:
        left_value = _numeric_value(left)
        right_value = _numeric_value(right)
    except (SyntaxError, ValueError):
        return "truth is outside the first exact evaluator"
    truth = {
        "=": left_value == right_value,
        "<": left_value < right_value,
        ">": left_value > right_value,
    }[operator]
    return f"truth={str(truth).lower()}"


@dataclass(frozen=True, slots=True)
class TextbookEvent:
    """One exact symbolic example from a locally reviewed textbook lesson."""

    event_id: str
    notation: str
    target: ConceptKind
    correlation_id: str

    def __post_init__(self) -> None:
        verified_kind = notation_kind(self.notation)
        if verified_kind is not self.target:
            raise ValueError(
                "The declared source label disagrees with the independent structure verifier."
            )


@dataclass(frozen=True, slots=True)
class ConceptPrototype:
    """A compressed numeric pattern for one verified textbook concept."""

    center: tuple[float, ...] = (0.0,) * _FEATURE_COUNT
    support: int = 0

    def __post_init__(self) -> None:
        if len(self.center) != _FEATURE_COUNT:
            raise ValueError("A concept prototype needs the declared feature count.")

    def updated(self, features: Sequence[float]) -> "ConceptPrototype":
        """Absorb verified structural features without retaining the notation."""

        if len(features) != _FEATURE_COUNT:
            raise ValueError("Unexpected textbook feature count.")
        next_support = self.support + 1
        next_center = tuple(
            center + (feature - center) / next_support
            for center, feature in zip(self.center, features)
        )
        return ConceptPrototype(center=next_center, support=next_support)


@dataclass(frozen=True, slots=True)
class TextbookConceptState:
    """The full persistent state for the first source-backed concept core."""

    expression: ConceptPrototype = ConceptPrototype()
    relation: ConceptPrototype = ConceptPrototype()

    def prototype_for(self, kind: ConceptKind) -> ConceptPrototype:
        return self.expression if kind is ConceptKind.EXPRESSION else self.relation

    def with_prototype(
        self,
        kind: ConceptKind,
        prototype: ConceptPrototype,
    ) -> "TextbookConceptState":
        if kind is ConceptKind.EXPRESSION:
            return TextbookConceptState(expression=prototype, relation=self.relation)
        return TextbookConceptState(expression=self.expression, relation=prototype)

    @property
    def total_support(self) -> int:
        return self.expression.support + self.relation.support


@dataclass(frozen=True, slots=True)
class TextbookConceptInference:
    """Inspectable result from the first textbook concept pathway."""

    event: TextbookEvent
    prediction: ConceptKind | None
    confidence: float
    features: tuple[float, ...]
    expression_distance: float | None
    relation_distance: float | None
    semantic_outcome: str
    active_pipe_ids: tuple[str, ...]
    abstain_reason: str | None = None


@dataclass(frozen=True, slots=True)
class TextbookConceptMetrics:
    """Fixed manifest metrics for the source-backed concept core."""

    cases: int
    answered: int
    correct: int
    errors: int

    @property
    def exact_accuracy(self) -> float:
        return self.correct / self.cases if self.cases else 0.0

    @property
    def coverage(self) -> float:
        return self.answered / self.cases if self.cases else 0.0

    @property
    def mean_error(self) -> float:
        return self.errors / self.cases if self.cases else 0.0


@dataclass(frozen=True, slots=True)
class TextbookCandidateAssessment:
    """Independent evidence for one source-backed candidate state."""

    candidate_state: TextbookConceptState
    parent_current: TextbookConceptMetrics
    candidate_current: TextbookConceptMetrics
    parent_protected: TextbookConceptMetrics
    candidate_protected: TextbookConceptMetrics
    parent_held_out: TextbookConceptMetrics
    candidate_held_out: TextbookConceptMetrics
    accepted: bool


class TextbookConceptPathwayCore:
    """Compact model for a single reviewed textbook concept distinction."""

    PIPE_IDS = (
        "textbook-notation-ingress",
        "structural-facets",
        "concept-prototype-readout",
        "verified-response",
    )
    MINIMUM_CONFIDENCE = 0.02

    def __init__(self) -> None:
        self.state = TextbookConceptState()
        self.verified_promotions = 0

    @staticmethod
    def _state_complete(state: TextbookConceptState) -> bool:
        return state.expression.support > 0 and state.relation.support > 0

    @staticmethod
    def _distance(features: Sequence[float], prototype: ConceptPrototype) -> float:
        return math.sqrt(
            sum((feature - center) ** 2 for feature, center in zip(features, prototype.center))
        )

    def infer(
        self,
        event: TextbookEvent,
        *,
        state: TextbookConceptState | None = None,
    ) -> TextbookConceptInference:
        """Route a textbook notation through the hard concept path or abstain."""

        selected = self.state if state is None else state
        features = notation_features(event.notation)
        outcome = semantic_outcome(event.notation)
        if not self._state_complete(selected):
            return TextbookConceptInference(
                event=event,
                prediction=None,
                confidence=0.0,
                features=features,
                expression_distance=None,
                relation_distance=None,
                semantic_outcome=outcome,
                active_pipe_ids=self.PIPE_IDS,
                abstain_reason="One or more textbook concept prototypes lack verified support.",
            )
        expression_distance = self._distance(features, selected.expression)
        relation_distance = self._distance(features, selected.relation)
        prediction = (
            ConceptKind.EXPRESSION
            if expression_distance < relation_distance
            else ConceptKind.RELATION
        )
        distance_sum = expression_distance + relation_distance
        confidence = (
            abs(expression_distance - relation_distance) / distance_sum
            if distance_sum > 0.0
            else 0.0
        )
        if confidence < self.MINIMUM_CONFIDENCE:
            return TextbookConceptInference(
                event=event,
                prediction=None,
                confidence=confidence,
                features=features,
                expression_distance=expression_distance,
                relation_distance=relation_distance,
                semantic_outcome=outcome,
                active_pipe_ids=self.PIPE_IDS,
                abstain_reason="Concept prototype distances are too similar to claim a label.",
            )
        return TextbookConceptInference(
            event=event,
            prediction=prediction,
            confidence=confidence,
            features=features,
            expression_distance=expression_distance,
            relation_distance=relation_distance,
            semantic_outcome=outcome,
            active_pipe_ids=self.PIPE_IDS,
        )

    def candidate_from(self, events: Iterable[TextbookEvent]) -> TextbookConceptState:
        """Build a child state from verified source events only."""

        candidate = self.state
        for event in events:
            prototype = candidate.prototype_for(event.target).updated(
                notation_features(event.notation)
            )
            candidate = candidate.with_prototype(event.target, prototype)
        return candidate

    def promote(self, state: TextbookConceptState) -> None:
        """Replace the parent state only after the independent gates pass."""

        self.state = state
        self.verified_promotions += 1

    def resource_ledger(self) -> dict[str, int]:
        """Report model-state estimates without counting the host or source files."""

        persistent_scalars = 2 * (_FEATURE_COUNT + 1) + 1
        return {
            "persistent_scalars": persistent_scalars,
            "estimated_persistent_bytes": persistent_scalars * 8,
            "active_pipes": len(self.PIPE_IDS),
            "estimated_transient_bytes": (_FEATURE_COUNT + 3) * 8,
        }


class TextbookConceptEvaluator:
    """Independent fixed-manifest evaluation for the source concept core."""

    def __init__(
        self,
        *,
        protected: Sequence[TextbookEvent],
        held_out: Sequence[TextbookEvent],
    ) -> None:
        self.protected = tuple(protected)
        self.held_out = tuple(held_out)

    def evaluate(
        self,
        core: TextbookConceptPathwayCore,
        events: Iterable[TextbookEvent],
        *,
        state: TextbookConceptState | None = None,
    ) -> TextbookConceptMetrics:
        """Score a state without changing it or retaining evaluated source text."""

        cases = answered = correct = errors = 0
        for event in events:
            cases += 1
            inference = core.infer(event, state=state)
            if inference.prediction is not None:
                answered += 1
            if inference.prediction is event.target:
                correct += 1
            else:
                errors += 1
        return TextbookConceptMetrics(cases, answered, correct, errors)

    def assess(
        self,
        core: TextbookConceptPathwayCore,
        events: Sequence[TextbookEvent],
    ) -> TextbookCandidateAssessment:
        """Assess a source-derived candidate against unchanged held-out events."""

        candidate_state = core.candidate_from(events)
        parent_current = self.evaluate(core, events)
        candidate_current = self.evaluate(core, events, state=candidate_state)
        parent_protected = self.evaluate(core, self.protected)
        candidate_protected = self.evaluate(core, self.protected, state=candidate_state)
        parent_held_out = self.evaluate(core, self.held_out)
        candidate_held_out = self.evaluate(core, self.held_out, state=candidate_state)
        accepted = (
            candidate_state.total_support > core.state.total_support
            and candidate_current.mean_error <= parent_current.mean_error
            and candidate_current.coverage >= parent_current.coverage
            and candidate_protected.mean_error <= parent_protected.mean_error
            and candidate_held_out.mean_error <= parent_held_out.mean_error
        )
        return TextbookCandidateAssessment(
            candidate_state=candidate_state,
            parent_current=parent_current,
            candidate_current=candidate_current,
            parent_protected=parent_protected,
            candidate_protected=candidate_protected,
            parent_held_out=parent_held_out,
            candidate_held_out=candidate_held_out,
            accepted=accepted,
        )


def response_text(inference: TextbookConceptInference) -> str:
    """Render the bounded, independently checked model response for the CLI."""

    if inference.prediction is None:
        return f"abstain; {inference.abstain_reason or 'no verified concept answer'}"
    return f"{inference.prediction.value}; {inference.semantic_outcome}"
