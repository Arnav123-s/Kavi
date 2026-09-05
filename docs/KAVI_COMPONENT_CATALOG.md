# Component catalog

Author: [Arnav123-s](https://github.com/Arnav123-s)

The [implementation reference](IMPLEMENTATION_REFERENCE.md) covers 56 package modules: the original 52 and four structural-learning modules. The [runtime contract](CIRCUIT_RUNTIME.md) identifies the current component interfaces.

| Layer | Components | Current status |
| --- | --- | --- |
| Representation | Bit ports, AND/XOR/NOT gates, connections and outputs | Implemented strict graph format |
| Execution | Repeated bit frames and one temporary state bit | Supplied interpreter with measured execution traces |
| Acquisition | Enumerated gate expressions and counterexample filtering | Implemented bounded structural search |
| Repair | Candidate transition changes and protected-domain acceptance | Implemented; first trial recorded |
| Reuse | Shared gate subexpressions and repeated execution across positions | Compiler sharing and supplied loop; cross-task library learning remains open |
| Teaching | Exact arithmetic generator and separate selection banks | Implemented external teacher |
| Evaluation | Sealed graph, reserved pairs, exhaustive audit and length transfer | Implemented independent final interface |
| Correctness evidence | Exhaustive local quantity-conservation check | Post-selection check; runtime proof remains outside its scope |
| Live interface | Run, watch, query, trace, inspect and controls | Implemented CLI |
| Earlier cores | Supplied symbolic contracts and recurrent text parameters | Retained as separate experiments |
| Broader learning | General libraries, learned control structure and calibrated doubt | Proposed |
| Physical core | Energy dynamics and structural development | Unimplemented hypothesis |

Artifact size, interpreter cost, learning workspace and external evidence are separate quantities. A small graph does not make its teacher or search free.
