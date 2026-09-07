"""Typed procedure libraries with learned circuits and bounded composition."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
from typing import Callable

from .circuit_core import Circuit, MAX_INPUT_BITS


SCHEMA = "kavi.procedure-library.v1"
Expr = tuple


def expression(value) -> Expr:
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError("An expression must be a nonempty instruction list.")
    return tuple(expression(item) if isinstance(item, (list, tuple)) else item for item in value)


def node_count(expr: Expr) -> int:
    if expr[0] in {"arg", "const"}:
        return 0
    return 1 + sum(node_count(child) for child in expr[2:])


def dependencies(expr: Expr) -> set[str]:
    if expr[0] in {"arg", "const"}:
        return set()
    return {expr[1]}.union(*(dependencies(child) for child in expr[2:]))


def describe(expr: Expr) -> str:
    if expr[0] == "arg":
        return f"x{expr[1]}"
    if expr[0] == "const":
        return str(expr[1])
    children = ", ".join(describe(child) for child in expr[2:])
    return f"{expr[1]}({children})" if expr[0] == "call" else f"{expr[0]}[{expr[1]}]({children})"


@dataclass(frozen=True)
class Procedure:
    name: str
    arity: int
    contract: str
    circuit: Circuit | None = None
    body: Expr | None = None
    connector: str = "ordered"

    def to_dict(self) -> dict:
        value = {"name": self.name, "arity": self.arity, "contract": self.contract}
        if self.circuit is not None:
            value.update(kind="circuit", circuit=self.circuit.to_dict())
        else:
            value.update(kind="program", body=self.body)
        if self.connector != "ordered":
            value["connector"] = self.connector
        return value


@dataclass
class Execution:
    value: int = 0
    calls: int = 0
    frames: int = 0
    gates: int = 0
    iterations: int = 0
    trace: list[dict] = field(default_factory=list)
    trace_events: int = 0
    trace_truncated: bool = False
    connector_comparisons: int = 0
    bit_tests: int = 0
    shifts: int = 0


@dataclass(frozen=True)
class Limits:
    max_calls: int = 10000
    max_gates: int = 1_000_000
    max_iterations: int = 4096
    max_depth: int = 64
    max_trace_entries: int = 128


class ExecutionLimit(ValueError):
    pass


class ProcedureLibrary:
    def __init__(self, procedures=()):
        self.procedures: dict[str, Procedure] = {}
        for procedure in procedures:
            self.add(procedure)

    def _validate_expr(self, expr: Expr, arity: int, depth: int = 0) -> None:
        if depth > 12 or not isinstance(expr, tuple) or len(expr) < 2 or not isinstance(expr[0], str):
            raise ValueError("Invalid or excessively nested expression.")
        if expr[0] == "arg":
            if len(expr) != 2 or type(expr[1]) is not int or not 0 <= expr[1] < arity:
                raise ValueError("Invalid argument reference.")
        elif expr[0] == "const":
            if len(expr) != 2 or type(expr[1]) is not int or expr[1] not in (0, 1):
                raise ValueError("Only the declared constants zero and one are available.")
        else:
            if expr[0] not in {"call", "repeat", "range", "binary_fold"} or not isinstance(expr[1], str):
                raise ValueError("Unsupported instruction.")
            callee = self.procedures.get(expr[1])
            if callee is None:
                raise ValueError("Callees must be earlier, acquired procedures; cycles are forbidden.")
            count = callee.arity if expr[0] == "call" else (2 if expr[0] == "range" else 3)
            if len(expr) != count + 2 or (expr[0] != "call" and callee.arity != 2):
                raise ValueError("Call or iteration arity mismatch.")
            for child in expr[2:]:
                self._validate_expr(child, arity, depth + 1)

    def add(self, procedure: Procedure) -> None:
        if (not isinstance(procedure.name, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,39}", procedure.name)
                or procedure.name in self.procedures or len(self.procedures) >= 32):
            raise ValueError("Invalid, duplicate or excessive procedure name.")
        if type(procedure.arity) is not int or not 1 <= procedure.arity <= 3:
            raise ValueError("Procedure arity must be from one through three.")
        if not isinstance(procedure.contract, str) or procedure.contract not in {"naturals", "ordered_pair", "ordered_prefix"}:
            raise ValueError("Unknown input contract.")
        if procedure.contract == "ordered_pair" and procedure.arity != 2:
            raise ValueError("An ordered-pair contract requires two inputs.")
        if procedure.contract == "ordered_prefix" and procedure.arity < 2:
            raise ValueError("An ordered prefix requires at least two inputs.")
        if procedure.connector not in {"ordered", "unordered_pair"}:
            raise ValueError("Unknown connector.")
        if procedure.connector == "unordered_pair" and (procedure.arity != 2 or procedure.contract != "naturals"):
            raise ValueError("An unordered connector requires two natural-number inputs.")
        if (procedure.circuit is None) == (procedure.body is None):
            raise ValueError("A procedure must contain exactly one circuit or program.")
        if procedure.circuit is not None and procedure.arity != 2:
            raise ValueError("A streaming circuit accepts two inputs.")
        if procedure.body is not None:
            self._validate_expr(procedure.body, procedure.arity)
            if node_count(procedure.body) > 32:
                raise ValueError("Program exceeds the instruction budget.")
        self.procedures[procedure.name] = procedure

    @staticmethod
    def _natural(value):
        if type(value) is not int or value < 0 or value.bit_length() > MAX_INPUT_BITS:
            raise ValueError(f"Values must be natural numbers of at most {MAX_INPUT_BITS} bits.")

    def execute(self, name: str, args: tuple[int, ...], *, trace=False,
                limits=Limits(), check: Callable[[], None] = lambda: None) -> Execution:
        if type(limits.max_trace_entries) is not int or not 0 <= limits.max_trace_entries <= 100000:
            raise ValueError("Trace capacity must be between zero and 100000 entries.")
        result = Execution()
        try:
            result.value = self._call(name, tuple(args), result, limits, trace, check, 0)
        except Exception as error:
            error.execution = result
            raise
        return result

    def execute_expr(self, expr: Expr, args: tuple[int, ...], *, trace=False,
                     limits=Limits(), check: Callable[[], None] = lambda: None) -> Execution:
        if type(limits.max_trace_entries) is not int or not 0 <= limits.max_trace_entries <= 100000:
            raise ValueError("Trace capacity must be between zero and 100000 entries.")
        self._validate_expr(expr, len(args))
        for value in args:
            self._natural(value)
        result = Execution()
        try:
            result.value = self._eval(expr, args, result, limits, trace, check, 0)
        except Exception as error:
            error.execution = result
            raise
        return result

    def apply(self, tag: str, name: str, values: tuple[int, ...], *,
              limits=Limits(), check: Callable[[], None] = lambda: None) -> Execution:
        """Evaluate one external search node using the same execution semantics."""
        result = Execution()
        for value in values:
            self._natural(value)
        try:
            result.value = self._apply(tag, name, values, result, limits, False, check, 0)
        except Exception as error:
            error.execution = result
            raise
        return result

    def _call(self, name, args, result, limits, trace, check, depth):
        if depth > limits.max_depth or result.calls >= limits.max_calls:
            raise ExecutionLimit("Procedure call budget exhausted.")
        check()
        procedure = self.procedures.get(name)
        if procedure is None or len(args) != procedure.arity:
            raise ValueError("Unknown procedure or argument count mismatch.")
        for value in args:
            self._natural(value)
        if procedure.connector == "unordered_pair":
            result.connector_comparisons += 1
            args = (args[1], args[0]) if args[0] > args[1] else args
        if procedure.contract in {"ordered_pair", "ordered_prefix"} and args[0] < args[1]:
            raise ValueError("This procedure requires its first operand to be at least its second.")
        result.calls += 1
        if procedure.circuit is not None:
            frames = max(args[0].bit_length(), args[1].bit_length(), 1) + 1
            gates = frames * len(procedure.circuit.gates)
            if result.gates + gates > limits.max_gates:
                raise ExecutionLimit("Gate execution budget exhausted.")
            observed = procedure.circuit.execute(*args)
            result.frames += observed.frames
            result.gates += observed.gate_evaluations
            value = observed.value
        else:
            value = self._eval(procedure.body, args, result, limits, trace, check, depth + 1)
        self._natural(value)
        if trace:
            result.trace_events += 1
            if len(result.trace) < limits.max_trace_entries:
                result.trace.append({"procedure": name, "inputs": args, "output": value, "depth": depth})
            else:
                result.trace_truncated = True
        return value

    def _eval(self, expr, args, result, limits, trace, check, depth):
        if depth > limits.max_depth:
            raise ExecutionLimit("Expression depth budget exhausted.")
        if expr[0] == "arg":
            return args[expr[1]]
        if expr[0] == "const":
            return expr[1]
        values = tuple(self._eval(child, args, result, limits, trace, check, depth + 1)
                       for child in expr[2:])
        return self._apply(expr[0], expr[1], values, result, limits, trace, check, depth + 1)

    def _apply(self, tag, name, values, result, limits, trace, check, depth):
        if tag == "call":
            return self._call(name, values, result, limits, trace, check, depth)
        if tag == "binary_fold":
            if len(values) != 3 or name not in self.procedures or self.procedures[name].arity != 2:
                raise ValueError("Binary fold requires a binary procedure and three values.")
            count, state, step = values
            while count:
                check()
                if result.iterations >= limits.max_iterations:
                    raise ExecutionLimit("Binary iteration budget exhausted.")
                result.iterations += 1
                result.bit_tests += 1
                if count & 1:
                    state = self._call(name, (state, step), result, limits, trace, check, depth + 1)
                count >>= 1
                result.shifts += 1
                if count:
                    step <<= 1
                    result.shifts += 1
                    self._natural(step)
            return state
        if tag not in {"repeat", "range"} or len(values) != (3 if tag == "repeat" else 2):
            raise ValueError("Invalid iteration instruction.")
        if name not in self.procedures or self.procedures[name].arity != 2:
            raise ValueError("Iteration requires an existing binary procedure.")
        count, state = values[:2]
        if count > limits.max_iterations - result.iterations:
            raise ExecutionLimit("Iteration budget exhausted.")
        for index in range(count):
            if result.iterations >= limits.max_iterations:
                raise ExecutionLimit("Nested iteration budget exhausted.")
            result.iterations += 1
            step = values[2] if tag == "repeat" else index + 1
            state = self._call(name, (state, step), result, limits, trace, check, depth + 1)
        return state

    def to_dict(self):
        extended = any(p.connector != "ordered" or (p.body is not None and self._has_binary(p.body))
                       for p in self.procedures.values())
        return {"schema": "kavi.procedure-library.v2" if extended else SCHEMA,
                "procedures": [value.to_dict() for value in self.procedures.values()]}

    @staticmethod
    def _has_binary(expr):
        return expr[0] == "binary_fold" or any(ProcedureLibrary._has_binary(x) for x in expr[2:] if isinstance(x, tuple))

    def encoded(self) -> bytes:
        return (json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")

    @property
    def digest(self):
        return hashlib.sha256(self.encoded()).hexdigest()

    @classmethod
    def from_dict(cls, value):
        if (not isinstance(value, dict) or set(value) != {"schema", "procedures"}
                or value["schema"] not in {SCHEMA, "kavi.procedure-library.v2"} or not isinstance(value["procedures"], list)
                or len(value["procedures"]) > 32):
            raise ValueError("Invalid library schema.")
        library = cls()
        for entry in value["procedures"]:
            if not isinstance(entry, dict):
                raise ValueError("Invalid procedure record.")
            kind = entry.get("kind")
            if kind not in {"circuit", "program"}:
                raise ValueError("Invalid procedure kind.")
            body_key = "circuit" if kind == "circuit" else "body"
            fields = {"name", "arity", "contract", "kind", body_key}
            if "connector" in entry and value["schema"] == "kavi.procedure-library.v2":
                fields.add("connector")
            if set(entry) != fields:
                raise ValueError("Unsupported procedure fields.")
            library.add(Procedure(entry["name"], entry["arity"], entry["contract"],
                                  Circuit.from_dict(entry["circuit"]) if kind == "circuit" else None,
                                  expression(entry["body"]) if kind == "program" else None,
                                  entry.get("connector", "ordered")))
            if value["schema"] == SCHEMA and library.to_dict()["schema"] != SCHEMA:
                raise ValueError("Extended instructions require schema version two.")
        return library

    @classmethod
    def load(cls, path: Path):
        if path.stat().st_size > 1_048_576:
            raise ValueError("Library file exceeds one MiB.")
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def closure(self, name: str):
        required = {name}
        pending = [name]
        while pending:
            current = self.procedures[pending.pop()]
            for dependency in dependencies(current.body) if current.body is not None else ():
                if dependency not in required:
                    required.add(dependency)
                    pending.append(dependency)
        return ProcedureLibrary(p for key, p in self.procedures.items() if key in required)

    def storage(self):
        return {"shared_library_bytes": len(self.encoded()),
                "independent_closure_bytes": sum(len(self.closure(name).encoded()) for name in self.procedures),
                "procedures": len(self.procedures)}
