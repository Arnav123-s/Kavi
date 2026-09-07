# Kavi

Author: [Arnav123-s](https://github.com/Arnav123-s)

Kavi learns reusable computations as circuit structure. Gates and connections determine the operation; temporary signals disappear after execution. A wrong answer supplies evidence that the current procedure needs repair. The objective is to improve that shared computation while preserving earlier correct behavior.

The structural learner acquires addition and subtraction transitions from examples using AND, XOR and NOT gates, then learns programs that call acquired operations. The original retained library contains 13 procedures in 2,238 bytes; a checked multiplication optimization produces a 2,272-byte library with the same 13 entries. Its arithmetic model contains no teaching equations or learned numerical edge weights. Encoding, state registers, iteration semantics, types and the search controller are supplied.

The acquired 321-byte addition graph satisfies all eight local full-adder identities. Together with the specified bit-stream executor, this gives a [correctness theorem for every finite width](docs/ADDITION_CORRECTNESS.md); the implementation currently accepts inputs up to 4,096 bits. The theorem is separate from the learning claim, which includes a 129-case selection bank.

The current [physical-pathway research](docs/PHYSICAL_PATHWAY_RESEARCH.md) distinguishes mechanisms we engineer from mechanisms the model learns to select, compose or improve. Heat, cooling, catalysts and a computational element table are proposed internal rules. They are not implemented or measured capabilities.

A first sentence-learning extension induces typed frames from annotated examples and routes recognized calculations to those procedures. It also retains source-linked lexical memory from six short original-language passages. General prose comprehension and autonomous invention of control semantics remain research goals. See the [connector and language results](experiments/2026-09-07-connectors-language.md).

## Run and inspect

The structural learner uses the Python standard library. Query the latest compiled library without source files:

```powershell
python -B -m kavi library ask --library experiments/library-20260907-compiled.json multiply 1000000 3 --trace
```

For the new original-source sentence trial, use the [reviewed configuration and live-window instructions](docs/CONNECTORS_AND_LANGUAGE_PROTOCOL.md). Its source packet and learned lexical artifact remain local. Earlier procedure-learning runs can be inspected or reproduced with their historical source prerequisites:

```powershell
python -B -m kavi.learning_window --config curriculum/library-scaling-run.json --run-dir runs/library-trial
```

Inspect the configuration and press **Start teaching**. The window shows the actual process, pause/stop controls and saved-procedure queries. Append `--start` for an already reviewed and authorized run. A full teaching replay needs the admitted local source witness. The published model supports inference without that source:

```powershell
python -m kavi library ask --library experiments/library-20260905-retained.json factorial 18
python -m kavi library ask --library experiments/library-20260905-retained.json power 20 10 --trace
python -m kavi library ask --library experiments/library-20260905-retained.json sum_squares 72 83
```

The [procedure runtime](docs/PROCEDURE_LIBRARY_RUNTIME.md) documents the complete interface. The original gate-acquisition experiment remains available:

```powershell
python -u -m kavi circuit run --config curriculum/circuit-run.json --run-dir runs/circuit-trial --interactive
```

Use a new run directory. The automatic trial has a 180-second limit and displays candidate graphs, counterexamples, accepted repairs, retention and final results. The console then accepts `12345 + 67890`, `/trace 7 5`, `/circuit`, `/status` and `/quit`. The launcher `scripts/start-circuit.ps1` provides the same workflow with a fresh timestamped directory.

To query the small published model directly:

```powershell
python -m kavi circuit ask --model experiments/circuit-20260905-model.json 255 1 --trace
```

The [runtime reference](docs/CIRCUIT_RUNTIME.md) documents pause, resume, stop, file formats and the complete interface.

## Measured result

The 7 September connector and sentence trial completed in 2.653 seconds. All 16,431 multiplication cases passed; 47 swapped pairs had identical complete call traces, and 516 earlier successful cases had zero regressions. Multiplication now canonicalizes interchangeable inputs and uses binary scanning through the acquired addition gates. This is a supplied compiler optimization, not discovery of a new algorithm by the learner.

The language model acquired 18 frames from 36 annotated sentences. It passed 12 new-argument calculations and seven clause-role checks in known constructions, recalled two taught definitions, and correctly reported the seven declared unsupported, ambiguous or invalid cases. The combined saved arithmetic and language artifacts occupy 29,082 bytes; the worker peaked at 26.36 MiB. Unfamiliar wording, philosophical explanation and creative writing remain unsupported. The [study](experiments/2026-09-07-connectors-language.md) records source scope, costs and all evidence boundaries.

Two library trials ran across three seeds each in 45.868 and 56.349 seconds. The second added a lesson that acquired a 113-byte call arrangement for scaling a large quantity by a small count. Powers and factorials then passed every declared follow-up test, including `20^10` and `18!`. The resulting programs execute acquired addition through earlier learned procedures.

Library growth also made search harder: the follow-up timed out on sum of squares. That operation was retained from the first trial after exact dependency checks, yielding the original 13-procedure artifact. Its multiplication remains sensitive to operand order; the new compiled artifact addresses that defect. Storage is compact, but the results do not establish advanced subject competence or nearly free future learning. See the [earlier study and failures](experiments/2026-09-05-procedure-library.md) and [advanced capability protocol](docs/ADVANCED_CAPABILITY_PROTOCOL.md).

The first declared trial used three seeds. Every seed acquired the same five-gate, 321-byte circuit. Each passed 127 unseen four-bit pairs, the full 65,536-pair eight-bit audit, and 190 longer-input cases up to 1,024 bits. The audit preserved all 6,561 answers the foundation circuit previously got right. The complete run took 5.281 seconds on one CPU process.

The eight-bit audit includes selection examples; the separate 127-case and length-transfer banks were withheld. The 321-byte figure is the model artifact, excluding the executor and learning workspace. These results establish a narrow operation-learning mechanism under strong, declared representation assumptions. See the [experiment record](experiments/2026-09-05-circuit-learning.md) and [machine-readable results](experiments/2026-09-05-circuit-learning.json).

## Documentation

- [Certified arithmetic and software efficiency](docs/CERTIFIED_ARITHMETIC_AND_SOFTWARE_EFFICIENCY.md): review audit, software algorithms, physical pathways and deferred recommendations
- [Printable certificate and software study](docs/Kavi_Certified_Arithmetic_and_Software_Efficiency.pdf)
- [Architecture](docs/DESIGN.md)
- [Engineering and research specification](docs/KAVI_ENGINEERING_SPECIFICATION.md)
- [Printable baseline specification](docs/Kavi_Engineering_and_Research.pdf)
- [Structural sharing and quantum research](docs/STRUCTURAL_SHARING_AND_QUANTUM_RESEARCH.md): DreamCoder, Babble, XRF/LIBS, mathematical design and evaluation
- [Printable structural sharing study](docs/Kavi_Structural_Sharing_and_Quantum_Research.pdf)
- [Shared connectors and sentence learning](docs/CONNECTORS_AND_LANGUAGE_PROTOCOL.md)
- [Adaptive circuit formulation](docs/ADAPTIVE_DATAFLOW_CIRCUIT.md)
- [Discrete circuit runtime](docs/CIRCUIT_RUNTIME.md)
- [Procedure library runtime](docs/PROCEDURE_LIBRARY_RUNTIME.md)
- [Evaluation protocol](docs/EVALUATION_PROTOCOL.md)
- [Complete documentation index](docs/DOCUMENTATION_INDEX.md)

## Earlier experiments and development

The repository also retains a symbolic pathway circuit with supplied operation contracts and a separate 66,880-parameter recurrent text model. Their measured language limitations and regressions remain documented. They are separate implementations; their capabilities are not part of the new circuit model.

Python 3.11 or later is declared. The first circuit trial used Python 3.12.14; the library and sentence trials used Python 3.13.5. All 181 tests passed using Python 3.13.5 with the existing PyTorch installation; PyTorch is needed only for the optional earlier text core and its tests.

```powershell
python -B -m unittest discover -s tests -q
python -m kavi --help
python -m kavi circuit --help
```

Private sources, conversations, large checkpoints, source-derived lexical memory and complete run logs remain in ignored local folders. Public artifacts contain arithmetic programs, measurements, authored exercises and source metadata. A software license has not yet been selected.
