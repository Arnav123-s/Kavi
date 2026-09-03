"""A small trainable symbol pathway core for Kavi's first curriculum stage.

The core deliberately learns a compressed pattern instead of retaining a table
of presented glyphs.  A glyph travels through one fixed typed path:

    glyph -> normalized codepoint coordinate -> class prototype readout

The only persistent learned state is one centroid and support count for each
class.  Candidate centroids are built from a finite batch, evaluated on fixed
protected and held-out symbols, and promoted only when they satisfy the
predeclared gate.  This is a narrow foundation experiment, not language
understanding or a general text model.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence


class GlyphKind(str, Enum):
    """The two exact categories used in the first generated symbol lesson."""

    LETTER = "letter"
    DIGIT = "digit"


@dataclass(frozen=True, slots=True)
class SymbolEvent:
    """One generated glyph classification lesson with an exact teacher label."""

    event_id: str
    glyph: str
    target: GlyphKind
    correlation_id: str

    def __post_init__(self) -> None:
        if len(self.glyph) != 1 or ord(self.glyph) > 127:
            raise ValueError("The stage-1 symbol core accepts one ASCII glyph.")


@dataclass(frozen=True, slots=True)
class Prototype:
    """A compressed class pattern: one coordinate mean and its evidence count."""

    center: float = 0.0
    support: int = 0

    def updated(self, coordinate: float) -> "Prototype":
        """Absorb one verified coordinate without retaining the raw glyph."""

        next_support = self.support + 1
        next_center = self.center + (coordinate - self.center) / next_support
        return Prototype(center=next_center, support=next_support)


@dataclass(frozen=True, slots=True)
class SymbolState:
    """The full persistent model state for this tiny first symbol core."""

    letter: Prototype = Prototype()
    digit: Prototype = Prototype()

    def prototype_for(self, kind: GlyphKind) -> Prototype:
        return self.letter if kind is GlyphKind.LETTER else self.digit

    def with_prototype(self, kind: GlyphKind, prototype: Prototype) -> "SymbolState":
        if kind is GlyphKind.LETTER:
            return SymbolState(letter=prototype, digit=self.digit)
        return SymbolState(letter=self.letter, digit=prototype)


@dataclass(frozen=True, slots=True)
class SymbolInference:
    """An inspectable inference result for a single hard symbol path."""

    event: SymbolEvent
    prediction: GlyphKind | None
    confidence: float
    coordinate: float
    letter_distance: float | None
    digit_distance: float | None
    active_pipe_ids: tuple[str, ...]
    abstain_reason: str | None = None


@dataclass(frozen=True, slots=True)
class SymbolMetrics:
    """Fixed-manifest measurements for the symbol core."""

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
class SymbolCandidateAssessment:
    """Before/after evidence for an isolated symbol-state candidate."""

    candidate_state: SymbolState
    parent_current: SymbolMetrics
    candidate_current: SymbolMetrics
    parent_protected: SymbolMetrics
    candidate_protected: SymbolMetrics
    parent_held_out: SymbolMetrics
    candidate_held_out: SymbolMetrics
    accepted: bool


class SymbolPathwayCore:
    """A model-shaped hard pathway with compact local prototype learning.

    The core does not keep a dictionary of taught characters.  It retains only
    two class centroids and their support counts.  That makes this a useful
    falsifiable test of pattern compression, while its deliberately tiny scope
    makes it unsuitable for claims about language or general intelligence.
    """

    PIPE_IDS = ("glyph-ingress", "ordinal-coordinate", "prototype-readout")

    def __init__(self) -> None:
        self.state = SymbolState()
        self.verified_support = 0

    @staticmethod
    def coordinate(glyph: str) -> float:
        """Map one ASCII glyph to a bounded numeric signal for the hard path."""

        if len(glyph) != 1 or ord(glyph) > 127:
            raise ValueError("Expected one ASCII glyph.")
        return ord(glyph) / 127.0

    @staticmethod
    def _state_complete(state: SymbolState) -> bool:
        return state.letter.support > 0 and state.digit.support > 0

    def infer(
        self,
        event: SymbolEvent,
        *,
        state: SymbolState | None = None,
    ) -> SymbolInference:
        """Route a glyph through the core and either classify or abstain."""

        selected = self.state if state is None else state
        coordinate = self.coordinate(event.glyph)
        if not self._state_complete(selected):
            return SymbolInference(
                event=event,
                prediction=None,
                confidence=0.0,
                coordinate=coordinate,
                letter_distance=None,
                digit_distance=None,
                active_pipe_ids=self.PIPE_IDS,
                abstain_reason="One or more class prototypes lack verified support.",
            )

        letter_distance = abs(coordinate - selected.letter.center)
        digit_distance = abs(coordinate - selected.digit.center)
        prediction = (
            GlyphKind.LETTER if letter_distance < digit_distance else GlyphKind.DIGIT
        )
        distance_sum = letter_distance + digit_distance
        confidence = (
            abs(letter_distance - digit_distance) / distance_sum
            if distance_sum > 0.0
            else 0.0
        )
        if confidence < 0.02:
            return SymbolInference(
                event=event,
                prediction=None,
                confidence=confidence,
                coordinate=coordinate,
                letter_distance=letter_distance,
                digit_distance=digit_distance,
                active_pipe_ids=self.PIPE_IDS,
                abstain_reason="Prototype distances are too similar to claim a class.",
            )
        return SymbolInference(
            event=event,
            prediction=prediction,
            confidence=confidence,
            coordinate=coordinate,
            letter_distance=letter_distance,
            digit_distance=digit_distance,
            active_pipe_ids=self.PIPE_IDS,
        )

    def candidate_from(self, events: Iterable[SymbolEvent]) -> SymbolState:
        """Build a child state through verified local centroid updates only."""

        candidate = self.state
        for event in events:
            coordinate = self.coordinate(event.glyph)
            prototype = candidate.prototype_for(event.target).updated(coordinate)
            candidate = candidate.with_prototype(event.target, prototype)
        return candidate

    def promote(self, state: SymbolState) -> None:
        """Replace the parent state only after an independent acceptance gate."""

        self.state = state
        self.verified_support += 1

    def resource_ledger(self) -> dict[str, int]:
        """Count the small persistent model state, not the full host process."""

        persistent_scalars = 5
        return {
            "persistent_scalars": persistent_scalars,
            "estimated_persistent_bytes": persistent_scalars * 8,
            "active_pipes": len(self.PIPE_IDS),
            "estimated_transient_bytes": 3 * 8,
        }


class SymbolEvaluator:
    """Independent fixed-manifest evaluator for candidate symbol states."""

    def __init__(
        self,
        *,
        protected: Sequence[SymbolEvent],
        held_out: Sequence[SymbolEvent],
    ) -> None:
        self.protected = tuple(protected)
        self.held_out = tuple(held_out)

    def evaluate(
        self,
        core: SymbolPathwayCore,
        events: Iterable[SymbolEvent],
        *,
        state: SymbolState | None = None,
    ) -> SymbolMetrics:
        """Score a state without changing it or retaining evaluated events."""

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
        return SymbolMetrics(cases, answered, correct, errors)

    def assess(
        self,
        core: SymbolPathwayCore,
        events: Sequence[SymbolEvent],
    ) -> SymbolCandidateAssessment:
        """Test a finite child candidate against unchanged parent manifests."""

        candidate_state = core.candidate_from(events)
        parent_current = self.evaluate(core, events)
        candidate_current = self.evaluate(core, events, state=candidate_state)
        parent_protected = self.evaluate(core, self.protected)
        candidate_protected = self.evaluate(core, self.protected, state=candidate_state)
        parent_held_out = self.evaluate(core, self.held_out)
        candidate_held_out = self.evaluate(core, self.held_out, state=candidate_state)
        accepted = (
            candidate_current.mean_error < parent_current.mean_error
            and candidate_protected.mean_error <= parent_protected.mean_error
            and candidate_held_out.mean_error <= parent_held_out.mean_error
        )
        return SymbolCandidateAssessment(
            candidate_state=candidate_state,
            parent_current=parent_current,
            candidate_current=candidate_current,
            parent_protected=parent_protected,
            candidate_protected=candidate_protected,
            parent_held_out=parent_held_out,
            candidate_held_out=candidate_held_out,
            accepted=accepted,
        )
