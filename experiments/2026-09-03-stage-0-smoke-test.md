# S0 smoke test: bounded hard-pathway trace

Experiment ID: S0-2026-09-03-01
Date: 2026-09-03
Source revision: d2eb577
Author: Arnav123-s
Status: completed smoke test; negative and positive results both retained

## Hypothesis

The first executable pathway fabric can show, under a finite resource budget:

1. strict type-compatible routing;
2. two correlated facets meeting at a typed join;
3. constructive versus destructive complex-number interference;
4. positive, negative, and neutral verifier-feedback paths;
5. candidate-only parameter updates checked on independent protected and
   held-out manifests;
6. a user-owned stop control.

This experiment does not test general intelligence, language understanding,
scientific reasoning, autonomy, or the Riemann hypothesis.

## Data and provenance

The curriculum was generated locally from seeded addition/subtraction examples.
The verifier used exact arithmetic computed locally. No web data, personal
inputs, textbook content, model weights, external services, or network access
were used. The protected and held-out manifests are fixed in the source and are
separate from the current generated event.

## Configuration

Command:

    python -u -m kavi live --steps 18 --seed 7 --workers 1 --max-active-routes 2 --conflict-every 5 --interval-ms 700 --ask 7 5 add

Runtime controls:

- finite step limit: 18;
- active facet-route limit: 2;
- independent evaluator workers: 1;
- configured visible interval: 700 milliseconds;
- no pause or stop file was present for this run.

Environment observed before the run:

- Python 3.13.5;
- Windows 11, 64-bit;
- Intel Core i7-10870H, 8 cores / 16 logical processors;
- 32 GB system memory;
- NVIDIA GeForce GTX 1650 Ti with approximately 4 GB dedicated memory.

The prototype was CPU-first. It did not invoke the GPU, install packages, alter
thermal settings, create a background service, or close applications.

## Checks before execution

    python -m unittest discover -s tests -v

Result: 6 tests passed in 0.008 seconds.

The test set covered hard type rejection, deterministic routing, constructive
and destructive joins, candidate-error reduction, explicit route-budget
abstention, and a pre-existing stop-file control.

## Observed trace result

The finite run completed all 18 events.

| Measurement | Observed value |
|---|---:|
| Candidate updates promoted | 4 |
| Correct answers before feedback | 1 |
| Explicit abstentions | 3 |
| Constructive join interference | approximately +1.843 |
| Deliberately destructive join interference | approximately -1.843 |
| Persistent state ledger estimate | 35 scalar values |
| Active pipes during a two-facet inference | 4 |
| Estimated transient state while answering | approximately 128 bytes |

The command was configured with 12.6 seconds of visible inter-event delay.
Observed command wall time was approximately 20.8 seconds including terminal
setup and streaming overhead.

The final same-process query produced:

    7 + 5 = 9; confidence=0.67; uncertainty=0.33

That answer is wrong. The result must not be described as successful arithmetic
learning.

## Failures and limitations

1. After 18 examples, the readout had not learned addition robustly. It
   sometimes improved its candidate metrics but still failed a simple unseen
   addition query.
2. The current strict exact-accuracy retention gate can reject a candidate that
   improves continuous error while reducing an accidental early rounded exact
   answer. This is a candidate-policy question for a separate, predeclared
   follow-up experiment; it was not changed during this run.
3. The live display wrote hard paths as 4/2, mixing four active pipes with the
   two-route cap. The underlying cap was respected, but the label is confusing
   and needs a separate UI-only correction.
4. Resource values are deliberately small model-state estimates, not full
   process-memory or thermal measurements.

## Decision

Keep this revision as a measured baseline. Do not scale the curriculum or claim
capability from it. Before the next gate, define and test a promotion policy
that handles early continuous learning without weakening protection of
established exact skills. Keep the evaluator, stop control, device budget, and
source code outside the learner's authority.
