# Learned configuration

Author: [Arnav123-s](https://github.com/Arnav123-s)

The active configuration consists of acquired operations, typed connections, branches, constants and dispatch state. Its structure can change while the learner continues to support earlier tasks.

An acquired operation generates results for new inputs through the same reusable computation. Addition is retained as a procedure for combining quantities; the deployed circuit does not require a memory of individual teaching equations. A wrong result supplies evidence that the current procedure or its application is defective. Repair should correct the general mechanism while preserving required earlier behavior, rather than append an answer for the failing teaching pair.

Signals and temporary execution state can disappear after an interaction while the configuration retains what was learned. Connections may also change temporarily during execution. The [adaptive dataflow circuit note](ADAPTIVE_DATAFLOW_CIRCUIT.md) distinguishes these two forms of adaptation and specifies the role of feedback. Independently trained numerical edge weights are optional in this representation; operation choices and connection addresses still occupy memory.

A fixed number of nodes does not imply fixed memory if constants, edge lists or external records grow. Measure serialized bytes and peak workspace in addition to graph size. A finite configuration can encode a general procedure, but cannot store arbitrary unlimited independent facts.

Learning should first repair a supported computation or introduce a small missing operation. Consolidation can then replace repeated subgraphs with shared procedures. A successful change needs evidence for both the new behavior and the covered earlier behavior.

The current recurrent core changes coefficients inside a fixed computation. Its small residual connectors and route-splitting experiments provide limited structural controls. A bounded acquisition mechanism is now implemented in the [discrete circuit learner](CIRCUIT_RUNTIME.md). It learns a transition graph while the executor and learning rule remain supplied. General program and library acquisition remain open. See sections 6 to 8 of the [specification](KAVI_ENGINEERING_SPECIFICATION.md).
