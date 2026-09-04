"""Finite multi-feed curriculum runtime for Kavi's unified pathway circuit.

One writer teaches the model.  Independent read-only viewers follow JSONL
channels for answers, active pathways, structural learning, and grading.  All
run artifacts stay under the ignored local ``runs`` directory.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import random
import time
from typing import Callable, Sequence

from .pathway_circuit import (
    CandidateAssessment,
    CategoryInference,
    CircuitSample,
    CircuitState,
    ClassificationMetrics,
    PathwayCircuitCore,
    StateDelta,
    arithmetic_target_weights,
)
from .runtime import ArithmeticCurriculum
from .source_manifest import SourceManifest
from .symbol_core import SymbolEvent
from .symbol_runtime import (
    SymbolCurriculum,
    held_out_manifest as symbol_held_out_manifest,
    protected_manifest as symbol_protected_manifest,
)
from .textbook_core import TextbookEvent, notation_features
from .textbook_runtime import LocalTextbookLesson
from .types import ArithmeticEvent
from .learning import (
    held_out_manifest as arithmetic_held_out_manifest,
    protected_manifest as arithmetic_protected_manifest,
)
from .unicode_core import ScriptEvent, UnicodeSignalContract
from .unicode_runtime import (
    SCRIPT_SPECS,
    UnicodeScriptCurriculum,
    contract_held_out_manifest,
    contract_protected_manifest,
    held_out_manifest as script_held_out_manifest,
    protected_manifest as script_protected_manifest,
)


CHANNELS = ("answers", "pathways", "learning", "grading")
TERMINAL_STATES = frozenset({"complete", "stopped", "failed"})


def _safe_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


class LiveEventBus:
    """Append-only local event channels for separate terminal viewers."""

    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir.resolve()
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.sequence = 0
        self.paths = {channel: self.run_dir / f"{channel}.jsonl" for channel in CHANNELS}
        if any(path.exists() and path.stat().st_size for path in self.paths.values()):
            raise ValueError("The live run directory already contains channel events.")
        for path in self.paths.values():
            path.touch(exist_ok=True)
        self.status_path = self.run_dir / "status.json"
        self.update_status("starting")

    def update_status(self, state: str, **values: object) -> None:
        _safe_write_json(
            self.status_path,
            {
                "schema_version": 1,
                "state": state,
                "sequence": self.sequence,
                **values,
            },
        )

    def emit(self, channel: str, kind: str, **values: object) -> None:
        if channel not in self.paths:
            raise ValueError(f"Unknown live event channel: {channel}")
        self.sequence += 1
        payload = {
            "schema_version": 1,
            "sequence": self.sequence,
            "channel": channel,
            "kind": kind,
            **values,
        }
        with self.paths[channel].open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, sort_keys=True) + "\n")
            stream.flush()


@dataclass(frozen=True, slots=True)
class PathwayLiveConfig:
    """Owner-controlled limits for one complete currently runnable curriculum pass."""

    run_dir: Path
    lesson_path: Path = Path(
        "private/lessons/basic-algebra-6e-expressions-relations-1-1.json"
    )
    source_manifest_path: Path = Path("curriculum/source-manifest.json")
    max_parallel_paths: int = 4
    interval_ms: int = 250
    start_delay_seconds: int = 6
    seed: int = 31
    pause_file: Path | None = None
    stop_file: Path | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.max_parallel_paths <= 8:
            raise ValueError("max_parallel_paths must be between one and eight.")
        if self.interval_ms < 0:
            raise ValueError("interval_ms cannot be negative.")
        if not 0 <= self.start_delay_seconds <= 30:
            raise ValueError("start_delay_seconds must be between zero and thirty.")


@dataclass(frozen=True, slots=True)
class PathwayRunSummary:
    completed_stage_ids: tuple[str, ...]
    stopped: bool
    next_gate: str
    routes: int
    jump_adapters: int


def _symbol_sample(event: SymbolEvent) -> CircuitSample:
    coordinate = ord(event.glyph) / 127.0
    return CircuitSample(
        event_id=event.event_id,
        task_id="glyph-kind",
        target=event.target.value,
        feature_names=("bias", "ascii-coordinate"),
        features=(1.0, coordinate),
        source_activations=(
            ("component/context-loop", 1.0),
            ("component/ascii-scalar-detector", 1.0),
        ),
        display_text=repr(event.glyph),
    )


def _script_sample(event: ScriptEvent) -> CircuitSample:
    coordinate = ord(event.glyph) / 0x10FFFF
    return CircuitSample(
        event_id=event.event_id,
        task_id="unicode-script",
        target=event.target.value,
        feature_names=("bias", "unicode-coordinate"),
        features=(1.0, coordinate),
        source_activations=(
            ("component/context-loop", 1.0),
            ("path/unicode-scalar", 1.0),
        ),
        display_text=f"{event.glyph!r} U+{ord(event.glyph):04X}",
    )


def _notation_sample(event: TextbookEvent, core: PathwayCircuitCore) -> CircuitSample:
    features = notation_features(event.notation)
    relation, arithmetic, letters, digits, extent = features
    route_ids = core.state.route_map()
    transform_ids = core.state.transform_map()
    letter_path = (
        "path/glyph-kind/letter"
        if "path/glyph-kind/letter" in route_ids
        else "component/letter-detector"
    )
    digit_path = (
        "path/glyph-kind/digit"
        if "path/glyph-kind/digit" in route_ids
        else "component/digit-detector"
    )
    compact = event.notation.replace(" ", "").replace("·", "*").replace("÷", "/")
    sources: list[tuple[str, float]] = [("component/context-loop", 1.0)]
    if letters > 0.0:
        sources.append((letter_path, letters))
    if digits > 0.0:
        sources.append((digit_path, digits))
    if arithmetic > 0.0:
        if "+" in compact and "path/arithmetic/add" in transform_ids:
            sources.append(("path/arithmetic/add", arithmetic))
        if "-" in compact and "path/arithmetic/subtract" in transform_ids:
            sources.append(("path/arithmetic/subtract", arithmetic))
        if not any(source_id.startswith("path/arithmetic/") for source_id, _ in sources):
            sources.append(("component/arithmetic-switch", arithmetic))
    if relation > 0.0:
        sources.append(("component/relation-switch", relation))
    if any(character in compact for character in "()[]"):
        sources.append(("component/grouping-loop", 1.0))
    sources.append(("component/extent-capacitor", extent))
    return CircuitSample(
        event_id=event.event_id,
        task_id="notation-kind",
        target=event.target.value,
        feature_names=("relation", "arithmetic", "letters", "digits", "extent"),
        features=features,
        source_activations=tuple(sources),
        display_text=repr(event.notation),
    )


class PathwayCurriculumRuntime:
    """Teach every currently implemented stage through one persistent circuit."""

    def __init__(
        self,
        config: PathwayLiveConfig,
        *,
        emit: Callable[[str], None] | None = None,
    ) -> None:
        self.config = config
        self.emit = emit or (lambda line: print(line, flush=True))
        self.bus = LiveEventBus(config.run_dir)
        source_manifest = SourceManifest.load(config.source_manifest_path)
        self.textbook_lesson = LocalTextbookLesson.load(config.lesson_path, source_manifest)
        self.core = PathwayCircuitCore()
        self.completed: list[str] = []
        self.random = random.Random(config.seed)
        self.state_path = self.bus.run_dir / "model-state.json"
        self.curriculum_state_path = self.bus.run_dir / "curriculum-state.json"
        self.archive_dir = self.bus.run_dir / "archive"
        self.promotion_index = 0

    def _checkpoint(self) -> None:
        _safe_write_json(self.state_path, self.core.state.as_mapping())
        _safe_write_json(
            self.curriculum_state_path,
            {
                "schema_version": 1,
                "completed_stage_ids": self.completed,
                "next_gate": "word-forms-and-definitions",
            },
        )

    def _promote(self, candidate: CircuitState, stage_id: str, delta: StateDelta) -> None:
        """Archive the frozen parent, then make only the accepted child active."""

        self.promotion_index += 1
        archive_path = self.archive_dir / f"parent-{self.promotion_index:04d}.json"
        _safe_write_json(
            archive_path,
            {
                "schema_version": 1,
                "stage": stage_id,
                "reason": "parent archived before independently verified promotion",
                "active_during_inference": False,
                "delta": {
                    "created_routes": list(delta.created_route_ids),
                    "modified_routes": list(delta.modified_route_ids),
                    "created_adapters": list(delta.created_adapter_ids),
                    "modified_adapters": list(delta.modified_adapter_ids),
                },
                "parent_state": self.core.state.as_mapping(),
            },
        )
        self.core.promote(candidate)
        self.bus.emit(
            "learning",
            "parent-archived",
            stage=stage_id,
            archive=archive_path.name,
            active_during_inference=False,
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

    def _step_wait(self) -> bool:
        if self._stop_requested() or not self._wait_if_paused():
            return False
        if self.config.interval_ms:
            time.sleep(self.config.interval_ms / 1000.0)
        return not self._stop_requested()

    def _trace_category(
        self,
        stage_id: str,
        phase: str,
        sample: CircuitSample,
        inference: CategoryInference,
    ) -> None:
        self.bus.emit(
            "pathways",
            "route-trace",
            stage=stage_id,
            phase=phase,
            event_id=sample.event_id,
            input=sample.display_text,
            waves=[list(wave) for wave in inference.activation_waves],
            candidates=[
                {
                    "route": candidate.route_id,
                    "label": candidate.output_label,
                    "distance": round(candidate.distance, 6),
                    "amplitude": [
                        round(candidate.real_amplitude, 6),
                        round(candidate.imaginary_amplitude, 6),
                    ],
                    "intensity": round(candidate.intensity, 6),
                }
                for candidate in inference.candidates
            ],
            selected_route=inference.selected_route_id,
            jumps=list(inference.active_adapter_ids),
            abstain_reason=inference.abstain_reason,
        )

    def _answer_category(
        self,
        stage_id: str,
        phase: str,
        sample: CircuitSample,
        inference: CategoryInference,
    ) -> None:
        self.bus.emit(
            "answers",
            "model-answer",
            stage=stage_id,
            phase=phase,
            event_id=sample.event_id,
            input=sample.display_text,
            answer=inference.prediction or "abstain",
            expected=sample.target,
            confidence=round(inference.confidence, 6),
        )

    def _trace_arithmetic(
        self,
        stage_id: str,
        phase: str,
        event: ArithmeticEvent,
        inference: object,
    ) -> None:
        self.bus.emit(
            "pathways",
            "route-trace",
            stage=stage_id,
            phase=phase,
            event_id=event.event_id,
            input=f"{event.text} = ?",
            waves=[list(wave) for wave in inference.activation_waves],
            candidates=list(inference.candidate_route_ids),
            selected_route=inference.selected_route_id,
            jumps=list(inference.active_adapter_ids),
            abstain_reason=inference.abstain_reason,
        )
        self.bus.emit(
            "answers",
            "model-answer",
            stage=stage_id,
            phase=phase,
            event_id=event.event_id,
            input=f"{event.text} = ?",
            answer="abstain" if inference.answer is None else str(inference.answer),
            expected=str(event.target),
            confidence=round(inference.confidence, 6),
        )

    def _emit_learning(
        self,
        stage_id: str,
        delta: StateDelta,
        accepted: bool,
        *,
        parent_protected: ClassificationMetrics,
        candidate_protected: ClassificationMetrics,
        parent_held_out: ClassificationMetrics,
        candidate_held_out: ClassificationMetrics,
    ) -> None:
        ledger = self.core.resource_ledger()
        self.bus.emit(
            "learning",
            "candidate-change",
            stage=stage_id,
            decision="PROMOTED" if accepted else "REJECTED",
            created_routes=list(delta.created_route_ids),
            modified_routes=list(delta.modified_route_ids),
            created_jumps=list(delta.created_adapter_ids),
            modified_jumps=list(delta.modified_adapter_ids),
            changed_objects=delta.changed_objects,
            protected_before=parent_protected.exact_accuracy,
            protected_after=candidate_protected.exact_accuracy,
            held_out_before=parent_held_out.exact_accuracy,
            held_out_after=candidate_held_out.exact_accuracy,
            model_routes=ledger["routes"],
            model_jump_adapters=ledger["jump_adapters"],
            numeric_payload_bytes=ledger["estimated_numeric_payload_bytes"],
        )

    def _grade_category_stage(
        self,
        stage_id: str,
        protected: Sequence[CircuitSample],
        held_out: Sequence[CircuitSample],
        protected_threshold: float,
        held_out_threshold: float,
    ) -> bool:
        for partition, samples in (("protected", protected), ("held-out", held_out)):
            ordered = list(samples)
            self.random.shuffle(ordered)
            for sample in ordered:
                inference = self.core.infer_category(
                    sample,
                    max_parallel_paths=self.config.max_parallel_paths,
                )
                self._trace_category(stage_id, partition, sample, inference)
                self._answer_category(stage_id, partition, sample, inference)
                self.bus.emit(
                    "grading",
                    "test-case",
                    stage=stage_id,
                    partition=partition,
                    event_id=sample.event_id,
                    input=sample.display_text,
                    expected=sample.target,
                    answer=inference.prediction or "abstain",
                    result="PASS" if inference.prediction == sample.target else "FAIL",
                )
                if not self._step_wait():
                    return False
        protected_metrics = self.core.evaluate_categories(
            protected,
            max_parallel_paths=self.config.max_parallel_paths,
        )
        held_out_metrics = self.core.evaluate_categories(
            held_out,
            max_parallel_paths=self.config.max_parallel_paths,
        )
        passed = (
            protected_metrics.exact_accuracy >= protected_threshold
            and held_out_metrics.exact_accuracy >= held_out_threshold
        )
        self.bus.emit(
            "grading",
            "stage-grade",
            stage=stage_id,
            protected_accuracy=protected_metrics.exact_accuracy,
            held_out_accuracy=held_out_metrics.exact_accuracy,
            protected_threshold=protected_threshold,
            held_out_threshold=held_out_threshold,
            result="PASS" if passed else "FAIL",
        )
        return passed

    def _teach_category_batches(
        self,
        stage_id: str,
        training: Sequence[CircuitSample],
        protected: Sequence[CircuitSample],
        held_out: Sequence[CircuitSample],
        batch_size: int,
    ) -> bool:
        for start in range(0, len(training), batch_size):
            batch = tuple(training[start : start + batch_size])
            for sample in batch:
                inference = self.core.infer_category(
                    sample,
                    max_parallel_paths=self.config.max_parallel_paths,
                )
                self._trace_category(stage_id, "teach-before", sample, inference)
                self._answer_category(stage_id, "teach-before", sample, inference)
            candidate, delta = self.core.propose_category_update(batch)
            assessment: CandidateAssessment = self.core.assess_category_candidate(
                batch,
                protected,
                held_out,
                candidate,
                delta,
                max_parallel_paths=self.config.max_parallel_paths,
            )
            self._emit_learning(
                stage_id,
                delta,
                assessment.accepted,
                parent_protected=assessment.parent_protected,
                candidate_protected=assessment.candidate_protected,
                parent_held_out=assessment.parent_held_out,
                candidate_held_out=assessment.candidate_held_out,
            )
            if assessment.accepted:
                self._promote(assessment.candidate_state, stage_id, delta)
                self._checkpoint()
            for sample in batch:
                inference = self.core.infer_category(
                    sample,
                    max_parallel_paths=self.config.max_parallel_paths,
                )
                self._trace_category(stage_id, "teach-after", sample, inference)
                self._answer_category(stage_id, "teach-after", sample, inference)
            if not self._step_wait():
                return False
        return True

    def _run_symbol_stage(self) -> bool:
        stage_id = "glyph-kinds"
        self.emit(f"[stage] {stage_id}: forming reusable letter and digit routes")
        curriculum = SymbolCurriculum(self.config.seed)
        training = tuple(_symbol_sample(curriculum.event_at(step)) for step in range(1, 9))
        protected = tuple(_symbol_sample(event) for event in symbol_protected_manifest())
        held_out = tuple(_symbol_sample(event) for event in symbol_held_out_manifest())
        if not self._teach_category_batches(stage_id, training, protected, held_out, 2):
            return False
        passed = self._grade_category_stage(stage_id, protected, held_out, 1.0, 1.0)
        if passed:
            self.completed.append(stage_id)
            self._checkpoint()
        return passed

    def _run_arithmetic_stage(self) -> bool:
        stage_id = "quantity-and-exact-relations"
        self.emit(f"[stage] {stage_id}: reusing the digit path inside arithmetic routes")
        curriculum = ArithmeticCurriculum(self.config.seed, conflict_every=0)
        training = tuple(curriculum.event_at(step) for step in range(1, 13))
        protected = arithmetic_protected_manifest()
        held_out = arithmetic_held_out_manifest()
        for event in training:
            before = self.core.infer_arithmetic(
                event,
                max_parallel_paths=self.config.max_parallel_paths,
            )
            self._trace_arithmetic(stage_id, "teach-before", event, before)
            candidate, delta = self.core.propose_arithmetic_update(
                event,
                arithmetic_target_weights(event.operation),
            )
            (
                accepted,
                parent_protected,
                candidate_protected,
                parent_held_out,
                candidate_held_out,
            ) = self.core.arithmetic_candidate_is_safe(
                event,
                candidate,
                protected,
                held_out,
                max_parallel_paths=self.config.max_parallel_paths,
            )
            self._emit_learning(
                stage_id,
                delta,
                accepted,
                parent_protected=parent_protected,
                candidate_protected=candidate_protected,
                parent_held_out=parent_held_out,
                candidate_held_out=candidate_held_out,
            )
            if accepted:
                self._promote(candidate, stage_id, delta)
                self._checkpoint()
            after = self.core.infer_arithmetic(
                event,
                max_parallel_paths=self.config.max_parallel_paths,
            )
            self._trace_arithmetic(stage_id, "teach-after", event, after)
            if not self._step_wait():
                return False
        for partition, events in (("protected", protected), ("held-out", held_out)):
            ordered = list(events)
            self.random.shuffle(ordered)
            for event in ordered:
                inference = self.core.infer_arithmetic(
                    event,
                    max_parallel_paths=self.config.max_parallel_paths,
                )
                self._trace_arithmetic(stage_id, partition, event, inference)
                self.bus.emit(
                    "grading",
                    "test-case",
                    stage=stage_id,
                    partition=partition,
                    event_id=event.event_id,
                    input=f"{event.text} = ?",
                    expected=str(event.target),
                    answer="abstain" if inference.answer is None else str(inference.answer),
                    result="PASS" if inference.answer == event.target else "FAIL",
                )
                if not self._step_wait():
                    return False
        protected_metrics = self.core.evaluate_arithmetic(protected)
        held_out_metrics = self.core.evaluate_arithmetic(held_out)
        passed = protected_metrics.exact_accuracy == 1.0 and held_out_metrics.exact_accuracy == 1.0
        self.bus.emit(
            "grading",
            "stage-grade",
            stage=stage_id,
            protected_accuracy=protected_metrics.exact_accuracy,
            held_out_accuracy=held_out_metrics.exact_accuracy,
            protected_threshold=1.0,
            held_out_threshold=1.0,
            result="PASS" if passed else "FAIL",
        )
        if passed:
            self.completed.append(stage_id)
            self._checkpoint()
        return passed

    def _run_unicode_contract_stage(self) -> bool:
        stage_id = "unicode-signal-contract"
        self.emit(f"[stage] {stage_id}: verifying the exact Unicode input route")
        passed = True
        cases = (*contract_protected_manifest(), *contract_held_out_manifest())
        for case in cases:
            signal = UnicodeSignalContract.inspect(case.glyph)
            exact = (
                signal.glyph == case.glyph
                and signal.code_point == ord(case.glyph)
                and chr(signal.code_point) == case.glyph
            )
            passed = passed and exact
            self.bus.emit(
                "answers",
                "model-answer",
                stage=stage_id,
                phase="contract",
                event_id=case.case_id,
                input=repr(case.glyph),
                answer=f"U+{signal.code_point:04X}",
                expected=f"U+{ord(case.glyph):04X}",
                confidence=1.0 if exact else 0.0,
            )
            self.bus.emit(
                "pathways",
                "route-trace",
                stage=stage_id,
                phase="contract",
                event_id=case.case_id,
                input=repr(case.glyph),
                waves=[["component/unicode-detector"], ["path/unicode-scalar"]],
                candidates=["path/unicode-scalar"],
                selected_route="path/unicode-scalar" if exact else None,
                jumps=["component/exact-codepoint-transformer"],
                abstain_reason=None if exact else "Exact scalar round-trip failed.",
            )
            self.bus.emit(
                "grading",
                "test-case",
                stage=stage_id,
                partition="exact-contract",
                event_id=case.case_id,
                input=repr(case.glyph),
                expected=f"U+{ord(case.glyph):04X}",
                answer=f"U+{signal.code_point:04X}",
                result="PASS" if exact else "FAIL",
            )
            if not self._step_wait():
                return False
        if passed:
            candidate = replace(
                self.core.state,
                verified_foundations=tuple(
                    sorted(
                        set((*self.core.state.verified_foundations, "path/unicode-scalar"))
                    )
                ),
            )
            delta = StateDelta(("path/unicode-scalar",), (), (), ())
            self._promote(candidate, stage_id, delta)
            self.completed.append(stage_id)
            self._checkpoint()
        self.bus.emit(
            "grading",
            "stage-grade",
            stage=stage_id,
            protected_accuracy=1.0 if passed else 0.0,
            held_out_accuracy=1.0 if passed else 0.0,
            protected_threshold=1.0,
            held_out_threshold=1.0,
            result="PASS" if passed else "FAIL",
        )
        return passed

    def _run_script_stage(self) -> bool:
        stage_id = "multiscript-glyph-foundations"
        self.emit(f"[stage] {stage_id}: branching the verified Unicode route into script routes")
        curriculum = UnicodeScriptCurriculum(self.config.seed)
        steps = len(SCRIPT_SPECS) * 3
        training = tuple(_script_sample(curriculum.event_at(step)) for step in range(1, steps + 1))
        protected = tuple(_script_sample(event) for event in script_protected_manifest())
        held_out = tuple(_script_sample(event) for event in script_held_out_manifest())
        if not self._teach_category_batches(
            stage_id,
            training,
            protected,
            held_out,
            len(SCRIPT_SPECS),
        ):
            return False
        passed = self._grade_category_stage(stage_id, protected, held_out, 1.0, 1.0)
        if passed:
            self.completed.append(stage_id)
            self._checkpoint()
        return passed

    def _run_textbook_stage(self) -> bool:
        stage_id = "textbook-concepts-expressions-relations"
        self.emit(
            f"[stage] {stage_id}: joining learned glyph and arithmetic paths through a reviewed lesson"
        )
        training = tuple(_notation_sample(event, self.core) for event in self.textbook_lesson.train)
        protected = tuple(_notation_sample(event, self.core) for event in self.textbook_lesson.protected)
        held_out = tuple(_notation_sample(event, self.core) for event in self.textbook_lesson.held_out)
        if not self._teach_category_batches(stage_id, training, protected, held_out, 2):
            return False
        passed = self._grade_category_stage(stage_id, protected, held_out, 0.9, 0.9)
        if passed:
            self.completed.append(stage_id)
            self._checkpoint()
        return passed

    def run(self) -> PathwayRunSummary:
        """Run all five implemented stages and stop at the declared next gate."""

        self.emit("Kavi unified path-centric curriculum")
        self.emit(f"  run directory: {self.bus.run_dir}")
        self.emit(
            "  model: one persistent circuit; learned routes and jump adapters are shared across stages"
        )
        self.emit(
            "  boundary: finite local run; no web fetching, background persistence, self-code changes, "
            "or claim of language/calculus capability"
        )
        self.emit(
            f"  start delay: {self.config.start_delay_seconds}s so all four viewers can attach"
        )
        self.bus.update_status("running", completed_stage_ids=[])
        if self.config.start_delay_seconds:
            time.sleep(self.config.start_delay_seconds)
        stages = (
            self._run_symbol_stage,
            self._run_arithmetic_stage,
            self._run_unicode_contract_stage,
            self._run_script_stage,
            self._run_textbook_stage,
        )
        try:
            for stage in stages:
                if self._stop_requested():
                    self.bus.update_status(
                        "stopped",
                        completed_stage_ids=self.completed,
                        next_gate="owner stop control",
                    )
                    return self._summary(True, "owner stop control")
                passed = stage()
                if not passed:
                    state = "stopped" if self._stop_requested() else "failed"
                    gate = "owner stop control" if state == "stopped" else "failed stage gate"
                    self.bus.update_status(
                        state,
                        completed_stage_ids=self.completed,
                        next_gate=gate,
                    )
                    return self._summary(state == "stopped", gate)
            gate = "word-forms-and-definitions (not implemented or source-approved yet)"
            self.bus.emit(
                "grading",
                "curriculum-boundary",
                completed_stage_ids=self.completed,
                next_gate=gate,
            )
            self.bus.update_status(
                "complete",
                completed_stage_ids=self.completed,
                next_gate=gate,
            )
            self.emit(f"[complete] five implemented stages passed; next gate: {gate}")
            return self._summary(False, gate)
        except Exception as error:
            self.bus.update_status(
                "failed",
                completed_stage_ids=self.completed,
                next_gate="runtime exception",
                error=f"{type(error).__name__}: {error}",
            )
            raise

    def _summary(self, stopped: bool, next_gate: str) -> PathwayRunSummary:
        ledger = self.core.resource_ledger()
        return PathwayRunSummary(
            completed_stage_ids=tuple(self.completed),
            stopped=stopped,
            next_gate=next_gate,
            routes=ledger["routes"],
            jump_adapters=ledger["jump_adapters"],
        )


def _status_state(path: Path) -> str | None:
    try:
        return str(json.loads(path.read_text(encoding="utf-8"))["state"])
    except (FileNotFoundError, json.JSONDecodeError, KeyError, OSError):
        return None


def format_live_event(event: dict[str, object]) -> str:
    """Format one local event for its dedicated low-overhead terminal."""

    channel = str(event["channel"])
    kind = str(event["kind"])
    stage = str(event.get("stage", "curriculum"))
    if channel == "answers":
        return (
            f"[{stage} | {event.get('phase')}] {event.get('input')}\n"
            f"  Kavi: {event.get('answer')} | expected: {event.get('expected')} | "
            f"confidence={float(event.get('confidence', 0.0)):.3f}"
        )
    if channel == "pathways":
        waves = event.get("waves", [])
        wave_lines = "\n".join(
            f"  wave {index}: " + " + ".join(str(item) for item in wave)
            for index, wave in enumerate(waves, start=1)
        )
        candidates = event.get("candidates", [])
        candidate_lines: list[str] = []
        for candidate in candidates:
            if isinstance(candidate, dict):
                candidate_lines.append(
                    f"    {candidate.get('route')}: intensity={float(candidate.get('intensity', 0.0)):.6f}; "
                    f"distance={float(candidate.get('distance', 0.0)):.4f}"
                )
            else:
                candidate_lines.append(f"    {candidate}")
        route_text = "\n".join(candidate_lines) or "    none"
        jumps = ", ".join(str(item) for item in event.get("jumps", [])) or "none"
        reason = event.get("abstain_reason")
        reason_line = f"\n  abstain: {reason}" if reason else ""
        return (
            f"[{stage} | {event.get('phase')}] {event.get('input')}\n"
            f"{wave_lines}\n  candidate routes:\n{route_text}\n"
            f"  selected: {event.get('selected_route') or 'none'}\n"
            f"  jump components: {jumps}{reason_line}"
        )
    if channel == "learning":
        if kind == "parent-archived":
            return (
                f"[{stage}] parent frozen outside the active brain\n"
                f"  archive: {event.get('archive')} | used during inference: "
                f"{event.get('active_during_inference')}"
            )
        created_routes = ", ".join(str(item) for item in event.get("created_routes", [])) or "none"
        modified_routes = ", ".join(str(item) for item in event.get("modified_routes", [])) or "none"
        created_jumps = ", ".join(str(item) for item in event.get("created_jumps", [])) or "none"
        modified_jumps = ", ".join(str(item) for item in event.get("modified_jumps", [])) or "none"
        return (
            f"[{stage}] {event.get('decision')} — {event.get('changed_objects')} local changes\n"
            f"  new routes: {created_routes}\n  reshaped routes: {modified_routes}\n"
            f"  new jump components: {created_jumps}\n  tuned jump components: {modified_jumps}\n"
            f"  protected: {float(event.get('protected_before', 0.0)):.2%} -> "
            f"{float(event.get('protected_after', 0.0)):.2%}; held-out: "
            f"{float(event.get('held_out_before', 0.0)):.2%} -> "
            f"{float(event.get('held_out_after', 0.0)):.2%}\n"
            f"  total routes={event.get('model_routes')}; jumps={event.get('model_jump_adapters')}; "
            f"numeric payload≈{event.get('numeric_payload_bytes')} bytes"
        )
    if channel == "grading" and kind == "test-case":
        return (
            f"[{stage} | {event.get('partition')}] {event.get('result')} {event.get('input')}\n"
            f"  expected: {event.get('expected')} | Kavi: {event.get('answer')}"
        )
    if channel == "grading" and kind == "stage-grade":
        return (
            f"[{stage}] {event.get('result')}\n"
            f"  protected={float(event.get('protected_accuracy', 0.0)):.2%} "
            f"(need {float(event.get('protected_threshold', 0.0)):.2%})\n"
            f"  held-out={float(event.get('held_out_accuracy', 0.0)):.2%} "
            f"(need {float(event.get('held_out_threshold', 0.0)):.2%})"
        )
    return (
        f"[curriculum boundary] completed: "
        f"{', '.join(str(item) for item in event.get('completed_stage_ids', []))}\n"
        f"  next gate: {event.get('next_gate')}"
    )


def watch_channel(
    run_dir: Path,
    channel: str,
    *,
    emit: Callable[[str], None] | None = None,
    poll_ms: int = 100,
) -> int:
    """Follow one finite local channel and exit after its writer finishes."""

    if channel not in CHANNELS:
        raise ValueError(f"channel must be one of: {', '.join(CHANNELS)}")
    output = emit or (lambda line: print(line, flush=True))
    root = run_dir.resolve()
    event_path = root / f"{channel}.jsonl"
    status_path = root / "status.json"
    output(f"Kavi {channel} feed")
    output(f"  waiting for: {event_path}")
    position = 0
    terminal_polls = 0
    while True:
        emitted = False
        try:
            with event_path.open("r", encoding="utf-8") as stream:
                stream.seek(position)
                for line in stream:
                    if not line.strip():
                        continue
                    output("\n" + format_live_event(json.loads(line)))
                    emitted = True
                position = stream.tell()
        except FileNotFoundError:
            pass
        state = _status_state(status_path)
        if state in TERMINAL_STATES and not emitted:
            terminal_polls += 1
            if terminal_polls >= 2:
                output(f"\n[feed closed] run state={state}")
                return 0 if state == "complete" else 1
        else:
            terminal_polls = 0
        time.sleep(max(10, poll_ms) / 1000.0)
