"""Exact Unicode signals and a tiny generated script-pathway model for Kavi.

This module deliberately separates two ideas that are easy to blur together:

* ``UnicodeSignalContract`` preserves one Unicode scalar exactly and reports
  metadata without replacing the input with a normalized form.
* ``UnicodeScriptPathwayCore`` is a small trainable prototype experiment over
  a declared, generated set of individual glyphs.  It is not a Unicode Script
  implementation, a language detector, or a text learner.

The learned state is one code-point-coordinate centroid and support count for
each of eleven explicitly declared pathways.  It contains no source text,
word list, glyph-to-label lookup table, or downloaded Unicode data file.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import unicodedata
from typing import Iterable, Sequence


MAX_UNICODE_SCALAR = 0x10FFFF


@dataclass(frozen=True, slots=True)
class UnicodeScalarSignal:
    """One preserved Unicode scalar and non-destructive local metadata."""

    glyph: str
    code_point: int
    category: str
    name: str | None
    nfc_matches_input: bool


class UnicodeSignalContract:
    """Validate and inspect exactly one Unicode scalar without rewriting it.

    Normalization is deliberately exposed only as an equality observation.  A
    later sequence-aware layer may use an explicitly chosen normalization view,
    but this ingress layer always preserves ``glyph`` and its exact code point.
    """

    PIPE_ID = "unicode-scalar-ingress"

    @staticmethod
    def inspect(glyph: str) -> UnicodeScalarSignal:
        """Return an exact signal for one scalar, rejecting non-scalars only."""

        if not isinstance(glyph, str) or len(glyph) != 1:
            raise ValueError("Expected exactly one Unicode scalar.")
        code_point = ord(glyph)
        if 0xD800 <= code_point <= 0xDFFF:
            raise ValueError("Unicode surrogate code points are not scalar values.")
        return UnicodeScalarSignal(
            glyph=glyph,
            code_point=code_point,
            category=unicodedata.category(glyph),
            name=unicodedata.name(glyph, None),
            nfc_matches_input=unicodedata.normalize("NFC", glyph) == glyph,
        )


class ScriptKind(str, Enum):
    """The bounded generated pathways used in this experiment.

    These labels name script-oriented prototype lanes, not languages or people.
    A prediction is meaningful only on the declared generated evaluation set.
    """

    LATIN = "latin"
    GREEK = "greek"
    CYRILLIC = "cyrillic"
    ARABIC = "arabic"
    DEVANAGARI = "devanagari"
    BENGALI = "bengali"
    TAMIL = "tamil"
    HIRAGANA = "hiragana"
    KATAKANA = "katakana"
    HAN = "han"
    HANGUL = "hangul"


@dataclass(frozen=True, slots=True)
class ScriptEvent:
    """One generated glyph lesson and its declared exact pathway label."""

    event_id: str
    glyph: str
    target: ScriptKind
    correlation_id: str

    def __post_init__(self) -> None:
        UnicodeSignalContract.inspect(self.glyph)


@dataclass(frozen=True, slots=True)
class ScriptPrototype:
    """One compressed code-point pattern and its verified evidence count."""

    center: float = 0.0
    support: int = 0

    def updated(self, coordinate: float) -> "ScriptPrototype":
        """Absorb one verified scalar without retaining its raw glyph."""

        next_support = self.support + 1
        next_center = self.center + (coordinate - self.center) / next_support
        return ScriptPrototype(center=next_center, support=next_support)


_ORDERED_KINDS = tuple(ScriptKind)


@dataclass(frozen=True, slots=True)
class UnicodeScriptState:
    """All persistent learned state for the bounded multiscript prototype core."""

    prototypes: tuple[ScriptPrototype, ...] = tuple(
        ScriptPrototype() for _ in _ORDERED_KINDS
    )

    def __post_init__(self) -> None:
        if len(self.prototypes) != len(_ORDERED_KINDS):
            raise ValueError("Unicode script state must have one prototype per pathway.")

    @staticmethod
    def _index(kind: ScriptKind) -> int:
        return _ORDERED_KINDS.index(kind)

    def prototype_for(self, kind: ScriptKind) -> ScriptPrototype:
        """Return the compact learned pattern for one declared pathway."""

        return self.prototypes[self._index(kind)]

    def with_prototype(
        self,
        kind: ScriptKind,
        prototype: ScriptPrototype,
    ) -> "UnicodeScriptState":
        """Create a candidate state with one updated pathway pattern."""

        values = list(self.prototypes)
        values[self._index(kind)] = prototype
        return UnicodeScriptState(tuple(values))

    @property
    def total_support(self) -> int:
        """Count verified lessons compressed into the candidate state."""

        return sum(prototype.support for prototype in self.prototypes)


@dataclass(frozen=True, slots=True)
class UnicodeScriptInference:
    """Inspectable output from the fixed Unicode script-pathway route."""

    event: ScriptEvent
    signal: UnicodeScalarSignal
    prediction: ScriptKind | None
    confidence: float
    coordinate: float
    distances: tuple[tuple[ScriptKind, float], ...]
    active_pipe_ids: tuple[str, ...]
    abstain_reason: str | None = None


@dataclass(frozen=True, slots=True)
class UnicodeScriptMetrics:
    """Exact fixed-manifest measurements for the small script-pathway core."""

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
class UnicodeScriptCandidateAssessment:
    """Independent before/after evidence for a proposed script-state update."""

    candidate_state: UnicodeScriptState
    parent_current: UnicodeScriptMetrics
    candidate_current: UnicodeScriptMetrics
    parent_protected: UnicodeScriptMetrics
    candidate_protected: UnicodeScriptMetrics
    parent_held_out: UnicodeScriptMetrics
    candidate_held_out: UnicodeScriptMetrics
    accepted: bool


class UnicodeScriptPathwayCore:
    """A hard-pathway model over compact generated scalar prototypes.

    The core first preserves the scalar, then converts its exact code point to
    a bounded coordinate, then compares that coordinate to learned centroids.
    It cannot claim an answer until each declared pathway has verified support.
    This is a testable compression mechanism, not a full script classifier.
    """

    PIPE_IDS = (
        UnicodeSignalContract.PIPE_ID,
        "exact-codepoint-coordinate",
        "script-prototype-readout",
    )
    MINIMUM_CONFIDENCE = 0.02

    def __init__(self) -> None:
        self.state = UnicodeScriptState()
        self.verified_promotions = 0

    @staticmethod
    def coordinate(signal: UnicodeScalarSignal) -> float:
        """Map an exact Unicode scalar to a bounded numeric signal."""

        return signal.code_point / MAX_UNICODE_SCALAR

    @staticmethod
    def _state_complete(state: UnicodeScriptState) -> bool:
        return all(prototype.support > 0 for prototype in state.prototypes)

    def infer(
        self,
        event: ScriptEvent,
        *,
        state: UnicodeScriptState | None = None,
    ) -> UnicodeScriptInference:
        """Route one scalar through the core and classify or abstain."""

        selected = self.state if state is None else state
        signal = UnicodeSignalContract.inspect(event.glyph)
        coordinate = self.coordinate(signal)
        if not self._state_complete(selected):
            return UnicodeScriptInference(
                event=event,
                signal=signal,
                prediction=None,
                confidence=0.0,
                coordinate=coordinate,
                distances=(),
                active_pipe_ids=self.PIPE_IDS,
                abstain_reason="One or more declared pathways lack verified support.",
            )

        distances = tuple(
            (kind, abs(coordinate - selected.prototype_for(kind).center))
            for kind in _ORDERED_KINDS
        )
        ordered = sorted(distances, key=lambda item: item[1])
        prediction, nearest_distance = ordered[0]
        second_distance = ordered[1][1]
        distance_sum = nearest_distance + second_distance
        confidence = (
            (second_distance - nearest_distance) / distance_sum
            if distance_sum > 0.0
            else 0.0
        )
        if confidence < self.MINIMUM_CONFIDENCE:
            return UnicodeScriptInference(
                event=event,
                signal=signal,
                prediction=None,
                confidence=confidence,
                coordinate=coordinate,
                distances=distances,
                active_pipe_ids=self.PIPE_IDS,
                abstain_reason="Nearest pathway prototypes are too similar to claim a lane.",
            )
        return UnicodeScriptInference(
            event=event,
            signal=signal,
            prediction=prediction,
            confidence=confidence,
            coordinate=coordinate,
            distances=distances,
            active_pipe_ids=self.PIPE_IDS,
        )

    def candidate_from(self, events: Iterable[ScriptEvent]) -> UnicodeScriptState:
        """Build a child state through verified local prototype updates only."""

        candidate = self.state
        for event in events:
            signal = UnicodeSignalContract.inspect(event.glyph)
            prototype = candidate.prototype_for(event.target).updated(
                self.coordinate(signal)
            )
            candidate = candidate.with_prototype(event.target, prototype)
        return candidate

    def promote(self, state: UnicodeScriptState) -> None:
        """Replace the parent only after protected and held-out evaluation."""

        self.state = state
        self.verified_promotions += 1

    def resource_ledger(self) -> dict[str, int]:
        """Expose the model-state estimate without conflating it with the host."""

        persistent_scalars = 2 * len(_ORDERED_KINDS) + 1
        return {
            "persistent_scalars": persistent_scalars,
            "estimated_persistent_bytes": persistent_scalars * 8,
            "active_pipes": len(self.PIPE_IDS),
            "estimated_transient_bytes": (len(_ORDERED_KINDS) + 3) * 8,
        }


class UnicodeScriptEvaluator:
    """Fixed-manifest evaluator kept separate from the learner update rule."""

    def __init__(
        self,
        *,
        protected: Sequence[ScriptEvent],
        held_out: Sequence[ScriptEvent],
    ) -> None:
        self.protected = tuple(protected)
        self.held_out = tuple(held_out)

    def evaluate(
        self,
        core: UnicodeScriptPathwayCore,
        events: Iterable[ScriptEvent],
        *,
        state: UnicodeScriptState | None = None,
    ) -> UnicodeScriptMetrics:
        """Measure a state without mutating it or retaining test events."""

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
        return UnicodeScriptMetrics(cases, answered, correct, errors)

    def assess(
        self,
        core: UnicodeScriptPathwayCore,
        events: Sequence[ScriptEvent],
    ) -> UnicodeScriptCandidateAssessment:
        """Assess a finite child state against unchanged fixed manifests."""

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
        return UnicodeScriptCandidateAssessment(
            candidate_state=candidate_state,
            parent_current=parent_current,
            candidate_current=candidate_current,
            parent_protected=parent_protected,
            candidate_protected=candidate_protected,
            parent_held_out=parent_held_out,
            candidate_held_out=candidate_held_out,
            accepted=accepted,
        )
