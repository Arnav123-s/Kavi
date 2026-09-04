"""Local-only, finite runtime for Kavi's reviewed textbook concept lesson.

The public repository contains only source metadata.  This runtime loads an
owner-provided private lesson manifest, verifies the exact PDF and extract
fingerprints, and then learns only from the listed source examples.  It never
fetches a source itself.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import time
from typing import Callable, Iterable

from .source_manifest import SourceLesson, SourceManifest
from .textbook_core import (
    ConceptKind,
    TextbookCandidateAssessment,
    TextbookConceptEvaluator,
    TextbookConceptMetrics,
    TextbookConceptPathwayCore,
    TextbookEvent,
    response_text,
)


_PARTITIONS = frozenset({"train", "protected", "held-out"})


def _sha256(path: Path) -> str:
    """Return a deterministic fingerprint without retaining a document body."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class LocalTextbookLesson:
    """A validated private source lesson whose body stays outside Git."""

    lesson_id: str
    source_lesson: SourceLesson
    attribution: str
    source_file: Path
    source_file_sha256: str
    extract_file: Path
    train: tuple[TextbookEvent, ...]
    protected: tuple[TextbookEvent, ...]
    held_out: tuple[TextbookEvent, ...]

    @staticmethod
    def _private_relative_path(lesson_path: Path, value: object) -> Path:
        relative = Path(str(value))
        if relative.is_absolute():
            raise ValueError("Private lesson paths must be relative to the lesson file.")
        candidate = (lesson_path.parent / relative).resolve()
        private_root = lesson_path.parent.parent.resolve()
        if not candidate.is_relative_to(private_root):
            raise ValueError("Private lesson paths must remain inside the private workspace.")
        return candidate

    @classmethod
    def load(cls, path: Path, source_manifest: SourceManifest) -> "LocalTextbookLesson":
        """Load one audited private lesson and verify its source fingerprints."""

        lesson_path = path.resolve()
        raw = json.loads(lesson_path.read_text(encoding="utf-8"))
        if int(raw["schema_version"]) != 1:
            raise ValueError("Unsupported private textbook lesson schema.")
        source_lesson = SourceLesson(
            source_id=str(raw["source_id"]),
            locator=str(raw["locator"]),
            concept_id=str(raw["concept_id"]),
            prerequisites=tuple(str(item) for item in raw["prerequisites"]),
            explanation=str(raw["lesson_summary"]),
            verifier_id=str(raw["verifier_id"]),
            source_extract_sha256=str(raw["source_extract_sha256"]),
        )
        source_lesson.validate_against(source_manifest)
        source_file = cls._private_relative_path(lesson_path, raw["source_file"])
        extract_file = cls._private_relative_path(lesson_path, raw["extract_file"])
        if not source_file.is_file() or not extract_file.is_file():
            raise ValueError("The reviewed source PDF and extract must both exist locally.")
        source_file_sha256 = str(raw["source_file_sha256"]).lower()
        if _sha256(source_file) != source_file_sha256:
            raise ValueError("The local source PDF does not match the reviewed fingerprint.")
        if _sha256(extract_file) != source_lesson.source_extract_sha256:
            raise ValueError("The local source extract does not match the reviewed fingerprint.")

        buckets: dict[str, list[TextbookEvent]] = {
            "train": [],
            "protected": [],
            "held-out": [],
        }
        for value in raw["events"]:
            partition = str(value["partition"])
            if partition not in _PARTITIONS:
                raise ValueError(f"Unknown textbook event partition: {partition}")
            target = ConceptKind(str(value["target"]))
            event_id = str(value["event_id"])
            buckets[partition].append(
                TextbookEvent(
                    event_id=event_id,
                    notation=str(value["notation"]),
                    target=target,
                    correlation_id=event_id,
                )
            )
        if not all(buckets[partition] for partition in _PARTITIONS):
            raise ValueError("A textbook lesson needs train, protected, and held-out cases.")
        train_kinds = {event.target for event in buckets["train"]}
        if train_kinds != {ConceptKind.EXPRESSION, ConceptKind.RELATION}:
            raise ValueError("Training examples must establish both first-lesson concepts.")
        identifiers = [
            event.event_id
            for partition in _PARTITIONS
            for event in buckets[partition]
        ]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Textbook lesson events need unique identifiers.")
        return cls(
            lesson_id=str(raw["lesson_id"]),
            source_lesson=source_lesson,
            attribution=str(raw["attribution"]),
            source_file=source_file,
            source_file_sha256=source_file_sha256,
            extract_file=extract_file,
            train=tuple(buckets["train"]),
            protected=tuple(buckets["protected"]),
            held_out=tuple(buckets["held-out"]),
        )


