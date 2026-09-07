# Kavi

Author: [Arnav123-s](https://github.com/Arnav123-s)

Kavi learns reusable computations as circuit structure. Gates and connections determine the operation; temporary signals disappear after execution. A wrong answer supplies evidence that the current procedure needs repair. The objective is to improve that shared computation while preserving earlier correct behavior.

The structural learner acquires addition and subtraction transitions from examples using AND, XOR and NOT gates, then learns programs that call acquired operations. A retained library contains 13 procedures in 2,238 bytes. Its model contains no teaching equations or learned numerical edge weights. Encoding, state registers, iteration semantics, types and the search controller are supplied. Language interpretation and autonomous invention of those components remain research goals.

## Run and inspect

The structural learner uses the Python standard library. Open a live procedure-learning window from this directory:

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

Two library trials ran across three seeds each in 45.868 and 56.349 seconds. The second added a lesson that acquired a 113-byte call arrangement for scaling a large quantity by a small count. Powers and factorials then passed every declared follow-up test, including `20^10` and `18!`. The resulting programs execute acquired addition through earlier learned procedures.

Library growth also made search harder: the follow-up timed out on sum of squares. That operation was retained from the first trial after exact dependency checks, yielding the 13-procedure artifact. Original multiplication remains sensitive to operand order. Storage is compact, but the results do not establish advanced subject competence or nearly free future learning. See the [complete study and failures](experiments/2026-09-05-procedure-library.md) and [advanced capability protocol](docs/ADVANCED_CAPABILITY_PROTOCOL.md).

The first declared trial used three seeds. Every seed acquired the same five-gate, 321-byte circuit. Each passed 127 unseen four-bit pairs, the full 65,536-pair eight-bit audit, and 190 longer-input cases up to 1,024 bits. The audit preserved all 6,561 answers the foundation circuit previously got right. The complete run took 5.281 seconds on one CPU process.

The eight-bit audit includes selection examples; the separate 127-case and length-transfer banks were withheld. The 321-byte figure is the model artifact, excluding the executor and learning workspace. These results establish a narrow operation-learning mechanism under strong, declared representation assumptions. See the [experiment record](experiments/2026-09-05-circuit-learning.md) and [machine-readable results](experiments/2026-09-05-circuit-learning.json).

## Documentation

- [Architecture](docs/DESIGN.md)
- [Engineering and research specification](docs/KAVI_ENGINEERING_SPECIFICATION.md)
- [Printable specification](docs/Kavi_Engineering_and_Research.pdf)
- [Adaptive circuit formulation](docs/ADAPTIVE_DATAFLOW_CIRCUIT.md)
- [Discrete circuit runtime](docs/CIRCUIT_RUNTIME.md)
- [Procedure library runtime](docs/PROCEDURE_LIBRARY_RUNTIME.md)
- [Evaluation protocol](docs/EVALUATION_PROTOCOL.md)
- [Complete documentation index](docs/DOCUMENTATION_INDEX.md)

## Earlier experiments and development

The repository also retains a symbolic pathway circuit with supplied operation contracts and a separate 66,880-parameter recurrent text model. Their measured language limitations and regressions remain documented. They are separate implementations; their capabilities are not part of the new circuit model.

Python 3.11 or later is declared. The first circuit trial used Python 3.12.14; the library trials used Python 3.13.5. All 169 tests passed using Python 3.13.5 with PyTorch 2.6.0+cu124; PyTorch is needed only for the optional text core and its tests.

```powershell
python -B -m unittest discover -s tests -q
python -m kavi --help
python -m kavi circuit --help
```

Private sources, conversations, large checkpoints and complete run logs remain in ignored local folders. The public circuit and compact trial results contain generated arithmetic data only. A software license has not yet been selected.
