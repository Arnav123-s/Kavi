"""An external experiment manager for candidate model updates.

This module belongs to the teacher, not to Kavi's inference model. Candidate
generation may later use other optimizers without adding them to model state.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from time import perf_counter
from typing import Callable, Iterable

from .pathway_circuit import CircuitState, StateDelta


@dataclass(frozen=True, slots=True)
class TeachingTrial:
    proposal_id: str
    candidate: CircuitState
    delta: StateDelta
    mistakes: int
    retained: bool
    previously_correct_retained: bool
    serialized_bytes: int
    elapsed_ms: float
    eligible: bool


def search_candidates(
    proposals: Iterable[tuple[str, CircuitState, StateDelta]],
    *,
    parent_mistakes: int,
    assess: Callable[[CircuitState], tuple[int, bool, bool]],
    max_serialized_bytes: int,
    max_trials: int = 3,
) -> tuple[TeachingTrial | None, tuple[TeachingTrial, ...]]:
    """Evaluate a finite proposal stream without promoting any candidate.

    Prefer configuration-only changes, then rank by mistakes and state size,
    and changed-object count. Timing is reported, not used as a noisy reward.
    """

    if max_serialized_bytes < 1 or not 1 <= max_trials <= 12:
        raise ValueError("Invalid teaching-search budget.")
    trials = []
    for proposal_id, candidate, delta in proposals:
        if len(trials) >= max_trials:
            break
        started = perf_counter()
        size = len(json.dumps(candidate.as_mapping()).encode("utf-8"))
        if size <= max_serialized_bytes:
            mistakes, retained, old_correct = assess(candidate)
        else:
            mistakes, retained, old_correct = parent_mistakes, False, False
        eligible = mistakes < parent_mistakes and retained and old_correct
        trials.append(TeachingTrial(
            proposal_id, candidate, delta, mistakes, retained, old_correct,
            size, (perf_counter() - started) * 1000, eligible,
        ))
    eligible = [trial for trial in trials if trial.eligible]
    selected = min(
        eligible,
        key=lambda trial: (
            len(trial.delta.created_route_ids) + len(trial.delta.created_adapter_ids),
            trial.mistakes, trial.serialized_bytes,
            trial.delta.changed_objects, trial.proposal_id,
        ),
        default=None,
    )
    return selected, tuple(trials)
