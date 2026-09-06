# Learning a usable multiplication order

Author: [Arnav123-s](https://github.com/Arnav123-s)

Revision: 5 September 2026

## Observation and hypothesis

The first procedure-library trial selected `multiply(a, b)` as adding `b` to zero `a` times. The operation gives correct values when it finishes, but its work grows with the numerical value of its first operand. A product with a large first operand can exceed its iteration budget even when reversing the operands would finish quickly. Powers and factorials inherit this cost when they pass their growing accumulator as that first operand.

The follow-up asks whether a small additional lesson can supply a useful alternative call order and improve downstream composition. It keeps the interpreter, graph operations, program language, search policy and execution limits fixed. No target multiplication implementation is added to inference.

## Teaching design

Insert a `scale(quantity, count)` lesson immediately before power. Its mathematical target is multiplication. The finite teaching universe has quantities `{0, 1, 16, 64, 256, 513, 1024, 2048}` and counts `0..7`. Of the 64 pairs, 24 are taught and 40 withheld. Fixed teaching anchors include `(0, 0)`, `(1, 1)` and `(1024, 2)`. The last case prevents an implementation that loops over the large quantity from satisfying the existing 512-iteration search limit.

The learner receives examples and the existing execution limit. It searches the same language of acquired calls and supplied iteration forms. An argument-swapping call is available as ordinary program structure; its arrangement is not given to search as a target. Both the shared-library and base-only conditions receive the added lesson. The experiment repeats acquisition from the declared addition prerequisite so all new search work is counted.

This is a curriculum change informed by the first trial's failures. It is not a blind replication or a paired comparison with identical teaching data. New seeds are 43, 59 and 73. Larger power probes use bases 17–20 and exponents 7–10; factorial probes use 15–18. They are distinct from the first trial's power and factorial transfer inputs. Earlier finite domain audits remain regression diagnostics. New random operands do not create new algorithm families.

## Measurements and expected limits

Record all successful and failed acquisitions, sealed final tests, calls and gate work, the added model bytes, and preserved earlier definitions. Compare downstream programs' actual dependencies: an improvement must execute the acquired scale procedure. The expected mechanism is a short wrapper that changes where the growing accumulator enters an earlier computation.

Both operand orders remain in multiplication and scale transfer tests. Learning a useful order for one task does not create an input-dependent choice of order. A wrapper may reverse which half of these probes fails. The original multiplication definition stays unchanged; this is append-only adaptation, not repair of a shared earlier definition. Efficient multiplication with two large operands requires a better algorithm or control structure.

The [configuration](../curriculum/library-scaling-run.json) retains three seeds, three program instructions, 20,000 candidates, 1,000,000 candidate cases and ten seconds per search. The whole-run ceiling remains 900 seconds, 512 MiB sampled process memory and 128 MiB of run files. All configured tasks finish before any final evaluation.

```powershell
python -B -m kavi.learning_window --config curriculum/library-scaling-run.json --run-dir runs/library-scaling-trial --start
```

Use this command for an already reviewed and authorized run. The visible window starts after opening and preserves pause, stop, its actual transcript and saved-procedure queries. The [runtime reference](PROCEDURE_LIBRARY_RUNTIME.md) gives the complete execution contract.
