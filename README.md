# Kavi

Author: [Arnav123-s](https://github.com/Arnav123-s)

Kavi is an experimental learner for acquiring reusable computations under a fixed resource budget. The intended model is an adaptive circuit: information activates computational paths, experience changes their connections and operations, and useful structure becomes reusable. Temporary signals can disappear while the learned configuration persists. Preserving earlier behavior as that configuration changes is a central research requirement.

The learning target is the operation itself: an addition pathway should combine new quantities without retrieving remembered teaching equations. A wrong answer diagnoses a failure of the current computation or its application. Corrections should repair the shared procedure and preserve its required earlier behavior.

The repository currently contains a symbolic pathway circuit and a separate 66,880-parameter recurrent text model. The symbolic curriculum supplies operation contracts. The text model learns numerical parameters through backpropagation. General program acquisition and library consolidation remain proposed.

## Technical documentation

Start with the [engineering and research specification](docs/KAVI_ENGINEERING_SPECIFICATION.md). It covers the current implementation, mathematics, measured results, closest research relatives, component inventory, experiment design and development milestones. A [printable edition](docs/Kavi_Engineering_and_Research.pdf) contains the same specification.

The subsequent [adaptive dataflow circuit note](docs/ADAPTIVE_DATAFLOW_CIRCUIT.md) clarifies the intended architecture, structural learning, correction and doubt, and its relationship to self-modifying computational graphs. This separate addition extends the design discussion in the specification and is not included in its PDF edition.

- [Implementation reference](docs/IMPLEMENTATION_REFERENCE.md)
- [Current text model equations](docs/WAVE_MODEL_MATH.md)
- [Typed program acquisition](docs/PATH_PROGRAM_LEARNING.md)
- [Evaluation protocol](docs/EVALUATION_PROTOCOL.md)
- [Operations and reproducibility](docs/OPERATIONS_AND_REPRODUCIBILITY.md)
- [Research references](docs/RESEARCH.md)
- [Complete documentation index](docs/DOCUMENTATION_INDEX.md)

## Evidence

Recorded text experiments show strong single-symbol copying, weak transfer to longer sequences and continuing loss of earlier correct answers. One selected consolidation preserved 196 guard answers but broke two previously correct answers on independent final confirmation. An additional forward-repair connector produced no final correctness advantage in the paired three-seed comparison.

See the [experiment records](experiments/README.md) for configurations, counts and regressions. These measurements support a narrow experimental learner; broad language competence has not been demonstrated.

## Development

Python 3.11 or later is declared. The verified environment is Python 3.13.5 with PyTorch 2.6.0+cu124. PyTorch is required for the optional text core and its tests. The symbolic core uses the standard library.

```powershell
python -B -m unittest discover -s tests -q
python -m kavi --help
python -m kavi.pathway_cli --help
python -m kavi.wave_cli --help
```

All 138 tests passed after the project relocation on 5 September 2026. Live launch scripts start teaching processes; review the [operating guide](docs/OPERATIONS_AND_REPRODUCIBILITY.md) before using them.

Private sources, conversations, checkpoints and run logs remain in ignored local folders. Public source manifests contain metadata and fingerprints. A software license has not yet been selected.
