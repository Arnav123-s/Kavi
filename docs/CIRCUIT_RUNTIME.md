# Discrete circuit learner

Author: [Arnav123-s](https://github.com/Arnav123-s)

Status: implemented. The experiment learns the operations and connections of a small streaming circuit from examples and corrections. The executor, search algorithm, gate vocabulary, input representation and curriculum are supplied. Learning those components themselves remains a later research problem.

## Architecture

| Component | Interface and responsibility |
| --- | --- |
| Teacher | Generates nonnegative integer operands and exact targets; owns the reference addition operation |
| Structural search | Proposes Boolean gate expressions and connections; rejects candidates using counterexamples |
| Candidate verifier | Executes the actual graph on teaching and protected cases |
| Circuit artifact | Stores gate kinds, source references and two output references; contains no teaching examples |
| Streaming executor | Reads two operand bits and one temporary state bit, executes the graph, emits a bit and updates the state |
| Final evaluator | Loads the sealed graph and measures independent cases without modifying it |
| CLI and records | Expose proposals, failures, accepted graphs, execution traces, controls and measurements |

The execution path is input encoding, repeated graph execution and output decoding. The learning path is candidate construction, verification, counterexample filtering and acceptance. Only the accepted graph becomes the deployed model. Search catalogs, teaching pairs, logs and evaluation records remain external artifacts.

## What is learned

The learner chooses `AND`, `XOR` and `NOT` gates, their input connections, and the references used for the emitted bit and next state. Identical subexpressions share a node when a candidate is compiled. This sharing is deterministic common-subexpression elimination. It is not yet learned abstraction across tasks.

There is no `ADD` gate and the executor never calls the teacher's addition function. The circuit cannot retrieve a teaching pair. Independently trained numerical edge multipliers and a neural proposal model are absent. Connection addresses and operation identifiers are stored information and count toward the artifact size.

The supplied inductive biases are substantial: two nonnegative integer inputs, least-significant-bit-first encoding, one state bit initialized to zero, a repeated processing loop, and one final frame with zero input bits. The task is acquisition of a transition circuit inside this executor. Discovery of iteration, representation, state capacity or an arbitrary program language is not measured here.

## Execution contract

References `0` through `4` name `left`, `right`, `state`, `zero` and `one`. Each later reference names a gate. Gates may reference only ports or earlier gates, so each frame is an acyclic computation. Both outputs observe the old state; the state update takes effect in the next frame.

Inputs must be nonnegative integers with at most 4,096 bits. The executor processes `max(bit_length(left), bit_length(right), 1) + 1` frames. It uses bit extraction and output assembly, and evaluates each stored gate once per frame. The graph description stays fixed as input length grows. Input storage, output storage and execution time still grow.

The model file uses the strict `kavi.discrete-circuit.v1` schema. Unknown fields, unknown operations, forward references, oversized graphs and incompatible execution contracts are rejected. Files larger than 64 KiB are rejected. Loading a graph does not execute arbitrary code.

## Learning and structural repair

The search constructs all 256 Boolean functions of three input bits from the gate vocabulary. Each function has an executable expression. Eight-bit truth masks accelerate candidate simulation during learning; they are not saved in the model or used by deployed inference.

The catalog retains one representative with minimum expression-tree gate count under its enumeration. It does not claim a globally minimum shared graph. Candidate pairs are compiled with shared subexpressions and restricted by the configured node budget. Ranking prefers fewer graph nodes, then smaller structural difference from the parent, then a deterministic function order.

For each proposal, the actual graph is checked on the current selection bank. A failed case refutes that procedure. The learner filters the remaining candidate procedures using that counterexample and repeats. It accepts a graph only when all current teaching and protected cases pass. Contradictory constraints or an exhausted search budget are recorded as failures.

The first phase uses examples without carries and fixes the next-state output to zero. The second phase enables the supplied state register's transition and introduces carry examples. That scheduled expansion of the search space is an engineered curriculum choice. The learner must discover how the state is updated and used.

A repair operates on the shared transition. The vocabulary cannot encode an arbitrary whole-operand answer table: its local expressions observe only the current two bits and one state bit. Success on a failing pair is checked alongside the protected domain, then on separate final inputs after selection is complete.

## Declared trial

The default configuration is [circuit-run.json](../curriculum/circuit-run.json).

| Setting | Value |
| --- | --- |
| Seeds | 7, 19, 31 |
| Teaching domain | Operands from 0 through 15 |
| Foundation bank | All 81 pairs with no overlapping set bits |
| Repair bank | 48 carry-producing pairs, including `1 + 1` |
| Independent same-width bank | The remaining 127 pairs |
| Exhaustive audit | All 65,536 pairs with operands from 0 through 255 |
| Length transfer | 16, 32, 64, 256 and 1,024 bits; six edge cases and 32 random pairs per width |
| Gate budget | 12 per candidate |
| Candidate limit | 65,536 possible pairs before the gate-budget restriction |
| Simulation limit | 1,000,000 candidate evaluations per learning phase |
| Wall-time limit | 180 seconds for the entire automatic run, including pauses |
| Process memory threshold | 512 MiB sampled working set |
| Run-directory threshold | 96 MiB sampled disk use |
| Device and workers | One CPU process; no numerical accelerator |

The exhaustive audit includes the selection domain, so its complete count is a domain audit rather than a wholly independent test count. The 127 reserved cases and the longer-input bank are independent of selection. Random transfer operands have the declared bit length. The graph hash is sealed before final evaluation, and the evaluator cannot trigger further learning.

A lookup control stores all teaching pairs and abstains on unknown pairs. Its coverage, correctness and serialized payload size are reported separately. The foundation circuit is the retention and structural-repair control. No superiority over a matched neural baseline is claimed by this experiment.

## Live CLI

From the repository root, start a finite run in a new directory:

```powershell
python -u -m kavi circuit run --config curriculum/circuit-run.json --run-dir runs/circuit-trial --interactive
```

The same interface is available as `python -m kavi.circuit_cli` or the installed `kavi-circuit` command. The PowerShell launcher `scripts/start-circuit.ps1` selects a fresh timestamped directory and opens the query console after the run. Pass `-Python` to select a particular interpreter.

The live stream shows catalog construction, candidate pathways, wrong outputs, counterexamples, remaining candidates, accepted graphs, final-test progress, regressions and run completion. Detailed JSON events preserve the fields behind each displayed line. No artificial delay is added to make learning appear gradual.

Use a second terminal to follow or control the selected run:

```powershell
python -m kavi circuit watch --run-dir runs/circuit-trial --follow
python -m kavi circuit status --run-dir runs/circuit-trial
python -m kavi circuit control --run-dir runs/circuit-trial pause
python -m kavi circuit control --run-dir runs/circuit-trial resume
python -m kavi circuit control --run-dir runs/circuit-trial stop
```

`PAUSE` and `STOP` files provide the same controls. A stop ends at the next control check and retains accepted models and available evidence. The wall-time limit continues while paused. Memory and disk limits are sampled guards, not operating-system quotas. A small amount of work may occur between checks.

After automatic work finishes, the optional console remains available for queries. It does not continue teaching in the background. It accepts `A + B`, `/trace A B`, `/circuit`, `/status`, `/pause`, `/resume`, `/stop` and `/quit`. The arithmetic command syntax is supplied parsing. Natural-language understanding and uncertain human-feedback interpretation are not implemented by this interface.

Standalone inspection and inference need only the model file:

```powershell
python -m kavi circuit inspect --model runs/circuit-trial/model.json
python -m kavi circuit ask --model runs/circuit-trial/model.json 255 1 --trace
python -m kavi circuit console --run-dir runs/circuit-trial
```

Trace rows show actual port bits, gate values, emitted bits and state transitions. Display is limited to 64 frames by default; execution still processes the complete input. Query output reports a computed value without claiming a calibrated probability of correctness.

## Evidence and invariants

Every final case records operands, target, learned prediction, foundation prediction and lookup prediction. Reports distinguish correct-to-correct, wrong-to-correct and correct-to-wrong transitions. Search measurements include every simulated candidate, executed candidate frame, proposal and verifier gate evaluation, including rejected candidates.

After selection, an independent check executes every combination of the two input bits and state bit and tests:

$$
e + 2c' = a + b + c.
$$

This is the local quantity-conservation identity for binary addition. If it holds for all eight rows, the zero initial state and documented framing support an induction argument for the whole operation. The final zero frame emits the remaining carry. The generated certificate records the eight checks and model hash. It is not a proof-assistant verification of the Python runtime, and it is never used to choose a candidate.

## Run artifacts

| File | Contents |
| --- | --- |
| `config.json`, `environment.json` | Budgets, seeds, interpreter, platform and source fingerprints |
| `events.jsonl`, `status.json` | Ordered learning events and current status |
| `search-catalog.json` | External function catalog used for structural search |
| `model.json` | Latest accepted graph, usable without the run directory |
| `seed-N/teaching.json` | External teaching bank |
| `seed-N/foundation.json`, `seed-N/learned.json` | Accepted procedure configurations |
| `seed-N/selection-lock.json` | Model fingerprint fixed before final evaluation |
| `seed-N/local-invariant.json` | Exhaustive local identity check after selection |
| `cases.jsonl`, `case-schema.json` | Per-case final evidence and column definitions |
| `seed-N/result.json`, `report.json` | Search costs, accuracy, retention, storage and resources |

All candidate filters are reproducible from the catalog, ranking rule and recorded counterexamples. The report counts simulated candidates; the event stream shows candidates proposed to the verifier. It does not print every discarded truth-mask pair. Full local run files remain under ignored `runs`; a compact experiment record belongs in `experiments`.

## Remaining architecture work

General language learning, autonomous invention of iteration or state capacity, learning the update rule, cross-task abstraction, noisy evidence, calibrated doubt and broad continual retention remain open. This implementation establishes a testable acquisition and repair mechanism for a deliberately small hypothesis class. Further stages should change one limitation at a time and retain independent final evaluation.
