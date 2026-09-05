# Procedure library runtime

Author: [Arnav123-s](https://github.com/Arnav123-s)

The second structural experiment extends the learned addition circuit with acquired subtraction and a library of executable programs. A teacher turns selected arithmetic ideas into formal examples. The learner chooses program structure; it does not read the source prose. This is an algorithmic foundation experiment. University or graduate competence requires separate subject-level assessment and is not established by these tasks.

## Architecture

| Module | Responsibility |
| --- | --- |
| `procedure_core.py` | Typed library records, strict serialization, acquired calls, bounded iteration and actual traces |
| `procedure_search.py` | Bottom-up program search, measured candidate work and ephemeral search caches |
| `library_curriculum.py` | Source fingerprints, teacher references, task partitions and independent test generators |
| `library_runtime.py` | Reviewed budgets, comparisons, append-only retention, selection locks and final evaluation |
| `library_cli.py` | CLI learning, library inspection, controls and standalone queries |
| `learning_window.py` | Visible preparation, operator start, process transcript, pause/stop and saved-procedure queries |

The first addition graph is imported as a declared acquired prerequisite. The learner acquires a subtraction transition from 48 examples with nonnegative answers. Both are stored as gate circuits. Subsequent programs can call previously acquired procedures, repeat a binary procedure with a fixed step value, or fold it over the integers from one through a supplied count.

The instruction forms are `arg`, `const`, `call`, `repeat` and `range`. Constants are zero and one. Input signatures, natural-number types, operation names, iteration semantics and curriculum order are supplied. The learner selects callees, argument expressions, nesting and iteration operands within that language. A selected iteration program is not evidence that the learner invented iteration itself.

Programs refer only to earlier definitions. Calls are pure and values are bounded to 4,096 bits. Inference limits separately bound calls, gate evaluations, nested iterations and depth. Temporary values and traces disappear after a query. Runtime limits can reject a mathematically valid input that is too costly for a selected algorithm.

## Acquisition and comparisons

Search builds expressions in increasing instruction-tree size. The declared tie order visits recent acquired procedures first, then repeated and indexed iteration forms. Candidate outputs on the selection bank are cached outside the deployed model. One representative per observed output vector is retained. This is a search heuristic based on teaching behavior, not a proof of semantic equivalence or a complete search of all programs.

A program is accepted only after fresh execution matches every teaching target. Counters include candidate programs, candidate cases, cache hits and misses, executed calls and gates, invalid candidates and final verification. Failed executions preserve partial cost. Each task has finite time, candidate and instruction budgets; unsuccessful tasks remain in the report.

Each task is also searched with only the acquired addition and subtraction circuits available. The same examples, syntax, instruction budget and resource ceilings are used. The vocabulary differs by design. This ablation tests access to acquired procedures; the two bounded hypothesis classes are not equally expressive. Failure of the base-only condition is not a general lower bound on learning without libraries. Recency order and the enlarged vocabulary can also make library search slower.

The curriculum attempts doubling, three-input sum, tripling, adjusted difference, multiplication, square, power, triangular sum, factorial and sum of squares. The teacher's exact operations are unavailable to inference. Elementary mathematical targets do not imply broad mathematical understanding.

## Sources and partitions

The exact local De Morgan witness is verified against `curriculum/arithmetic-original.json` and its admitted source record. Selected paragraphs are 28–30, 35–38, 39–41, 47–49 and 206–207. The run records extract fingerprints and keeps source text in its ignored directory. Power, triangular sums and sum of squares are separately authored composition probes; they are not attributed as quotations from these excerpts.

All task selection finishes before final evaluation begins. The selected library is sealed by its canonical hash. Withheld same-domain cases, finite exhaustive audits and larger-input probes are separate fields. Audits overlap teaching domains and are labeled accordingly. Failed acquisitions and execution-limit errors are recorded, including both operand orders for large-input multiplication. A repeated-addition implementation may handle one order and exhaust its iteration budget in the other.

Earlier procedure definitions remain unchanged during this experiment. Protected teaching banks are checked after each accepted extension. This establishes retention under append-only growth; it does not establish safe changes to shared earlier definitions. A post-selection eight-row subtraction identity check is also recorded. Its composition argument is not formal verification of the host implementation.

## Storage hypothesis

Record canonical model bytes after every accepted stage, the marginal increase, and the acquired procedures actually exercised by later calls. Compare one shared library with the sum of independently packaged dependency closures for each operation. The latter is a packaging control, not an optimally compressed lower bound. Model files use canonical serialization so their file size agrees with the reported artifact size.

Graph reuse can reduce duplicated descriptions while execution, input size and temporary memory still grow. A small new procedure can express a large family of calculations. These facts do not establish that arbitrary future knowledge costs almost no additional storage. Measure the growth curve and transfer benefit across increasingly different tasks before making that claim.

## Declared live run

The [configuration](../curriculum/library-run.json) specifies three seeds, at most three program instructions, 20,000 candidates and 1,000,000 candidate cases per search, and ten seconds per program search. Total automatic work is limited to 900 seconds on one CPU process, with sampled thresholds of 512 MiB process memory and 128 MiB run-directory size. The inference fuel budget and the stricter search-execution budget are separate from these whole-run ceilings. Pauses count toward the whole-run wall limit. Preparation before Start is outside learning time.

Open the visible window with `scripts/start-live-library.ps1`, or:

```powershell
python -B -m kavi.learning_window --config curriculum/library-run.json --run-dir runs/library-trial
```

Inspect the configuration and press **Start teaching**. The same run is available in a terminal with `python -u -m kavi library run --config curriculum/library-run.json --run-dir runs/library-trial --interactive`. Use a new run directory. The window displays actual events and preserves its transcript after the finite worker finishes. Its controls request pause, resume or stop; closing it requests stop. A query operates on the latest saved library without further training.

```powershell
python -m kavi library inspect --library runs/library-trial/library.json
python -m kavi library ask --library runs/library-trial/library.json multiply 12 5 --trace
python -m kavi library status --run-dir runs/library-trial
python -m kavi library control --run-dir runs/library-trial pause
python -m kavi library control --run-dir runs/library-trial resume
python -m kavi library control --run-dir runs/library-trial stop
```

Each seed stores accepted stages, base-only libraries, search records, teaching banks, a selection lock, identity checks and final results. `events.jsonl`, `cases.jsonl`, `source-witness.json`, `environment.json`, `status.json` and `report.json` preserve the complete local evidence. A completed experiment can contain failed tasks; completion is not a mastery label.
