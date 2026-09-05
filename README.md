# Kavi

Author: [Arnav123-s](https://github.com/Arnav123-s)

Kavi learns reusable computations as circuit structure. Gates and connections determine the operation; temporary signals disappear after execution. A wrong answer supplies evidence that the current procedure needs repair. The objective is to improve that shared computation while preserving earlier correct behavior.

The current structural learner acquires a binary-addition transition from examples using AND, XOR and NOT gates. Its saved model contains no teaching equations or learned numerical edge weights. The bit-processing loop, one state register, encoding and search controller are supplied. Broader language learning and autonomous invention of those components remain research goals.

## Run and inspect

The structural learner uses the Python standard library. From this directory:

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

The first declared trial used three seeds. Every seed acquired the same five-gate, 321-byte circuit. Each passed 127 unseen four-bit pairs, the full 65,536-pair eight-bit audit, and 190 longer-input cases up to 1,024 bits. The audit preserved all 6,561 answers the foundation circuit previously got right. The complete run took 5.281 seconds on one CPU process.

The eight-bit audit includes selection examples; the separate 127-case and length-transfer banks were withheld. The 321-byte figure is the model artifact, excluding the executor and learning workspace. These results establish a narrow operation-learning mechanism under strong, declared representation assumptions. See the [experiment record](experiments/2026-09-05-circuit-learning.md) and [machine-readable results](experiments/2026-09-05-circuit-learning.json).

## Documentation

- [Architecture](docs/DESIGN.md)
- [Engineering and research specification](docs/KAVI_ENGINEERING_SPECIFICATION.md)
- [Printable specification](docs/Kavi_Engineering_and_Research.pdf)
- [Adaptive circuit formulation](docs/ADAPTIVE_DATAFLOW_CIRCUIT.md)
- [Discrete circuit runtime](docs/CIRCUIT_RUNTIME.md)
- [Evaluation protocol](docs/EVALUATION_PROTOCOL.md)
- [Complete documentation index](docs/DOCUMENTATION_INDEX.md)

## Earlier experiments and development

The repository also retains a symbolic pathway circuit with supplied operation contracts and a separate 66,880-parameter recurrent text model. Their measured language limitations and regressions remain documented. They are separate implementations; their capabilities are not part of the new circuit model.

Python 3.11 or later is declared. The circuit trial used Python 3.12.14. All 153 tests passed using Python 3.13.5 with PyTorch 2.6.0+cu124; PyTorch is needed only for the optional text core and its tests.

```powershell
python -B -m unittest discover -s tests -q
python -m kavi --help
python -m kavi circuit --help
```

Private sources, conversations, large checkpoints and complete run logs remain in ignored local folders. The public circuit and compact trial results contain generated arithmetic data only. A software license has not yet been selected.
