"""Finite, observable runtime for Kavi's generated glyph-foundation stage."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Callable

from .symbol_core import (
    GlyphKind,
    SymbolCandidateAssessment,
    SymbolEvaluator,
    SymbolEvent,
    SymbolMetrics,
    SymbolPathwayCore,
)


def glyph_kind(glyph: str) -> GlyphKind:
    """Return the exact generated teacher label for one stage-1 ASCII glyph."""

    if "a" <= glyph <= "z":
        return GlyphKind.LETTER
    if "0" <= glyph <= "9":
        return GlyphKind.DIGIT
    raise ValueError("Stage-1 lessons are limited to lowercase letters and digits.")


def _event(event_id: str, glyph: str) -> SymbolEvent:
    return SymbolEvent(
        event_id=event_id,
        glyph=glyph,
        target=glyph_kind(glyph),
        correlation_id=event_id,
    )


def protected_manifest() -> tuple[SymbolEvent, ...]:
    """Fixed symbols whose learned categorization must not silently regress."""

    return (
        _event("symbol-protected-a", "a"),
        _event("symbol-protected-z", "z"),
        _event("symbol-protected-0", "0"),
        _event("symbol-protected-9", "9"),
    )


def held_out_manifest() -> tuple[SymbolEvent, ...]:
    """Unpresented symbols that test compressed category transfer."""

    return (
        _event("symbol-held-e", "e"),
        _event("symbol-held-t", "t"),
        _event("symbol-held-3", "3"),
        _event("symbol-held-7", "7"),
    )


@dataclass(frozen=True, slots=True)
class SymbolRuntimeConfig:
    """Hard bounds for one finite generated symbol-curriculum run."""

    steps: int = 24
    seed: int = 7
    batch_size: int = 8
    interval_ms: int = 80
    pause_file: Path | None = None
    stop_file: Path | None = None

    def __post_init__(self) -> None:
        if self.steps < 1:
            raise ValueError("steps must be at least one")
        if self.batch_size < 2:
            raise ValueError("batch_size must be at least two")
        if self.interval_ms < 0:
            raise ValueError("interval_ms cannot be negative")


class SymbolCurriculum:
    """A fixed, generated alphabet-and-digit bootstrap sequence.

    The generator constructs symbols from ASCII ranges in canonical code-point
    order. It neither reads nor embeds a textbook, word list, web page, or
    private corpus. The ``seed`` remains in the public configuration for
    compatibility, but intentionally does not alter this prerequisite order.
    """

    _EXCLUDED = frozenset({"a", "e", "t", "z", "0", "3", "7", "9"})

    def __init__(self, seed: int) -> None:
        del seed
        letters = [chr(code) for code in range(ord("a"), ord("z") + 1)]
        digits = [chr(code) for code in range(ord("0"), ord("9") + 1)]
        self._letters = [glyph for glyph in letters if glyph not in self._EXCLUDED]
        self._digits = [glyph for glyph in digits if glyph not in self._EXCLUDED]

    def event_at(self, step: int) -> SymbolEvent:
        """Interleave fixed independent classes in a reproducible order."""

        if step < 1:
            raise ValueError("step must be at least one")
        if step % 2:
            glyph = self._letters[(step // 2) % len(self._letters)]
        else:
            glyph = self._digits[(step // 2 - 1) % len(self._digits)]
        return _event(f"symbol-{step:04d}", glyph)


@dataclass(frozen=True, slots=True)
class SymbolRunSummary:
    """Measured result of a finite symbol-stage run."""

    completed_steps: int
    stopped: bool
    promoted_candidates: int
    protected: SymbolMetrics
    held_out: SymbolMetrics


class SymbolRuntime:
    """Run the first generated Kavi symbol stage without background behavior."""

    def __init__(
        self,
        config: SymbolRuntimeConfig,
        *,
        emit: Callable[[str], None] | None = None,
    ) -> None:
        self.config = config
        self.emit = emit or (lambda line: print(line, flush=True))
        self.core = SymbolPathwayCore()
        self.curriculum = SymbolCurriculum(config.seed)
        self.evaluator = SymbolEvaluator(
            protected=protected_manifest(),
            held_out=held_out_manifest(),
        )

    def _stop_requested(self) -> bool:
        return self.config.stop_file is not None and self.config.stop_file.exists()

    def _wait_if_paused(self) -> bool:
        announced = False
        while self.config.pause_file is not None and self.config.pause_file.exists():
            if self._stop_requested():
                return False
            if not announced:
                self.emit(
                    f"[control] paused while {self.config.pause_file} exists; "
                    "remove it to continue or create the stop file."
                )
                announced = True
            time.sleep(0.25)
        return True

    def _emit_event(self, step: int, event: SymbolEvent) -> None:
        inference = self.core.infer(event)
        prediction = inference.prediction.value if inference.prediction else "abstain"
        self.emit(f"\n[{step:03d}] glyph {event.glyph!r}; verified kind={event.target.value}")
        self.emit(f"  hard path: {' > '.join(inference.active_pipe_ids)}")
        self.emit(f"  coordinate: {inference.coordinate:.4f}; answer: {prediction}")
        self.emit(f"  confidence: {inference.confidence:.2f}")
        if inference.abstain_reason:
            self.emit(f"  abstain reason: {inference.abstain_reason}")

    def _emit_assessment(self, assessment: SymbolCandidateAssessment) -> None:
        decision = "promoted" if assessment.accepted else "rejected"
        self.emit(f"  candidate: {decision}; parent remains frozen until this gate")
        self.emit(
            "  current error: "
            f"{assessment.parent_current.mean_error:.2f} to "
            f"{assessment.candidate_current.mean_error:.2f}"
        )
        self.emit(
            "  protected error: "
            f"{assessment.parent_protected.mean_error:.2f} to "
            f"{assessment.candidate_protected.mean_error:.2f}; held-out error: "
            f"{assessment.parent_held_out.mean_error:.2f} to "
            f"{assessment.candidate_held_out.mean_error:.2f}"
        )
        ledger = self.core.resource_ledger()
        self.emit(
            "  ledger (explicit estimate): "
            f"{ledger['persistent_scalars']} persistent scalars, "
            f"{ledger['active_pipes']} active pipes, "
            f"about {ledger['estimated_transient_bytes']} transient bytes"
        )

    def _summary(self, completed: int, stopped: bool, promoted: int) -> SymbolRunSummary:
        return SymbolRunSummary(
            completed_steps=completed,
            stopped=stopped,
            promoted_candidates=promoted,
            protected=self.evaluator.evaluate(self.core, self.evaluator.protected),
            held_out=self.evaluator.evaluate(self.core, self.evaluator.held_out),
        )

    def run(self) -> SymbolRunSummary:
        """Run at most the configured number of lessons and candidate batches."""

        self.emit("Kavi generated symbol-core trace")
        self.emit(
            "  boundary: finite generated lessons; no source download, raw-text "
            "retention, background persistence, or source rewrite."
        )
        batch: list[SymbolEvent] = []
        completed = promoted = 0
        for step in range(1, self.config.steps + 1):
            if self._stop_requested() or not self._wait_if_paused():
                self.emit("[control] stop requested; preserving the current in-memory parent.")
                return self._summary(completed, True, promoted)
            event = self.curriculum.event_at(step)
            self._emit_event(step, event)
            batch.append(event)
            completed += 1
            if len(batch) == self.config.batch_size or step == self.config.steps:
                assessment = self.evaluator.assess(self.core, tuple(batch))
                self._emit_assessment(assessment)
                if assessment.accepted:
                    self.core.promote(assessment.candidate_state)
                    promoted += 1
                batch.clear()
            if self.config.interval_ms:
                time.sleep(self.config.interval_ms / 1000.0)
        return self._summary(completed, False, promoted)
