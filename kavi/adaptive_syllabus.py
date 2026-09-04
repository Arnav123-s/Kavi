"""Finite, source-gated adaptive study loops for Kavi's textbook concept core.

The loop is intentionally narrow. It never discovers, downloads, or reads a
new book on its own. A human-reviewed local syllabus declares primary and
repair lesson identifiers, while every lesson still has to pass the existing
source, license, PDF, and extract-fingerprint gates. The saved state contains
only compact numeric prototypes, unit IDs, and attempt counts.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import random
import time
from typing import Callable, Sequence

from .source_manifest import SourceManifest
from .textbook_core import (
    ConceptKind,
    ConceptPrototype,
    TextbookConceptEvaluator,
    TextbookConceptMetrics,
    TextbookConceptPathwayCore,
    TextbookConceptState,
    TextbookEvent,
    response_text,
)
from .textbook_runtime import LocalTextbookLesson


STATE_SCHEMA_VERSION = 1


def _stable_seed(seed: int, *parts: str) -> int:
    """Derive a repeatable random-order seed without using process hash state."""

    material = "\x1f".join((str(seed), *parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def _validate_lesson_id(value: str) -> str:
    """Keep a local syllabus from escaping its configured lesson workspace."""

    if not value or value in {".", ".."} or "/" in value or "\\" in value:
        raise ValueError("Lesson identifiers must be simple local filenames without paths.")
    return value


@dataclass(frozen=True, slots=True)
class AdaptiveUnit:
    """One prerequisite-ordered concept unit and its approved repair queue."""

    unit_id: str
    title: str
    lesson_id: str
    repair_lesson_ids: tuple[str, ...]
    prerequisites: tuple[str, ...]
    max_attempts: int

    @classmethod
    def from_mapping(cls, value: dict[str, object], default_attempts: int) -> "AdaptiveUnit":
        repair_ids = tuple(
            _validate_lesson_id(str(item)) for item in value.get("repair_lesson_ids", [])
        )
        unit = cls(
            unit_id=str(value["unit_id"]),
            title=str(value["title"]),
            lesson_id=_validate_lesson_id(str(value["lesson_id"])),
            repair_lesson_ids=repair_ids,
            prerequisites=tuple(str(item) for item in value.get("prerequisites", [])),
            max_attempts=int(value.get("max_attempts", default_attempts)),
        )
        if not unit.unit_id or not unit.title:
            raise ValueError("Adaptive units need non-empty identifiers and titles.")
        if unit.max_attempts < 1:
            raise ValueError("An adaptive unit needs at least one finite attempt.")
        if len(repair_ids) != len(set(repair_ids)):
            raise ValueError("A repair lesson may appear only once in an adaptive unit.")
        if unit.lesson_id in repair_ids:
            raise ValueError("The primary lesson must not masquerade as a repair lesson.")
        return unit


@dataclass(frozen=True, slots=True)
class AdaptiveSyllabus:
    """A private, finite syllabus; it contains identifiers rather than source text."""

    schema_version: int
    syllabus_id: str
    title: str
    seed: int
    minimum_protected_accuracy: float
    minimum_held_out_accuracy: float
    evaluation_cases_per_partition: int | None
    default_max_attempts: int
    units: tuple[AdaptiveUnit, ...]

    @classmethod
    def load(cls, path: Path) -> "AdaptiveSyllabus":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if int(raw["schema_version"]) != STATE_SCHEMA_VERSION:
            raise ValueError("Unsupported adaptive syllabus schema.")
        default_attempts = int(raw.get("default_max_attempts", 3))
        syllabus = cls(
            schema_version=int(raw["schema_version"]),
            syllabus_id=str(raw["syllabus_id"]),
            title=str(raw["title"]),
            seed=int(raw.get("seed", 31)),
            minimum_protected_accuracy=float(raw.get("minimum_protected_accuracy", 0.9)),
            minimum_held_out_accuracy=float(raw.get("minimum_held_out_accuracy", 0.9)),
            evaluation_cases_per_partition=(
                int(raw["evaluation_cases_per_partition"])
                if raw.get("evaluation_cases_per_partition") is not None
                else None
            ),
            default_max_attempts=default_attempts,
            units=tuple(
                AdaptiveUnit.from_mapping(item, default_attempts) for item in raw["units"]
            ),
        )
        syllabus.validate()
        return syllabus

    def validate(self) -> None:
        if not self.syllabus_id or not self.title:
            raise ValueError("An adaptive syllabus needs an identifier and title.")
        if self.default_max_attempts < 1:
            raise ValueError("default_max_attempts must be positive.")
        if self.evaluation_cases_per_partition is not None and (
            self.evaluation_cases_per_partition < 1
        ):
            raise ValueError("evaluation_cases_per_partition must be positive when set.")
        for threshold in (
            self.minimum_protected_accuracy,
            self.minimum_held_out_accuracy,
        ):
            if not 0.0 <= threshold <= 1.0:
                raise ValueError("Adaptive accuracy thresholds must be in [0, 1].")
        identifiers = [unit.unit_id for unit in self.units]
        if not identifiers or len(identifiers) != len(set(identifiers)):
            raise ValueError("Adaptive syllabus units need unique non-empty identifiers.")
        known = set(identifiers)
        positions = {unit.unit_id: index for index, unit in enumerate(self.units)}
        for unit in self.units:
            if unit.unit_id in unit.prerequisites:
                raise ValueError(f"Adaptive unit {unit.unit_id} cannot require itself.")
            if not set(unit.prerequisites).issubset(known):
                raise ValueError(f"Adaptive unit {unit.unit_id} has an unknown prerequisite.")
            if any(positions[item] >= positions[unit.unit_id] for item in unit.prerequisites):
                raise ValueError(
                    f"Adaptive unit {unit.unit_id} must require only earlier units."
                )


@dataclass(frozen=True, slots=True)
class AdaptiveStudyState:
    """Local checkpoint state with no document body or example strings."""

    schema_version: int
    completed_unit_ids: tuple[str, ...]
    attempts_by_unit: tuple[tuple[str, int], ...]
    model_state: TextbookConceptState
    verified_promotions: int

    @classmethod
    def empty(cls) -> "AdaptiveStudyState":
        return cls(
            schema_version=STATE_SCHEMA_VERSION,
            completed_unit_ids=(),
            attempts_by_unit=(),
            model_state=TextbookConceptState(),
            verified_promotions=0,
        )

    @staticmethod
    def _prototype_from_mapping(value: object) -> ConceptPrototype:
        if not isinstance(value, dict):
            raise ValueError("Adaptive checkpoint prototype must be an object.")
        center = tuple(float(item) for item in value["center"])
        if not all(math.isfinite(item) for item in center):
            raise ValueError("Adaptive checkpoint contains a non-finite prototype value.")
        support = int(value["support"])
        if support < 0:
            raise ValueError("Adaptive checkpoint support cannot be negative.")
        return ConceptPrototype(center=center, support=support)

    @classmethod
    def load(cls, path: Path) -> "AdaptiveStudyState":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if int(raw["schema_version"]) != STATE_SCHEMA_VERSION:
            raise ValueError("Adaptive checkpoint schema does not match this runtime.")
        model = raw["model_state"]
        if not isinstance(model, dict):
            raise ValueError("Adaptive checkpoint lacks compact model state.")
        attempts_raw = raw.get("attempts_by_unit", {})
        if not isinstance(attempts_raw, dict):
            raise ValueError("Adaptive checkpoint attempts must be an object.")
        attempts = tuple(sorted((str(key), int(value)) for key, value in attempts_raw.items()))
        if any(value < 0 for _, value in attempts):
            raise ValueError("Adaptive checkpoint attempt counts cannot be negative.")
        promotions = int(raw["verified_promotions"])
        if promotions < 0:
            raise ValueError("Adaptive checkpoint promotion count cannot be negative.")
        return cls(
            schema_version=STATE_SCHEMA_VERSION,
            completed_unit_ids=tuple(str(item) for item in raw["completed_unit_ids"]),
            attempts_by_unit=attempts,
            model_state=TextbookConceptState(
                expression=cls._prototype_from_mapping(model["expression"]),
                relation=cls._prototype_from_mapping(model["relation"]),
            ),
            verified_promotions=promotions,
        )

    def as_mapping(self) -> dict[str, object]:
        def prototype(value: ConceptPrototype) -> dict[str, object]:
            return {"center": list(value.center), "support": value.support}

        return {
            "schema_version": self.schema_version,
            "completed_unit_ids": list(self.completed_unit_ids),
            "attempts_by_unit": dict(self.attempts_by_unit),
            "model_state": {
                "expression": prototype(self.model_state.expression),
                "relation": prototype(self.model_state.relation),
            },
            "verified_promotions": self.verified_promotions,
        }


@dataclass(frozen=True, slots=True)
class AdaptiveRuntimeConfig:
    """Explicit bounds for a visible local adaptive syllabus pass."""

    syllabus_path: Path
    source_manifest_path: Path
    lesson_root: Path
    state_file: Path | None = None
    max_units: int = 1
    seed: int | None = None
    interval_ms: int = 0
    pause_file: Path | None = None
    stop_file: Path | None = None

    def __post_init__(self) -> None:
        if self.max_units < 1:
            raise ValueError("max_units must be at least one.")
        if self.interval_ms < 0:
            raise ValueError("interval_ms cannot be negative.")


@dataclass(frozen=True, slots=True)
class AdaptiveUnitResult:
    """One transparent advancement or repair decision."""

    unit_id: str
    outcome: str
    attempts: int
    protected_accuracy: float | None
    held_out_accuracy: float | None
    detail: str


@dataclass(frozen=True, slots=True)
class AdaptiveRunSummary:
    """Result of a bounded adaptive pass, never a background worker state."""

    completed_unit_ids: tuple[str, ...]
    results: tuple[AdaptiveUnitResult, ...]
    stopped: bool


class AdaptiveSyllabusRuntime:
    """Teach reviewed local lessons, test them, then select only declared repairs."""

    def __init__(
        self,
        config: AdaptiveRuntimeConfig,
        *,
        emit: Callable[[str], None] | None = None,
    ) -> None:
        self.config = config
        self.emit = emit or (lambda line: print(line, flush=True))
        self.syllabus = AdaptiveSyllabus.load(config.syllabus_path)
        self.source_manifest = SourceManifest.load(config.source_manifest_path)
        self.state = self._load_state()
        known_ids = {unit.unit_id for unit in self.syllabus.units}
        if not set(self.state.completed_unit_ids).issubset(known_ids):
            raise ValueError("Adaptive checkpoint refers to an unknown unit.")
        if not {unit_id for unit_id, _ in self.state.attempts_by_unit}.issubset(known_ids):
            raise ValueError("Adaptive checkpoint refers to an unknown attempt unit.")
        self.completed = set(self.state.completed_unit_ids)
        self.attempts = dict(self.state.attempts_by_unit)
        self.core = TextbookConceptPathwayCore()
        self.core.state = self.state.model_state
        self.core.verified_promotions = self.state.verified_promotions

    @property
    def seed(self) -> int:
        return self.syllabus.seed if self.config.seed is None else self.config.seed

    def _load_state(self) -> AdaptiveStudyState:
        if self.config.state_file is None or not self.config.state_file.exists():
            return AdaptiveStudyState.empty()
        return AdaptiveStudyState.load(self.config.state_file)

    def _checkpoint(self) -> None:
        ordered_completed = tuple(
            unit.unit_id for unit in self.syllabus.units if unit.unit_id in self.completed
        )
        self.state = AdaptiveStudyState(
            schema_version=STATE_SCHEMA_VERSION,
            completed_unit_ids=ordered_completed,
            attempts_by_unit=tuple(sorted(self.attempts.items())),
            model_state=self.core.state,
            verified_promotions=self.core.verified_promotions,
        )
        if self.config.state_file is None:
            return
        target = self.config.state_file
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(f"{target.suffix}.tmp")
        temporary.write_text(
            json.dumps(self.state.as_mapping(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(target)

    def _lesson(self, lesson_id: str) -> LocalTextbookLesson:
        safe_id = _validate_lesson_id(lesson_id)
        path = self.config.lesson_root / f"{safe_id}.json"
        if not path.is_file():
            raise ValueError(f"The approved local lesson {safe_id} is unavailable.")
        return LocalTextbookLesson.load(path, self.source_manifest)

    def _randomized(
        self,
        events: Sequence[TextbookEvent],
        *labels: str,
        limit: int | None = None,
    ) -> tuple[TextbookEvent, ...]:
        selected = list(events)
        random.Random(_stable_seed(self.seed, *labels)).shuffle(selected)
        if limit is not None and limit < len(selected):
            selected = selected[:limit]
        return tuple(selected)

    def _balanced_training(
        self,
        events: Sequence[TextbookEvent],
        *labels: str,
    ) -> tuple[TextbookEvent, ...]:
        """Randomize within categories while making each first lesson batch useful."""

        rng = random.Random(_stable_seed(self.seed, *labels))
        buckets = {
            kind: [event for event in events if event.target is kind]
            for kind in ConceptKind
        }
        for bucket in buckets.values():
            rng.shuffle(bucket)
        ordered: list[TextbookEvent] = []
        while buckets[ConceptKind.EXPRESSION] and buckets[ConceptKind.RELATION]:
            pair = [
                buckets[ConceptKind.EXPRESSION].pop(),
                buckets[ConceptKind.RELATION].pop(),
            ]
            rng.shuffle(pair)
            ordered.extend(pair)
        remainder = buckets[ConceptKind.EXPRESSION] + buckets[ConceptKind.RELATION]
        rng.shuffle(remainder)
        ordered.extend(remainder)
        return tuple(ordered)

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

    def _wait_between_batches(self) -> bool:
        if self._stop_requested() or not self._wait_if_paused():
            return False
        if self.config.interval_ms:
            time.sleep(self.config.interval_ms / 1000.0)
        return not self._stop_requested()

    def _teach(
        self,
        *,
        unit: AdaptiveUnit,
        attempt: int,
        lesson: LocalTextbookLesson,
        evaluator: TextbookConceptEvaluator,
    ) -> bool:
        train = self._balanced_training(
            lesson.train,
            unit.unit_id,
            lesson.lesson_id,
            str(attempt),
            "train",
        )
        self.emit(
            f"[teach] unit={unit.unit_id}; attempt={attempt}; "
            f"lesson={lesson.lesson_id}; randomized verified events={len(train)}"
        )
        for offset in range(0, len(train), 2):
            if not self._wait_if_paused() or self._stop_requested():
                return False
            batch = train[offset : offset + 2]
            for event in batch:
                inference = self.core.infer(event)
                self.emit(
                    f"  [learn] {event.event_id}: {event.notation!r}; "
                    f"expected={event.target.value}; model={response_text(inference)}"
                )
            assessment = evaluator.assess(self.core, batch)
            if assessment.accepted:
                self.core.promote(assessment.candidate_state)
                self._checkpoint()
                decision = "promoted"
            else:
                decision = "rejected"
            self.emit(
                f"  [candidate] {decision}; current error "
                f"{assessment.parent_current.mean_error:.2f}->{assessment.candidate_current.mean_error:.2f}; "
                f"protected {assessment.parent_protected.mean_error:.2f}->{assessment.candidate_protected.mean_error:.2f}; "
                f"held-out {assessment.parent_held_out.mean_error:.2f}->{assessment.candidate_held_out.mean_error:.2f}"
            )
            if not self._wait_between_batches():
                return False
        return True

    def _grade(
        self,
        label: str,
        events: Sequence[TextbookEvent],
        evaluator: TextbookConceptEvaluator,
    ) -> TextbookConceptMetrics:
        """Show every test decision without leaking a test result back into training."""

        self.emit(f"[test] {label}; randomized fixed questions={len(events)}")
        for event in events:
            inference = self.core.infer(event)
            predicted = inference.prediction.value if inference.prediction else "abstain"
            passed = inference.prediction is event.target
            self.emit(
                f"  [grade] {'PASS' if passed else 'FAIL'} {event.event_id}: "
                f"expected={event.target.value}; model={predicted}; "
                f"checked={inference.semantic_outcome}; confidence={inference.confidence:.2f}"
            )
            if not passed:
                why = inference.abstain_reason or "nearest compact prototype chose the other class"
                self.emit(f"    [diagnosis] {why}; this held-out target is not trained on.")
        metrics = evaluator.evaluate(self.core, events)
        self.emit(
            f"  [score] {label}: accuracy={metrics.exact_accuracy:.2f}; "
            f"coverage={metrics.coverage:.2f}; errors={metrics.errors}/{metrics.cases}"
        )
        return metrics

    def _unit_result(
        self,
        unit: AdaptiveUnit,
        outcome: str,
        protected: TextbookConceptMetrics | None,
        held_out: TextbookConceptMetrics | None,
        detail: str,
    ) -> AdaptiveUnitResult:
        return AdaptiveUnitResult(
            unit_id=unit.unit_id,
            outcome=outcome,
            attempts=self.attempts.get(unit.unit_id, 0),
            protected_accuracy=protected.exact_accuracy if protected else None,
            held_out_accuracy=held_out.exact_accuracy if held_out else None,
            detail=detail,
        )

    def _run_unit(self, unit: AdaptiveUnit) -> tuple[AdaptiveUnitResult, bool]:
        try:
            anchor = self._lesson(unit.lesson_id)
        except (KeyError, OSError, ValueError) as error:
            return (
                self._unit_result(unit, "not-admitted", None, None, f"Primary lesson rejected: {error}"),
                False,
            )
        starting_attempt = self.attempts.get(unit.unit_id, 0)
        if starting_attempt >= unit.max_attempts:
            return (
                self._unit_result(
                    unit,
                    "attempt-budget-exhausted",
                    None,
                    None,
                    "No further teaching attempt is authorized by this finite syllabus.",
                ),
                False,
            )
        for attempt in range(starting_attempt, unit.max_attempts):
            if attempt == 0:
                lesson_id = unit.lesson_id
            elif not unit.repair_lesson_ids:
                return (
                    self._unit_result(
                        unit,
                        "needs-reviewed-repair-lesson",
                        None,
                        None,
                        "The 90% gate failed and no approved local repair lesson is declared.",
                    ),
                    False,
                )
            else:
                lesson_id = unit.repair_lesson_ids[(attempt - 1) % len(unit.repair_lesson_ids)]
            try:
                lesson = self._lesson(lesson_id)
            except (KeyError, OSError, ValueError) as error:
                return (
                    self._unit_result(
                        unit,
                        "not-admitted",
                        None,
                        None,
                        f"Teaching or repair lesson rejected: {error}",
                    ),
                    False,
                )
            if lesson.source_lesson.concept_id != anchor.source_lesson.concept_id:
                return (
                    self._unit_result(
                        unit,
                        "not-admitted",
                        None,
                        None,
                        "A repair lesson must declare the same independently verified concept.",
                    ),
                    False,
                )
            protected = self._randomized(
                anchor.protected,
                unit.unit_id,
                str(attempt),
                "protected",
                limit=self.syllabus.evaluation_cases_per_partition,
            )
            held_out = self._randomized(
                anchor.held_out,
                unit.unit_id,
                str(attempt),
                "held-out",
                limit=self.syllabus.evaluation_cases_per_partition,
            )
            evaluator = TextbookConceptEvaluator(protected=protected, held_out=held_out)
            self.emit(
                f"\n[unit] {unit.unit_id}: {unit.title}; attempt={attempt + 1}/{unit.max_attempts}"
            )
            if not self._teach(
                unit=unit,
                attempt=attempt + 1,
                lesson=lesson,
                evaluator=evaluator,
            ):
                self._checkpoint()
                return (
                    self._unit_result(
                        unit,
                        "stopped",
                        None,
                        None,
                        "Stop control ended the finite adaptive unit.",
                    ),
                    True,
                )
            protected_metrics = self._grade("protected", protected, evaluator)
            held_out_metrics = self._grade("held-out", held_out, evaluator)
            self.attempts[unit.unit_id] = attempt + 1
            passed = (
                protected_metrics.exact_accuracy >= self.syllabus.minimum_protected_accuracy
                and held_out_metrics.exact_accuracy >= self.syllabus.minimum_held_out_accuracy
            )
            self._checkpoint()
            if passed:
                self.completed.add(unit.unit_id)
                self._checkpoint()
                return (
                    self._unit_result(
                        unit,
                        "mastered",
                        protected_metrics,
                        held_out_metrics,
                        "Both random-order fixed test partitions met the declared 90% gate.",
                    ),
                    False,
                )
            self.emit(
                f"[repair] gate not met: protected={protected_metrics.exact_accuracy:.2f}; "
                f"held-out={held_out_metrics.exact_accuracy:.2f}. "
                "The held-out questions remain evaluation-only."
            )
            if unit.repair_lesson_ids and attempt + 1 < unit.max_attempts:
                next_lesson = unit.repair_lesson_ids[attempt % len(unit.repair_lesson_ids)]
                self.emit(f"[repair] next approved local repair lesson: {next_lesson}")
        return (
            self._unit_result(
                unit,
                "not-mastered",
                protected_metrics,
                held_out_metrics,
                "The finite repair-attempt budget ended below the declared 90% gate.",
            ),
            False,
        )

    def run(self) -> AdaptiveRunSummary:
        """Run at most the configured number of declared local syllabus units."""

        self.emit(f"Kavi adaptive textbook syllabus: {self.syllabus.title}")
        self.emit(
            "  boundary: declared local lessons only; no source download, test-answer training, "
            "background worker, source rewrite, or self-modifying code."
        )
        results: list[AdaptiveUnitResult] = []
        attempted_units = 0
        for unit in self.syllabus.units:
            if unit.unit_id in self.completed:
                self.emit(f"[skip] {unit.unit_id}: already mastered in the local checkpoint")
                continue
            missing = [item for item in unit.prerequisites if item not in self.completed]
            if missing:
                results.append(
                    self._unit_result(
                        unit,
                        "waiting-prerequisite",
                        None,
                        None,
                        f"Missing mastered prerequisites: {', '.join(missing)}",
                    )
                )
                break
            if attempted_units >= self.config.max_units:
                self.emit("[boundary] configured maximum adaptive units reached")
                break
            result, stopped = self._run_unit(unit)
            results.append(result)
            attempted_units += 1
            self.emit(
                f"[unit result] {result.unit_id}: {result.outcome}; "
                f"attempts={result.attempts}; {result.detail}"
            )
            if stopped:
                return AdaptiveRunSummary(tuple(self.state.completed_unit_ids), tuple(results), True)
            if result.outcome != "mastered":
                return AdaptiveRunSummary(tuple(self.state.completed_unit_ids), tuple(results), False)
        return AdaptiveRunSummary(tuple(self.state.completed_unit_ids), tuple(results), False)
