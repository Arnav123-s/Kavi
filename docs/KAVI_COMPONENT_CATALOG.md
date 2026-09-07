# Component catalog

Author: [Arnav123-s](https://github.com/Arnav123-s)

The [implementation reference](IMPLEMENTATION_REFERENCE.md) covers 62 package modules: the original 52, four circuit-learning modules and six procedure-library modules. The [circuit](CIRCUIT_RUNTIME.md) and [procedure](PROCEDURE_LIBRARY_RUNTIME.md) runtime contracts identify the current interfaces.

| Layer | Components | Current status |
| --- | --- | --- |
| Representation | Bit ports, AND/XOR/NOT gates, connections and outputs | Implemented strict graph format |
| Execution | Repeated bit frames and one temporary state bit | Supplied interpreter with measured execution traces |
| Acquisition | Enumerated gate expressions and counterexample filtering | Implemented bounded structural search |
| Repair | Candidate transition changes and protected-domain acceptance | Implemented; first trial recorded |
| Reuse | Shared gates and programs calling acquired operations | Bounded cross-task reuse measured; abstraction invention remains open |
| Procedure acquisition | Typed calls, repeated application and integer-range folds | Program arrangements learned under supplied instruction semantics |
| Teaching | Exact arithmetic generator and separate selection banks | Implemented external teacher |
| Evaluation | Sealed graph, reserved pairs, exhaustive audit and length transfer | Implemented independent final interface |
| Correctness evidence | Exhaustive local quantity-conservation check | Post-selection check; runtime proof remains outside its scope |
| Live interface | Run, watch, query, trace, inspect and controls | Implemented CLI and visible learning window |
| Earlier cores | Supplied symbolic contracts and recurrent text parameters | Retained as separate experiments |
| Broader learning | General abstraction discovery, learned control semantics and calibrated doubt | Proposed |
| Physical core | Energy dynamics and structural development | Unimplemented hypothesis |

Artifact size, interpreter cost, learning workspace and external evidence are separate quantities. A small graph does not make its teacher or search free.
