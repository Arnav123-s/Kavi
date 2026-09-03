"""Model-first curriculum automation for Kavi.

The school is not the product.  It is the bounded teaching and measurement
layer around the Kavi model cores.  It can advance only through a declared
finite plan, uses only locally generated lessons for runnable early stages, and
stops rather than silently downloading or ingesting a source that has not
passed review.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Callable

from .lesson_runtime import ExplanationRuntime
from .runtime import RuntimeConfig
from .symbol_runtime import SymbolRunSummary, SymbolRuntime, SymbolRuntimeConfig


RUNNABLE = "runnable"
WAITING_CAPABILITY = "awaiting-model-capability"
WAITING_SOURCE_REVIEW = "awaiting-source-review"
VALID_STAGE_STATUSES = frozenset(
    {RUNNABLE, WAITING_CAPABILITY, WAITING_SOURCE_REVIEW}
)
VALID_ENGINES = frozenset({"symbol-prototypes", "arithmetic-explanations"})


@dataclass(frozen=True, slots=True)
class CurriculumStage:
    """One dependency-ordered stage in the public curriculum plan."""

    stage_id: str
    title: str
    status: str
    engine: str | None
    prerequisites: tuple[str, ...]
    source_ids: tuple[str, ...]
    minimum_protected_accuracy: float
    minimum_held_out_accuracy: float
    waiting_reason: str | None

    @classmethod
    def from_mapping(cls, value: dict[str, object]) -> "CurriculumStage":
        return cls(
            stage_id=str(value["stage_id"]),
            title=str(value["title"]),
            status=str(value["status"]),
            engine=str(value["engine"]) if value.get("engine") else None,
            prerequisites=tuple(str(item) for item in value.get("prerequisites", [])),
            source_ids=tuple(str(item) for item in value.get("source_ids", [])),
            minimum_protected_accuracy=float(
                value.get("minimum_protected_accuracy", 1.0)
            ),
            minimum_held_out_accuracy=float(value.get("minimum_held_out_accuracy", 1.0)),
            waiting_reason=(
                str(value["waiting_reason"]) if value.get("waiting_reason") else None
            ),
        )


@dataclass(frozen=True, slots=True)
class CurriculumPlan:
    """A locally validated stage graph; it never fetches source material."""

    schema_version: int
    title: str
    stages: tuple[CurriculumStage, ...]

    @classmethod
    def load(cls, path: Path) -> "CurriculumPlan":
        raw = json.loads(path.read_text(encoding="utf-8"))
        plan = cls(
            schema_version=int(raw["schema_version"]),
            title=str(raw["title"]),
            stages=tuple(CurriculumStage.from_mapping(item) for item in raw["stages"]),
        )
        plan.validate()
        return plan

    def validate(self) -> None:
        identifiers = [stage.stage_id for stage in self.stages]
        if not identifiers or len(identifiers) != len(set(identifiers)):
            raise ValueError("Curriculum stages need unique, non-empty identifiers.")
        known = set(identifiers)
        for stage in self.stages:
            if stage.status not in VALID_STAGE_STATUSES:
                raise ValueError(f"Unknown curriculum status: {stage.status}")
            if stage.status == RUNNABLE and stage.engine not in VALID_ENGINES:
                raise ValueError(f"Runnable stage {stage.stage_id} lacks a supported engine.")
            if stage.status != RUNNABLE and stage.engine is not None:
                raise ValueError(f"Waiting stage {stage.stage_id} must not select an engine.")
            if stage.stage_id in stage.prerequisites:
                raise ValueError(f"Stage {stage.stage_id} cannot require itself.")
            if not set(stage.prerequisites).issubset(known):
                raise ValueError(f"Stage {stage.stage_id} refers to an unknown prerequisite.")
            for threshold in (
                stage.minimum_protected_accuracy,
                stage.minimum_held_out_accuracy,
            ):
                if not 0.0 <= threshold <= 1.0:
                    raise ValueError("Curriculum accuracy thresholds must be in [0, 1].")


@dataclass(frozen=True, slots=True)
class SchoolState:
    """Opt-in local checkpoint data, separate from model state and public Git."""

    schema_version: int
    completed_stage_ids: tuple[str, ...]

    @classmethod
    def load(cls, path: Path) -> "SchoolState":
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            schema_version=int(raw["schema_version"]),
            completed_stage_ids=tuple(str(item) for item in raw["completed_stage_ids"]),
        )

    def as_mapping(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "completed_stage_ids": list(self.completed_stage_ids),
        }


@dataclass(frozen=True, slots=True)
class SchoolConfig:
    """Finite, owner-controlled bounds for an automated curriculum pass."""

    plan_path: Path
    max_stages: int = 2
    lessons_per_stage: int = 24
    symbol_batch_size: int = 8
    seed: int = 7
    interval_ms: int = 80
    pause_file: Path | None = None
    stop_file: Path | None = None
    state_file: Path | None = None

    def __post_init__(self) -> None:
        if self.max_stages < 1:
            raise ValueError("max_stages must be at least one")
        if self.lessons_per_stage < 1:
            raise ValueError("lessons_per_stage must be at least one")
        if self.symbol_batch_size < 2:
            raise ValueError("symbol_batch_size must be at least two")
        if self.interval_ms < 0:
            raise ValueError("interval_ms cannot be negative")


@dataclass(frozen=True, slots=True)
class StageResult:
    """A compact, non-sensitive record of one curriculum decision."""

    stage_id: str
    outcome: str
    detail: str


@dataclass(frozen=True, slots=True)
class SchoolSummary:
    """Outcome of one finite automation pass."""

    completed_stage_ids: tuple[str, ...]
    results: tuple[StageResult, ...]
    stopped: bool


class ModelSchool:
    """Advance Kavi cores only through declared, evaluator-gated stages."""

    def __init__(
        self,
        config: SchoolConfig,
        *,
        emit: Callable[[str], None] | None = None,
    ) -> None:
        self.config = config
        self.emit = emit or (lambda line: print(line, flush=True))
        self.plan = CurriculumPlan.load(config.plan_path)
        self.state = self._load_state()

    def _load_state(self) -> SchoolState:
        if self.config.state_file is None or not self.config.state_file.exists():
            return SchoolState(schema_version=self.plan.schema_version, completed_stage_ids=())
        state = SchoolState.load(self.config.state_file)
        if state.schema_version != self.plan.schema_version:
            raise ValueError("Checkpoint schema does not match the curriculum plan.")
        known = {stage.stage_id for stage in self.plan.stages}
        if not set(state.completed_stage_ids).issubset(known):
            raise ValueError("Checkpoint refers to stages outside the curriculum plan.")
        return state

    def _save_state(self) -> None:
        if self.config.state_file is None:
            return
        path = self.config.state_file
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(f"{path.suffix}.tmp")
        temporary.write_text(
            json.dumps(self.state.as_mapping(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)

    def list_stages(self) -> tuple[CurriculumStage, ...]:
        """Return the ordered curriculum without starting any lesson."""

        return self.plan.stages

    @staticmethod
    def _meets_thresholds(
        protected_accuracy: float,
        held_out_accuracy: float,
        stage: CurriculumStage,
    ) -> bool:
        return (
            protected_accuracy >= stage.minimum_protected_accuracy
            and held_out_accuracy >= stage.minimum_held_out_accuracy
        )

    def _run_symbol_stage(self, stage: CurriculumStage) -> StageResult:
        runtime = SymbolRuntime(
            SymbolRuntimeConfig(
                steps=self.config.lessons_per_stage,
                seed=self.config.seed,
                batch_size=self.config.symbol_batch_size,
                interval_ms=self.config.interval_ms,
                pause_file=self.config.pause_file,
                stop_file=self.config.stop_file,
            ),
            emit=self.emit,
        )
        summary: SymbolRunSummary = runtime.run()
        if summary.stopped:
            return StageResult(stage.stage_id, "stopped", "Stop control ended the finite stage.")
        passed = self._meets_thresholds(
            summary.protected.exact_accuracy,
            summary.held_out.exact_accuracy,
            stage,
        )
        detail = (
            f"protected={summary.protected.exact_accuracy:.2f}; "
            f"held-out={summary.held_out.exact_accuracy:.2f}; "
            f"promoted candidates={summary.promoted_candidates}"
        )
        return StageResult(stage.stage_id, "passed" if passed else "not-promoted", detail)

    def _run_arithmetic_stage(self, stage: CurriculumStage) -> StageResult:
        runtime = ExplanationRuntime(
            RuntimeConfig(
                steps=self.config.lessons_per_stage,
                seed=self.config.seed,
                conflict_every=0,
                interval_ms=self.config.interval_ms,
                pause_file=self.config.pause_file,
                stop_file=self.config.stop_file,
            ),
            emit=self.emit,
        )
        summary = runtime.run()
        if summary.stopped:
            return StageResult(stage.stage_id, "stopped", "Stop control ended the finite stage.")
        protected = runtime.evaluator.evaluate(runtime.fabric, runtime.evaluator.protected)
        held_out = runtime.evaluator.evaluate(runtime.fabric, runtime.evaluator.held_out)
        passed = self._meets_thresholds(
            protected.exact_accuracy,
            held_out.exact_accuracy,
            stage,
        )
        detail = (
            f"protected={protected.exact_accuracy:.2f}; "
            f"held-out={held_out.exact_accuracy:.2f}; "
            f"promoted candidates={summary.promoted_candidates}"
        )
        return StageResult(stage.stage_id, "passed" if passed else "not-promoted", detail)

    def _run_stage(self, stage: CurriculumStage) -> StageResult:
        if stage.engine == "symbol-prototypes":
            return self._run_symbol_stage(stage)
        if stage.engine == "arithmetic-explanations":
            return self._run_arithmetic_stage(stage)
        raise ValueError(f"No implementation for stage engine {stage.engine}.")

    def run(self) -> SchoolSummary:
        """Run a finite sequence and stop at the first failed or waiting gate."""

        completed = list(self.state.completed_stage_ids)
        completed_set = set(completed)
        results: list[StageResult] = []
        attempts = 0
        self.emit(f"Kavi model curriculum: {self.plan.title}")
        self.emit(
            "  boundary: finite declared stages only; no source download, "
            "unreviewed ingestion, background scheduling, or source rewrite."
        )
        for stage in self.plan.stages:
            if stage.stage_id in completed_set:
                self.emit(f"[skip] {stage.stage_id}: already completed in the local checkpoint")
                continue
            missing = [item for item in stage.prerequisites if item not in completed_set]
            if missing:
                results.append(
                    StageResult(
                        stage.stage_id,
                        "waiting-prerequisite",
                        f"Missing completed prerequisites: {', '.join(missing)}",
                    )
                )
                break
            if stage.status != RUNNABLE:
                reason = stage.waiting_reason or "This stage is intentionally gated."
                self.emit(f"[gate] {stage.stage_id}: {reason}")
                results.append(StageResult(stage.stage_id, "waiting", reason))
                break
            if attempts >= self.config.max_stages:
                self.emit("[boundary] configured maximum stages reached")
                break
            self.emit(f"\n[stage] {stage.stage_id}: {stage.title}")
            result = self._run_stage(stage)
            results.append(result)
            attempts += 1
            self.emit(f"[stage result] {result.stage_id}: {result.outcome}; {result.detail}")
            if result.outcome == "stopped":
                return SchoolSummary(tuple(completed), tuple(results), True)
            if result.outcome != "passed":
                return SchoolSummary(tuple(completed), tuple(results), False)
            completed.append(stage.stage_id)
            completed_set.add(stage.stage_id)
            self.state = SchoolState(self.plan.schema_version, tuple(completed))
            self._save_state()
        return SchoolSummary(tuple(completed), tuple(results), False)
