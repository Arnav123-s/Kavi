# Kavi evaluation protocol

Author: Arnav123-s
Status: binding protocol for the current prototype; extend by explicit revision for later stages

## Purpose

Predeclare tests, resource budgets, baselines and candidate-selection rules.
Record per-case outputs and all attempted candidates. The full experimental
design is in section 13 of the [engineering specification](KAVI_ENGINEERING_SPECIFICATION.md).

## Test partitions

The current arithmetic harness has three distinct partitions.

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
