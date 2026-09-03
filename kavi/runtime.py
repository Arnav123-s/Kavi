"""Bounded, observable execution for the initial Kavi experiment."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import random
import time
from typing import Callable

from .graph import PathwayFabric
from .learning import IndependentEvaluator, VerifierGatedLearner
from .types import ArithmeticEvent, Feedback, Inference, Operation


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    """Hard runtime limits for the first local experiment."""

    steps: int = 24
    seed: int = 7
    max_active_routes: int = 2
    evaluator_workers: int = 1
    conflict_every: int = 7
    interval_ms: int = 80
    pause_file: Path | None = None
    stop_file: Path | None = None

    def __post_init__(self) -> None:
        if self.steps < 1:
            raise ValueError("steps must be at least one")
        if self.max_active_routes < 1:
            raise ValueError("max_active_routes must be at least one")
        if self.evaluator_workers not in (1, 2):
            raise ValueError("evaluator_workers must be one or two")
        if self.conflict_every < 0:
            raise ValueError("conflict_every cannot be negative")
        if self.interval_ms < 0:
            raise ValueError("interval_ms cannot be negative")


class ArithmeticCurriculum:
    """A reproducible generator with no external corpus or network access."""

    def __init__(self, seed: int, conflict_every: int) -> None:
        self._random = random.Random(seed)
        self._conflict_every = conflict_every

    def event_at(self, step: int) -> ArithmeticEvent:
        operation = Operation.ADD if step % 2 else Operation.SUBTRACT
        left = self._random.randint(1, 12)
        right = self._random.randint(1, 12)
        if operation is Operation.SUBTRACT and right > left:
            left, right = right, left
        conflicted = self._conflict_every > 0 and step % self._conflict_every == 0
        return ArithmeticEvent(
            event_id=f"event-{step:04d}",
            left=left,
            right=right,
            operation=operation,
            correlation_id=f"correlation-{step:04d}",
            conflicted=conflicted,
        )


@dataclass(frozen=True, slots=True)
class RunSummary:
    """A compact outcome for a deliberately finite run."""

    completed_steps: int
    stopped: bool
    promoted_candidates: int
    correct_answers: int
    abstentions: int


class LiveRuntime:
    """Runs serial pathway steps and emits a human-readable event trace."""

    def __init__(
        self,
        config: RuntimeConfig,
        *,
        emit: Callable[[str], None] | None = None,
    ) -> None:
        self.config = config
        self.emit = emit or (lambda line: print(line, flush=True))
        self.fabric = PathwayFabric()
        self.evaluator = IndependentEvaluator(workers=config.evaluator_workers)
        self.learner = VerifierGatedLearner(self.evaluator)
        self.curriculum = ArithmeticCurriculum(config.seed, config.conflict_every)

    @property
    def device_profile(self) -> str:
        logical_cpus = os.cpu_count() or 1
        return (
            f"serial pathway microsteps; max active routes "
            f"{self.config.max_active_routes}; evaluator workers "
            f"{self.config.evaluator_workers}; host logical CPUs detected "
            f"{logical_cpus}"
        )

    def _stop_requested(self) -> bool:
        return self.config.stop_file is not None and self.config.stop_file.exists()

    def _wait_if_paused(self) -> bool:
        """Return false if stopped while waiting; never deletes control files."""

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

    def _emit_event(self, step: int, inference: Inference, feedback: Feedback) -> None:
        event = inference.event
        quantity_route = (
            " > ".join(inference.quantity_signal.pipe_ids)
            if inference.quantity_signal
            else "none"
        )
        relation_route = (
            " > ".join(inference.relation_signal.pipe_ids)
            if inference.relation_signal
            else "none"
        )
        join_kind = (
            "constructive" if inference.interference > 0 else "destructive"
            if inference.interference < 0
            else "neutral"
        )
        answer = "abstain" if inference.answer is None else str(inference.answer)
        ledger = self.fabric.resource_ledger(inference)
        self.emit(f"\n[{step:03d}] event {event.event_id}: {event.text} = ?")
        self.emit(
            f"  hard paths ({len(inference.active_pipe_ids)}/{self.config.max_active_routes}):"
        )
        self.emit(f"    quantity: {quantity_route}")
        self.emit(f"    relation: {relation_route}")
        self.emit(
            f"  typed join: {join_kind}; interference={inference.interference:+.3f}; "
            f"confidence={inference.confidence:.2f}; uncertainty={inference.uncertainty:.2f}"
        )
        self.emit(f"  answer path: {answer}")
        if inference.abstain_reason:
            self.emit(f"  abstain reason: {inference.abstain_reason}")
        self.emit(f"  verifier: {feedback.verdict}")
        self.emit(
            f"  feedback path: {feedback.valence.value}; "
            f"{feedback.candidate_action}"
        )
        if feedback.parent_protected is not None:
            self.emit(
                "  candidate checks: protected "
                f"{feedback.parent_protected.mean_absolute_error:.2f}"
                f" to {feedback.candidate_protected.mean_absolute_error:.2f} MAE, "
                "held-out "
                f"{feedback.parent_held_out.mean_absolute_error:.2f}"
                f" to {feedback.candidate_held_out.mean_absolute_error:.2f} MAE"
            )
        self.emit(
            "  ledger (explicit estimate): "
            f"{ledger['persistent_scalars']} persistent scalars, "
            f"{ledger['active_pipes']} active pipes, "
            f"about {ledger['estimated_transient_bytes']} transient bytes"
        )

    def run(self) -> RunSummary:
        """Run at most steps events, honoring user-controlled stop and pause."""

        self.emit("Kavi stage-0 live pathway trace")
        self.emit(f"  profile: {self.device_profile}")
        self.emit(
            "  boundary: finite local test; no network, source rewrite, "
            "background persistence, or hardware-limit changes."
        )
        completed = promoted = correct = abstentions = 0
        for step in range(1, self.config.steps + 1):
            if self._stop_requested() or not self._wait_if_paused():
                self.emit("[control] stop requested; preserving the current in-memory parent.")
                return RunSummary(completed, True, promoted, correct, abstentions)
            event = self.curriculum.event_at(step)
            inference = self.fabric.infer(
                event,
                max_active_routes=self.config.max_active_routes,
            )
            feedback = self.learner.observe(self.fabric, inference)
            self._emit_event(step, inference, feedback)
            completed += 1
            promoted += int(feedback.promoted)
            correct += int(inference.answer == event.target)
            abstentions += int(inference.answer is None)
            if self.config.interval_ms:
                time.sleep(self.config.interval_ms / 1000.0)
        return RunSummary(completed, False, promoted, correct, abstentions)

    def ask(self, left: int, right: int, operation: Operation) -> Inference:
        """Answer one extra exact problem with the learned in-memory paths."""

        event = ArithmeticEvent(
            event_id="interactive-query",
            left=left,
            right=right,
            operation=operation,
            correlation_id="interactive-query",
        )
        return self.fabric.infer(event, max_active_routes=self.config.max_active_routes)
