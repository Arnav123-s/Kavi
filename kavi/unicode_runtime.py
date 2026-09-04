"""Finite, visible generated Unicode stages for the Kavi model core.

The contract stage proves only that individual Unicode scalars are preserved.
The script stage then trains and tests a small prototype core on a balanced,
hand-declared set of individual code points.  Neither stage reads a document,
downloads Unicode data, or learns a language.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Callable, Iterable

from .unicode_core import (
    ScriptEvent,
    ScriptKind,
    UnicodeScriptCandidateAssessment,
    UnicodeScriptEvaluator,
    UnicodeScriptMetrics,
    UnicodeScriptPathwayCore,
    UnicodeSignalContract,
)


@dataclass(frozen=True, slots=True)
class ScriptSpec:
    """One declared generated pathway and disjoint training/test glyphs."""

    kind: ScriptKind
    training_glyphs: tuple[str, ...]
    protected_glyph: str
    held_out_glyph: str

    def __post_init__(self) -> None:
        values = (*self.training_glyphs, self.protected_glyph, self.held_out_glyph)
        if not self.training_glyphs or len(values) != len(set(values)):
            raise ValueError("Generated script samples must be non-empty and disjoint.")
        for glyph in values:
            UnicodeSignalContract.inspect(glyph)


# These are individual generated scalar lessons, not words, quotations, or a
# copied source.  The order follows code-point neighborhoods so the tiny model
# has a visible, reproducible bounded experiment.
SCRIPT_SPECS: tuple[ScriptSpec, ...] = (
    ScriptSpec(ScriptKind.LATIN, ("b", "c", "d"), "A", "o"),
    ScriptSpec(ScriptKind.GREEK, ("\u03b2", "\u03b3", "\u03b4"), "\u0391", "\u03bf"),
    ScriptSpec(ScriptKind.CYRILLIC, ("\u0431", "\u0432", "\u0433"), "\u0410", "\u043e"),
    ScriptSpec(ScriptKind.ARABIC, ("\u0628", "\u062b", "\u062c"), "\u062a", "\u062f"),
    ScriptSpec(ScriptKind.DEVANAGARI, ("\u0905", "\u0907", "\u0909"), "\u0906", "\u090f"),
    ScriptSpec(ScriptKind.BENGALI, ("\u0985", "\u0987", "\u0989"), "\u0986", "\u098f"),
    ScriptSpec(ScriptKind.TAMIL, ("\u0b85", "\u0b87", "\u0b89"), "\u0b86", "\u0b8f"),
    ScriptSpec(ScriptKind.HIRAGANA, ("\u3042", "\u3046", "\u3048"), "\u3044", "\u304a"),
    ScriptSpec(ScriptKind.KATAKANA, ("\u30a2", "\u30a6", "\u30a8"), "\u30a4", "\u30aa"),
    ScriptSpec(ScriptKind.HAN, ("\u4e00", "\u4e8c", "\u4e09"), "\u4e2d", "\u5b57"),
    ScriptSpec(ScriptKind.HANGUL, ("\uac00", "\ub2e4", "\ub77c"), "\ub098", "\ub9c8"),
)


def _script_event(event_id: str, glyph: str, kind: ScriptKind) -> ScriptEvent:
    return ScriptEvent(
        event_id=event_id,
        glyph=glyph,
        target=kind,
        correlation_id=event_id,
    )


def protected_manifest() -> tuple[ScriptEvent, ...]:
    """One fixed unpresented protected glyph per declared pathway."""

    return tuple(
        _script_event(f"unicode-protected-{spec.kind.value}", spec.protected_glyph, spec.kind)
        for spec in SCRIPT_SPECS
    )


def held_out_manifest() -> tuple[ScriptEvent, ...]:
    """One fixed unpresented transfer glyph per declared pathway.

    The Latin, Greek, and Cyrillic entries deliberately include the code points
    ``o``, ``ο``, and ``о``.  Their visual similarity is not merged: the
    contract preserves distinct scalars and the evaluator expects distinct
    pathway labels.
    """

    return tuple(
        _script_event(f"unicode-held-out-{spec.kind.value}", spec.held_out_glyph, spec.kind)
        for spec in SCRIPT_SPECS
    )


@dataclass(frozen=True, slots=True)
class UnicodeContractCase:
    """One exact, source-free scalar preservation check."""

    case_id: str
    glyph: str


def contract_protected_manifest() -> tuple[UnicodeContractCase, ...]:
    """Fixed exact-scalar checks, including visually similar distinct letters."""

    return (
        UnicodeContractCase("contract-latin-a", "A"),
        UnicodeContractCase("contract-greek-alpha", "\u0391"),
        UnicodeContractCase("contract-cyrillic-a", "\u0410"),
        UnicodeContractCase("contract-arabic-beh", "\u0628"),
        UnicodeContractCase("contract-devanagari-a", "\u0905"),
        UnicodeContractCase("contract-hangul-ga", "\uac00"),
    )


def contract_held_out_manifest() -> tuple[UnicodeContractCase, ...]:
    """Additional scalar checks, including a scalar with a different NFC view."""

    return (
        UnicodeContractCase("contract-latin-o", "o"),
        UnicodeContractCase("contract-greek-omicron", "\u03bf"),
        UnicodeContractCase("contract-cyrillic-o", "\u043e"),
        UnicodeContractCase("contract-han-middle", "\u4e2d"),
        UnicodeContractCase("contract-combining-grave-tone", "\u0340"),
    )


@dataclass(frozen=True, slots=True)
class UnicodeContractMetrics:
    """Exact preservation metrics for a finite scalar contract check."""

    cases: int
    passed: int

    @property
    def exact_accuracy(self) -> float:
        return self.passed / self.cases if self.cases else 0.0


@dataclass(frozen=True, slots=True)
class UnicodeContractRunSummary:
    """Result of a finite, non-learning Unicode contract pass."""

    completed_cases: int
    stopped: bool
    protected: UnicodeContractMetrics
    held_out: UnicodeContractMetrics


@dataclass(frozen=True, slots=True)
class UnicodeContractRuntimeConfig:
    """Owner-controlled bounds for the finite scalar-contract check."""

    interval_ms: int = 80
    pause_file: Path | None = None
    stop_file: Path | None = None

    def __post_init__(self) -> None:
        if self.interval_ms < 0:
            raise ValueError("interval_ms cannot be negative")


class UnicodeContractRuntime:
    """Run the exact scalar contract visibly, with pause and stop controls."""

    def __init__(
        self,
        config: UnicodeContractRuntimeConfig,
        *,
        emit: Callable[[str], None] | None = None,
    ) -> None:
        self.config = config
        self.emit = emit or (lambda line: print(line, flush=True))
        self.protected = contract_protected_manifest()
        self.held_out = contract_held_out_manifest()

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

    @staticmethod
    def _check(case: UnicodeContractCase) -> bool:
        signal = UnicodeSignalContract.inspect(case.glyph)
        return (
            signal.glyph == case.glyph
            and signal.code_point == ord(case.glyph)
            and chr(signal.code_point) == case.glyph
        )

    @classmethod
    def _measure(cls, cases: Iterable[UnicodeContractCase]) -> UnicodeContractMetrics:
        sequence = tuple(cases)
        return UnicodeContractMetrics(
            cases=len(sequence),
            passed=sum(1 for case in sequence if cls._check(case)),
        )

    def _summary(self, completed: int, stopped: bool) -> UnicodeContractRunSummary:
        return UnicodeContractRunSummary(
            completed_cases=completed,
            stopped=stopped,
            protected=self._measure(self.protected),
            held_out=self._measure(self.held_out),
        )

    def run(self) -> UnicodeContractRunSummary:
        """Perform the fixed scalar checks without creating a learned state."""

        self.emit("Kavi Unicode scalar-contract trace")
        self.emit(
            "  boundary: exact one-scalar preservation only; no normalization "
            "rewrite, source text, download, or language claim."
        )
        completed = 0
        cases = (*self.protected, *self.held_out)
        for index, case in enumerate(cases, start=1):
            if self._stop_requested() or not self._wait_if_paused():
                self.emit("[control] stop requested; no model state was changed.")
                return self._summary(completed, True)
            signal = UnicodeSignalContract.inspect(case.glyph)
            exact = self._check(case)
            self.emit(
                f"[{index:03d}] scalar {signal.glyph!r}; U+{signal.code_point:04X}; "
                f"category={signal.category}; exact-round-trip={exact}; "
                f"nfc-matches-input={signal.nfc_matches_input}"
            )
            completed += 1
            if self.config.interval_ms:
                time.sleep(self.config.interval_ms / 1000.0)
        return self._summary(completed, False)


@dataclass(frozen=True, slots=True)
class UnicodeScriptRuntimeConfig:
    """Hard bounds for a finite generated Unicode script-pathway run."""

    steps: int = len(SCRIPT_SPECS) * 3
    seed: int = 7
    batch_size: int = len(SCRIPT_SPECS)
    interval_ms: int = 80
    pause_file: Path | None = None
    stop_file: Path | None = None

    def __post_init__(self) -> None:
        if self.steps < len(SCRIPT_SPECS):
            raise ValueError("The script stage needs one lesson for each declared pathway.")
        if self.batch_size < len(SCRIPT_SPECS):
            raise ValueError("Each candidate batch must cover every declared pathway.")
        if self.interval_ms < 0:
            raise ValueError("interval_ms cannot be negative")


class UnicodeScriptCurriculum:
    """A fixed, script-balanced sequence of generated individual scalars."""

    def __init__(self, seed: int) -> None:
        del seed

    def event_at(self, step: int) -> ScriptEvent:
        """Cycle one scalar through each pathway before repeating any lane."""

        if step < 1:
            raise ValueError("step must be at least one")
        offset = step - 1
        spec = SCRIPT_SPECS[offset % len(SCRIPT_SPECS)]
        generation = offset // len(SCRIPT_SPECS)
        glyph = spec.training_glyphs[generation % len(spec.training_glyphs)]
        return _script_event(f"unicode-script-{step:04d}", glyph, spec.kind)


@dataclass(frozen=True, slots=True)
class UnicodeScriptRunSummary:
    """Measured result of one finite generated script-pathway run."""

    completed_steps: int
    stopped: bool
    promoted_candidates: int
    protected: UnicodeScriptMetrics
    held_out: UnicodeScriptMetrics


class UnicodeScriptRuntime:
    """Run the small Unicode script-pathway core with a visible trace."""

    def __init__(
        self,
        config: UnicodeScriptRuntimeConfig,
        *,
        emit: Callable[[str], None] | None = None,
    ) -> None:
        self.config = config
        self.emit = emit or (lambda line: print(line, flush=True))
        self.core = UnicodeScriptPathwayCore()
        self.curriculum = UnicodeScriptCurriculum(config.seed)
        self.evaluator = UnicodeScriptEvaluator(
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

    def _emit_event(self, step: int, event: ScriptEvent) -> None:
        inference = self.core.infer(event)
        prediction = inference.prediction.value if inference.prediction else "abstain"
        self.emit(
            f"\n[{step:03d}] scalar {event.glyph!r}; U+{inference.signal.code_point:04X}; "
            f"verified lane={event.target.value}"
        )
        self.emit(f"  hard path: {' > '.join(inference.active_pipe_ids)}")
        self.emit(f"  coordinate: {inference.coordinate:.6f}; answer: {prediction}")
        self.emit(f"  confidence: {inference.confidence:.2f}")
        if inference.abstain_reason:
            self.emit(f"  abstain reason: {inference.abstain_reason}")

    def _emit_assessment(self, assessment: UnicodeScriptCandidateAssessment) -> None:
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

    def _summary(self, completed: int, stopped: bool, promoted: int) -> UnicodeScriptRunSummary:
        return UnicodeScriptRunSummary(
            completed_steps=completed,
            stopped=stopped,
            promoted_candidates=promoted,
            protected=self.evaluator.evaluate(self.core, self.evaluator.protected),
            held_out=self.evaluator.evaluate(self.core, self.evaluator.held_out),
        )

    def run(self) -> UnicodeScriptRunSummary:
        """Run only the configured finite lesson count and candidate batches."""

        self.emit("Kavi generated Unicode script-pathway trace")
        self.emit(
            "  boundary: generated single scalars only; no source download, raw "
            "text retention, background persistence, or language claim."
        )
        batch: list[ScriptEvent] = []
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
