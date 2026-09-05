"""Budgeted program acquisition with explicit, externally cached search work."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
import time
from typing import Callable, Sequence

from .procedure_core import Expr, Limits, ProcedureLibrary, describe


@dataclass(frozen=True)
class ProgramExample:
    inputs: tuple[int, ...]
    target: int


@dataclass
class ProgramStats:
    candidates: int = 0
    candidate_cases: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    executed_calls: int = 0
    executed_gates: int = 0
    executed_iterations: int = 0
    semantic_duplicates: int = 0
    invalid_candidates: int = 0
    retained_vectors: int = 0
    verification_cases: int = 0
    seconds: float = 0
    state: str = "searching"


class SearchExhausted(RuntimeError):
    pass


@dataclass(frozen=True)
class Term:
    expr: Expr
    values: tuple[int, ...]


def compositions(total: int, parts: int):
    if parts == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for rest in compositions(total - first, parts - 1):
                yield (first, *rest)


@dataclass
class ProgramSearch:
    library: ProcedureLibrary
    max_nodes: int = 3
    max_candidates: int = 20000
    max_candidate_cases: int = 1_000_000
    max_seconds: float = 45
    limits: Limits = Limits(max_calls=3000, max_gates=100000, max_iterations=512)
    check: Callable[[], None] = lambda: None
    notify: Callable[[str, dict], None] = lambda *_: None
    stats: ProgramStats = field(default_factory=ProgramStats)
    max_cache_entries: int = 100000

    def learn(self, arity: int, examples: Sequence[ProgramExample]) -> Expr:
        if not examples or not 1 <= arity <= 3 or not 1 <= self.max_nodes <= 4:
            raise ValueError("Invalid examples, arity or program search budget.")
        if min(self.max_candidates, self.max_candidate_cases, self.max_seconds) <= 0:
            raise ValueError("Program search budgets must be positive.")
        if any(len(example.inputs) != arity for example in examples):
            raise ValueError("Teaching example arity mismatch.")
        self.stats = ProgramStats()
        started = time.monotonic()
        wanted = tuple(example.target for example in examples)
        cache = {}
        by_cost: dict[int, list[Term]] = {}
        known = set()

        def check_budget():
            self.check()
            if time.monotonic() - started >= self.max_seconds:
                raise SearchExhausted("Program search time budget exhausted.")

        def submit(expr: Expr, values: tuple[int, ...], cost: int):
            if values == wanted:
                return expr
            if values in known:
                self.stats.semantic_duplicates += 1
            else:
                known.add(values)
                by_cost.setdefault(cost, []).append(Term(expr, values))
                self.stats.retained_vectors += 1
            return None

        try:
            for index in range(arity):
                found = submit(("arg", index), tuple(e.inputs[index] for e in examples), 0)
                if found is not None:
                    self.stats.state = "accepted"
                    return found
            for value in (0, 1):
                found = submit(("const", value), tuple(value for _ in examples), 0)
                if found is not None:
                    self.stats.state = "accepted"
                    return found
            # Recency is a declared prior favoring reuse of a recently acquired procedure.
            names = list(reversed(self.library.procedures))
            operations = [("call", name, self.library.procedures[name].arity) for name in names]
            operations += [(tag, name, 3 if tag == "repeat" else 2)
                           for tag in ("repeat", "range") for name in names
                           if self.library.procedures[name].arity == 2]
            self.notify("program_search_started", {"available_procedures": names,
                                                     "max_nodes": self.max_nodes,
                                                     "teaching_cases": len(examples)})
            for cost in range(1, self.max_nodes + 1):
                check_budget()
                for tag, name, count in operations:
                    for costs in compositions(cost - 1, count):
                        pools = [by_cost.get(value, ()) for value in costs]
                        if any(not pool for pool in pools):
                            continue
                        for children in product(*pools):
                            if self.stats.candidates >= self.max_candidates:
                                raise SearchExhausted("Candidate program budget exhausted.")
                            check_budget()
                            expr = (tag, name, *(child.expr for child in children))
                            self.stats.candidates += 1
                            values = []
                            invalid = False
                            for row in range(len(examples)):
                                if self.stats.candidate_cases >= self.max_candidate_cases:
                                    raise SearchExhausted("Candidate-case budget exhausted.")
                                self.stats.candidate_cases += 1
                                args = tuple(child.values[row] for child in children)
                                key = (tag, name, args)
                                if key in cache:
                                    value = cache[key]
                                    self.stats.cache_hits += 1
                                else:
                                    self.stats.cache_misses += 1
                                    try:
                                        observed = self.library.apply(tag, name, args, limits=self.limits,
                                                                      check=check_budget)
                                        value = observed.value
                                        self.stats.executed_calls += observed.calls
                                        self.stats.executed_gates += observed.gates
                                        self.stats.executed_iterations += observed.iterations
                                    except Exception as error:
                                        partial = getattr(error, "execution", None)
                                        if partial is not None:
                                            self.stats.executed_calls += partial.calls
                                            self.stats.executed_gates += partial.gates
                                            self.stats.executed_iterations += partial.iterations
                                        if not isinstance(error, ValueError):
                                            raise
                                        value = None
                                    if len(cache) < self.max_cache_entries:
                                        cache[key] = value
                                if value is None:
                                    invalid = True
                                    break
                                values.append(value)
                            if invalid:
                                self.stats.invalid_candidates += 1
                            else:
                                found = submit(expr, tuple(values), cost)
                                if found is not None:
                                    # Verify the full expression with fresh execution and no search cache.
                                    for example in examples:
                                        self.stats.verification_cases += 1
                                        observed = self.library.execute_expr(found, example.inputs,
                                                                             limits=self.limits, check=check_budget)
                                        self.stats.executed_calls += observed.calls
                                        self.stats.executed_gates += observed.gates
                                        self.stats.executed_iterations += observed.iterations
                                        if observed.value != example.target:
                                            raise RuntimeError("Candidate-vector and program execution disagree.")
                                    self.stats.state = "accepted"
                                    self.notify("program_accepted", {"program": describe(found), "nodes": cost,
                                                                      "candidates": self.stats.candidates,
                                                                      "candidate_cases": self.stats.candidate_cases})
                                    return found
                            if self.stats.candidates % 200 == 0:
                                self.notify("program_search_progress", {"nodes": cost,
                                            "candidates": self.stats.candidates,
                                            "retained_vectors": self.stats.retained_vectors,
                                            "current": describe(expr)})
            raise SearchExhausted("No program found within the declared grammar and node budget.")
        except SearchExhausted:
            self.stats.state = "exhausted"
            raise
        finally:
            self.stats.seconds = time.monotonic() - started
