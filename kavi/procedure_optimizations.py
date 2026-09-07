"""Checked compilation of an acquired repeated-addition procedure."""

from dataclasses import replace
from itertools import product

from .procedure_core import ProcedureLibrary


def addition_certificate(circuit):
    """Check the complete local transition identity, with its framing assumptions."""
    if circuit.to_dict()["initial_state"] != 0:
        raise ValueError("Addition requires a zero initial carry.")
    rows = []
    for a, b, carry in product((0, 1), repeat=3):
        ports = [a, b, carry, 0, 1]
        for gate in circuit.gates:
            values = [ports[i] for i in gate.inputs]
            ports.append((values[0] ^ values[1]) if gate.op == "XOR" else
                         (values[0] & values[1]) if gate.op == "AND" else 1 - values[0])
        emit, state = ports[circuit.emit], ports[circuit.next_state]
        if emit + 2 * state != a + b + carry:
            raise ValueError("The dependency does not satisfy the addition identity.")
        rows.append([a, b, carry, emit, state])
    return rows


def compile_product(library, name="multiply"):
    """Return a fresh library; never mutate or retrain the original artifact.

    Binary scanning, shifts and normalization are supplied compiler semantics.
    The acquired gate dependency and the original procedure are verified first.
    """
    original = library.procedures[name]
    body = original.body
    if (original.arity != 2 or original.contract != "naturals" or original.connector != "ordered"
            or body is None or body[0] != "repeat" or body[3] != ("const", 0)
            or {body[2], body[4]} != {("arg", 0), ("arg", 1)}):
        raise ValueError("Only repeated addition with zero accumulator and both inputs is eligible.")
    dependency = library.procedures[body[1]]
    if dependency.circuit is None or dependency.contract != "naturals" or dependency.connector != "ordered":
        raise ValueError("The loop dependency must be a natural-number addition circuit.")
    rows = addition_certificate(dependency.circuit)
    replacement = replace(original, connector="unordered_pair",
                          body=("binary_fold", dependency.name, ("arg", 0), ("const", 0), ("arg", 1)))
    result = ProcedureLibrary(replacement if p.name == name else p for p in library.procedures.values())
    return result, {"kind": "checked_compiler_transformation", "source_sha256": library.digest,
                    "result_sha256": result.digest, "procedure": name, "addition_rows": rows,
                    "invariant": "accumulator + count * step = initial_left * initial_right",
                    "scope": "Exact natural-number results within declared value and execution limits; not a formal proof of Python."}
