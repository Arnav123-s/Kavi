"""Discrete gate graphs with temporary state and a fixed streaming executor."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


PORTS = ("left", "right", "state", "zero", "one")
SCHEMA = "kavi.discrete-circuit.v1"
MAX_GATES = 32
MAX_INPUT_BITS = 4096


@dataclass(frozen=True)
class Gate:
    op: str
    inputs: tuple[int, ...]


@dataclass(frozen=True)
class Execution:
    value: int
    frames: int
    gate_evaluations: int
    trace: tuple[dict, ...] = ()
    trace_truncated: bool = False


@dataclass(frozen=True)
class Circuit:
    """A graph is model data; it has no teaching records or host-code hooks.

    References 0..4 address PORTS. Later references address earlier gates.
    Both outputs observe the same old state; the next state is committed once
    per frame. The framing and one state bit are supplied inductive biases.
    """

    gates: tuple[Gate, ...]
    emit: int
    next_state: int

    def __post_init__(self) -> None:
        if len(self.gates) > MAX_GATES:
            raise ValueError("Circuit exceeds the gate budget.")
        for index, gate in enumerate(self.gates):
            arity = {"AND": 2, "XOR": 2, "NOT": 1}.get(gate.op)
            if arity is None or len(gate.inputs) != arity:
                raise ValueError("Unknown gate or invalid arity.")
            if any(type(ref) is not int or not 0 <= ref < len(PORTS) + index
                   for ref in gate.inputs):
                raise ValueError("Gate references must point to ports or earlier gates.")
        for ref in (self.emit, self.next_state):
            if type(ref) is not int or not 0 <= ref < len(PORTS) + len(self.gates):
                raise ValueError("Invalid circuit output reference.")

    def _values(self, left: int, right: int, state: int) -> list[int]:
        values = [left, right, state, 0, 1]
        for gate in self.gates:
            first = values[gate.inputs[0]]
            if gate.op == "NOT":
                value = first ^ 1
            elif gate.op == "AND":
                value = first & values[gate.inputs[1]]
            else:
                value = first ^ values[gate.inputs[1]]
            values.append(value)
        return values

    def step(self, left: int, right: int, state: int) -> tuple[int, int]:
        if any(type(bit) is not int or bit not in (0, 1) for bit in (left, right, state)):
            raise ValueError("Gate inputs must be integer bits.")
        values = self._values(left, right, state)
        return values[self.emit], values[self.next_state]

    def execute(self, left: int, right: int, *, trace: bool = False,
                trace_limit: int = 64) -> Execution:
        """Execute the graph on least-significant-bit-first framed integers."""
        for value in (left, right):
            if type(value) is not int or value < 0 or value.bit_length() > MAX_INPUT_BITS:
                raise ValueError(f"Inputs must be nonnegative integers of at most {MAX_INPUT_BITS} bits.")
        if type(trace_limit) is not int or not 0 <= trace_limit <= 256:
            raise ValueError("Trace limit must be between 0 and 256.")
        frames = max(left.bit_length(), right.bit_length(), 1) + 1
        state, result = 0, 0
        records = []
        for index in range(frames):
            a, b = (left >> index) & 1, (right >> index) & 1
            values = self._values(a, b, state)
            bit, following = values[self.emit], values[self.next_state]
            result |= bit << index
            if trace and len(records) < trace_limit:
                records.append({"frame": index, "left": a, "right": b, "state_in": state,
                                "gates": values[len(PORTS):], "emit": bit, "state_out": following})
            state = following
        return Execution(result, frames, frames * len(self.gates), tuple(records),
                         trace and frames > trace_limit)

    def to_dict(self) -> dict:
        return {"schema": SCHEMA, "ports": list(PORTS), "initial_state": 0,
                "framing": "lsb-first-one-zero-padding-frame",
                "gates": [{"op": gate.op, "inputs": list(gate.inputs)} for gate in self.gates],
                "emit": self.emit, "next_state": self.next_state}

    @classmethod
    def from_dict(cls, value: dict) -> Circuit:
        fields = {"schema", "ports", "initial_state", "framing", "gates", "emit", "next_state"}
        if not isinstance(value, dict) or set(value) != fields:
            raise ValueError("Circuit file has missing or unsupported fields.")
        if (value["schema"] != SCHEMA or value["ports"] != list(PORTS)
                or type(value["initial_state"]) is not int or value["initial_state"] != 0
                or value["framing"] != "lsb-first-one-zero-padding-frame"):
            raise ValueError("Unsupported circuit execution contract.")
        raw = value["gates"]
        if not isinstance(raw, list) or len(raw) > MAX_GATES:
            raise ValueError("Invalid gate list.")
        gates = []
        for gate in raw:
            if (not isinstance(gate, dict) or set(gate) != {"op", "inputs"}
                    or not isinstance(gate["op"], str) or not isinstance(gate["inputs"], list)):
                raise ValueError("Invalid gate record.")
            gates.append(Gate(gate["op"], tuple(gate["inputs"])))
        return cls(tuple(gates), value["emit"], value["next_state"])

    def encoded(self) -> bytes:
        return (json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.encoded()).hexdigest()

    @classmethod
    def load(cls, path: Path) -> Circuit:
        if path.stat().st_size > 65536:
            raise ValueError("Circuit file is too large.")
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def describe(self) -> list[str]:
        def name(ref: int) -> str:
            return PORTS[ref] if ref < len(PORTS) else f"g{ref - len(PORTS)}"
        lines = [f"g{index} = {gate.op}({', '.join(name(ref) for ref in gate.inputs)})"
                 for index, gate in enumerate(self.gates)]
        return [*lines, f"emit = {name(self.emit)}", f"next_state = {name(self.next_state)}"]


def function_masks(circuit: Circuit) -> tuple[int, int]:
    """Describe one graph step for search diagnostics, outside inference."""
    emit, state = 0, 0
    for row in range(8):
        out, following = circuit.step(row & 1, (row >> 1) & 1, (row >> 2) & 1)
        emit |= out << row
        state |= following << row
    return emit, state