@dataclass(frozen=True, slots=True)
class TextbookRuntimeConfig:
    """Finite owner-controlled bounds for a reviewed local textbook lesson."""

    lesson_path: Path
    source_manifest_path: Path
    steps: int | None = None
    batch_size: int | None = None
    interval_ms: int = 80
    pause_file: Path | None = None
    stop_file: Path | None = None

    def __post_init__(self) -> None:
        if self.steps is not None and self.steps < 1:
            raise ValueError("steps must be positive when supplied")
        if self.batch_size is not None and self.batch_size < 2:
            raise ValueError("batch_size must be at least two when supplied")
        if self.interval_ms < 0:
            raise ValueError("interval_ms cannot be negative")


@dataclass(frozen=True, slots=True)
class TextbookRunSummary:
    """Measured result of one finite reviewed-textbook lesson run."""

    completed_steps: int
    stopped: bool
    promoted_candidates: int
    protected: TextbookConceptMetrics
    held_out: TextbookConceptMetrics


class TextbookConceptRuntime:
    """Teach one vetted local source lesson with a visible, finite trace."""

    def __init__(
        self,
        config: TextbookRuntimeConfig,
        *,
        emit: Callable[[str], None] | None = None,
    ) -> None:
        self.config = config
        self.emit = emit or (lambda line: print(line, flush=True))
        source_manifest = SourceManifest.load(config.source_manifest_path)
        self.lesson = LocalTextbookLesson.load(config.lesson_path, source_manifest)
        self.core = TextbookConceptPathwayCore()
        self.evaluator = TextbookConceptEvaluator(
            protected=self.lesson.protected,
            held_out=self.lesson.held_out,
        )
        self.events = self._selected_events()
        self.batch_size = self._selected_batch_size()

    def _selected_events(self) -> tuple[TextbookEvent, ...]:
        requested = self.config.steps or len(self.lesson.train)
        if requested > len(self.lesson.train):
            raise ValueError("The finite run cannot repeat or invent textbook lesson events.")
        events = self.lesson.train[:requested]
        if {event.target for event in events} != {ConceptKind.EXPRESSION, ConceptKind.RELATION}:
            raise ValueError("Selected source events must include both first-lesson concepts.")
        return events

    def _selected_batch_size(self) -> int:
        batch_size = self.config.batch_size or min(2, len(self.events))
        if batch_size > len(self.events):
            raise ValueError("A source lesson batch cannot exceed its selected event count.")
        return batch_size

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

    def _emit_event(self, step: int, event: TextbookEvent) -> None:
        inference = self.core.infer(event)
        answer = response_text(inference)
        self.emit(f"\n[{step:03d}] textbook notation {event.notation!r}; verified concept={event.target.value}")
        self.emit(f"  hard path: {' > '.join(inference.active_pipe_ids)}")
        self.emit(
            "  structural facets: "
            + ", ".join(f"{feature:.2f}" for feature in inference.features)
        )
        self.emit(f"  model response: {answer}")
        self.emit(f"  confidence: {inference.confidence:.2f}")

    def _emit_assessment(self, assessment: TextbookCandidateAssessment) -> None:
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

    def _emit_readouts(self, events: Iterable[TextbookEvent]) -> None:
        self.emit("\n[readout] protected and held-out textbook examples after the final gate")
        for event in events:
            inference = self.core.infer(event)
            self.emit(
                f"  {event.notation!r} -> {response_text(inference)}; "
                f"confidence={inference.confidence:.2f}"
            )

    def _summary(self, completed: int, stopped: bool, promoted: int) -> TextbookRunSummary:
        return TextbookRunSummary(
            completed_steps=completed,
            stopped=stopped,
            promoted_candidates=promoted,
            protected=self.evaluator.evaluate(self.core, self.evaluator.protected),
            held_out=self.evaluator.evaluate(self.core, self.evaluator.held_out),
        )

    def run(self) -> TextbookRunSummary:
        """Run each selected local textbook event at most once, visibly."""

        self.emit("Kavi reviewed textbook-concept trace")
        self.emit(
            f"  source: {self.lesson.source_lesson.source_id}; "
            f"locator: {self.lesson.source_lesson.locator}"
        )
        self.emit(
            "  boundary: one locally fingerprinted lesson; no network fetch, "
            "source rewrite, background persistence, or broader language claim."
        )
        batch: list[TextbookEvent] = []
        completed = promoted = 0
        for step, event in enumerate(self.events, start=1):
            if self._stop_requested() or not self._wait_if_paused():
                self.emit("[control] stop requested; preserving the current in-memory parent.")
                return self._summary(completed, True, promoted)
            self._emit_event(step, event)
            batch.append(event)
            completed += 1
            if len(batch) == self.batch_size or step == len(self.events):
                assessment = self.evaluator.assess(self.core, tuple(batch))
                self._emit_assessment(assessment)
                if assessment.accepted:
                    self.core.promote(assessment.candidate_state)
                    promoted += 1
                batch.clear()
            if self.config.interval_ms:
                time.sleep(self.config.interval_ms / 1000.0)
        if not self._stop_requested():
            self._emit_readouts((*self.evaluator.protected, *self.evaluator.held_out))
        return self._summary(completed, False, promoted)
