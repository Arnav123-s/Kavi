# Structural acquisition and repair of addition

Author: [Arnav123-s](https://github.com/Arnav123-s)

Date: 5 September 2026

Source revision: `7908156e0241a9df4293e56231660fb234ca44de`

Experiment: `circuit-20260905-01`

## Question

Can a learner acquire a reusable addition transition using only Boolean gates, repair an incomplete shared procedure from counterexamples, and retain earlier correct behavior without a deployed answer table?

The implementation uses counterexample-guided search over circuits with two input bits, one temporary state bit and two output references. The teacher supplies whole-operand examples. The supplied gate vocabulary is AND, XOR and NOT. There is no ADD primitive or supplied target gate arrangement. The binary representation, processing loop, state capacity, output framing and search controller are engineered.

## Configuration and partitions

The run used the checked-in [configuration](../curriculum/circuit-run.json): seeds 7, 19 and 31; a 12-gate candidate limit; at most 65,536 candidate pairs and 1,000,000 candidate simulations per learning phase; a 180-second total wall-time limit; a sampled 512 MiB working-set threshold and 96 MiB run-directory threshold. Computation used one CPU process.

Each seed used all 81 four-bit pairs without overlapping set bits to acquire a foundation procedure. A second bank contained 48 carry-producing pairs, including a fixed first counterexample, `1 + 1`. The remaining 127 four-bit pairs were reserved for final confirmation. The foundation bank became a protection set during repair. Both banks influenced selection and are counted as exposed data.

After acceptance, the graph hash was sealed. Final evaluation checked the 127 reserved pairs, all 65,536 eight-bit pairs, and 190 larger-input cases. The larger cases used 16, 32, 64, 256 and 1,024 bits, with six fixed edge cases and 32 random pairs at each width. Random operands have the stated bit length. The exhaustive audit overlaps the selection domain; its whole denominator must not be described as independent unseen data.

## Results

| Seed | Gates / model bytes | Unseen 4-bit pairs | Exhaustive 8-bit pairs | Longer inputs | Audit regressions |
| --- | --- | --- | --- | --- | --- |
| 7 | 5 / 321 | 127 / 127 | 65,536 / 65,536 | 190 / 190 | 0 |
| 19 | 5 / 321 | 127 / 127 | 65,536 / 65,536 | 190 / 190 | 0 |
| 31 | 5 / 321 | 127 / 127 | 65,536 / 65,536 | 190 / 190 | 0 |

All three seeds selected the same graph, with SHA-256 `73f10ae9b5bd8fd01fc66fad37dbd1f9b661ef8d56dfc46857b56fbb21740b17`. Its 321-byte serialization contains only the execution contract, gates, connections and outputs. The saved [circuit](circuit-20260905-model.json) can be loaded without any teaching records. The [machine-readable report](2026-09-05-circuit-learning.json) contains the measured counters and source fingerprints.

The learned transition is:

```text
g0 = XOR(left, right)
g1 = XOR(g0, state)
g2 = XOR(left, state)
g3 = AND(g0, g2)
g4 = XOR(g3, left)
emit = g1
next_state = g4
```

The foundation was a one-gate XOR circuit with the next-state output fixed to zero. It passed all 81 protection cases but failed `1 + 1`. On the eight-bit audit it answered 6,561 cases correctly. Repair increased that count to 65,536, correcting 58,975 cases and breaking none of the 6,561 earlier correct cases. This is an exhaustive finite-domain retention result.

The lookup control retained 129 teaching pairs in an external table. It answered none of the 127 reserved pairs or 190 longer-input cases. On the exhaustive audit it answered 129 cases, all correctly. Its serialized payload was 1,188 to 1,193 bytes, excluding the lookup interpreter. The 321-byte circuit size likewise excludes its executor. These are explicit representation controls, not a comparison with a trained neural baseline.

## Learning cost

| Seed | Foundation counterexamples | Repair counterexamples | Candidate simulations, both phases | Repair seconds |
| --- | --- | --- | --- | --- |
| 7 | 2 | 6 | 83,353 | 0.297 |
| 19 | 1 | 6 | 71,151 | 0.297 |
| 31 | 1 | 6 | 73,183 | 0.296 |

Catalog construction enumerated all 256 three-input Boolean functions through 14,306 binary expression combinations, reaching expression-tree cost seven. It took approximately 0.047 seconds and was shared across seeds. The gate budget admitted 65,438 recurrent candidate pairs per repair phase. Each repair proposed seven candidates to the verifier; six were refuted before acceptance.

Counterexample counts are not complete data-exposure counts. Accepted procedures were checked on the full 129-case selection bank, and earlier proposals were checked until a failure. The report records those verifier executions and candidate simulations separately. At acceptance, two candidates remained consistent with the accumulated counterexamples for seeds 7 and 19, and five for seed 31. Only the selected candidate was verified against the complete selection bank. The selected graph also reflects the declared complexity ranking; the examples did not uniquely identify it through the counterexamples alone.

The complete run took 5.281 seconds wall time and 5.219 seconds process CPU time using Python 3.12.14 on Windows. Peak process working set was 33.51 MiB. Recorded case data occupied 8,371,250 bytes; the run directory occupied approximately 8.32 MiB before the final report write. These quantities include the external experimental harness, not just the learned circuit. Temperature and energy consumption were not measured. Short intervals are limited by clock resolution and are not standalone speed benchmarks.

## Local correctness check

After model selection, an independent check tested all eight local input/state combinations against `emit + 2*next_state = left + right + state`. All eight held for every selected graph. Together with zero initial state, one final zero-input frame and the documented executor semantics, this identity supports an induction argument for addition over longer bit strings. The runtime accepts inputs up to 4,096 bits; the declared three-seed transfer trial reached 1,024 bits.

This is an exhaustive check of a local invariant with a mathematical argument for composition. It is not a proof-assistant verification of the Python implementation. The check did not participate in selection. Unit tests separately exercise serialization, isolated inference, long carries, invalid graphs, contradictory teaching signals, pause/stop controls and budget exhaustion. All 153 repository tests passed before this run.

## Interpretation

The run demonstrates acquisition of a compact operation and a shared repair inside a small, explicitly defined hypothesis class. An incomplete operation became a complete binary-addition transition through structural selection; inference does not recall the examples that caused the repair.

The one-bit state register and processing loop were supplied, and their availability was expanded on a fixed curriculum schedule. The learner did not invent its representation, learning algorithm, state capacity or iteration. Common-subexpression sharing was performed by the compiler. General library learning, language interpretation, calibrated doubt, uncertain human-feedback learning and open-ended structural development remain unimplemented. The experiment establishes no advantage over a matched modern neural model and no broad intelligence result.

## Reproduction and live inspection

From the repository root:

```powershell
python -B -m unittest discover -s tests -q
python -u -m kavi circuit run --config curriculum/circuit-run.json --run-dir runs/circuit-reproduction --interactive
python -m kavi circuit ask --model experiments/circuit-20260905-model.json 12345 67890 --trace
```

The run directory must be new. The console accepts addition queries, `/trace`, `/circuit`, `/status` and control commands. The complete original local evidence is under `runs/circuit-20260905-01`; public source fingerprints and compact results are sufficient to identify the implementation and reproduce the declared experiment. See the [runtime reference](../docs/CIRCUIT_RUNTIME.md) for controls, artifacts and limitations.
