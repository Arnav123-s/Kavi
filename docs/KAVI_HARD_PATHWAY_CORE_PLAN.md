# Executable pathway core

Author: [Arnav123-s](https://github.com/Arnav123-s)

Status: proposed program-learning core.

A pathway is a computation with typed inputs, operations and outputs. Intermediate values may enter an existing procedure when they satisfy its port contract. Shared subprocedures provide reuse; branches distinguish contexts that need different behavior.

The first core should use pure list, scalar, Boolean and integer operations with bounded execution. Acquire target programs from examples, then extract shared abstractions across solved tasks. Keep parsing, search, verification and execution independently measurable.

Finite parallel paths are candidate computations, each with a cost. A compact procedure can apply to larger inputs while consuming additional time and workspace. Connection patterns and constants still count as stored information.

See [typed program acquisition](PATH_PROGRAM_LEARNING.md) for the implementation outline and sections 6, 7, 11 and 13 of the [engineering specification](KAVI_ENGINEERING_SPECIFICATION.md) for semantics, capacity, interfaces and experiments.
