# Kavi evaluation protocol

Author: Arnav123-s
Status: structural-circuit protocol and preserved earlier prototype acceptance rules

## Purpose

Predeclare tests, resource budgets, baselines and candidate-selection rules.
Record per-case outputs and all attempted candidates. The full experimental
design is in section 13 of the [engineering specification](KAVI_ENGINEERING_SPECIFICATION.md).

## Structural circuit protocol

The implemented [runtime](CIRCUIT_RUNTIME.md) uses 81 foundation cases, 48 repair cases and 127 independent final cases for each declared seed. Both foundation and repair banks affect selection. The accepted graph is sealed before the reserved bank, exhaustive eight-bit audit, longer-input tests and local invariant check. The complete exhaustive audit overlaps training and is labeled accordingly.

Every candidate must preserve the foundation bank and satisfy the repair bank. Final evaluation cannot alter the graph. Teaching examples and search catalogs are unavailable to deployed inference. A first result is recorded in [structural acquisition and repair](../experiments/2026-09-05-circuit-learning.md).

The principal measurements are exact correctness, per-case gains and regressions, gate and frame evaluations, complete candidate simulation counts, verifier calls, encoded model bytes, search time, process memory and external evidence storage. A local eight-row identity check is evaluated only after selection; its induction argument depends on the documented executor. No broad retention or calibrated-confidence claim follows from the finite trial.

## Procedure library protocol

The newer [procedure-library protocol](PROCEDURE_LIBRARY_RUNTIME.md) seals each complete selected library before final evaluation, and reports task-level withheld, audit and transfer results. Its comparison with base-only addition/subtraction uses the same per-task examples and ceilings but a different bounded vocabulary. Retention is checked under immutable earlier definitions. The [scaling follow-up](SCALING_LESSON_PROTOCOL.md) was designed after observing the first trial; new seeds and larger probes do not make it a blind replication. The [advanced capability protocol](ADVANCED_CAPABILITY_PROTOCOL.md) sets separate requirements for subject-level assessment.

## Earlier arithmetic prototype partitions

The earlier stage-0 arithmetic harness has three distinct partitions.

| Partition | Role | Current location |
| --- | --- | --- |
| Current event | The specific event that proposed a local update. | `ArithmeticCurriculum` |
| Protected manifest | Earlier fixed cases that must not regress. | kavi.learning.protected_manifest. |
| Held-out manifest | Fixed combinations used to accept or reject updates; development validation. | kavi.learning.held_out_manifest. |

Despite its code name, `held_out_manifest` participates in candidate acceptance.
It is a validation set. A final confirmation bank must remain separate from
training and selection. Record exposure whenever a reserved question is used
to teach or select a change.

The protected and held-out manifests are intentionally tiny because this is a
prototype. Passing them demonstrates only the stated narrow property. It does
not establish general arithmetic competence or broader reasoning ability.

## Measurements

For every parent and candidate, record:

- Cases: number of cases evaluated.
- Answered: number of non-abstaining answers.
- Correct: exact rounded answers equal to targets.
- Exact accuracy: correct divided by cases.
- Coverage: answered divided by cases.
- Mean absolute error: total absolute raw-answer error divided by cases.
- Candidate decision: promoted or rejected.
- Persistent scalar count, active pipes, and estimated transient bytes from the
  prototype ledger.
- Elapsed time, interpreter version, device configuration, and configuration
  parameters whenever an experiment record is made.

For later stages, add source provenance, numerical precision, peak process
memory, peak working memory, energy or thermal measurements where available,
and every external state required for reproduction.

## Target-only acceptance rule

The target-only learner promotes a candidate only when all of the following
are true:

1. The candidate’s raw error on the current event is lower than the parent’s.
2. Protected-manifest exact accuracy does not decrease.
3. Protected-manifest mean absolute error does not increase.
4. Held-out-manifest mean absolute error does not increase.

Otherwise the parent remains untouched. An abstention receives neutral
feedback and does not invent an update merely to avoid an uncertain output.

## Explanation-learning acceptance rule

An explanation must first pass its local verifier and refer to the same event
that produced the inference. Its rule may guide a candidate but cannot promote
one directly.

The explanation variant requires lower current error and no increase in
protected or held-out mean absolute error. Once the parent has reached its
declared protected-accuracy floor, candidate exact protected accuracy also may
not decrease. This protects a mature exact skill from being traded for a
slightly better continuous score.

## Experimental comparison rule

To compare mechanisms, hold constant whenever possible:

- Curriculum generator and seed.
- Current, protected, and held-out partitions.
- Initial parameters and numerical precision.
- Step limit, active-route limit, evaluator-worker limit, and device state.
- Acceptance policy and definitions of all metrics.

Change one declared mechanism at a time. A mechanism that wins only by using a
larger uncounted cache, different data, a more forgiving test, or a changed
evaluator has not made a fair improvement.

## Failure handling

Record rejection, abstention, route incompatibility, evaluator disagreement,
resource overflow, rights-review failure, and inability to reproduce as
results. Do not silently retry until a preferred result appears. A later run
may investigate a failure, but it must name the changed hypothesis and retain
the earlier record.

## What would justify a next stage

A future stage needs a written mechanism, a source and rights gate, a new
curriculum boundary, a larger fixed evaluation plan, a measured resource budget,
and independent review of its evaluator. It must improve a predeclared metric
without unacceptable retention, transfer, or resource regressions.

For proposed repeated growth and consolidation, also follow
[GROWTH_CYCLES.md](GROWTH_CYCLES.md).
