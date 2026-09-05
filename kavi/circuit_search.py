"""Counterexample-guided search over discrete streaming circuit structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Callable, Sequence

from .circuit_core import Circuit, Gate, PORTS, function_masks


Expr = tuple
Check = Callable[[], None]
Notify = Callable[[str, dict], None]


@dataclass(frozen=True)
class Example:
    left: int
    right: int
    target: int


@dataclass
class SearchStats:
    candidates: int = 0
    proposals: int = 0
    counterexamples: int = 0
    candidate_evaluations: int = 0
    candidate_frames: int = 0
    verifier_executions: int = 0
    verifier_gate_evaluations: int = 0
    surviving_candidates: int = 0


class NoConsistentCircuit(RuntimeError):
    pass


@lru_cache(maxsize=8192)
def expression_parts(expr: Expr) -> frozenset[Expr]:
    if len(expr) == 1:
        return frozenset()
    parts = {expr}
    for child in expr[1:]:
        parts.update(expression_parts(child))
    return frozenset(parts)


def compile_pair(first: Expr, second: Expr) -> Circuit:
    """Share identical subexpressions while materializing a gate graph."""
    gates: list[Gate] = []
    references: dict[Expr, int] = {}

    def visit(expr: Expr) -> int:
        if len(expr) == 1:
            return expr[0]
        if expr not in references:
            children = tuple(visit(child) for child in expr[1:])
            references[expr] = len(PORTS) + len(gates)
            gates.append(Gate(expr[0], children))
        return references[expr]

    first_ref, second_ref = visit(first), visit(second)
    return Circuit(tuple(gates), first_ref, second_ref)


def build_catalog(check: Check = lambda: None, notify: Notify = lambda *_: None) -> dict[int, Expr]:
    """Enumerate all 3-input Boolean functions from AND, XOR and NOT.

    Truth masks accelerate external search only. Each surviving function has
    a gate expression. Masks and teaching pairs are absent from saved models.
    The first representative has minimum expression-tree gate count in this
    grammar; joint DAG size is used later. Global minimum DAGs are not claimed.
    """
    catalog = {0: (3,), 255: (4,)}
    for port in range(3):
        catalog[sum(((row >> port) & 1) << row for row in range(8))] = (port,)
    by_cost: dict[int, list[tuple[int, Expr]]] = {0: sorted(catalog.items())}
    attempts = 0
    for cost in range(1, 10):
        check()
        found: dict[int, Expr] = {}

        def consider(mask: int, expr: Expr) -> None:
            if mask not in catalog and (mask not in found or repr(expr) < repr(found[mask])):
                found[mask] = expr

        for mask, expr in by_cost.get(cost - 1, []):
            consider(mask ^ 255, ("NOT", expr))
        for left_cost in range(cost):
            right_cost = cost - 1 - left_cost
            if left_cost > right_cost:
                continue
            for a_mask, a_expr in by_cost.get(left_cost, []):
                for b_mask, b_expr in by_cost.get(right_cost, []):
                    if left_cost == right_cost and a_mask > b_mask:
                        continue
                    children = tuple(sorted((a_expr, b_expr), key=repr))
                    consider(a_mask & b_mask, ("AND", *children))
                    consider(a_mask ^ b_mask, ("XOR", *children))
                    attempts += 2
                    if attempts % 1024 == 0:
                        check()
        by_cost[cost] = sorted(found.items())
        catalog.update(found)
        notify("catalog", {"tree_gates": cost, "functions": len(catalog), "combinations": attempts})
        if len(catalog) == 256:
            return catalog
    raise RuntimeError("Boolean function catalog did not reach completeness within its grammar budget.")


def predict_masks(emit: int, transition: int, left: int, right: int) -> int:
    """Fast external candidate simulation, checked against the gate executor."""
    state, result = 0, 0
    for index in range(max(left.bit_length(), right.bit_length(), 1) + 1):
        row = ((left >> index) & 1) | (((right >> index) & 1) << 1) | (state << 2)
        result |= ((emit >> row) & 1) << index
        state = (transition >> row) & 1
    return result


@dataclass
class CircuitSearch:
    catalog: dict[int, Expr]
    max_nodes: int = 12
    max_candidates: int = 65536
    max_evaluations: int = 1_000_000
    check: Check = lambda: None
    notify: Notify = lambda *_: None
    stats: SearchStats = field(default_factory=SearchStats)

    def learn(self, examples: Sequence[Example], *, protected: Sequence[Example] = (),
              state_enabled: bool = True, parent: Circuit | None = None) -> Circuit:
        if not examples:
            raise ValueError("Learning requires teaching examples.")
        if not 1 <= self.max_nodes <= 32 or not 1 <= self.max_candidates <= 65536:
            raise ValueError("Invalid structural search budget.")
        if self.max_evaluations < 1:
            raise ValueError("Candidate evaluation budget must be positive.")
        self.stats = SearchStats()
        old_masks = function_masks(parent) if parent else (0, 0)
        old_parts = expression_parts(self.catalog[old_masks[0]]) | expression_parts(self.catalog[old_masks[1]])
        pool = []
        for first in sorted(self.catalog):
            self.check()
            for second in (sorted(self.catalog) if state_enabled else [0]):
                parts = expression_parts(self.catalog[first]) | expression_parts(self.catalog[second])
                if len(parts) <= self.max_nodes:
                    distance = len(parts ^ old_parts) + (first != old_masks[0]) + (second != old_masks[1])
                    pool.append((len(parts), distance, first, second))
        pool.sort()
        if len(pool) > self.max_candidates:
            raise ValueError(f"Search requires {len(pool)} candidates; configured limit is {self.max_candidates}.")
        self.stats.candidates = len(pool)
        self.notify("search_space", {"candidates": len(pool), "protected": len(protected),
                                     "teaching": len(examples), "state_enabled": state_enabled})
        verification_bank = [*protected, *examples]
        while pool:
            self.check()
            _, _, first, second = pool[0]
            circuit = compile_pair(self.catalog[first], self.catalog[second])
            self.stats.proposals += 1
            self.notify("candidate", {"proposal": self.stats.proposals, "gates": len(circuit.gates),
                                      "remaining": len(pool), "circuit": circuit.to_dict(),
                                      "pathway": circuit.describe()})
            failed = None
            for index, example in enumerate(verification_bank):
                if index % 64 == 0:
                    self.check()
                observed = circuit.execute(example.left, example.right)
                self.stats.verifier_executions += 1
                self.stats.verifier_gate_evaluations += observed.gate_evaluations
                if observed.value != example.target:
                    failed = (example, observed.value, "protected" if index < len(protected) else "teaching")
                    break
            if failed is None:
                self.stats.surviving_candidates = len(pool)
                self.notify("accepted", {"sha256": circuit.digest, "gates": len(circuit.gates),
                                         "bytes": len(circuit.encoded()), "verified_cases": len(verification_bank),
                                         "pathway": circuit.describe()})
                return circuit
            example, actual, source = failed
            self.stats.counterexamples += 1
            self.notify("counterexample", {"left": example.left, "right": example.right,
                                           "actual": actual, "expected": example.target, "source": source,
                                           "meaning": "current procedure fails its task contract"})
            retained = []
            frames = max(example.left.bit_length(), example.right.bit_length(), 1) + 1
            for index, candidate in enumerate(pool):
                if index % 256 == 0:
                    self.check()
                if self.stats.candidate_evaluations >= self.max_evaluations:
                    raise RuntimeError("Candidate evaluation budget exhausted.")
                self.stats.candidate_evaluations += 1
                self.stats.candidate_frames += frames
                if predict_masks(candidate[2], candidate[3], example.left, example.right) == example.target:
                    retained.append(candidate)
            pool = retained
            self.notify("filtered", {"remaining": len(pool), "candidate_evaluations": self.stats.candidate_evaluations})
        raise NoConsistentCircuit("No circuit in the declared search space satisfies the observed constraints.")
