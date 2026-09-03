"""The initial hard-routed pathway fabric.

This file is intentionally the core of the prototype. There is no separate
opaque neural network hidden behind it: each pipe owns its type contract,
coupling, phase, stability, plasticity, and eligibility state. The small
readout path is also a path inside the same fabric.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from heapq import heappop, heappush
from math import cos, pi, sin
from typing import Iterable

from .types import (
    ArithmeticEvent,
    Information,
    Inference,
    Operation,
    Route,
    Signal,
    SignalType,
)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(slots=True)
class Pipe:
    """One typed, capacity-limited directed pipe in the learning fabric."""

    pipe_id: str
    source: str
    target: str
    input_type: SignalType
    output_type: SignalType
    scope: frozenset[Operation]
    capacity: int = 1
    coupling: float = 1.0
    phase: float = 0.0
    stability: float = 0.0
    plasticity: float = 1.0
    eligibility: float = 0.0
    verified_support: int = 0

    def admits(self, information: Information) -> bool:
        """Hard admission: no type or scope match means exactly zero flow."""

        return (
            information.kind is self.input_type
            and information.operation in self.scope
            and self.capacity > 0
        )

    @property
    def deterministic_cost(self) -> float:
        """A fixed cost used by Dijkstra's shortest compatible-path policy."""

        coupling_cost = 1.0 / max(self.coupling, 0.05)
        stability_discount = 0.15 * (self.stability / (1.0 + self.stability))
        phase_cost = 0.03 * abs(self.phase) / pi
        return coupling_cost + phase_cost - stability_discount

    def complex_gain(self, event: ArithmeticEvent) -> complex:
        """Return the classical complex gain carried by this pipe.

        A conflicted test event flips only the relation side at its final
        junction pipe. This creates a visible destructive-interference case
        without corrupting the arithmetic target or any stored path.
        """

        phase = self.phase
        if event.conflicted and self.pipe_id == "relation-to-join":
            phase += pi
        return self.coupling * complex(cos(phase), sin(phase))

    def record_activity(self, amplitude: complex, decay: float = 0.88) -> None:
        """Keep only a fading local credit trace, not the raw event."""

        activity = abs(amplitude) ** 2
        self.eligibility = decay * self.eligibility + activity

    def confirm_success(self) -> None:
        """Give tested successful pipes evidence-weighted stability."""

        self.verified_support += 1
        self.stability += 0.12
        self.plasticity = max(0.08, self.plasticity * 0.985)


@dataclass(slots=True)
class ReadoutPath:
    """A tiny learned arithmetic transformation owned by the pathway fabric."""

    pipe_id: str = "arithmetic-readout"
    weights: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    stability: float = 0.0
    plasticity: float = 1.0
    eligibility: float = 0.0
    verified_support: int = 0

    @staticmethod
    def features(event: ArithmeticEvent) -> tuple[float, float, float]:
        """Quantity-plus-relation features after both typed facets meet."""

        return (float(event.left), float(event.operation.sign * event.right), 1.0)

    def raw_value(
        self,
        event: ArithmeticEvent,
        weights: tuple[float, float, float] | None = None,
    ) -> float:
        selected = tuple(self.weights) if weights is None else weights
        return sum(weight * feature for weight, feature in zip(selected, self.features(event)))

    def candidate_weights(
        self,
        event: ArithmeticEvent,
        target: int,
        trace_strength: float,
        learning_rate: float,
    ) -> tuple[float, float, float]:
        """Propose a normalized local correction for an isolated candidate.

        The parent is not modified here. Promotion is decided by the separate
        evaluator in learning.py.
        """

        features = self.features(event)
        raw_value = self.raw_value(event)
        error = target - raw_value
        norm = 1.0 + sum(feature * feature for feature in features)
        local_rate = min(0.45, learning_rate * (1.0 + 0.05 * trace_strength))
        return tuple(
            weight + local_rate * error * feature / norm
            for weight, feature in zip(self.weights, features)
        )

    def promote(self, candidate: tuple[float, float, float]) -> None:
        """Replace only the readout path after independent checks pass."""

        self.weights[:] = candidate
        self.verified_support += 1
        self.stability += 0.16
        self.plasticity = max(0.08, self.plasticity * 0.99)


