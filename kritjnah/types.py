"""Small, explicit data contracts for the pathway fabric.

The runtime does not store raw lessons in the model. A current event creates
temporary typed facets; verified learning changes pathway parameters only after
an isolated candidate passes its declared checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SignalType(str, Enum):
    """Strict information contracts accepted by pipes."""

    QUANTITY = "quantity"
    RELATION = "relation"


class Operation(str, Enum):
    """The first exact, small curriculum domain."""

    ADD = "add"
    SUBTRACT = "subtract"

    @property
    def sign(self) -> int:
        return 1 if self is Operation.ADD else -1

    @property
    def symbol(self) -> str:
        return "+" if self is Operation.ADD else "−"


class FeedbackValence(str, Enum):
    """Feedback control paths, not a sentiment classifier."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass(frozen=True, slots=True)
class ArithmeticEvent:
    """One generated, exact arithmetic question.

    Conflicted deliberately creates a phase conflict in the relation facet. It
    is a test input for uncertainty handling, not a claim that the mathematical
    statement itself is ambiguous.
    """

    event_id: str
    left: int
    right: int
    operation: Operation
    correlation_id: str
    conflicted: bool = False

    @property
    def target(self) -> int:
        return self.left + self.operation.sign * self.right

    @property
    def text(self) -> str:
        return f"{self.left} {self.operation.symbol} {self.right}"


@dataclass(frozen=True, slots=True)
class Information:
    """A typed event facet travelling through one or more hard pipes."""

    event_id: str
    correlation_id: str
    kind: SignalType
    payload: tuple[float, ...]
    operation: Operation


@dataclass(frozen=True, slots=True)
class Signal:
    """A temporary amplitude travelling through a route.

    Amplitude is an ordinary complex number held by classical software. Its
    phase lets a typed join distinguish constructive and destructive
    interference; it does not represent a physical qubit.
    """

    information: Information
    amplitude: complex
    pipe_ids: tuple[str, ...]
    route_cost: float


@dataclass(frozen=True, slots=True)
class Route:
    """The deterministic lowest-cost compatible route for one typed facet."""

    pipe_ids: tuple[str, ...]
    total_cost: float


@dataclass(frozen=True, slots=True)
class Inference:
    """Observable result of one bounded pathway-settling attempt."""

    event: ArithmeticEvent
    answer: int | None
    raw_value: float | None
    confidence: float
    uncertainty: float
    interference: float
    quantity_signal: Signal | None
    relation_signal: Signal | None
    abstain_reason: str | None = None

    @property
    def active_pipe_ids(self) -> tuple[str, ...]:
        ids: list[str] = []
        for signal in (self.quantity_signal, self.relation_signal):
            if signal is not None:
                ids.extend(signal.pipe_ids)
        return tuple(ids)


@dataclass(frozen=True, slots=True)
class Metrics:
    """A compact evaluator report over a fixed manifest."""

    cases: int
    answered: int
    correct: int
    total_absolute_error: float

    @property
    def exact_accuracy(self) -> float:
        return self.correct / self.cases if self.cases else 0.0

    @property
    def coverage(self) -> float:
        return self.answered / self.cases if self.cases else 0.0

    @property
    def mean_absolute_error(self) -> float:
        return self.total_absolute_error / self.cases if self.cases else 0.0


@dataclass(frozen=True, slots=True)
class Feedback:
    """The verifier's outcome and candidate-promotion decision."""

    valence: FeedbackValence
    verdict: str
    candidate_action: str
    promoted: bool
    parent_protected: Metrics | None
    candidate_protected: Metrics | None
    parent_held_out: Metrics | None
    candidate_held_out: Metrics | None
