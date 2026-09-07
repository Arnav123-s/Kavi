# Implementation reference

Author: [Arnav123-s](https://github.com/Arnav123-s)

The package contains separate symbolic and recurrent experiments. A supplied operation contract, an acquired coefficient and a learned program are distinct forms of supervision.

The following inventory covers the earlier symbolic and recurrent cores, structural circuit learning, procedure acquisition, connectors, sentence learning and the foundation extension. Earlier cores are retained as separate experiments; they should not be added together as though they constituted one trained model.

### Foundation extension

| Module | Responsibility |
| --- | --- |
| `foundation_curriculum.py` | Authored tasks, disjoint banks, fixed/cumulative comparisons and measured follow-ups |
| `rational_paths.py` | Supplied exact sign/fraction representation over acquired integer dependencies; bounded learned call compositions |
| `curriculum_cli.py` | Read-only queries of published consolidated checkpoints |

The [foundation study](../experiments/2026-09-07-foundation-curriculum.md) documents the teaching windows and runner scripts. `procedure_search.py` now permits explicit call-only and operation-family restrictions while preserving defaults. `grounded_language.py` has an optional most-literal-token resolution policy, serialized as schema v2; its previous v1 behavior remains supported.

### Current structural learner

| Module | Responsibility |
| --- | --- |
| `circuit_core.py` | Validated gate graphs, streaming execution, model serialization and traces |
| `circuit_search.py` | Boolean expression catalog, graph sharing, ranking and counterexample-guided acquisition |
| `circuit_runtime.py` | Teacher partitions, finite run controls, protected behavior, sealed evaluation and evidence |
| `circuit_cli.py` | Live runs, watching, inspection, direct queries and the interactive console |

The runtime uses a supplied processing loop and one state register. Its learner acquires their transition circuit. [Implementation contract](CIRCUIT_RUNTIME.md).

### Acquired procedure library

| Module | Responsibility |
| --- | --- |
| `procedure_core.py` | Strict typed library schema, actual acquired calls, bounded iteration and serialization |
| `procedure_search.py` | Bottom-up search, temporary candidate caching, budgets and measured work |
| `library_curriculum.py` | Source fingerprints, formal exercises, task partitions and final probes |
| `library_runtime.py` | Acquisition, comparisons, immutable earlier definitions and sealed evaluation |
| `library_cli.py` | Run, inspect, query, status and controls |
| `learning_window.py` | Visible start, real process transcript, pause/stop and saved-procedure queries |

The learner chooses program arrangements in a supplied language. Two measured trials and a retained 13-procedure artifact are described in the [study](../experiments/2026-09-05-procedure-library.md). [Runtime contract](PROCEDURE_LIBRARY_RUNTIME.md).

### Shared connectors and sentence learning

| Module | Responsibility |
| --- | --- |
| `procedure_optimizations.py` | Check local addition behavior and compile a repeated-addition body to canonical binary multiplication |
| `grounded_language.py` | Learn typed sentence frames from annotations; retain source-linked lexical memory; interpret or decline new requests |
| `connector_language_cli.py` | Source admission, finite live trial, sealed evaluation and saved-model text queries |

The existing procedure executor implements the connector and binary fold; the existing live window supports the new runner. [Protocol](CONNECTORS_AND_LANGUAGE_PROTOCOL.md) and [measured results](../experiments/2026-09-07-connectors-language.md).

### A.1 Initial pathway and explanation experiments

| Module | Responsibility |
| --- | --- |
| `types.py` | Event, pathway, trace and update data contracts |
| `graph.py` | Initial routed graph, path selection and numeric execution |
| `learning.py` | Verification and candidate pathway updates for generated arithmetic |
| `runtime.py` | Finite event loop, controls, measurements and persistence |
| `cli.py` | Root command dispatch and earlier stage-0 interface |
| `lessons.py` | Structured teaching explanations and lesson examples |
| `explanation_learning.py` | Translation of supplied explanations into checked updates |
| `lesson_runtime.py` | Finite explanation-learning experiment loop |
| `lesson_cli.py` | Explanation experiment commands |
| `__init__.py` | Package metadata and import boundary |
| `__main__.py` | Entry point for `python -m kavi` |

### A.2 Symbolic learning and composition

| Module | Responsibility |
| --- | --- |
| `symbol_core.py` | Trainable signal prototypes for early symbol tasks |
| `symbol_runtime.py` | Finite symbol curriculum and recorded evaluations |
| `unicode_core.py` | Unicode scalar representation and small script-route model |
| `unicode_runtime.py` | Generated scalar and script curriculum controls |
| `textbook_core.py` | Compact numeric concept core for the reviewed algebra lesson |
| `textbook_runtime.py` | Source fingerprint checks and finite concept teaching |
| `school.py` | Prerequisite and promotion orchestration across early cores |
| `school_cli.py` | Curriculum inspection and finite school commands |
| `adaptive_syllabus.py` | Adaptive checks, diagnosis and repair queues |
| `adaptive_cli.py` | Adaptive syllabus command-line interface |
| `pathway_circuit.py` | Unified routes, prototypes, adapters and typed composition execution |
| `pathway_live.py` | Cross-stage teaching, checkpointing and multiple event feeds |
| `pathway_cli.py` | Unified circuit commands and feed access |
| `composition_curriculum.py` | Supplied structural contracts and composition teaching cases |
| `composition_evaluation.py` | Separate composition audit generator |
| `developmental.py` | Supported mastery checks, correction rounds and fresh tests |
| `teaching_search.py` | External candidate-update comparison and selection |
| `script_reference.py` | Teacher access to fingerprinted Unicode script data |

### A.3 Text learning and sources

| Module | Responsibility |
| --- | --- |
| `wave_core.py` | Complex recurrent byte model, loss, optimization and generation |
| `continuous_teacher.py` | Resumable book teaching and interaction queues |
| `language_teacher.py` | Language prerequisites and answer-focused corrections |
| `language_curriculum.py` | Small generated language tasks and exact targets |
| `book_curriculum.py` | Source admission, arithmetic units and exam partitions |
| `mixed_quizzes.py` | Fresh copying, joining and sequence-position tasks |
| `multilingual_bridge.py` | Small writing-system subsets, mixed quizzes and retention |
| `wave_cli.py` | Text run controller, read-only feeds and local console |
| `source_manifest.py` | Source records, fingerprints and teaching-scope validation |
| `source_cli.py` | Source admission inspection |
| `teaching_sources.py` | Reviewed-source lookup and bounded teaching packets |
| `catalog_cli.py` | Read-only people-and-works catalog interface |

### A.4 Experiments and common infrastructure

| Module | Responsibility |
| --- | --- |
| `strategy_trials.py` | Teaching recipes and comparison partitions |
| `teaching_comparison.py` | Isolated comparisons of teacher methods |
| `pathway_trials.py` | Damped updates, rewiring and route-splitting candidates |
| `repair_trials.py` | Small context-dependent residual connectors |
| `flow_preservation.py` | Reference-gradient displacement projection |
| `consolidation_trials.py` | Bounded interpolation search with guard verification |
| `forward_repair.py` | Continued learning from the latest configuration and jump variants |
| `trial_resources.py` | Process resource observations and available sensor readings |
| `file_io.py` | Atomic writes with Windows reader-lock handling |
| `terminal.py` | Terminal encoding and output compatibility |
| `friendly_live.py` | Readable presentation of recorded lessons and computations |

The `scripts` directory contains launchers, checkpoint comparisons and finite experiment drivers. `curriculum` contains source manifests, teaching policies and generated-task definitions. `tests` contains implementation regressions. `experiments` contains public measurement records. `runs` and `private` hold local evidence and material excluded from public version control.

The [engineering specification](KAVI_ENGINEERING_SPECIFICATION.md) connects these modules to their equations, experiment records and limitations.