class PathwayFabric:
    """A sparse, type-safe graph that is the prototype's complete learner."""

    def __init__(self) -> None:
        all_operations = frozenset(Operation)
        self._pipes: dict[str, Pipe] = {
            "quantity-ingress": Pipe(
                pipe_id="quantity-ingress",
                source="ingress",
                target="quantity-mid",
                input_type=SignalType.QUANTITY,
                output_type=SignalType.QUANTITY,
                scope=all_operations,
                coupling=1.00,
            ),
            "quantity-to-join": Pipe(
                pipe_id="quantity-to-join",
                source="quantity-mid",
                target="typed-join",
                input_type=SignalType.QUANTITY,
                output_type=SignalType.QUANTITY,
                scope=all_operations,
                coupling=0.96,
            ),
            "relation-ingress": Pipe(
                pipe_id="relation-ingress",
                source="ingress",
                target="relation-mid",
                input_type=SignalType.RELATION,
                output_type=SignalType.RELATION,
                scope=all_operations,
                coupling=1.00,
            ),
            "relation-to-join": Pipe(
                pipe_id="relation-to-join",
                source="relation-mid",
                target="typed-join",
                input_type=SignalType.RELATION,
                output_type=SignalType.RELATION,
                scope=all_operations,
                coupling=0.96,
            ),
        }
        self.readout = ReadoutPath()
        self._outgoing: dict[str, tuple[Pipe, ...]] = {}
        for pipe in self._pipes.values():
            self._outgoing.setdefault(pipe.source, tuple())
            self._outgoing[pipe.source] = tuple(
                sorted(
                    (*self._outgoing[pipe.source], pipe),
                    key=lambda item: item.pipe_id,
                )
            )

    @property
    def pipes(self) -> dict[str, Pipe]:
        """Expose pipes for immutable inspection and controlled tests."""

        return self._pipes

    @staticmethod
    def facets(event: ArithmeticEvent) -> tuple[Information, Information]:
        """Split one event into two lawful, correlated typed facets."""

        quantity = Information(
            event_id=event.event_id,
            correlation_id=event.correlation_id,
            kind=SignalType.QUANTITY,
            payload=(float(event.left), float(event.right)),
            operation=event.operation,
        )
        relation = Information(
            event_id=event.event_id,
            correlation_id=event.correlation_id,
            kind=SignalType.RELATION,
            payload=(float(event.operation.sign),),
            operation=event.operation,
        )
        return quantity, relation

    def shortest_compatible_route(
        self,
        information: Information,
        start: str = "ingress",
        goal: str = "typed-join",
    ) -> Route | None:
        """Use deterministic Dijkstra routing over hard-compatible pipes.

        This is a modest, inspectable use of shortest-path mathematics. It does
        not claim that a single scalar can solve general cognition.
        """

        queue: list[tuple[float, str, tuple[str, ...]]] = [(0.0, start, ())]
        best: dict[str, float] = {start: 0.0}
        while queue:
            cost, node, route_ids = heappop(queue)
            if cost != best.get(node):
                continue
            if node == goal:
                return Route(route_ids, cost)
            for pipe in self._outgoing.get(node, ()):
                if not pipe.admits(information):
                    continue
                new_cost = cost + pipe.deterministic_cost
                previous = best.get(pipe.target)
                if previous is None or new_cost < previous:
                    best[pipe.target] = new_cost
                    heappush(
                        queue,
                        (new_cost, pipe.target, (*route_ids, pipe.pipe_id)),
                    )
        return None

    def _propagate(
        self,
        event: ArithmeticEvent,
        information: Information,
        route: Route,
    ) -> Signal:
        amplitude = complex(1.0, 0.0)
        for pipe_id in route.pipe_ids:
            amplitude *= self._pipes[pipe_id].complex_gain(event)
        return Signal(
            information=information,
            amplitude=amplitude,
            pipe_ids=route.pipe_ids,
            route_cost=route.total_cost,
        )

    @staticmethod
    def _typed_join(
        quantity_signal: Signal,
        relation_signal: Signal,
    ) -> float:
        """Return interference only when correlated facets are lawful to join."""

        quantity_info = quantity_signal.information
        relation_info = relation_signal.information
        if (
            quantity_info.event_id != relation_info.event_id
            or quantity_info.correlation_id != relation_info.correlation_id
        ):
            raise ValueError("Refusing to join signals from different events.")
        combined = quantity_signal.amplitude + relation_signal.amplitude
        return (
            abs(combined) ** 2
            - abs(quantity_signal.amplitude) ** 2
            - abs(relation_signal.amplitude) ** 2
        )

    def infer(
        self,
        event: ArithmeticEvent,
        *,
        max_active_routes: int = 2,
        readout_weights: tuple[float, float, float] | None = None,
    ) -> Inference:
        """Run one bounded, serial-first pathway settling attempt."""

        if max_active_routes < 2:
            return Inference(
                event=event,
                answer=None,
                raw_value=None,
                confidence=0.0,
                uncertainty=1.0,
                interference=0.0,
                quantity_signal=None,
                relation_signal=None,
                abstain_reason="The two required typed facets exceed the route budget.",
            )

        quantity_information, relation_information = self.facets(event)
        quantity_route = self.shortest_compatible_route(quantity_information)
        relation_route = self.shortest_compatible_route(relation_information)
        if quantity_route is None or relation_route is None:
            return Inference(
                event=event,
                answer=None,
                raw_value=None,
                confidence=0.0,
                uncertainty=1.0,
                interference=0.0,
                quantity_signal=None,
                relation_signal=None,
                abstain_reason="No complete hard-compatible route exists.",
            )

        quantity_signal = self._propagate(event, quantity_information, quantity_route)
        relation_signal = self._propagate(event, relation_information, relation_route)
        interference = self._typed_join(quantity_signal, relation_signal)
        coherence = _clamp((interference + 2.0) / 4.0, 0.0, 1.0)
        support = self.readout.verified_support
        confidence = coherence * (0.20 + 0.80 * support / (support + 3.0))
        uncertainty = 1.0 - confidence

        if coherence < 0.10:
            return Inference(
                event=event,
                answer=None,
                raw_value=None,
                confidence=confidence,
                uncertainty=uncertainty,
                interference=interference,
                quantity_signal=quantity_signal,
                relation_signal=relation_signal,
                abstain_reason="Destructive typed-join interference; awaiting evidence.",
            )

        raw_value = self.readout.raw_value(event, readout_weights)
        return Inference(
            event=event,
            answer=round(raw_value),
            raw_value=raw_value,
            confidence=confidence,
            uncertainty=uncertainty,
            interference=interference,
            quantity_signal=quantity_signal,
            relation_signal=relation_signal,
        )

    def record_eligibility(self, inference: Inference) -> float:
        """Record fading local activity from this event, then discard the event."""

        trace_total = 0.0
        for signal in (inference.quantity_signal, inference.relation_signal):
            if signal is None:
                continue
            for pipe_id in signal.pipe_ids:
                pipe = self._pipes[pipe_id]
                pipe.record_activity(signal.amplitude)
                trace_total += pipe.eligibility
        self.readout.eligibility = 0.88 * self.readout.eligibility + trace_total
        return self.readout.eligibility

    def confirm_positive(self, inference: Inference) -> None:
        """Strengthen only paths that produced a verified correct result."""

        for pipe_id in inference.active_pipe_ids:
            self._pipes[pipe_id].confirm_success()
        self.readout.verified_support += 1
        self.readout.stability += 0.12
        self.readout.plasticity = max(0.08, self.readout.plasticity * 0.985)

    def resource_ledger(self, inference: Inference | None = None) -> dict[str, int]:
        """Return an explicit estimate, not a claim of full process accounting."""

        persistent_scalars = len(self._pipes) * 7 + len(self.readout.weights) + 4
        active_pipe_count = len(inference.active_pipe_ids) if inference else 0
        transient_complex_values = 2 if inference and inference.answer is not None else 0
        return {
            "persistent_scalars": persistent_scalars,
            "estimated_persistent_bytes": persistent_scalars * 8,
            "active_pipes": active_pipe_count,
            "estimated_transient_bytes": transient_complex_values * 16
            + active_pipe_count * 24,
        }

    def inspect_paths(self) -> Iterable[Pipe]:
        """Yield pipes in stable order for a CLI or evaluator."""

        yield from (self._pipes[key] for key in sorted(self._pipes))
