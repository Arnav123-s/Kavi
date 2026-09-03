# Kavi implementation stage 0: observable hard-pathway testbed

Author: Arnav123-s
Status: implemented prototype; no broad intelligence claim

## What is implemented

This is the first executable slice of the Kavi design. It is intentionally
small enough to inspect and falsify:

1. A pathway fabric is the learner. Four typed pipes plus one readout path are
   the whole active model for this experiment; there is no hidden general neural
   network behind a router.
2. One arithmetic event splits into lawful quantity and relation facets. Each
   facet can travel only through pipes whose type and operation scope match.
3. Dijkstra's algorithm chooses the deterministic lowest-cost compatible route.
   It is a routing policy, not a claim that shortest paths solve cognition.
4. A typed join keeps both facets tied to the same event/correlation key and
   computes ordinary complex-number interference. A destructive join abstains
   rather than quietly averaging a contradictory signal.
5. An exact arithmetic verifier produces one of three visible feedback paths:
   positive (correct), negative (wrong), or neutral (abstained).
6. A negative result creates an in-memory candidate that changes only the
   active readout path. The separate evaluator compares it with the frozen
   parent on protected and held-out manifests before promotion.
7. The live CLI streams paths, join state, answer, verifier result, candidate
   decision, and an explicit small state estimate.

The complex amplitudes are a classical numerical emulation of selected
phase/interference behaviour. They are not physical quantum computation and do
not provide a quantum-speed claim.

## Deliberate limits

- This does not implement a frontier general model, web learning, autonomous
  source-code modification, background persistence, or an unstoppable agent.
- The learner has only a small generated addition/subtraction curriculum and
  exact arithmetic verifier. It cannot yet understand arbitrary natural
  language, textbooks, science, or mathematical research.
- Resource values in the trace are explicit model-state estimates, not a claim
  to measure all Python or operating-system memory.
- Inference is serial-first. At most two evaluator workers may score
  independent test cases; this is deliberately separate from the causal path
  microsteps.

## Run it

From C:\Kavi:

    python -m unittest discover -s tests -v
    python -u -m kavi paths
    python -u -m kavi live --steps 24 --seed 7 --ask 7 5 add

The live command is finite by default. It does not create a background process,
write a training log, access the network, install anything, or alter thermal
limits.

### User controls

    python -u -m kavi live --steps 100 --pause-file C:\Kavi\PAUSE --stop-file C:\Kavi\STOP

- Create C:\Kavi\PAUSE to pause safely. Remove it to continue.
- Create C:\Kavi\STOP to stop before the next event.
- Kavi never creates, deletes, or ignores either control file.

## Ordered next gates

The code follows the existing K-HPC and quantum-flow documents. It does not
skip straight to structural self-modification.

| Gate | Candidate | Required evidence before the next gate |
|---|---|---|
| S0 | This exact generated arithmetic trace | tests pass; routes are type-safe; stop control works |
| Q0 | One real-valued hard pipe baseline | equal-budget accuracy/coverage/resource record |
| Q1 | Verified mid-pipeline port | measured benefit vs. Q0 |
| Q2 | Two-facet typed join | transfer and conflict handling vs. Q1 |
| Q3 | Bounded correlation state | benefit after its temporary cost is counted |
| Q4 | This classical phase/interference behaviour | benefit over Q3, not just a visual novelty |
| Q5 | Candidate-only local coupling/phase adaptation | retention and held-out checks vs. global-gradient baseline |
| H2/H3 | Budgeted adapters, then consolidation | verified coverage gain per byte and microstep |
| broader curriculum | Carefully sourced educational material | provenance, permissions, held-out tests, and an independent evaluator |

A failed gate is a result, not permission to redefine the score or make the
learner rewrite its evaluator, limits, or source code.
