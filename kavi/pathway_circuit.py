"""Kavi's path-centric adaptive circuit core.

The learned objects in this module are complete routes and the small jump
adapters that connect them.  Individual elements are deliberately simple:
they detect, gate, resist, accumulate, join, loop, or transform a signal.  A
single element never owns a concept and is never described as doing the
thinking.  Inference is the bounded search and composition of compatible
routes.

The complex amplitudes below are a classical, quantum-inspired routing
calculation.  They do not claim quantum hardware, quantum speed-up, or a model
of physical consciousness.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from math import cos, pi, sin, sqrt
from typing import Iterable, Mapping, Sequence

from .types import ArithmeticEvent, Operation


PathValue = int | str | bool


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _route_slug(value: str) -> str:
    return "".join(character if character.isalnum() else "-" for character in value).strip("-")


class ElementKind(str, Enum):
    """Local circuit roles; none is an independent reasoning unit."""

    DETECTOR = "detector"
    RESISTOR = "resistor"
    SWITCH = "switch"
    CAPACITOR = "capacitor"
    JUNCTION = "junction"
    LOOP = "loop"
    JUMP = "jump"
    TRANSFORMER = "transformer"


@dataclass(frozen=True, slots=True)
class CircuitElement:
    """One bounded local operation used inside one or more pathways."""

    element_id: str
    kind: ElementKind
    role: str


@dataclass(frozen=True, slots=True)
class CircuitSample:
    """A supervised categorical event; raw prompts are never put in model state."""

    event_id: str
    task_id: str
    target: str
    feature_names: tuple[str, ...]
    features: tuple[float, ...]
    source_activations: tuple[tuple[str, float], ...]
    display_text: str = ""

    def __post_init__(self) -> None:
        if not self.event_id or not self.task_id or not self.target:
            raise ValueError("Circuit samples need event, task, and target identifiers.")
        if not self.features or len(self.features) != len(self.feature_names):
            raise ValueError("Circuit sample feature names and values must align.")
        if len(self.feature_names) != len(set(self.feature_names)):
            raise ValueError("Circuit feature names must be unique.")
        if any(not 0.0 <= value <= 1.0 for value in self.features):
            raise ValueError("Circuit features must be normalized to [0, 1].")
        source_ids = [source_id for source_id, _ in self.source_activations]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("A source pathway may appear only once per sample.")
        if any(not 0.0 <= value <= 1.0 for _, value in self.source_activations):
            raise ValueError("Source activations must be normalized to [0, 1].")


def _value_matches_type(type_id: str, value: PathValue) -> bool:
    if type_id == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if type_id == "boolean":
        return isinstance(value, bool)
    if type_id == "scalar":
        return (
            isinstance(value, str)
            and len(value) == 1
            and not 0xD800 <= ord(value) <= 0xDFFF
        )
    if type_id == "concept-label":
        return isinstance(value, str) and bool(value)
    return False


@dataclass(frozen=True, slots=True)
class CompositionLiteral:
    """One temporary typed value entering a compositional pathway."""

    node_id: str
    type_id: str
    value: PathValue

    def __post_init__(self) -> None:
        if not self.node_id or not _value_matches_type(self.type_id, self.value):
            raise ValueError("A composition literal needs a valid identifier, type, and value.")


@dataclass(frozen=True, slots=True)
class CompositionCall:
    """A temporary tree node whose meaning is supplied by a learned route."""

    node_id: str
    operator_id: str
    arguments: tuple[CompositionLiteral | "CompositionCall", ...]

    def __post_init__(self) -> None:
        if not self.node_id or not self.operator_id or not self.arguments:
            raise ValueError("A composition call needs an identifier, operator, and arguments.")
        if not isinstance(self.arguments, tuple) or any(
            not isinstance(child, (CompositionLiteral, CompositionCall))
            for child in self.arguments
        ):
            raise ValueError("Composition arguments must be an immutable tuple of typed nodes.")


@dataclass(frozen=True, slots=True)
class CompositionExample:
    """One evaluator case; its tree and display text never enter model state."""

    event_id: str
    expression: CompositionCall
    expected_type: str
    expected_value: PathValue
    display_text: str

    def __post_init__(self) -> None:
        if not self.event_id or not _value_matches_type(self.expected_type, self.expected_value):
            raise ValueError("A composition example needs a typed expected result.")
        if not isinstance(self.expression, CompositionCall):
            raise ValueError("A composition example needs a call expression.")


@dataclass(frozen=True, slots=True)
class CompositionRule:
    """A verified operator contract used to form one reusable pathway."""

    rule_id: str
    operator_id: str
    input_types: tuple[str, ...]
    output_type: str
    target_path_id: str

    def __post_init__(self) -> None:
        if not all((self.rule_id, self.operator_id, self.output_type, self.target_path_id)):
            raise ValueError("A composition rule needs complete identifiers.")
        if not self.input_types:
            raise ValueError("A composition rule needs at least one input type.")

@dataclass(frozen=True, slots=True)
class PathRoute:
    """A learned categorical route: its topology and shape are the memory."""

    route_id: str
    task_id: str
    output_label: str
    feature_names: tuple[str, ...]
    center: tuple[float, ...]
    source_path_ids: tuple[str, ...]
    support: int = 0
    resistance: float = 1.0
    coupling: float = 0.5
    phase: float = 0.0
    revision: int = 0

    def updated(self, sample: CircuitSample) -> "PathRoute":
        if sample.task_id != self.task_id or sample.target != self.output_label:
            raise ValueError("A route can absorb evidence only for its own task and label.")
        if sample.feature_names != self.feature_names:
            raise ValueError("A route cannot silently change its feature contract.")
        next_support = self.support + 1
        center = tuple(
            old + (new - old) / next_support
            for old, new in zip(self.center, sample.features)
        )
        active_sources = tuple(
            source_id for source_id, value in sample.source_activations if value > 0.0
        )
        sources = tuple(sorted(set((*self.source_path_ids, *active_sources))))
        return replace(
            self,
            center=center,
            source_path_ids=sources,
            support=next_support,
            resistance=max(0.08, self.resistance * 0.90),
            coupling=min(1.50, self.coupling + 0.06),
            revision=self.revision + 1,
        )


@dataclass(frozen=True, slots=True)
class TransformRoute:
    """A reusable arithmetic transformation pathway."""

    route_id: str
    operation: str
    weights: tuple[float, float, float]
    source_path_ids: tuple[str, ...]
    support: int = 0
    resistance: float = 1.0
    coupling: float = 0.5
    phase: float = 0.0
    revision: int = 0

    def updated(
        self,
        target_weights: tuple[float, float, float],
        source_path_ids: Sequence[str],
    ) -> "TransformRoute":
        next_support = self.support + 1
        weights = tuple(
            old + (target - old) / next_support
            for old, target in zip(self.weights, target_weights)
        )
        return replace(
            self,
            weights=weights,
            source_path_ids=tuple(sorted(set((*self.source_path_ids, *source_path_ids)))),
            support=next_support,
            resistance=max(0.08, self.resistance * 0.90),
            coupling=min(1.50, self.coupling + 0.06),
            revision=self.revision + 1,
        )


@dataclass(frozen=True, slots=True)
class CompositionRoute:
    """A learned typed connection from an operator to an existing pathway."""

    route_id: str
    operator_id: str
    input_types: tuple[str, ...]
    output_type: str
    target_path_id: str
    source_path_ids: tuple[str, ...]
    support: int = 0
    resistance: float = 1.0
    coupling: float = 0.5
    phase: float = 0.0
    revision: int = 0

    def updated(self, rule: CompositionRule, source_path_ids: Sequence[str]) -> "CompositionRoute":
        if (
            rule.operator_id != self.operator_id
            or rule.input_types != self.input_types
            or rule.output_type != self.output_type
            or rule.target_path_id != self.target_path_id
        ):
            raise ValueError("A composition route cannot silently change its typed contract.")
        return replace(
            self,
            source_path_ids=tuple(sorted(set((*self.source_path_ids, *source_path_ids)))),
            support=self.support + 1,
            resistance=max(0.08, self.resistance * 0.90),
            coupling=min(1.50, self.coupling + 0.06),
            revision=self.revision + 1,
        )

@dataclass(frozen=True, slots=True)
class JumpAdapter:
    """A small local connection that changes flow without replacing a route."""

    adapter_id: str
    source_path_id: str
    target_route_id: str
    conductance: float = 0.0
    phase: float = 0.0
    support: int = 0

    def updated(self, activation: float) -> "JumpAdapter":
        next_support = self.support + 1
        conductance = self.conductance + (activation - self.conductance) / next_support
        return replace(
            self,
            conductance=_clamp(conductance, 0.0, 1.0),
            support=next_support,
        )


@dataclass(frozen=True, slots=True)
class CircuitState:
    """All persistent learned state; it contains no lesson strings or documents."""

    routes: tuple[PathRoute, ...] = ()
    transforms: tuple[TransformRoute, ...] = ()
    composition_routes: tuple[CompositionRoute, ...] = ()
    adapters: tuple[JumpAdapter, ...] = ()
    verified_foundations: tuple[str, ...] = ()
    promotions: int = 0

    def route_map(self) -> dict[str, PathRoute]:
        return {route.route_id: route for route in self.routes}

    def transform_map(self) -> dict[str, TransformRoute]:
        return {route.route_id: route for route in self.transforms}

    def composition_map(self) -> dict[str, CompositionRoute]:
        return {route.route_id: route for route in self.composition_routes}

    def adapter_map(self) -> dict[str, JumpAdapter]:
        return {adapter.adapter_id: adapter for adapter in self.adapters}

    @property
    def total_support(self) -> int:
        return (
            sum(route.support for route in self.routes)
            + sum(route.support for route in self.transforms)
            + sum(route.support for route in self.composition_routes)
        )

    def as_mapping(self) -> dict[str, object]:
        return {
            "schema_version": 2,
            "promotions": self.promotions,
            "verified_foundations": list(self.verified_foundations),
            "routes": [
                {
                    "route_id": route.route_id,
                    "task_id": route.task_id,
                    "output_label": route.output_label,
                    "feature_names": list(route.feature_names),
                    "center": list(route.center),
                    "source_path_ids": list(route.source_path_ids),
                    "support": route.support,
                    "resistance": route.resistance,
                    "coupling": route.coupling,
                    "phase": route.phase,
                    "revision": route.revision,
                }
                for route in self.routes
            ],
            "transforms": [
                {
                    "route_id": route.route_id,
                    "operation": route.operation,
                    "weights": list(route.weights),
                    "source_path_ids": list(route.source_path_ids),
                    "support": route.support,
                    "resistance": route.resistance,
                    "coupling": route.coupling,
                    "phase": route.phase,
                    "revision": route.revision,
                }
                for route in self.transforms
            ],
            "composition_routes": [
                {
                    "route_id": route.route_id,
                    "operator_id": route.operator_id,
                    "input_types": list(route.input_types),
                    "output_type": route.output_type,
                    "target_path_id": route.target_path_id,
                    "source_path_ids": list(route.source_path_ids),
                    "support": route.support,
                    "resistance": route.resistance,
                    "coupling": route.coupling,
                    "phase": route.phase,
                    "revision": route.revision,
                }
                for route in self.composition_routes
            ],
            "adapters": [
                {
                    "adapter_id": adapter.adapter_id,
                    "source_path_id": adapter.source_path_id,
                    "target_route_id": adapter.target_route_id,
                    "conductance": adapter.conductance,
                    "phase": adapter.phase,
                    "support": adapter.support,
                }
                for adapter in self.adapters
            ],
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> "CircuitState":
        if int(value.get("schema_version", 0)) not in (1, 2):
            raise ValueError("Unsupported path-centric state schema.")
        routes = tuple(
            PathRoute(
                route_id=str(item["route_id"]),
                task_id=str(item["task_id"]),
                output_label=str(item["output_label"]),
                feature_names=tuple(str(name) for name in item["feature_names"]),
                center=tuple(float(number) for number in item["center"]),
                source_path_ids=tuple(str(path_id) for path_id in item["source_path_ids"]),
                support=int(item["support"]),
                resistance=float(item["resistance"]),
                coupling=float(item["coupling"]),
                phase=float(item["phase"]),
                revision=int(item["revision"]),
            )
            for item in value.get("routes", [])
        )
        transforms = tuple(
            TransformRoute(
                route_id=str(item["route_id"]),
                operation=str(item["operation"]),
                weights=tuple(float(number) for number in item["weights"]),
                source_path_ids=tuple(str(path_id) for path_id in item["source_path_ids"]),
                support=int(item["support"]),
                resistance=float(item["resistance"]),
                coupling=float(item["coupling"]),
                phase=float(item["phase"]),
                revision=int(item["revision"]),
            )
            for item in value.get("transforms", [])
        )
        composition_routes = tuple(
            CompositionRoute(
                route_id=str(item["route_id"]),
                operator_id=str(item["operator_id"]),
                input_types=tuple(str(type_id) for type_id in item["input_types"]),
                output_type=str(item["output_type"]),
                target_path_id=str(item["target_path_id"]),
                source_path_ids=tuple(str(path_id) for path_id in item["source_path_ids"]),
                support=int(item["support"]),
                resistance=float(item["resistance"]),
                coupling=float(item["coupling"]),
                phase=float(item["phase"]),
                revision=int(item["revision"]),
            )
            for item in value.get("composition_routes", [])
        )
        adapters = tuple(
            JumpAdapter(
                adapter_id=str(item["adapter_id"]),
                source_path_id=str(item["source_path_id"]),
                target_route_id=str(item["target_route_id"]),
                conductance=float(item["conductance"]),
                phase=float(item["phase"]),
                support=int(item["support"]),
            )
            for item in value.get("adapters", [])
        )
        return cls(
            routes=tuple(sorted(routes, key=lambda item: item.route_id)),
            transforms=tuple(sorted(transforms, key=lambda item: item.route_id)),
            composition_routes=tuple(
                sorted(composition_routes, key=lambda item: item.route_id)
            ),
            adapters=tuple(sorted(adapters, key=lambda item: item.adapter_id)),
            verified_foundations=tuple(
                sorted(str(path_id) for path_id in value.get("verified_foundations", []))
            ),
            promotions=int(value.get("promotions", 0)),
        )


@dataclass(frozen=True, slots=True)
class RouteCandidate:
    """One explicit route considered during categorical inference."""

    route_id: str
    output_label: str
    distance: float
    real_amplitude: float
    imaginary_amplitude: float
    intensity: float
    active_adapter_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CategoryInference:
    """Observable categorical routing result."""

    event_id: str
    task_id: str
    prediction: str | None
    confidence: float
    active_source_path_ids: tuple[str, ...]
    activation_waves: tuple[tuple[str, ...], ...]
    candidates: tuple[RouteCandidate, ...]
    selected_route_id: str | None
    active_adapter_ids: tuple[str, ...]
    abstain_reason: str | None = None


@dataclass(frozen=True, slots=True)
class ArithmeticInference:
    """Observable numeric answer produced by a selected transform route."""

    event: ArithmeticEvent
    answer: int | None
    raw_value: float | None
    confidence: float
    active_source_path_ids: tuple[str, ...]
    activation_waves: tuple[tuple[str, ...], ...]
    candidate_route_ids: tuple[str, ...]
    selected_route_id: str | None
    active_adapter_ids: tuple[str, ...]
    abstain_reason: str | None = None


@dataclass(frozen=True, slots=True)
class CompositionStep:
    """One observable call in a nested path execution."""

    node_id: str
    operator_id: str
    input_types: tuple[str, ...]
    output_type: str | None
    answer: PathValue | None
    selected_route_id: str | None
    target_path_id: str | None
    active_source_path_ids: tuple[str, ...]
    activation_waves: tuple[tuple[str, ...], ...]
    active_adapter_ids: tuple[str, ...]
    intensity: float
    abstain_reason: str | None = None


@dataclass(frozen=True, slots=True)
class CompositionInference:
    """Observable result of executing one finite typed path tree."""

    event_id: str
    answer: PathValue | None
    output_type: str | None
    confidence: float
    steps: tuple[CompositionStep, ...]
    selected_route_ids: tuple[str, ...]
    active_adapter_ids: tuple[str, ...]
    abstain_reason: str | None = None


@dataclass(frozen=True, slots=True)
class _NodeResult:
    value: PathValue | None
    type_id: str | None
    confidence: float
    steps: tuple[CompositionStep, ...]
    selected_route_ids: tuple[str, ...]
    active_adapter_ids: tuple[str, ...]
    abstain_reason: str | None = None

@dataclass(frozen=True, slots=True)
class ClassificationMetrics:
    cases: int
    answered: int
    correct: int

    @property
    def exact_accuracy(self) -> float:
        return self.correct / self.cases if self.cases else 0.0

    @property
    def coverage(self) -> float:
        return self.answered / self.cases if self.cases else 0.0

    @property
    def errors(self) -> int:
        return self.cases - self.correct


@dataclass(frozen=True, slots=True)
class StateDelta:
    """Exact structural difference between a frozen parent and a candidate."""

    created_route_ids: tuple[str, ...]
    modified_route_ids: tuple[str, ...]
    created_adapter_ids: tuple[str, ...]
    modified_adapter_ids: tuple[str, ...]

    @property
    def changed_objects(self) -> int:
        return sum(
            len(values)
            for values in (
                self.created_route_ids,
                self.modified_route_ids,
                self.created_adapter_ids,
                self.modified_adapter_ids,
            )
        )


@dataclass(frozen=True, slots=True)
class CandidateAssessment:
    candidate_state: CircuitState
    delta: StateDelta
    parent_current: ClassificationMetrics
    candidate_current: ClassificationMetrics
    parent_protected: ClassificationMetrics
    candidate_protected: ClassificationMetrics
    parent_held_out: ClassificationMetrics
    candidate_held_out: ClassificationMetrics
    accepted: bool


class PathwayCircuitCore:
    """One persistent sparse circuit shared across Kavi's bounded stages."""

    MINIMUM_CONFIDENCE = 0.02
    ELEMENTS = (
        CircuitElement("component/input-detector", ElementKind.DETECTOR, "turn input into bounded local signals"),
        CircuitElement("component/type-switch", ElementKind.SWITCH, "block signals that violate a route contract"),
        CircuitElement("component/route-resistor", ElementKind.RESISTOR, "penalize weak or unstable routes"),
        CircuitElement("component/context-capacitor", ElementKind.CAPACITOR, "hold one event's context until its paths join"),
        CircuitElement("component/path-junction", ElementKind.JUNCTION, "combine correlated path amplitudes"),
        CircuitElement("component/recheck-loop", ElementKind.LOOP, "return a failed candidate to the verifier"),
        CircuitElement("component/jump-adapter", ElementKind.JUMP, "bridge a reusable source path to a target route"),
        CircuitElement("component/output-transformer", ElementKind.TRANSFORMER, "turn a selected route into a typed output"),
    )

    def __init__(self, state: CircuitState | None = None) -> None:
        self.state = state or CircuitState()

    @staticmethod
    def _waves(source_ids: Sequence[str], max_parallel_paths: int) -> tuple[tuple[str, ...], ...]:
        if max_parallel_paths < 1:
            raise ValueError("The active path budget must be positive.")
        ordered = tuple(dict.fromkeys(source_ids))
        return tuple(
            ordered[index : index + max_parallel_paths]
            for index in range(0, len(ordered), max_parallel_paths)
        )

    @staticmethod
    def _distance(left: Sequence[float], right: Sequence[float]) -> float:
        if len(left) != len(right):
            raise ValueError("Cannot compare routes with different feature contracts.")
        return sqrt(sum((a - b) ** 2 for a, b in zip(left, right)) / len(left))

    @staticmethod
    def _adapter_id(source_path_id: str, target_route_id: str) -> str:
        return f"adapter/{_route_slug(source_path_id)}/{_route_slug(target_route_id)}"

    @staticmethod
    def _category_route_id(task_id: str, label: str) -> str:
        return f"path/{_route_slug(task_id)}/{_route_slug(label)}"

    @staticmethod
    def _transform_route_id(operation: Operation) -> str:
        return f"path/arithmetic/{operation.value}"

    @staticmethod
    def _composition_route_id(rule: CompositionRule) -> str:
        signature = "-".join((*rule.input_types, "to", rule.output_type))
        return f"path/composition/{_route_slug(rule.operator_id)}/{_route_slug(signature)}"

    def infer_category(
        self,
        sample: CircuitSample,
        *,
        state: CircuitState | None = None,
        max_parallel_paths: int = 4,
    ) -> CategoryInference:
        selected = self.state if state is None else state
        routes = tuple(route for route in selected.routes if route.task_id == sample.task_id)
        active_sources = tuple(
            source_id for source_id, activation in sample.source_activations if activation > 0.0
        )
        waves = self._waves(active_sources, max_parallel_paths)
        if len(routes) < 2:
            return CategoryInference(
                event_id=sample.event_id,
                task_id=sample.task_id,
                prediction=None,
                confidence=0.0,
                active_source_path_ids=active_sources,
                activation_waves=waves,
                candidates=(),
                selected_route_id=None,
                active_adapter_ids=(),
                abstain_reason="The task has fewer than two verified output pathways.",
            )

        activation_by_source = dict(sample.source_activations)
        adapters = tuple(selected.adapters)
        candidates: list[RouteCandidate] = []
        for route in routes:
            if route.feature_names != sample.feature_names:
                continue
            distance = self._distance(sample.features, route.center)
            # Resonance is relative to a learned route's own scale. Inverse
            # distance keeps small-but-real Unicode block separations visible
            # instead of flattening them under one global exponential scale.
            coherence = 1.0 / (1e-6 + distance)
            active_jumps: list[str] = []
            amplitude = complex(0.0, 0.0)
            for adapter in adapters:
                if adapter.target_route_id != route.route_id:
                    continue
                activation = activation_by_source.get(adapter.source_path_id, 0.0)
                if activation <= 0.0:
                    continue
                phase = route.phase + adapter.phase + pi * min(distance, 1.0) * 0.25
                amplitude += (
                    adapter.conductance
                    * activation
                    * complex(cos(phase), sin(phase))
                )
                active_jumps.append(adapter.adapter_id)
            if active_jumps:
                amplitude *= route.coupling * coherence / (
                    (1.0 + route.resistance) * sqrt(len(active_jumps))
                )
            intensity = abs(amplitude) ** 2
            candidates.append(
                RouteCandidate(
                    route_id=route.route_id,
                    output_label=route.output_label,
                    distance=distance,
                    real_amplitude=amplitude.real,
                    imaginary_amplitude=amplitude.imag,
                    intensity=intensity,
                    active_adapter_ids=tuple(active_jumps),
                )
            )

        candidates.sort(key=lambda item: (-item.intensity, item.route_id))
        if not candidates or candidates[0].intensity <= 0.0:
            return CategoryInference(
                event_id=sample.event_id,
                task_id=sample.task_id,
                prediction=None,
                confidence=0.0,
                active_source_path_ids=active_sources,
                activation_waves=waves,
                candidates=tuple(candidates),
                selected_route_id=None,
                active_adapter_ids=(),
                abstain_reason="No learned jump connects the active sources to an output route.",
            )
        top = candidates[0]
        second_intensity = candidates[1].intensity if len(candidates) > 1 else 0.0
        denominator = top.intensity + second_intensity
        confidence = (
            (top.intensity - second_intensity) / denominator if denominator else 0.0
        )
        if confidence < self.MINIMUM_CONFIDENCE:
            return CategoryInference(
                event_id=sample.event_id,
                task_id=sample.task_id,
                prediction=None,
                confidence=confidence,
                active_source_path_ids=active_sources,
                activation_waves=waves,
                candidates=tuple(candidates),
                selected_route_id=None,
                active_adapter_ids=(),
                abstain_reason="Competing route intensities are too similar.",
            )
        return CategoryInference(
            event_id=sample.event_id,
            task_id=sample.task_id,
            prediction=top.output_label,
            confidence=confidence,
            active_source_path_ids=active_sources,
            activation_waves=waves,
            candidates=tuple(candidates),
            selected_route_id=top.route_id,
            active_adapter_ids=top.active_adapter_ids,
        )

    def propose_category_update(
        self,
        samples: Iterable[CircuitSample],
    ) -> tuple[CircuitState, StateDelta]:
        routes = self.state.route_map()
        adapters = self.state.adapter_map()
        original_routes = dict(routes)
        original_adapters = dict(adapters)
        for sample in samples:
            route_id = self._category_route_id(sample.task_id, sample.target)
            route = routes.get(route_id)
            if route is None:
                route = PathRoute(
                    route_id=route_id,
                    task_id=sample.task_id,
                    output_label=sample.target,
                    feature_names=sample.feature_names,
                    center=(0.0,) * len(sample.features),
                    source_path_ids=(),
                )
            route = route.updated(sample)
            routes[route_id] = route
            for source_path_id, activation in sample.source_activations:
                if activation <= 0.0:
                    continue
                adapter_id = self._adapter_id(source_path_id, route_id)
                adapter = adapters.get(
                    adapter_id,
                    JumpAdapter(adapter_id, source_path_id, route_id),
                )
                adapters[adapter_id] = adapter.updated(activation)

        candidate = replace(
            self.state,
            routes=tuple(sorted(routes.values(), key=lambda item: item.route_id)),
            adapters=tuple(sorted(adapters.values(), key=lambda item: item.adapter_id)),
        )
        delta = self._delta(original_routes, original_adapters, routes, adapters)
        return candidate, delta

    def infer_arithmetic(
        self,
        event: ArithmeticEvent,
        *,
        state: CircuitState | None = None,
        max_parallel_paths: int = 4,
    ) -> ArithmeticInference:
        selected = self.state if state is None else state
        digit_path = (
            "path/glyph-kind/digit"
            if "path/glyph-kind/digit" in selected.route_map()
            else "component/digit-detector"
        )
        operator_source = f"component/operator-{event.operation.value}"
        source_ids = ("component/context-loop", digit_path, operator_source)
        waves = self._waves(source_ids, max_parallel_paths)
        candidates = tuple(
            route
            for route in selected.transforms
            if operator_source in route.source_path_ids
        )
        if not candidates:
            return ArithmeticInference(
                event=event,
                answer=None,
                raw_value=None,
                confidence=0.0,
                active_source_path_ids=source_ids,
                activation_waves=waves,
                candidate_route_ids=(),
                selected_route_id=None,
                active_adapter_ids=(),
                abstain_reason="No verified transform pathway accepts this operation signal.",
            )
        route = sorted(candidates, key=lambda item: (-item.support, item.route_id))[0]
        features = (float(event.left), float(event.right), 1.0)
        raw_value = sum(weight * feature for weight, feature in zip(route.weights, features))
        adapter_ids = tuple(
            adapter.adapter_id
            for adapter in selected.adapters
            if adapter.target_route_id == route.route_id
            and adapter.source_path_id in source_ids
        )
        confidence = route.coupling / (route.coupling + route.resistance)
        return ArithmeticInference(
            event=event,
            answer=round(raw_value),
            raw_value=raw_value,
            confidence=confidence,
            active_source_path_ids=source_ids,
            activation_waves=waves,
            candidate_route_ids=tuple(item.route_id for item in candidates),
            selected_route_id=route.route_id,
            active_adapter_ids=adapter_ids,
        )

    def propose_arithmetic_update(
        self,
        event: ArithmeticEvent,
        target_weights: tuple[float, float, float],
    ) -> tuple[CircuitState, StateDelta]:
        routes = self.state.transform_map()
        adapters = self.state.adapter_map()
        original_routes = dict(routes)
        original_adapters = dict(adapters)
        route_id = self._transform_route_id(event.operation)
        digit_path = (
            "path/glyph-kind/digit"
            if "path/glyph-kind/digit" in self.state.route_map()
            else "component/digit-detector"
        )
        sources = (
            "component/context-loop",
            digit_path,
            f"component/operator-{event.operation.value}",
        )
        route = routes.get(
            route_id,
            TransformRoute(
                route_id=route_id,
                operation=event.operation.value,
                weights=(0.0, 0.0, 0.0),
                source_path_ids=(),
            ),
        ).updated(target_weights, sources)
        routes[route_id] = route
        for source_id in sources:
            adapter_id = self._adapter_id(source_id, route_id)
            adapter = adapters.get(adapter_id, JumpAdapter(adapter_id, source_id, route_id))
            adapters[adapter_id] = adapter.updated(1.0)
        candidate = replace(
            self.state,
            transforms=tuple(sorted(routes.values(), key=lambda item: item.route_id)),
            adapters=tuple(sorted(adapters.values(), key=lambda item: item.adapter_id)),
        )
        delta = self._delta(original_routes, original_adapters, routes, adapters)
        return candidate, delta

    @staticmethod
    def _composition_sources(rule: CompositionRule) -> tuple[str, ...]:
        values = [f"component/operator-{_route_slug(rule.operator_id)}"]
        values.extend(f"component/type-{_route_slug(type_id)}" for type_id in rule.input_types)
        values.append(rule.target_path_id)
        return tuple(dict.fromkeys(values))

    @staticmethod
    def _composition_shape(
        node: CompositionLiteral | CompositionCall,
        max_depth: int,
        max_nodes: int,
    ) -> tuple[int, int]:
        """Inspect only up to the budget, without recursive input traversal."""

        pending = [(iter((node,)), 1)]
        depth = count = 0
        while pending:
            siblings, level = pending[-1]
            child = next(siblings, None)
            if child is None:
                pending.pop()
                continue
            count += 1
            depth = max(depth, level)
            if depth > max_depth or count > max_nodes:
                return depth, count
            if isinstance(child, CompositionCall):
                pending.append((iter(child.arguments), level + 1))
        return depth, count

    @staticmethod
    def _composition_target_contract(
        target_path_id: str,
    ) -> tuple[tuple[str, ...], str] | None:
        return {
            "path/arithmetic/add": (("integer", "integer"), "integer"),
            "path/arithmetic/subtract": (("integer", "integer"), "integer"),
            "task/glyph-kind": (("scalar",), "concept-label"),
            "task/unicode-script": (("scalar",), "concept-label"),
            "component/equality-transformer": (
                ("concept-label", "concept-label"),
                "boolean",
            ),
            "component/select-integer-transformer": (
                ("boolean", "integer", "integer"),
                "integer",
            ),
        }.get(target_path_id)

    @staticmethod
    def _composition_target_available(state: CircuitState, target_path_id: str) -> bool:
        if target_path_id.startswith("path/arithmetic/"):
            return target_path_id in state.transform_map()
        if target_path_id == "task/glyph-kind":
            return len([route for route in state.routes if route.task_id == "glyph-kind"]) >= 2
        if target_path_id == "task/unicode-script":
            return len([route for route in state.routes if route.task_id == "unicode-script"]) >= 2
        return target_path_id in {
            "component/equality-transformer",
            "component/select-integer-transformer",
        }

    def _execute_composition_target(
        self,
        node_id: str,
        route: CompositionRoute,
        arguments: tuple[tuple[str, PathValue], ...],
        *,
        state: CircuitState,
        max_parallel_paths: int,
    ) -> tuple[
        PathValue | None,
        str | None,
        float,
        tuple[str, ...],
        tuple[str, ...],
        str | None,
    ]:
        target = route.target_path_id
        if self._composition_target_contract(target) != (
            route.input_types, route.output_type
        ):
            return None, None, 0.0, (), (), "Stored target contract is invalid."
        if target in {"path/arithmetic/add", "path/arithmetic/subtract"}:
            operation = Operation.ADD if target.endswith("/add") else Operation.SUBTRACT
            left = int(arguments[0][1])
            right = int(arguments[1][1])
            if abs(left) > 2**52 or abs(right) > 2**52:
                return None, None, 0.0, (), (), (
                    "Arithmetic operands exceed the exact float-transform input range."
                )
            inference = self.infer_arithmetic(
                ArithmeticEvent(node_id, left, right, operation, node_id),
                state=state,
                max_parallel_paths=max_parallel_paths,
            )
            if inference.answer is None or inference.selected_route_id != target:
                return None, None, 0.0, (), inference.active_adapter_ids, (
                    inference.abstain_reason or "The target arithmetic path did not execute."
                )
            return (
                inference.answer,
                "integer",
                inference.confidence,
                (inference.selected_route_id,),
                inference.active_adapter_ids,
                None,
            )
        if target == "task/glyph-kind":
            glyph = str(arguments[0][1])
            if ord(glyph) > 127:
                return None, None, 0.0, (), (), "The glyph-kind path accepts ASCII scalars only."
            inference = self.infer_category(
                CircuitSample(
                    event_id=f"{node_id}-glyph-query",
                    task_id="glyph-kind",
                    target="query-only",
                    feature_names=("bias", "ascii-coordinate"),
                    features=(1.0, ord(glyph) / 127.0),
                    source_activations=(
                        ("component/context-loop", 1.0),
                        ("component/ascii-scalar-detector", 1.0),
                    ),
                ),
                state=state,
                max_parallel_paths=max_parallel_paths,
            )
            if inference.prediction is None:
                return None, None, 0.0, (), inference.active_adapter_ids, inference.abstain_reason
            return (
                inference.prediction,
                "concept-label",
                inference.confidence,
                (inference.selected_route_id,) if inference.selected_route_id else (),
                inference.active_adapter_ids,
                None,
            )
        if target == "task/unicode-script":
            glyph = str(arguments[0][1])
            inference = self.infer_category(
                CircuitSample(
                    event_id=f"{node_id}-script-query",
                    task_id="unicode-script",
                    target="query-only",
                    feature_names=("bias", "unicode-coordinate"),
                    features=(1.0, ord(glyph) / 0x10FFFF),
                    source_activations=(
                        ("component/context-loop", 1.0),
                        ("path/unicode-scalar", 1.0),
                    ),
                ),
                state=state,
                max_parallel_paths=max_parallel_paths,
            )
            if inference.prediction is None:
                return None, None, 0.0, (), inference.active_adapter_ids, inference.abstain_reason
            return (
                inference.prediction,
                "concept-label",
                inference.confidence,
                (inference.selected_route_id,) if inference.selected_route_id else (),
                inference.active_adapter_ids,
                None,
            )
        if target == "component/equality-transformer":
            return (
                arguments[0][1] == arguments[1][1],
                "boolean",
                1.0,
                (target,),
                (),
                None,
            )
        if target == "component/select-integer-transformer":
            selected = arguments[1][1] if bool(arguments[0][1]) else arguments[2][1]
            return int(selected), "integer", 1.0, (target,), (), None
        return None, None, 0.0, (), (), f"Unsupported target path: {target}"

    def _infer_composition_node(
        self,
        node: CompositionLiteral | CompositionCall,
        *,
        state: CircuitState,
        max_parallel_paths: int,
    ) -> _NodeResult:
        if isinstance(node, CompositionLiteral):
            return _NodeResult(node.value, node.type_id, 1.0, (), (), ())

        child_results = tuple(
            self._infer_composition_node(
                child,
                state=state,
                max_parallel_paths=max_parallel_paths,
            )
            for child in node.arguments
        )
        child_steps = tuple(step for child in child_results for step in child.steps)
        child_routes = tuple(
            dict.fromkeys(route_id for child in child_results for route_id in child.selected_route_ids)
        )
        child_adapters = tuple(
            dict.fromkeys(adapter_id for child in child_results for adapter_id in child.active_adapter_ids)
        )
        failed_child = next((child for child in child_results if child.value is None), None)
        if failed_child is not None:
            reason = f"A required child path abstained: {failed_child.abstain_reason}"
            step = CompositionStep(
                node.node_id,
                node.operator_id,
                tuple(child.type_id or "unknown" for child in child_results),
                None,
                None,
                None,
                None,
                child_routes,
                self._waves(child_routes, max_parallel_paths) if child_routes else (),
                child_adapters,
                0.0,
                reason,
            )
            return _NodeResult(None, None, 0.0, (*child_steps, step), child_routes, child_adapters, reason)

        input_types = tuple(str(child.type_id) for child in child_results)
        routes = tuple(
            route
            for route in state.composition_routes
            if route.operator_id == node.operator_id and route.input_types == input_types
        )
        if not routes:
            reason = "No learned composition route accepts this operator and type signature."
            active_sources = tuple(
                dict.fromkeys(
                    (
                        f"component/operator-{_route_slug(node.operator_id)}",
                        *(f"component/type-{_route_slug(type_id)}" for type_id in input_types),
                        *child_routes,
                    )
                )
            )
            step = CompositionStep(
                node.node_id,
                node.operator_id,
                input_types,
                None,
                None,
                None,
                None,
                active_sources,
                self._waves(active_sources, max_parallel_paths),
                child_adapters,
                0.0,
                reason,
            )
            return _NodeResult(None, None, 0.0, (*child_steps, step), child_routes, child_adapters, reason)

        route = sorted(routes, key=lambda item: (-item.support, item.route_id))[0]
        active_sources = tuple(
            dict.fromkeys(
                (
                    f"component/operator-{_route_slug(node.operator_id)}",
                    *(f"component/type-{_route_slug(type_id)}" for type_id in input_types),
                    route.target_path_id,
                    *child_routes,
                )
            )
        )
        adapter_ids: list[str] = []
        amplitude = complex(0.0, 0.0)
        for adapter in state.adapters:
            if adapter.target_route_id != route.route_id or adapter.source_path_id not in active_sources:
                continue
            phase = route.phase + adapter.phase
            amplitude += adapter.conductance * complex(cos(phase), sin(phase))
            adapter_ids.append(adapter.adapter_id)
        if adapter_ids:
            amplitude *= route.coupling / (
                (1.0 + route.resistance) * sqrt(len(adapter_ids))
            )
        intensity = abs(amplitude) ** 2
        if not adapter_ids or intensity <= 0.0:
            reason = "The typed route exists, but no learned jump conducts this call."
            step = CompositionStep(
                node.node_id,
                node.operator_id,
                input_types,
                None,
                None,
                route.route_id,
                route.target_path_id,
                active_sources,
                self._waves(active_sources, max_parallel_paths),
                tuple(adapter_ids),
                intensity,
                reason,
            )
            selected = tuple(dict.fromkeys((*child_routes, route.route_id)))
            active = tuple(dict.fromkeys((*child_adapters, *adapter_ids)))
            return _NodeResult(None, None, 0.0, (*child_steps, step), selected, active, reason)

        arguments = tuple((str(child.type_id), child.value) for child in child_results)
        value, output_type, target_confidence, target_routes, target_adapters, reason = (
            self._execute_composition_target(
                node.node_id,
                route,
                arguments,
                state=state,
                max_parallel_paths=max_parallel_paths,
            )
        )
        route_confidence = route.coupling / (route.coupling + route.resistance)
        confidence = min(
            route_confidence,
            target_confidence,
            *(child.confidence for child in child_results),
        )
        step = CompositionStep(
            node.node_id,
            node.operator_id,
            input_types,
            output_type,
            value,
            route.route_id,
            route.target_path_id,
            active_sources,
            self._waves(active_sources, max_parallel_paths),
            tuple(dict.fromkeys((*adapter_ids, *target_adapters))),
            intensity,
            reason,
        )
        selected = tuple(dict.fromkeys((*child_routes, route.route_id, *target_routes)))
        active = tuple(
            dict.fromkeys((*child_adapters, *adapter_ids, *target_adapters))
        )
        return _NodeResult(
            value,
            output_type,
            confidence if value is not None else 0.0,
            (*child_steps, step),
            selected,
            active,
            reason,
        )

    def infer_composition(
        self,
        example: CompositionExample,
        *,
        state: CircuitState | None = None,
        max_parallel_paths: int = 4,
        max_depth: int = 8,
        max_nodes: int = 64,
    ) -> CompositionInference:
        """Execute one bounded tree by recursively triggering learned routes."""

        if not 1 <= max_depth <= 64 or not 1 <= max_nodes <= 4096:
            raise ValueError("Composition budgets must be depth 1..64 and nodes 1..4096.")
        if not 1 <= max_parallel_paths <= 8:
            raise ValueError("max_parallel_paths must be between one and eight.")
        depth, nodes = self._composition_shape(example.expression, max_depth, max_nodes)
        if depth > max_depth or nodes > max_nodes:
            reason = f"Composition budget exceeded: depth={depth}/{max_depth}, nodes={nodes}/{max_nodes}."
            return CompositionInference(example.event_id, None, None, 0.0, (), (), (), reason)
        selected = self.state if state is None else state
        result = self._infer_composition_node(
            example.expression,
            state=selected,
            max_parallel_paths=max_parallel_paths,
        )
        return CompositionInference(
            example.event_id,
            result.value,
            result.type_id,
            result.confidence,
            result.steps,
            result.selected_route_ids,
            result.active_adapter_ids,
            result.abstain_reason,
        )

    def propose_composition_update(
        self,
        rule: CompositionRule,
    ) -> tuple[CircuitState, StateDelta]:
        """Build an isolated typed route from a verified structural contract."""

        if not self._composition_target_available(self.state, rule.target_path_id):
            raise ValueError(f"Composition target is not verified: {rule.target_path_id}")
        expected_contract = self._composition_target_contract(rule.target_path_id)
        if expected_contract != (rule.input_types, rule.output_type):
            raise ValueError("Composition rule does not match the target path's typed contract.")
        routes = self.state.composition_map()
        adapters = self.state.adapter_map()
        original_routes = dict(routes)
        original_adapters = dict(adapters)
        route_id = self._composition_route_id(rule)
        sources = self._composition_sources(rule)
        route = routes.get(
            route_id,
            CompositionRoute(
                route_id=route_id,
                operator_id=rule.operator_id,
                input_types=rule.input_types,
                output_type=rule.output_type,
                target_path_id=rule.target_path_id,
                source_path_ids=(),
            ),
        ).updated(rule, sources)
        routes[route_id] = route
        for source_path_id in sources:
            adapter_id = self._adapter_id(source_path_id, route_id)
            adapter = adapters.get(
                adapter_id,
                JumpAdapter(adapter_id, source_path_id, route_id),
            )
            adapters[adapter_id] = adapter.updated(1.0)
        candidate = replace(
            self.state,
            composition_routes=tuple(sorted(routes.values(), key=lambda item: item.route_id)),
            adapters=tuple(sorted(adapters.values(), key=lambda item: item.adapter_id)),
        )
        delta = self._delta(original_routes, original_adapters, routes, adapters)
        return candidate, delta

    @staticmethod
    def _delta(
        old_routes: Mapping[str, object],
        old_adapters: Mapping[str, JumpAdapter],
        new_routes: Mapping[str, object],
        new_adapters: Mapping[str, JumpAdapter],
    ) -> StateDelta:
        created_routes = tuple(sorted(set(new_routes) - set(old_routes)))
        modified_routes = tuple(
            sorted(
                route_id
                for route_id in set(new_routes) & set(old_routes)
                if new_routes[route_id] != old_routes[route_id]
            )
        )
        created_adapters = tuple(sorted(set(new_adapters) - set(old_adapters)))
        modified_adapters = tuple(
            sorted(
                adapter_id
                for adapter_id in set(new_adapters) & set(old_adapters)
                if new_adapters[adapter_id] != old_adapters[adapter_id]
            )
        )
        return StateDelta(
            created_routes,
            modified_routes,
            created_adapters,
            modified_adapters,
        )

    def verify_foundation(self, path_id: str) -> None:
        """Promote one externally verified sensor path without source text."""

        foundations = tuple(sorted(set((*self.state.verified_foundations, path_id))))
        self.state = replace(
            self.state,
            verified_foundations=foundations,
            promotions=self.state.promotions + int(path_id not in self.state.verified_foundations),
        )

    def promote(self, candidate: CircuitState) -> None:
        """Replace the parent only after an independent evaluator accepts it."""

        self.state = replace(candidate, promotions=self.state.promotions + 1)

    def evaluate_categories(
        self,
        samples: Iterable[CircuitSample],
        *,
        state: CircuitState | None = None,
        max_parallel_paths: int = 4,
    ) -> ClassificationMetrics:
        cases = answered = correct = 0
        for sample in samples:
            inference = self.infer_category(
                sample,
                state=state,
                max_parallel_paths=max_parallel_paths,
            )
            cases += 1
            answered += int(inference.prediction is not None)
            correct += int(inference.prediction == sample.target)
        return ClassificationMetrics(cases, answered, correct)

    def assess_category_candidate(
        self,
        current: Sequence[CircuitSample],
        protected: Sequence[CircuitSample],
        held_out: Sequence[CircuitSample],
        candidate: CircuitState,
        delta: StateDelta,
        *,
        max_parallel_paths: int = 4,
    ) -> CandidateAssessment:
        parent_current = self.evaluate_categories(current, max_parallel_paths=max_parallel_paths)
        candidate_current = self.evaluate_categories(
            current, state=candidate, max_parallel_paths=max_parallel_paths
        )
        parent_protected = self.evaluate_categories(
            protected, max_parallel_paths=max_parallel_paths
        )
        candidate_protected = self.evaluate_categories(
            protected, state=candidate, max_parallel_paths=max_parallel_paths
        )
        parent_held_out = self.evaluate_categories(
            held_out, max_parallel_paths=max_parallel_paths
        )
        candidate_held_out = self.evaluate_categories(
            held_out, state=candidate, max_parallel_paths=max_parallel_paths
        )
        accepted = (
            candidate.total_support > self.state.total_support
            and candidate_current.errors <= parent_current.errors
            and candidate_protected.errors <= parent_protected.errors
            and candidate_held_out.errors <= parent_held_out.errors
            and delta.changed_objects > 0
        )
        return CandidateAssessment(
            candidate,
            delta,
            parent_current,
            candidate_current,
            parent_protected,
            candidate_protected,
            parent_held_out,
            candidate_held_out,
            accepted,
        )

    def evaluate_compositions(
        self,
        examples: Iterable[CompositionExample],
        *,
        state: CircuitState | None = None,
        max_parallel_paths: int = 4,
    ) -> ClassificationMetrics:
        cases = answered = correct = 0
        for example in examples:
            inference = self.infer_composition(
                example,
                state=state,
                max_parallel_paths=max_parallel_paths,
            )
            cases += 1
            answered += int(inference.answer is not None)
            correct += int(
                inference.output_type == example.expected_type
                and inference.answer == example.expected_value
            )
        return ClassificationMetrics(cases, answered, correct)

    def assess_composition_candidate(
        self,
        current: Sequence[CompositionExample],
        protected: Sequence[CompositionExample],
        held_out: Sequence[CompositionExample],
        candidate: CircuitState,
        delta: StateDelta,
        *,
        max_parallel_paths: int = 4,
    ) -> CandidateAssessment:
        parent_current = self.evaluate_compositions(
            current, max_parallel_paths=max_parallel_paths
        )
        candidate_current = self.evaluate_compositions(
            current, state=candidate, max_parallel_paths=max_parallel_paths
        )
        parent_protected = self.evaluate_compositions(
            protected, max_parallel_paths=max_parallel_paths
        )
        candidate_protected = self.evaluate_compositions(
            protected, state=candidate, max_parallel_paths=max_parallel_paths
        )
        parent_held_out = self.evaluate_compositions(
            held_out, max_parallel_paths=max_parallel_paths
        )
        candidate_held_out = self.evaluate_compositions(
            held_out, state=candidate, max_parallel_paths=max_parallel_paths
        )
        accepted = (
            candidate.total_support > self.state.total_support
            and candidate_current.errors < parent_current.errors
            and candidate_protected.errors <= parent_protected.errors
            and candidate_held_out.errors <= parent_held_out.errors
            and delta.changed_objects > 0
        )
        return CandidateAssessment(
            candidate,
            delta,
            parent_current,
            candidate_current,
            parent_protected,
            candidate_protected,
            parent_held_out,
            candidate_held_out,
            accepted,
        )

    def evaluate_arithmetic(
        self,
        events: Iterable[ArithmeticEvent],
        *,
        state: CircuitState | None = None,
        max_parallel_paths: int = 4,
    ) -> ClassificationMetrics:
        cases = answered = correct = 0
        for event in events:
            inference = self.infer_arithmetic(
                event,
                state=state,
                max_parallel_paths=max_parallel_paths,
            )
            cases += 1
            answered += int(inference.answer is not None)
            correct += int(inference.answer == event.target)
        return ClassificationMetrics(cases, answered, correct)

    def arithmetic_candidate_is_safe(
        self,
        event: ArithmeticEvent,
        candidate: CircuitState,
        protected: Sequence[ArithmeticEvent],
        held_out: Sequence[ArithmeticEvent],
        *,
        max_parallel_paths: int = 4,
    ) -> tuple[bool, ClassificationMetrics, ClassificationMetrics, ClassificationMetrics, ClassificationMetrics]:
        parent_protected = self.evaluate_arithmetic(
            protected, max_parallel_paths=max_parallel_paths
        )
        candidate_protected = self.evaluate_arithmetic(
            protected, state=candidate, max_parallel_paths=max_parallel_paths
        )
        parent_held_out = self.evaluate_arithmetic(
            held_out, max_parallel_paths=max_parallel_paths
        )
        candidate_held_out = self.evaluate_arithmetic(
            held_out, state=candidate, max_parallel_paths=max_parallel_paths
        )
        parent_current = self.infer_arithmetic(event, max_parallel_paths=max_parallel_paths)
        candidate_current = self.infer_arithmetic(
            event, state=candidate, max_parallel_paths=max_parallel_paths
        )
        parent_error = (
            abs(event.target) if parent_current.answer is None else abs(event.target - parent_current.answer)
        )
        candidate_error = (
            abs(event.target)
            if candidate_current.answer is None
            else abs(event.target - candidate_current.answer)
        )
        accepted = (
            candidate.total_support > self.state.total_support
            and candidate_error <= parent_error
            and candidate_protected.errors <= parent_protected.errors
            and candidate_held_out.errors <= parent_held_out.errors
        )
        return (
            accepted,
            parent_protected,
            candidate_protected,
            parent_held_out,
            candidate_held_out,
        )

    def resource_ledger(self) -> dict[str, int]:
        """Count explicit model state; Python container overhead is reported separately."""

        route_scalars = sum(len(route.center) + 6 for route in self.state.routes)
        transform_scalars = sum(len(route.weights) + 6 for route in self.state.transforms)
        composition_scalars = len(self.state.composition_routes) * 5
        adapter_scalars = len(self.state.adapters) * 3
        persistent_scalars = (
            route_scalars + transform_scalars + composition_scalars + adapter_scalars + 1
        )
        return {
            "routes": (
                len(self.state.routes)
                + len(self.state.transforms)
                + len(self.state.composition_routes)
            ),
            "composition_routes": len(self.state.composition_routes),
            "jump_adapters": len(self.state.adapters),
            "persistent_scalars": persistent_scalars,
            "estimated_numeric_payload_bytes": persistent_scalars * 8,
        }


def arithmetic_target_weights(operation: Operation) -> tuple[float, float, float]:
    """Exact teacher explanation for the two admitted arithmetic relations."""

    if operation is Operation.ADD:
        return (1.0, 1.0, 0.0)
    if operation is Operation.SUBTRACT:
        return (1.0, -1.0, 0.0)
    raise ValueError(f"No admitted arithmetic explanation for {operation.value}.")
